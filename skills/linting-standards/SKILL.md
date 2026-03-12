---
name: linting-standards
description: Linting configuration for Python (ruff), Go (golangci-lint), TypeScript (biome), Terraform (tflint), and Shell (shellcheck)
---

# Linting Standards

Apply these linting standards to maintain code quality. Linting should be automated in CI/CD and enforced before commits.

## Universal Principles

1. **Automate Everything** - Linting should run automatically
2. **Fail Fast** - Run linters early in CI pipeline
3. **Fix, Don't Ignore** - Address issues, don't disable rules

## Python (ruff + basedpyright)

### Tools
- **Linter/Formatter**: `ruff` (replaces black, isort, flake8)
- **Type Checker**: `basedpyright` (stricter pyright fork)

### pyproject.toml Configuration (Block Standard)

```toml
[tool.ruff]
target-version = "py313"
src = ["src", "tests"]
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

[tool.basedpyright]
include = ["src"]
typeCheckingMode = "strict"
failOnWarnings = false
```

### justfile Commands
```just
format:
    uv run ruff format .

lint:
    uv run ruff check --fix .

typecheck:
    uv run basedpyright src/

check:
    uv run nox
```

### noxfile.py Sessions
```python
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
```

## Go (golangci-lint)

### .golangci.yml Configuration
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

### justfile Commands
```just
lint:
    golangci-lint run ./...

format:
    gofmt -s -w .
    goimports -w .
```

## TypeScript/JavaScript (biome)

### biome.json Configuration
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

## Terraform (tflint + tfsec)

### .tflint.hcl Configuration
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

### justfile Commands
```just
format:
    terraform fmt -recursive

lint:
    tflint --recursive
    tfsec .
```

## Shell/Bash (shellcheck + shfmt)

### justfile Commands
```just
lint-shell:
    shellcheck scripts/*.sh

format-shell:
    shfmt -w scripts/
```

## Pre-commit Hooks (lefthook)

### lefthook.yml
```yaml
pre-commit:
  parallel: true
  commands:
    lint-python:
      glob: "*.py"
      run: uv run ruff check {staged_files}
    format-python:
      glob: "*.py"
      run: uv run ruff format --check {staged_files}
    lint-go:
      glob: "*.go"
      run: golangci-lint run {staged_files}
    lint-ts:
      glob: "*.{ts,tsx}"
      run: biome check {staged_files}
```

## Verification Checklist

- [ ] Python: ruff config with Block's rule selection
- [ ] Python: basedpyright in strict mode
- [ ] Python: Line length is 120 (Block standard)
- [ ] Go: golangci-lint with gosec enabled
- [ ] TypeScript: biome configured
- [ ] Terraform: tflint + tfsec configured
- [ ] `just lint` and `just format` commands work
- [ ] CI runs `just check` (nox for Python)
