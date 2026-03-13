---
name: python-project-structure
description: Standard directory structure and configuration for Python projects using uv workspace monorepo layout with app/{name}/src/{name}/ and app/{name}/tests/ structure
argument-hint: "[project-name]"
---

# Python Project Structure

ALL Python projects use the uv workspace monorepo layout, even single-app projects. This ensures a consistent structure across every project and makes adding packages trivial.

## Project Layout

Every Python project follows this structure. There is no "flat" or "simple" alternative.

```
project-name/
├── app/
│   └── my_app/                     # One directory per workspace member
│       ├── src/
│       │   └── my_app/             # Package code (src layout)
│       │       ├── __init__.py
│       │       └── ...
│       ├── tests/
│       │   ├── __init__.py
│       │   ├── conftest.py         # Shared fixtures
│       │   ├── unit/
│       │   └── integration/
│       └── pyproject.toml          # Member package config
├── development/
│   ├── .yamllint.yaml
│   ├── .pre-commit-config-py.yaml
│   └── .pre-commit-config-yaml.yaml
├── .hooks/
├── justfile
├── noxfile.py                      # CI session definitions
├── pyproject.toml                  # Root workspace config
├── uv.lock
├── AGENTS.md
├── CONTRIBUTING.md
└── README.md
```

### Multi-Package Example

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
├── .hooks/
├── justfile
├── noxfile.py
├── pyproject.toml
└── uv.lock
```

## Package Manager

**uv is required.** No `pip`, no `requirements.txt`, no `setup.py`, no `setup.cfg`. Every project uses `pyproject.toml` managed by uv.

```bash
uv sync              # Install all dependencies
uv sync --frozen     # Install from lockfile (CI)
uv lock --upgrade    # Update lockfile
uv add <package>     # Add a dependency
uv run <command>     # Run in project venv
```

## Required Files

### Root pyproject.toml

```toml
[project]
name = "project-name"
version = "0.1.0"
requires-python = ">=3.11"

[tool.uv]
package = false

[tool.uv.workspace]
members = ["app/*"]
```

### Member pyproject.toml (app/{name}/pyproject.toml)

```toml
[project]
name = "my-app"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "httpx",
    "pydantic>=2.0",
]

[dependency-groups]
dev = ["ruff", "basedpyright", "pytest", "pytest-cov", "nox"]

[tool.uv.sources]
settings = { workspace = true }
```

### justfile

```just
[private]
default:
    @just --list --unsorted

install:
    uv sync

format:
    uv run ruff format .

lint:
    uv run ruff check --fix .

typecheck:
    uv run basedpyright app/*/src/

test pkg="*" *args="":
    uv run pytest app/{{pkg}}/tests/ -v --tb=short {{args}}

test-cov:
    uv run pytest app/*/tests/ --cov=app --cov-report=term-missing --tb=short

check:
    uv run nox

setup-hooks:
    git config core.hooksPath .hooks

pre-commit:
    uv run pre-commit run --all-files --config development/.pre-commit-config-py.yaml
    uv run pre-commit run --all-files --config development/.pre-commit-config-yaml.yaml

update:
    uv lock --upgrade

clean:
    rm -rf dist/ build/ .pytest_cache/ .basedpyright/
    find . -type d -name __pycache__ -exec rm -rf {} +
```

## Key Patterns

### 1. Always app/{name}/src/{name}/ Layout

Every package lives under `app/`. The `src/` subdirectory prevents import shadowing:

```
app/
└── my_app/
    ├── src/
    │   └── my_app/        # Package code here
    │       ├── __init__.py
    │       └── core.py
    ├── tests/
    │   └── test_core.py
    └── pyproject.toml
```

### 2. Project Types

- **Library**: Publishable package with `[build-system]` in member pyproject.toml
- **Application**: Standalone service with `[tool.uv] package = false` in root

### 3. Dev Dependencies

Use dependency groups in the member pyproject.toml, not extras:

```toml
[dependency-groups]
dev = ["ruff", "basedpyright", "pytest", "pytest-cov", "nox"]
```

### 4. Naming Conventions

- **Project name**: lowercase with dashes (`my-project`)
- **Directory name**: lowercase with underscores (`my_project`)
- **Module name**: lowercase with underscores (`my_project`)
- **`app/` directory name** matches the module name

### 5. Workspace Cross-References

When one package depends on another in the workspace:

```toml
# In app/api/pyproject.toml
[tool.uv.sources]
settings = { workspace = true }
logger = { workspace = true }
```

## Verification Checklist

- [ ] ALL code lives under `app/{name}/src/{name}/`
- [ ] ALL tests live under `app/{name}/tests/`
- [ ] Root `pyproject.toml` has `[tool.uv.workspace]` with `members = ["app/*"]`
- [ ] Each `app/*` member has `src/`, `tests/`, and `pyproject.toml`
- [ ] `[tool.uv.sources]` maps workspace packages with `{ workspace = true }`
- [ ] uv is the only package manager (no pip, no requirements.txt)
- [ ] `uv.lock` committed to version control
- [ ] `justfile` has install, format, lint, test, typecheck, check commands
- [ ] All Python commands use `uv run` prefix
- [ ] `noxfile.py` defines CI sessions
- [ ] `development/` contains shared config (`.yamllint.yaml`, pre-commit configs)
- [ ] `.hooks/` used for git hooks (`git config core.hooksPath .hooks`)
- [ ] Coverage threshold set to 80%
- [ ] Line length is 120

## Reference Files

- [pyproject-template.md](references/pyproject-template.md) -- Full pyproject.toml, noxfile.py, and CONTRIBUTING.md templates
- [workspace-template.md](references/workspace-template.md) -- Root and member pyproject.toml, justfile, and yamllint config
