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

## Layered Image Hierarchy (Monorepo)

For uv workspace monorepos or projects where multiple images share a common base, use a layered `docker/` directory with a separate `containers/` directory for standalone workloads.

```
project-name/
├── app/                          # Workspace packages (source code)
│   ├── package-a/
│   │   ├── src/package_a/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── package-b/
│       ├── src/package_b/
│       ├── tests/
│       └── pyproject.toml
├── docker/                       # Build-time image hierarchy
│   ├── base/
│   │   └── Dockerfile            # Layer 0: python + uv + all workspace deps
│   ├── app-name/
│   │   └── Dockerfile            # Layer 1: FROM base, adds app config + CMD
│   └── docker-compose.yml        # Orchestrates all services
├── containers/                   # Standalone runtime containers
│   └── sandbox/
│       ├── Dockerfile            # Self-contained, does NOT extend base
│       └── entrypoint.sh         # Entry script for the container
├── pyproject.toml                # Root workspace config
├── uv.lock
├── .dockerignore
├── .hadolint.yaml
├── justfile
└── .env.example
```

### docker/ vs containers/

These directories serve different purposes:

| Directory | Purpose | Extends base? | Part of compose? |
|-----------|---------|---------------|------------------|
| `docker/` | Build hierarchy for the main application | Yes (layered) | Yes |
| `containers/` | Isolated, standalone containers for sandboxes, tools, sidecars | No (self-contained) | Optional (profiles) |

**`docker/`** holds the image layers that share a common base and compose into the main application stack. The base image installs uv, copies workspace `pyproject.toml` files, syncs deps, and copies source. Child images (`FROM base`) add config and entrypoints.

**`containers/`** holds standalone Dockerfiles for isolated workloads -- sandboxes, security scanners, one-off tools. These build independently and don't inherit from the base image. They're useful when you need process isolation, restricted permissions, or a different base entirely.

### Base Image Pattern

The base Dockerfile installs shared deps and copies all workspace package manifests before source code, maximizing layer cache:

```dockerfile
# docker/base/Dockerfile
FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Copy all workspace pyproject.toml files first (cached layer)
COPY pyproject.toml uv.lock ./
COPY app/package-a/pyproject.toml app/package-a/pyproject.toml
COPY app/package-b/pyproject.toml app/package-b/pyproject.toml

# Create stub __init__.py so uv can resolve workspace members
RUN for pkg in package_a package_b; do \
    mkdir -p "app/${pkg}/src/${pkg}" && \
    touch "app/${pkg}/src/${pkg}/__init__.py"; \
    done

ARG UV_INSECURE_HOST=""
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_INSECURE_HOST="$UV_INSECURE_HOST" \
    uv sync --no-dev --frozen 2>/dev/null || uv sync --no-dev

# Copy actual source (least-cached layer)
COPY app/ app/

RUN useradd -r -m -s /bin/false app
```

### Child Image Pattern

Child images reference the base by local tag, add app-specific config, and set the entrypoint:

```dockerfile
# docker/app-name/Dockerfile
FROM project-base:local

LABEL description="App description"

COPY config/ /app/config/
USER app
CMD ["uv", "run", "app-name", "serve"]
```

### Compose with Build Profiles

Use profiles to separate the build-only base from running services:

```yaml
services:
  base:
    build:
      context: ..
      dockerfile: docker/base/Dockerfile
    image: project-base:local
    profiles:
      - build

  app:
    build:
      context: ..
      dockerfile: docker/app-name/Dockerfile
    image: project-app:local
    container_name: project-app
    depends_on:
      base:
        condition: service_completed_successfully
    restart: unless-stopped

  sandbox:
    build:
      context: ../containers/sandbox
    image: project-sandbox:local
    profiles:
      - sandbox
    volumes:
      - sandbox_output:/workspace/output
```

### Standalone Container Pattern

Containers in `containers/` are self-contained -- they install their own deps and have their own entrypoint:

