---
name: dockerfile-best-practices
description: Writing production-grade Dockerfiles with multi-stage builds, security hardening, layer optimization, non-root users, and hadolint linting. Use when writing a Dockerfile, optimizing Docker image size, improving Docker security, or reviewing Docker configurations.
---

# Dockerfile Best Practices

Write Dockerfiles that produce small, secure, reproducible images. These practices apply to any language or framework.

## Multi-Stage Builds

Separate build-time dependencies from the final runtime image. This reduces image size by 50-80% and removes compilers, dev headers, and build tools from production.

```dockerfile
# Stage 1: Build
FROM python:3.12-slim AS build

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

COPY src/ ./src/

# Stage 2: Runtime
FROM python:3.12-slim AS runtime

COPY --from=build /app /app
WORKDIR /app

USER 1000
EXPOSE 8000
CMD ["python", "-m", "app.main"]
```

### Stage Naming

Use descriptive, uppercase `AS` aliases:

```dockerfile
FROM node:20-slim AS build
FROM node:20-slim AS runtime
FROM oraclelinux:9-slim AS base    # OS-level setup
FROM base AS app                   # Application layer
```

### Reusable Base Stages

When multiple stages share setup, create a common base:

```dockerfile
FROM python:3.12-slim AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

FROM base AS build
# build-time deps here

FROM base AS runtime
# runtime only
```

### Layered Image Hierarchy (Monorepo)

For uv workspace monorepos where multiple images share deps, build a base image that all child images extend. This avoids reinstalling the same workspace deps in every Dockerfile.

All Dockerfiles live in `containers/`. The base image is at `containers/base/Dockerfile`, child images at `containers/{name}/Dockerfile`, and standalone containers at `containers/{name}/Dockerfile` with their own entrypoint scripts. Compose and build config lives in `docker/`.

```dockerfile
# containers/base/Dockerfile — shared deps for all workspace packages
FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Copy workspace manifests first for layer caching
COPY pyproject.toml uv.lock ./
COPY app/pkg-a/pyproject.toml app/pkg-a/pyproject.toml
COPY app/pkg-b/pyproject.toml app/pkg-b/pyproject.toml

# Stub __init__.py so uv can resolve workspace members during sync
RUN for pkg in pkg_a pkg_b; do \
    mkdir -p "app/${pkg}/src/${pkg}" && \
    touch "app/${pkg}/src/${pkg}/__init__.py"; \
    done

# Corporate proxy support via build arg
ARG UV_INSECURE_HOST=""
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_INSECURE_HOST="$UV_INSECURE_HOST" \
    uv sync --no-dev --frozen 2>/dev/null || uv sync --no-dev

# Source code last (invalidates cache on every change)
COPY app/ app/
RUN useradd -r -m -s /bin/false app
```

```dockerfile
# containers/my-service/Dockerfile — extends base, adds config + entrypoint
FROM project-base:local
COPY config.yaml /app/config.yaml
USER app
CMD ["uv", "run", "my-service", "serve"]
```

Key patterns:
- **`UV_COMPILE_BYTECODE=1`** -- precompile `.pyc` for faster startup
- **`UV_LINK_MODE=copy`** -- copy files instead of hardlinks (works across Docker layers)
- **`ARG UV_INSECURE_HOST`** -- allows builds behind corporate TLS-intercepting proxies
- **`--mount=type=cache`** -- caches uv downloads across builds
- **Fallback sync** -- `uv sync --frozen 2>/dev/null || uv sync --no-dev` handles missing lockfile gracefully

## Layer Optimization

Docker caches layers. Order instructions from least to most frequently changing:

```dockerfile
# 1. Base image (rarely changes)
FROM python:3.12-slim

# 2. System dependencies (changes monthly)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Application dependencies (changes weekly)
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# 4. Application code (changes every commit)
COPY src/ ./src/
```

### Combine Related RUN Commands

Each `RUN` creates a layer. Combine related operations and clean up in the same layer:

```dockerfile
# Good: single layer, cleanup included
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Bad: cleanup in separate layer doesn't reduce size
RUN apt-get update && apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*
```

### pip and Package Manager Caching

Disable caches to reduce layer size:

```dockerfile
# Python
RUN python3 -m pip --no-cache-dir install -U package-name

# Node
RUN npm ci --omit=dev && npm cache clean --force

# Go
RUN go build -o /app && rm -rf /root/.cache/go-build
```

## Security

### Non-Root User

Never run containers as root. Create a dedicated user:

```dockerfile
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

USER app
```

For minimal images without `useradd`:

```dockerfile
USER 1000
```

### Pin Base Image Versions

Avoid `:latest` -- pin to specific versions for reproducibility:

