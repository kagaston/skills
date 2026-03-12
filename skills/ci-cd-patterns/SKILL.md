---
name: ci-cd-patterns
description: CI/CD pipeline patterns including justfile commands, GitHub Actions, and Docker
---

# CI/CD Patterns

Apply these CI/CD patterns for consistent, reliable automated pipelines.

## Pipeline Stages

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Lint   │ → │  Test   │ → │  Build  │ → │ Deploy  │
└─────────┘   └─────────┘   └─────────┘   └─────────┘
```

## Pre-commit Hooks (.hooks/ + pre-commit framework)

Use a custom `.hooks/` directory with dispatcher scripts that invoke the pre-commit framework. Configs live in `development/`.

### Hook scripts

**`.hooks/pre-commit`** (dispatcher):
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

**`.hooks/pre-commit-py`** (Python-specific):
```sh
#!/bin/sh
exec 1>&2
REPO_ROOT="$(git rev-parse --show-toplevel)"
if [ -n "$(git diff --cached --name-only --diff-filter=ACM | grep -e '\.py$')" ]; then
  uv run pre-commit run --config "${REPO_ROOT}/development/.pre-commit-config-py.yaml"
fi
```

**`.hooks/pre-commit-yaml`** (YAML-specific):
```sh
#!/bin/sh
exec 1>&2
REPO_ROOT="$(git rev-parse --show-toplevel)"
if [ -n "$(git diff --cached --name-only --diff-filter=ACM | grep -e '\.yaml$' -e '\.yml$')" ]; then
  uv run pre-commit run --config "${REPO_ROOT}/development/.pre-commit-config-yaml.yaml"
fi
```

**`.hooks/pre-push`** (dispatcher):
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

**`.hooks/pre-push-py`** (Python tests):
```sh
#!/bin/sh
exec 1>&2
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}" && uv run pytest tests/ -v --tb=short
```

### Pre-commit configs in `development/`

**`development/.pre-commit-config-py.yaml`** (ruff, not pylint):
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

**`development/.pre-commit-config-yaml.yaml`**:
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

**`development/.yamllint.yaml`** (optional, for yamllint):
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

### justfile recipes

```just
# Set up git hooks to use .hooks/
setup-hooks:
    git config core.hooksPath .hooks

# Run all pre-commit checks manually (both configs)
pre-commit:
    uv run pre-commit run --all-files --config development/.pre-commit-config-py.yaml
    uv run pre-commit run --all-files --config development/.pre-commit-config-yaml.yaml
```

## CI Preflight Checklist

Run all CI checks locally before pushing. Execute in order; stop and fix at each step.

1. **Format** — `just format` or `ruff format . && ruff check --fix .`
2. **Lint** — `just lint` or `ruff check . && mypy .`
3. **Typecheck** — `just lint` (if separate) or `mypy .`
4. **Test** — `just test` or `pytest tests/ -v`
5. **Push** — only after all pass

```just
# Run full CI preflight locally
preflight: format lint test
```

## justfile Standards

Every project should have a `justfile` with these standard commands:

```just
default:
    @just --list

# Development
install:
    uv sync

dev:
    uv run python -m app.cli serve --reload

# Quality
format:
    ruff format .
    ruff check --fix .

lint:
    ruff check .
    mypy .

check: lint
    ruff format --check .

# Testing
test:
    pytest tests/ -v

test-cov:
    pytest tests/ --cov=app --cov-report=term-missing

# Build & Deploy
build:
    uv build

docker-build:
    docker build -t app:latest .

# Utilities
clean:
    rm -rf dist/ build/ .pytest_cache/ .mypy_cache/
    find . -type d -name __pycache__ -exec rm -rf {} +

update:
    uv lock --upgrade
```

## GitHub Actions

### Python Project
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
      - run: uv run mypy .

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

### Go Project
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

### Terraform
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

## Release Management

### Semantic Versioning
```
MAJOR.MINOR.PATCH

1.0.0 - Initial release
1.1.0 - New feature (backward compatible)
1.1.1 - Bug fix
2.0.0 - Breaking change
```

### Changelog Format
```markdown
# Changelog

## [1.2.0] - 2024-01-15

### Added
- New authentication endpoint

### Changed
- Improved error messages

### Fixed
- Race condition in session handling
```

## Verification Checklist

- [ ] justfile has standard commands (install, dev, format, lint, test, build)
- [ ] `.hooks/` scripts and `development/` pre-commit configs in place
- [ ] `just setup-hooks` and `just pre-commit` work
- [ ] CI preflight sequence (format → lint → typecheck → test) documented
- [ ] GitHub Actions workflow exists
- [ ] Lint job runs before test job
- [ ] Coverage reporting configured
- [ ] Dockerfile uses multi-stage build
