# Pre-commit Hook Scripts and Configs

Complete hook scripts and pre-commit framework configurations for the `.hooks/` + `development/` pattern.

## Hook Scripts

### .hooks/pre-commit (dispatcher)

```sh
#!/bin/sh
echo "[+] Running pre-commit checks"
for script in .hooks/pre-commit-*; do
  if [ -f "$script" ]; then
    $script
    result=$?
    if [ $result -ne 0 ]; then
      exit $result
    fi
  fi
done
echo "[+] Done with pre-commit checks"
```

### .hooks/pre-commit-py (Python-specific)

```sh
#!/bin/sh
exec 1>&2
REPO_ROOT="$(git rev-parse --show-toplevel)"
if [ -n "$(git diff --cached --name-only --diff-filter=ACM | grep -e '\.py$')" ]; then
  uv run pre-commit run --config "${REPO_ROOT}/development/.pre-commit-config-py.yaml"
fi
```

### .hooks/pre-commit-yaml (YAML-specific)

```sh
#!/bin/sh
exec 1>&2
REPO_ROOT="$(git rev-parse --show-toplevel)"
if [ -n "$(git diff --cached --name-only --diff-filter=ACM | grep -e '\.yaml$' -e '\.yml$')" ]; then
  uv run pre-commit run --config "${REPO_ROOT}/development/.pre-commit-config-yaml.yaml"
fi
```

### .hooks/pre-push (dispatcher)

```sh
#!/bin/sh
echo "[+] Running pre-push checks"
for script in .hooks/pre-push-*; do
  if [ -f "$script" ]; then
    $script
    result=$?
    if [ $result -ne 0 ]; then
      exit $result
    fi
  fi
done
echo "[+] Done with pre-push checks"
```

### .hooks/pre-push-py (Python tests)

```sh
#!/bin/sh
exec 1>&2
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}" && uv run pytest tests/ -v --tb=short
```

## Pre-commit Framework Configs

### development/.pre-commit-config-py.yaml (ruff)

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        entry: uv run ruff check
        language: system
        types: [python]
        args: ["--fix"]
        stages: [pre-commit, manual]
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format --check
        language: system
        types: [python]
        stages: [pre-commit, manual]
```

### development/.pre-commit-config-yaml.yaml

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
  - repo: https://github.com/adrienverge/yamllint.git
    rev: v1.34.0
    hooks:
      - id: yamllint
        args: ["-c", "development/.yamllint.yaml"]
```

### development/.yamllint.yaml

```yaml
yaml-files:
  - '*.yaml'
  - '*.yml'
rules:
  document-start: disable
  line-length:
    max: 150
  indentation:
    spaces: 2
```

## GitHub Actions Workflows

### Python CI

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

env:
  PYTHON_VERSION: "3.11"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - uses: astral-sh/setup-uv@v1
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run basedpyright src/

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - uses: astral-sh/setup-uv@v1
      - run: uv sync --frozen
      - run: uv run pytest tests/ -v --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3

  build:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv build
```

### Go CI

```yaml
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.21"
      - uses: golangci/golangci-lint-action@v3

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.21"
      - run: go test -v -race -coverprofile=coverage.out ./...
```

### Terraform CI

```yaml
name: Terraform

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform fmt -check -recursive
      - run: terraform init -backend=false
        working-directory: global
      - run: terraform validate
        working-directory: global

  tflint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: terraform-linters/setup-tflint@v4
      - run: tflint --init
      - run: tflint --recursive
```

### Docker CI

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

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build image
        uses: docker/build-push-action@v5
        with:
          context: .
          load: true
          tags: app:ci
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Test container structure
        run: |
          curl -fsSLO https://storage.googleapis.com/container-structure-test/latest/container-structure-test-linux-amd64
          chmod +x container-structure-test-linux-amd64
          ./container-structure-test-linux-amd64 test --image app:ci --config structure-test.yaml

      - name: Scan for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: app:ci
          severity: CRITICAL,HIGH
          exit-code: 1

  push:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: |
            org/image
            ghcr.io/${{ github.repository }}
          tags: |
            type=sha
            type=semver,pattern={{version}}
            type=raw,value=latest

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Docker CI with docker-compose (Multi-Service)

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

      - name: Lint all Dockerfiles
        run: find . -name 'Dockerfile' -exec hadolint {} +

      - name: Lint shell scripts
        uses: ludeeus/action-shellcheck@2.0.0
        with:
          scandir: scripts

  build-and-test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Build services
        run: docker compose build

      - name: Start services
        run: docker compose up -d

      - name: Wait for healthy
        run: |
          for i in $(seq 1 30); do
            if docker compose ps | grep -q "(unhealthy)\|(starting)"; then
              sleep 2
            else
              break
            fi
          done
          docker compose ps

      - name: Run integration tests
        run: docker compose exec -T api pytest tests/ -v

      - name: Tear down
        if: always()
        run: docker compose down -v
```

## Docker Patterns

### Multi-stage Python Dockerfile

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app/ ./app/
ENV PATH="/app/.venv/bin:$PATH"
RUN useradd -m -u 1000 appuser
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "-m", "app.cli", "serve"]
```

### Multi-stage Go Dockerfile

```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server ./cmd/server

FROM gcr.io/distroless/static AS runtime
WORKDIR /app
COPY --from=builder /app/server .
USER 1000
EXPOSE 8080
CMD ["./server"]
```