```dockerfile
# Good: pinned
FROM python:3.12.3-slim
FROM node:20.14-alpine

# Acceptable: minor version pinned
FROM python:3.12-slim

# Bad: unpinnable
FROM python:latest
FROM ubuntu
```

### Pin Package Versions

```dockerfile
# Debian/Ubuntu
RUN apt-get install -y --no-install-recommends \
    curl=7.88.1-10+deb12u5

# Oracle Linux / RHEL
RUN microdnf -y install java-11-openjdk curl \
    && microdnf -y clean all

# Alpine
RUN apk add --no-cache curl=8.5.0-r0
```

### Remove Unnecessary Packages

```dockerfile
# Install only what's needed, clean up immediately
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

### No Secrets in Images

Never `COPY` secrets or embed them in `ENV`:

```dockerfile
# Bad
ENV API_KEY=sk-12345
COPY .env /app/.env

# Good: pass at runtime
# docker run -e API_KEY=sk-12345 myimage
```

Use BuildKit secret mounts for build-time secrets:

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
```

### Scan for Vulnerabilities

```bash
docker scout cves myimage:latest
trivy image myimage:latest
```

## Metadata

Use `LABEL` for image metadata (not the deprecated `MAINTAINER`):

```dockerfile
LABEL maintainer="team@company.com"
LABEL version="1.0.0"
LABEL description="API service for user management"
LABEL org.opencontainers.image.source="https://github.com/org/repo"
```

## ENTRYPOINT vs CMD

```dockerfile
# Use JSON array form (exec form) -- not shell form
# Good: runs as PID 1, receives signals properly
CMD ["python", "-m", "app.main"]
ENTRYPOINT ["python", "-m", "app.main"]

# Bad: runs via /bin/sh -c, won't receive SIGTERM
CMD python -m app.main
```

Use `ENTRYPOINT` for the main binary, `CMD` for default arguments:

```dockerfile
ENTRYPOINT ["python", "-m", "app.main"]
CMD ["--port", "8000"]
```

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

## .dockerignore

Exclude files that don't belong in the build context. This speeds up builds and prevents leaking sensitive files:

```
.git/
.github/
.idea/
.vscode/
*.md
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
.mypy_cache/
dist/
build/
*.log
```

## Linting with hadolint

