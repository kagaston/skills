# uv Workspace Monorepo Templates

Templates for multi-package Python projects using uv's workspace feature.

## Root pyproject.toml

```toml
[project]
name = "project-name"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "my-settings",
    "my-logger",
    "my-api",
]

[dependency-groups]
dev = [
    "pytest>=9.0",
    "pytest-asyncio>=1.0",
    "pytest-cov>=6.0",
    "ruff>=0.9",
    "yamllint>=1.0",
    "pre-commit>=4.0",
    "pyyaml>=6.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"

[tool.uv.workspace]
members = ["app/*"]
exclude = ["app/__pycache__", "app/.pytest_cache"]

[tool.uv.sources]
my-settings = { workspace = true }
my-logger = { workspace = true }
my-api = { workspace = true }
```

## Workspace Member pyproject.toml (e.g. app/settings/)

```toml
[project]
name = "my-settings"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/settings"]
```

## Member with Workspace Dependencies (e.g. app/api/)

```toml
[project]
name = "my-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "my-settings",
    "my-logger",
    "fastapi",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/api"]

[tool.uv.sources]
my-settings = { workspace = true }
my-logger = { workspace = true }
```

## Workspace justfile

```just
default:
    @just --list

sync:
    uv sync

test pkg="*":
    uv run pytest app/{{pkg}}/tests/ -v --tb=short

test-cov:
    uv run pytest app/*/tests/ --cov=app --cov-report=term-missing --tb=short

lint:
    uv run ruff check app/*/src/ app/*/tests/
    uv run yamllint -c development/.yamllint.yaml agents/ playbooks/

fmt:
    uv run ruff format app/*/src/ app/*/tests/

pre-commit:
    uv run pre-commit run --all-files --config development/.pre-commit-config-py.yaml
    uv run pre-commit run --all-files --config development/.pre-commit-config-yaml.yaml

setup-hooks:
    git config core.hooksPath .hooks
```

## development/.yamllint.yaml

```yaml
extends: default

rules:
  line-length:
    max: 120
  truthy:
    allowed-values: ["true", "false", "yes", "no"]
  comments:
    min-spaces-from-content: 1
```
