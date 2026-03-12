# Hook Scripts and Configs

Complete dispatcher scripts, language hooks, and pre-commit framework configurations.

## .hooks/ Directory Structure

```
.hooks/
├── pre-commit           # Dispatcher: runs all pre-commit-* scripts
├── pre-commit-py        # Python: runs pre-commit with Python config
├── pre-commit-yaml      # YAML: runs pre-commit with YAML config
├── pre-push             # Dispatcher: runs all pre-push-* scripts
└── pre-push-py          # Python: runs pytest on push
```

## Dispatcher Scripts

### .hooks/pre-commit

```bash
#!/usr/bin/env bash
set -euo pipefail
HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)"
for hook in "$HOOKS_DIR"/pre-commit-*; do
    [ -x "$hook" ] && "$hook"
done
```

### .hooks/pre-push

```bash
#!/usr/bin/env bash
set -euo pipefail
HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)"
for hook in "$HOOKS_DIR"/pre-push-*; do
    [ -x "$hook" ] && "$hook"
done
```

## Language Hook Scripts

### .hooks/pre-commit-py

```bash
#!/usr/bin/env bash
set -euo pipefail
# Only run when Python files are staged
if git diff --cached --name-only --diff-filter=ACM | grep -q '\.py$'; then
    uv run pre-commit run --all-files --config development/.pre-commit-config-py.yaml
fi
```

### .hooks/pre-commit-yaml

```bash
#!/usr/bin/env bash
set -euo pipefail
# Only run when YAML files are staged
if git diff --cached --name-only --diff-filter=ACM | grep -qE '\.(yaml|yml)$'; then
    uv run pre-commit run --all-files --config development/.pre-commit-config-yaml.yaml
fi
```

### .hooks/pre-push-py

```bash
#!/usr/bin/env bash
set -euo pipefail
uv run pytest -v --tb=short
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
        args: ["--fix", "app/*/src/", "app/*/tests/"]
        stages: [pre-commit, manual]
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format --check
        language: system
        types: [python]
        args: ["app/*/src/", "app/*/tests/"]
        stages: [pre-commit, manual]
```

Adapt paths (`app/*/src/`, `app/*/tests/`) to match your project layout (e.g. `src/`, `tests/`).

### development/.pre-commit-config-yaml.yaml

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
        stages: [pre-commit, manual]
      - id: end-of-file-fixer
        stages: [pre-commit, manual]
      - id: trailing-whitespace
        stages: [pre-commit, manual]
      - id: check-added-large-files
        stages: [pre-commit, manual]
  - repo: https://github.com/adrienverge/yamllint.git
    rev: v1.34.0
    hooks:
      - id: yamllint
        args: ["-c", "development/.yamllint.yaml"]
        stages: [pre-commit, manual]
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

## Project Layout Adaptation

| Layout | Python paths in pre-commit config |
|--------|-----------------------------------|
| `app/*/src/`, `app/*/tests/` | `app/*/src/`, `app/*/tests/` |
| Flat `src/`, `tests/` | `src/`, `tests/` |
| Single package | `package_name/`, `tests/` |