```dockerfile
# containers/sandbox/Dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl jq \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -r -m -s /bin/bash sandbox
WORKDIR /workspace
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER sandbox
ENTRYPOINT ["/entrypoint.sh"]
```

```bash
# containers/sandbox/entrypoint.sh
#!/usr/bin/env bash
set -euo pipefail

TASK="$1"
TIMEOUT="${TIMEOUT:-300}"
OUTPUT_DIR="${OUTPUT_DIR:-/workspace/output}"

mkdir -p "$OUTPUT_DIR"
timeout "$TIMEOUT" "$TASK" >"$OUTPUT_DIR/stdout.log" 2>"$OUTPUT_DIR/stderr.log" || true
echo '{"status": "complete"}' > "$OUTPUT_DIR/status.json"
```

## Dual Deployment Project (Compose + K8s)

For projects that support both Docker Compose (local dev) and Kubernetes (cluster deployment):

```
project-name/
├── docker-compose.yml           # Local development stack
├── k8s/
│   ├── namespace.yaml           # K8s namespace isolation
│   ├── configmap.yaml           # Shared configuration
│   ├── app-deployment.yaml      # App Deployment + Service
│   └── worker-deployment.yaml   # Worker Deployment
├── scripts/
│   └── setup.sh                 # One-command local bootstrap
├── justfile                     # up/down + k8s-apply/k8s-delete
├── .hadolint.yaml               # Dockerfile linting config
├── .yamllint                    # YAML linting config
├── AGENTS.md
├── CONTRIBUTING.md
└── README.md
```

The compose file and K8s manifests should mirror the same topology -- same services, same ports, same environment variables. Use ConfigMaps in K8s to hold the same values that `environment:` holds in compose.

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

### Layered Hierarchy

```just
compose := "docker compose -f docker/docker-compose.yml"

# Build the base image first, then all services
docker-build:
    docker build -f docker/base/Dockerfile -t project-base:local .
    {{compose}} build

# Build and start the full stack
up: docker-build
    {{compose}} up -d

down:
    {{compose}} down

logs service="":
    {{compose}} logs -f {{service}}

# Build a standalone container
container-build name:
    docker build -f containers/{{name}}/Dockerfile -t project-{{name}}:local containers/{{name}}/

# Lint all Dockerfiles (docker/ and containers/)
lint-docker:
    @find docker/ containers/ -name 'Dockerfile' -exec hadolint {} +

# Run the sandbox container on-demand
sandbox recipe:
    {{compose}} --profile sandbox run --rm goose-sandbox {{recipe}}

clean:
    {{compose}} down -v --rmi local
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

### Pre-Built Image Stack

When services use published images (no local Dockerfiles):

```yaml
services:
  app:
    image: org/app:1.2.3
    container_name: my-app
    hostname: app
    ports:
      - "8000:8000"
    networks:
      - app-network
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./config:/app/config:ro
      - ./data:/app/data

  worker:
    image: org/worker:1.2.3
    hostname: worker
    deploy:
      replicas: 2
    ports:
      - "9000"
    networks:
      - app-network
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      MASTER_HOST: app
      WORKER_MEMORY: 1G

  db:
    image: postgres:16-alpine
    networks:
      - app-network
    restart: unless-stopped
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s

networks:
  app-network:
    driver: bridge

volumes:
  pgdata:
