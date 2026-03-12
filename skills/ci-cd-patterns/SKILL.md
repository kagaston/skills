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

## justfile Standards

Every project should have a `justfile` with these standard commands:

```just
# Default recipe - show available commands
default:
    @just --list

# =============================================================================
# Development
# =============================================================================

# Install dependencies
install:
    uv sync

# Run development server
dev:
    uv run python -m app.cli serve --reload

# =============================================================================
# Quality
# =============================================================================

# Format code
format:
    ruff format .
    ruff check --fix .

# Lint code
lint:
    ruff check .
    mypy .

# Check all (for CI)
check: lint
    ruff format --check .

# =============================================================================
# Testing
# =============================================================================

# Run all tests
test:
    pytest tests/ -v

# Run tests with coverage
test-cov:
    pytest tests/ --cov=app --cov-report=term-missing

# =============================================================================
# Build & Deploy
# =============================================================================

# Build package
build:
    uv build

# Build Docker image
docker-build:
    docker build -t app:latest .

# =============================================================================
# Utilities
# =============================================================================

# Clean build artifacts
clean:
    rm -rf dist/ build/ .pytest_cache/ .mypy_cache/
    find . -type d -name __pycache__ -exec rm -rf {} +

# Update dependencies
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
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

# Runtime stage
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
# Build stage
FROM golang:1.21-alpine as builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server ./cmd/server

# Runtime stage
FROM alpine:3.19
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /app/server .
RUN adduser -D appuser
USER appuser
EXPOSE 8080
CMD ["./server"]
```

## Pre-commit Hooks

### lefthook.yml
```yaml
pre-commit:
  parallel: true
  commands:
    lint-python:
      glob: "*.py"
      run: ruff check {staged_files}
    format-python:
      glob: "*.py"
      run: ruff format --check {staged_files}
    lint-go:
      glob: "*.go"
      run: golangci-lint run {staged_files}
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
- [ ] GitHub Actions workflow exists
- [ ] Lint job runs before test job
- [ ] Coverage reporting configured
- [ ] Dockerfile uses multi-stage build
- [ ] Pre-commit hooks configured
