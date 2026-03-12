---
name: python-project-structure
description: Standard directory structure and configuration for Python projects based on Block's copier template
argument-hint: "[project-name]"
---

# Python Project Structure

When creating or reviewing Python projects, follow this standard structure derived from Block's official Python copier template.

## Standard Layout (Default)

Use this single-package layout for most projects:

```
project-name/
├── src/
│   └── module_name/            # Main package (use src layout)
│       ├── __init__.py
│       └── ...
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures
│   └── test_*.py
├── bin/                        # Hermit binaries (Block-specific)
├── CONTRIBUTING.md             # Contribution guidelines
├── README.md                   # Project overview
├── justfile                    # Task runner commands
├── noxfile.py                  # CI session definitions
└── pyproject.toml              # Project configuration
```

## Required Files

### justfile

Standard commands every project should have:

```just
[private]
default:
    @just --list --unsorted

format:
    uv run ruff format .

lint:
    uv run ruff check --fix .

test *args:
    uv run pytest tests/ {{args}}

typecheck:
    uv run basedpyright src/

check:
    uv run nox
```

See [pyproject-template.md](references/pyproject-template.md) for the full `pyproject.toml`, `noxfile.py`, and `CONTRIBUTING.md` templates.

## Key Patterns

### 1. Use src/ Layout

Put your package under `src/` to avoid import issues:

```
src/
└── my_package/
    ├── __init__.py
    └── core.py
```

### 2. Project Types

- **Library**: Publishable package with `[build-system]`
- **Application**: Standalone service with `[tool.uv] package = false`

### 3. Dev Dependencies

Use dependency groups, not extras:

```toml
[dependency-groups]
dev = ["ruff", "basedpyright", "pytest", "pytest-cov", "nox"]
```

### 4. Naming Conventions

- **Project name**: lowercase with dashes (`my-project`)
- **Module name**: lowercase with underscores (`my_project`)

---

## uv Workspace Monorepo

For multi-package projects, use uv's workspace feature. Each workspace member is a separate package under `app/`:

```
project-name/
├── app/
│   ├── settings/
│   │   ├── src/
│   │   │   └── settings/
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── logger/
│   │   ├── src/
│   │   │   └── logger/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── api/
│       ├── src/
│       │   └── api/
│       ├── tests/
│       └── pyproject.toml
├── development/
│   ├── .yamllint.yaml
│   ├── .pre-commit-config-py.yaml
│   └── .pre-commit-config-yaml.yaml
├── .hooks/
├── justfile
├── pyproject.toml              # Root workspace config
└── uv.lock
```

See [workspace-template.md](references/workspace-template.md) for the full root and member `pyproject.toml` templates, workspace justfile, and yamllint config.

---

## Verification Checklist

### Single-Package (Default)

- [ ] Uses `src/` layout for package code
- [ ] `pyproject.toml` has ruff, basedpyright, pytest config
- [ ] `justfile` has format, lint, test, typecheck, check commands
- [ ] `noxfile.py` defines CI sessions
- [ ] `CONTRIBUTING.md` documents setup and commands
- [ ] Coverage threshold set to 80%
- [ ] Line length is 120 (Block standard)

### uv Workspace Monorepo

- [ ] Root `pyproject.toml` has `[tool.uv.workspace]` with `members = ["app/*"]`
- [ ] Each `app/*` member has `src/`, `tests/`, and `pyproject.toml`
- [ ] `[tool.uv.sources]` maps workspace packages with `{ workspace = true }`
- [ ] `development/` contains shared config (`.yamllint.yaml`, pre-commit configs)
- [ ] `justfile` has test, lint, fmt, sync, setup-hooks
- [ ] `.hooks/` used for git hooks (`git config core.hooksPath .hooks`)

## Reference Files

- [pyproject-template.md](references/pyproject-template.md) -- Full pyproject.toml, noxfile.py, and CONTRIBUTING.md for single-package projects
- [workspace-template.md](references/workspace-template.md) -- Root and member pyproject.toml, justfile, and yamllint config for monorepos
