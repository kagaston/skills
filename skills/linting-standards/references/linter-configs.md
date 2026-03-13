# Ruff Configuration

Complete `pyproject.toml` configuration for ruff linting and formatting.

## pyproject.toml

```toml
[tool.ruff]
target-version = "py313"
src = ["app/*/src", "app/*/tests"]
line-length = 120

[tool.ruff.lint]
select = [
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "C90",    # mccabe complexity
    "D",      # pydocstyle
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "I",      # isort
    "PLR",    # Pylint refactor
    "PT",     # flake8-pytest-style
    "RUF",    # Ruff-specific
    "S",      # flake8-bandit (security)
    "SIM",    # flake8-simplify
    "T20",    # flake8-print
    "UP",     # pyupgrade
]
fixable = ["ALL"]
ignore = ["D107", "D415", "D212", "D100", "D104"]
exclude = ["app/*/tests/**"]

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"**/tests/**/*.py" = ["D", "S101", "T20"]
"noxfile.py" = ["D", "S101", "T20"]

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true
```

## BasedPyright

```toml
[tool.basedpyright]
include = ["app/*/src"]
typeCheckingMode = "strict"
failOnWarnings = false
```

## noxfile.py Sessions

```python
@nox.session(python=PYTHON_VERSION)
def format(session: nox.Session) -> None:
    """Check code formatting with ruff (no fixes)."""
    session.install(*DEV_DEPS)
    session.run("ruff", "format", "--check", "app/*/src/", "app/*/tests/")

@nox.session(python=PYTHON_VERSION)
def lint(session: nox.Session) -> None:
    """Lint the codebase using ruff (no fixes)."""
    session.install(*DEV_DEPS)
    session.run("ruff", "check", "app/*/src/", "app/*/tests/")

@nox.session(python=PYTHON_VERSION)
def typecheck(session: nox.Session) -> None:
    """Type check using basedpyright."""
    session.install(*DEV_DEPS)
    session.install(".")
    session.run("basedpyright", "app/*/src/")
```

## Go (.golangci.yml)

```yaml
run:
  timeout: 5m

linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gofmt
    - goimports
    - misspell
    - gocritic
    - revive
    - gosec

linters-settings:
  goimports:
    local-prefixes: github.com/yourorg
```

## TypeScript (biome.json)

```json
{
  "$schema": "https://biomejs.dev/schemas/1.5.0/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "correctness": {
        "noUnusedVariables": "error",
        "noUnusedImports": "error"
      },
      "style": {
        "useConst": "error"
      }
    }
  },
  "formatter": {
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  }
}
```

## Terraform (.tflint.hcl)

```hcl
config {
  module = true
}

plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

rule "terraform_documented_variables" {
  enabled = true
}
```

## YAML (.yamllint)

```yaml
---
extends: default

rules:
  document-start: disable
  line-length:
    max: 150
    allow-non-breakable-words: true
    allow-non-breakable-inline-mappings: true
  indentation:
    spaces: 2
    indent-sequences: consistent
  comments:
    min-spaces-from-content: 1
  truthy:
    allowed-values: ["true", "false", "yes", "no"]
    check-keys: false
```
