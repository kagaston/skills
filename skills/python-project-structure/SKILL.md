---
name: python-project-structure
description: Standard directory structure and configuration for Python projects based on Block's copier template
---

# Python Project Structure

When creating or reviewing Python projects, follow this standard structure derived from Block's official Python copier template.

## Standard Layout

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

### pyproject.toml

Use `uv` for dependency management with this structure:

```toml
[project]
name = "project-name"
version = "0.1.0"
readme = "README.md"
requires-python = ">=3.13"
authors = [{ name = "Author Name", email = "author@example.com" }]
dependencies = []

[dependency-groups]
dev = []

# For libraries (publishable packages)
[build-system]
requires = ["uv_build>=0.8.22,<0.9.0"]
build-backend = "uv_build"

# For applications (not published)
# [tool.uv]
# package = false

# --- Ruff ---
[tool.ruff]
target-version = "py313"
src = ["src", "tests"]
line-length = 120

[tool.ruff.lint]
select = ["B", "C4", "C90", "D", "E", "F", "I", "PLR", "PT", "RUF", "S", "SIM", "T20", "UP"]
fixable = ["ALL"]
ignore = ["D107", "D415", "D212", "D100", "D104"]
exclude = ["tests/**"]

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pylint]
max-args = 5
max-branches = 12
max-returns = 6
max-statements = 50

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"**/tests/**/*.py" = ["D", "S101", "T20"]
"noxfile.py" = ["D", "S101", "T20"]

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true

# --- BasedPyright ---
[tool.basedpyright]
include = ["src"]
typeCheckingMode = "strict"
failOnWarnings = false

# --- Pytest ---
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-ra", "--strict-markers", "--strict-config", "--cov=src/module_name", "--cov-report=term-missing", "--cov-fail-under=80"]
filterwarnings = ["error"]

[tool.coverage.run]
omit = ["**/__init__.py"]
```

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

### noxfile.py

CI session definitions:

```python
"""Nox sessions for CI validation."""
import nox

nox.options.default_venv_backend = "uv"

PYTHON_VERSION = "3.13"
PYPROJECT = nox.project.load_toml("pyproject.toml")
DEV_DEPS = nox.project.dependency_groups(PYPROJECT, "dev")

@nox.session(python=PYTHON_VERSION)
def format(session: nox.Session) -> None:
    """Check code formatting with ruff (no fixes)."""
    session.install(*DEV_DEPS)
    session.run("ruff", "format", "--check", "src/", "tests/")

@nox.session(python=PYTHON_VERSION)
def lint(session: nox.Session) -> None:
    """Lint the codebase using ruff (no fixes)."""
    session.install(*DEV_DEPS)
    session.run("ruff", "check", "src/", "tests/")

@nox.session(python=PYTHON_VERSION)
def typecheck(session: nox.Session) -> None:
    """Type check using basedpyright."""
    session.install(*DEV_DEPS)
    session.install(".")
    session.run("basedpyright", "src/")

@nox.session(python=PYTHON_VERSION)
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    session.install(*DEV_DEPS)
    session.install(".")
    session.run("pytest", "tests/", *session.posargs)
```

### CONTRIBUTING.md

```markdown
# Contributing to project-name

### Setup
\`\`\`bash
uv sync
\`\`\`

### Commands
- `just format` - Format code
- `just lint` - Lint code
- `just test` - Run tests
- `just typecheck` - Type check
- `just check` - Run all CI checks

### Adding dependencies
- `uv add <package>` - Add a runtime dependency
- `uv add --dev <package>` - Add a dev dependency
```

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

## Verification Checklist

- [ ] Uses `src/` layout for package code
- [ ] `pyproject.toml` has ruff, basedpyright, pytest config
- [ ] `justfile` has format, lint, test, typecheck, check commands
- [ ] `noxfile.py` defines CI sessions
- [ ] `CONTRIBUTING.md` documents setup and commands
- [ ] Coverage threshold set to 80%
- [ ] Line length is 120 (Block standard)
