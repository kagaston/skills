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

## Docker Patterns

### Multi-stage Python Dockerfile

```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app/ ./app/
ENV PATH="/app/.venv/bin:$PATH"
RUN useradd -m appuser
USER appuser
EXPOSE 8000
CMD ["python", "-m", "app.cli", "serve"]
```

### Multi-stage Go Dockerfile

```dockerfile
FROM golang:1.21-alpine as builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server ./cmd/server

FROM alpine:3.19
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /app/server .
RUN adduser -D appuser
USER appuser
EXPOSE 8080
CMD ["./server"]
```