```

### Key Patterns

- **`depends_on` with conditions** -- `service_healthy` waits for health, `service_started` waits for container start, `service_completed_successfully` waits for one-time jobs (migrations)
- **Named volumes** -- persist data across container restarts
- **`env_file`** -- load environment from `.env` (gitignored)
- **`target: runtime`** -- use a specific multi-stage build target for `build:`
- **Bind mounts** -- `./src:/app/src` for live reload in dev, `:ro` for read-only config
- **`restart: unless-stopped`** -- auto-restart on failure but not after manual stop
- **`deploy.replicas`** -- run multiple instances of stateless workers
- **`container_name` + `hostname`** -- predictable names for primary services; omit for replicated workers
- **Explicit networks** -- isolate service communication with named bridge networks
- **`start_period`** in healthchecks -- grace period before health failures count

### Healthcheck Patterns

| Service | Test command |
|---------|-------------|
| PostgreSQL | `pg_isready -U postgres` |
| MySQL | `mysqladmin ping -h localhost` |
| Redis | `redis-cli ping` |
| HTTP API | `curl -f http://localhost:8000/health \|\| exit 1` |
| Spark Master | `curl -f http://localhost:8080/ \|\| exit 1` |

### Profiles

Selectively enable optional services (monitoring, debugging):

```yaml
services:
  api:
    # always starts (no profile)

  grafana:
    image: grafana/grafana:latest
    profiles: [monitoring]
    ports:
      - "3000:3000"

  debug-tools:
    image: nicolaka/netshoot
    profiles: [debug]
```

```bash
docker compose up -d                          # core services only
docker compose --profile monitoring up -d     # core + grafana
docker compose --profile debug up -d          # core + debug tools
```

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

### Production Layering

Use multiple compose files to layer environments:

```bash
# Development (default)
docker compose up -d

# Production (overlay)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

```yaml
# docker-compose.prod.yml
services:
  api:
    restart: always
    deploy:
      replicas: 3
    environment:
      - LOG_LEVEL=WARNING
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
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

### setup.sh Pattern (Environment Bootstrap)

A single script that installs tools, starts the container runtime, and brings up the stack. Useful for projects where contributors need a one-command setup:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Full project bootstrap: install tools, start runtime, bring up services.
# Usage: ./scripts/setup.sh

echo "==> Checking prerequisites..."
command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh"; exit 1; }

echo "==> Installing tools..."
brew install --quiet just docker docker-compose

echo "==> Creating local directories..."
mkdir -p data logs

echo "==> Starting services..."
docker compose up -d

echo ""
echo "Done! Services are starting up."
echo "  App:  http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
```

### bootstrap.sh Pattern (Dockerfile Provisioning)

A single script that runs in both root and non-root phases of a multi-stage Docker build:

```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID == 0 ]]; then
    apt-get update && apt-get install -y --no-install-recommends curl
    rm -rf /var/lib/apt/lists/*

    groupadd --gid 1000 app
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app
else
    pip install uv && uv sync --frozen --no-dev
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

- [ ] Dockerfile at project root (or per-service under `docker/` or `services/`)
- [ ] .dockerignore excludes dev files, .git, .env, IDE configs
- [ ] justfile has build, lint-docker, and clean recipes
- [ ] CI pipeline: lint → build → scan → push
- [ ] hadolint passes on all Dockerfiles (both `docker/` and `containers/`)
- [ ] .env.example documents required environment variables
- [ ] Build scripts use `set -euo pipefail`
- [ ] Tagging strategy includes both version and latest
- [ ] docker-compose uses healthchecks with `start_period` for service dependencies
- [ ] `depends_on` uses `condition: service_healthy` (not bare `depends_on`)
- [ ] Services use `restart: unless-stopped` or `restart: always`
- [ ] Explicit named networks for service isolation
- [ ] K8s manifests mirror compose topology (if dual deployment)
- [ ] YAML files linted with yamllint
- [ ] No secrets committed (`.env` is gitignored, `.env.example` has no values)
- [ ] Layered hierarchy: `docker/base/` installs shared deps, child images use `FROM base`
- [ ] `containers/` holds standalone Dockerfiles that don't extend the base
- [ ] Base image copies `pyproject.toml` files before source code for layer caching
- [ ] Entrypoint scripts in `containers/` use `set -euo pipefail` and are `chmod +x`
- [ ] Compose profiles separate build-only and on-demand services