[hadolint](https://github.com/hadolint/hadolint) catches Dockerfile anti-patterns and enforces best practices. It combines Dockerfile-specific rules with ShellCheck for inline shell commands.

```bash
# Install
brew install hadolint         # macOS
apt-get install hadolint      # Debian/Ubuntu

# Run
hadolint Dockerfile
```

### Key Rules

| Rule | What it catches |
|------|----------------|
| DL3007 | Using `:latest` tag |
| DL3008 | Not pinning apt package versions |
| DL3009 | Not cleaning apt cache after install |
| DL3025 | Using shell form for CMD (should be JSON) |
| DL3015 | Not using `--no-install-recommends` with apt-get |
| DL4006 | Not setting `SHELL` with pipefail for pipe commands |

### .hadolint.yaml

Place at project root to configure rules and trusted registries:

```yaml
ignored:
  - DL3008    # pin versions in apt-get (sometimes impractical)

trustedRegistries:
  - docker.io
  - ghcr.io

failure-threshold: warning
strict-labels: true
```

### CI Integration

```yaml
# GitHub Actions
- name: Lint Dockerfile
  uses: hadolint/hadolint-action@v3.1.0
  with:
    dockerfile: Dockerfile
```

### justfile

```just
lint-docker:
    hadolint Dockerfile
```

## Container Testing

Testing Docker images requires a layered approach -- static analysis catches structural issues, runtime tests catch real-world failures.

### Layered Validation

```
1. Lint (pre-build)     → hadolint validates Dockerfile syntax and best practices
2. Build               → docker build catches build errors
3. Scan (post-build)   → trivy / docker scout catches CVEs
4. Structure (static)  → container-structure-test validates filesystem, metadata, env vars
5. Runtime (dynamic)   → dgoss / testcontainers verifies the container actually works
```

### Container Structure Test

[container-structure-test](https://github.com/GoogleContainerTools/container-structure-test) validates static image properties without running the container:

```yaml
# structure-test.yaml
schemaVersion: "2.0.0"

metadataTest:
  exposedPorts: ["8888"]
  cmd: ["jupyter-lab"]
  user: "jupyter"

fileExistenceTests:
  - name: "workspace directory exists"
    path: /opt/workspace
    shouldExist: true
    permissions: "drwxrwx---"
    uid: 1000
    gid: 1000

commandTests:
  - name: "python3 is installed"
    command: "python3"
    args: ["--version"]
    expectedOutput: ["Python 3"]

  - name: "java is installed"
    command: "java"
    args: ["-version"]
    expectedError: ["openjdk version"]

envVarTests:
  - name: "JUPYTER_HOME is set"
    key: "JUPYTER_HOME"
    value: "/opt/workspace"
```

```bash
# Install
brew install container-structure-test  # macOS

# Run against a built image
container-structure-test test --image org/image:latest --config structure-test.yaml
```

### dgoss (Runtime Contract Testing)

[dgoss](https://github.com/goss-io/goss) tests containers by actually running them, verifying ports, processes, and files at runtime:

```yaml
# goss.yaml
port:
  tcp:8888:
    listening: true

process:
  jupyter-lab:
    running: true

user:
  jupyter:
    exists: true
    uid: 1000

file:
  /opt/workspace:
    exists: true
    owner: jupyter
    filetype: directory

command:
  python3 --version:
    exit-status: 0
    stdout:
      - "Python 3"
```

```bash
# Install goss + dgoss
curl -fsSL https://goss.rocks/install | sh

# Run against a Docker image
dgoss run -p 8888:8888 org/image:latest
```

### Testcontainers (Integration Tests)

[Testcontainers](https://testcontainers.com) spins up real containers for integration tests in application code:

```python
# Python
from testcontainers.postgres import PostgresContainer

def test_database_migration():
    with PostgresContainer("postgres:16-alpine") as postgres:
        engine = create_engine(postgres.get_connection_url())
        run_migrations(engine)
        assert table_exists(engine, "users")
```

```go
// Go
func TestAPIWithDatabase(t *testing.T) {
    ctx := context.Background()
    pg, err := postgres.Run(ctx, "postgres:16-alpine")
    assert.NoError(t, err)
    defer pg.Terminate(ctx)

    connStr, _ := pg.ConnectionString(ctx)
    // test against real database
}
```

### justfile

```just
test-structure:
    container-structure-test test --image org/image:latest --config structure-test.yaml

test-runtime:
    dgoss run org/image:latest

test-docker: build test-structure test-runtime
```

## Base Image Selection

| Use case | Recommended base | Size |
|----------|-----------------|------|
| Python API | `python:3.12-slim` | ~150 MB |
| Node.js API | `node:20-alpine` | ~130 MB |
| Go binary | `gcr.io/distroless/static` | ~5 MB |
| Java | `eclipse-temurin:21-jre-alpine` | ~100 MB |
| General Linux | `ubuntu:24.04` or `debian:bookworm-slim` | ~75 MB |
| Minimal RHEL | `oraclelinux:9-slim` with microdnf | ~110 MB |

Prefer `-slim` or `-alpine` variants. Use distroless for maximum security when you don't need a shell.

## Standalone Container Pattern (containers/)

Standalone containers live in `containers/{name}/` and are self-contained -- they don't extend the project's base image. Use them for sandboxes, one-off tools, security scanners, or any workload that needs process isolation.

```dockerfile
# containers/sandbox/Dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
RUN useradd -r -m -s /bin/bash sandbox
RUN mkdir -p /workspace/output && chown -R sandbox:sandbox /workspace

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER sandbox
ENTRYPOINT ["/entrypoint.sh"]
```

Pair each Dockerfile with an `entrypoint.sh`:
- `set -euo pipefail` at the top
- Accept the task as the first argument
- Use `TIMEOUT` env var with a default for bounded execution
- Write output to `OUTPUT_DIR` (default `/workspace/output`)
- Write a `status.json` on completion

## Verification Checklist

- [ ] Multi-stage build separates build and runtime
- [ ] Non-root user in final stage
- [ ] Base image version pinned (not `:latest`)
- [ ] Layer order: system deps → app deps → app code
- [ ] `--no-install-recommends` for apt, `--no-cache` for apk
- [ ] Package caches cleaned in same RUN layer
- [ ] No secrets in image (ENV, COPY)
- [ ] CMD/ENTRYPOINT use JSON array form
- [ ] .dockerignore excludes .git, .env, IDE files, docs
- [ ] `hadolint` passes (with `.hadolint.yaml` if custom rules needed)
- [ ] LABEL metadata present (maintainer, version)
- [ ] Container structure tests validate metadata, files, and env vars
- [ ] Runtime tests verify ports, processes, and user after container starts
- [ ] Vulnerability scan (trivy/docker scout) runs in CI
- [ ] Layered base image copies pyproject.toml manifests before source for cache efficiency
- [ ] `UV_COMPILE_BYTECODE=1` and `UV_LINK_MODE=copy` set in base image
- [ ] Standalone containers in `containers/` are self-contained (no `FROM base`)
- [ ] Entrypoint scripts in `containers/` use `set -euo pipefail` and write status.json
