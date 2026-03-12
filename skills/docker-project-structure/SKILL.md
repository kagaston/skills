---
name: docker-project-structure
description: Project structure and workflow patterns for Docker-based projects including directory layout, justfile commands, CI pipelines, build/push scripts, tagging strategies, and docker-compose patterns. Use when setting up a Docker project, creating a container build pipeline, structuring a Docker-based repo, or adding Docker to an existing project.
argument-hint: "[project-name]"
---

# Docker Project Structure

Standard patterns for organising Docker-based projects -- from single-image repos to multi-service applications.

## Single-Image Project

For projects that produce one Docker image (tools, APIs, base images):

```
project-name/
├── Dockerfile                   # Image build definition
├── .dockerignore                # Exclude files from build context
├── scripts/
│   ├── bootstrap.sh             # Container provisioning script
│   └── build.sh                 # Build and push automation
├── justfile                     # Task runner
├── .github/
│   ├── workflows/
│   │   └── ci.yml               # Lint → Build → (Push)
│   ├── pull_request_template.md
│   └── ISSUE_TEMPLATE/
├── AGENTS.md
├── CONTRIBUTING.md
└── README.md
```

## Multi-Service Project

For projects with multiple containers (app + database + cache + worker):

```
project-name/
├── docker-compose.yml           # Service orchestration
├── docker-compose.override.yml  # Local dev overrides
├── services/
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── .dockerignore
│   │   └── src/
│   ├── worker/
│   │   ├── Dockerfile
│   │   ├── .dockerignore
│   │   └── src/
│   └── web/
│       ├── Dockerfile
│       ├── .dockerignore
│       └── src/
├── scripts/
│   └── init-db.sh               # Database initialisation
├── justfile
├── .env.example                 # Required env vars (no secrets)
└── README.md
```

## Adding Docker to an Existing Project

When a project already has source code and needs Docker support:

```
existing-project/
├── Dockerfile                   # At project root
├── .dockerignore                # Exclude dev files from context
├── docker-compose.yml           # Optional: for local dev with services
├── src/                         # Existing code (unchanged)
├── pyproject.toml               # Existing config (unchanged)
├── justfile                     # Add docker-* recipes
└── ...
```

## justfile Recipes

### Single-Image

```just
[private]
default:
    @just --list --unsorted

build version="latest":
    docker build -t org/image:{{version}} -t org/image:latest .

push version="latest":
    docker push --all-tags org/image

run:
    docker run -p 8000:8000 org/image:latest

lint-docker:
    hadolint Dockerfile

lint-shell:
    shellcheck scripts/*.sh

format-shell:
    shfmt -i 2 -ci -w scripts/

clean:
    docker image prune -f
```

### Multi-Service

```just
[private]
default:
    @just --list --unsorted

up:
    docker compose up -d

down:
    docker compose down

logs service="":
    docker compose logs -f {{service}}

build:
    docker compose build

rebuild:
    docker compose build --no-cache

shell service="api":
    docker compose exec {{service}} /bin/sh

lint-docker:
    @find . -name 'Dockerfile' -exec hadolint {} +

clean:
    docker compose down -v --rmi local
    docker image prune -f
```

## docker-compose.yml Patterns

### Development Stack

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: dev-only-password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

### Key Patterns

- **`depends_on` with `condition: service_healthy`** -- wait for database readiness, not just container start
- **Named volumes** -- persist data across container restarts
- **`env_file`** -- load environment from `.env` (gitignored)
- **`target: runtime`** -- use a specific multi-stage build target
- **Volume mounts** -- bind-mount source code for live reload in dev

### Override File

Use `docker-compose.override.yml` for local dev settings (auto-loaded by docker compose):

```yaml
services:
  api:
    volumes:
      - ./src:/app/src
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
```

## .env.example

Commit a template showing required variables (never commit actual `.env`):

```bash
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=app
POSTGRES_PASSWORD=

# Application
API_PORT=8000
LOG_LEVEL=INFO
SECRET_KEY=
```

## Build Scripts

### bootstrap.sh Pattern

A single provisioning script that runs in both root and non-root phases of a multi-stage build:

```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID == 0 ]]; then
    # Root phase: system packages, user creation, global deps
    apt-get update && apt-get install -y --no-install-recommends curl
    rm -rf /var/lib/apt/lists/*

    groupadd --gid 1000 app
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app
else
    # User phase: application-level setup
    pip install --no-cache-dir -r requirements.txt
fi
```

### build.sh Pattern

Automate tagging and pushing:

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly REPO="org/image"
readonly VERSION="${1:-latest}"

docker build -t "${REPO}:${VERSION}" -t "${REPO}:latest" .

if [[ "${PUSH:-false}" == "true" ]]; then
    docker push --all-tags "${REPO}"
fi
```

## Tagging Strategy

| Tag | When | Example |
|-----|------|---------|
| `latest` | Every build from main | `org/image:latest` |
| Semantic version | Tagged releases | `org/image:1.2.3` |
| Git SHA | Every CI build | `org/image:abc1234` |
| Branch | Feature testing | `org/image:feat-auth` |

```bash
docker build \
    -t "org/image:${VERSION}" \
    -t "org/image:latest" \
    -t "org/image:$(git rev-parse --short HEAD)" \
    .
```

## CI Pipeline

### GitHub Actions

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint Dockerfile
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile

      - name: Lint shell scripts
        uses: ludeeus/action-shellcheck@2.0.0
        with:
          scandir: scripts

  build:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t app:ci .

      - name: Scan for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: app:ci
          severity: CRITICAL,HIGH

  push:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            org/image:latest
            org/image:${{ github.sha }}
```

### Pipeline Stages

```
Lint (hadolint + shellcheck) → Build → Scan (trivy) → Push (main only)
```

Lint before build to fail fast. Scan after build to catch vulnerabilities before pushing.

## .dockerignore

Always create a `.dockerignore` to keep the build context small and prevent leaking files:

```
.git/
.github/
.idea/
.vscode/
*.md
!README.md
.gitignore
.dockerignore
.env
.env.*
justfile
Makefile
docker-compose*.yml
__pycache__/
*.pyc
node_modules/
.pytest_cache/
dist/
build/
*.log
```

## Verification Checklist

- [ ] Dockerfile at project root (or per-service under `services/`)
- [ ] .dockerignore excludes dev files, .git, .env, IDE configs
- [ ] justfile has build, lint-docker, and clean recipes
- [ ] CI pipeline: lint → build → scan → push
- [ ] hadolint passes on all Dockerfiles
- [ ] .env.example documents required environment variables
- [ ] Build scripts use `set -euo pipefail`
- [ ] Tagging strategy includes both version and latest
- [ ] docker-compose uses health checks for service dependencies
- [ ] No secrets committed (`.env` is gitignored, `.env.example` has no values)
