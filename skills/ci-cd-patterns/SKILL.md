---
name: ci-cd-patterns
description: CI/CD pipeline patterns including justfile commands, GitHub Actions, and Docker
---

# CI/CD Patterns

Apply these CI/CD patterns for consistent, reliable automated pipelines.

## Pipeline Stages

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Lint   │ -> │  Test   │ -> │  Build  │ -> │ Deploy  │
└─────────┘   └─────────┘   └─────────┘   └─────────┘
```

## Pre-commit Hooks (.hooks/ + pre-commit framework)

Use a custom `.hooks/` directory with dispatcher scripts that invoke the pre-commit framework. Configs live in `development/`.

See [precommit-configs.md](references/precommit-configs.md) for the full hook scripts, pre-commit framework configs, and language-specific dispatchers.

### justfile Recipes

```just
setup-hooks:
    git config core.hooksPath .hooks

pre-commit:
    uv run pre-commit run --all-files --config development/.pre-commit-config-py.yaml
    uv run pre-commit run --all-files --config development/.pre-commit-config-yaml.yaml
```

## CI Preflight Checklist

Run all CI checks locally before pushing. Execute in order; stop and fix at each step.

1. **Format** -- `just format` or `uv run ruff format .`
2. **Lint** -- `just lint` or `uv run ruff check --fix .`
3. **Typecheck** -- `just typecheck` or `uv run basedpyright src/`
4. **Test** -- `just test` or `uv run pytest tests/ -v`
5. **Push** -- only after all pass

```just
preflight: format lint typecheck test
```

## justfile Standards

Every project should have a `justfile` with these standard commands:

```just
default:
    @just --list

install:
    uv sync

dev:
    uv run python -m app.cli serve --reload

format:
    uv run ruff format .

lint:
    uv run ruff check --fix .

typecheck:
    uv run basedpyright src/

test:
    uv run pytest tests/ -v

test-cov:
    uv run pytest tests/ --cov=app --cov-report=term-missing

check:
    uv run nox

build:
    uv build

docker-build:
    docker build -t app:latest .

clean:
    rm -rf dist/ build/ .pytest_cache/ .basedpyright/
    find . -type d -name __pycache__ -exec rm -rf {} +

update:
    uv lock --upgrade
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

- [ ] justfile has standard commands (install, dev, format, lint, typecheck, test, check, build)
- [ ] All Python commands use `uv run` prefix
- [ ] `.hooks/` scripts and `development/` pre-commit configs in place
- [ ] `just setup-hooks` and `just pre-commit` work
- [ ] CI preflight sequence (format -> lint -> typecheck -> test) documented
- [ ] `check` runs `uv run nox` (or `format lint typecheck test` chain)
- [ ] GitHub Actions workflow exists
- [ ] Lint job runs before test job
- [ ] Coverage reporting configured
- [ ] Dockerfile uses multi-stage build

## Reference Files

- [precommit-configs.md](references/precommit-configs.md) -- Full hook scripts, pre-commit YAML configs, GitHub Actions workflows, and Docker patterns
