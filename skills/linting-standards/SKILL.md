---
name: linting-standards
description: Linting configuration for Python (ruff), Go (golangci-lint), TypeScript (biome), Terraform (tflint + tfsec), Shell (shellcheck + shfmt), and YAML (yamllint)
---

# Linting Standards

Apply these linting standards to maintain code quality. Linting should be automated in CI/CD and enforced before commits.

## Universal Principles

1. **Automate Everything** -- linting should run automatically
2. **Fail Fast** -- run linters early in CI pipeline
3. **Fix, Don't Ignore** -- address issues, don't disable rules

## Multi-Language Quality Gate

All must pass before commit: **format -> lint -> typecheck -> test**

| Step | Purpose |
|------|---------|
| 1. Format | Apply consistent style (quotes, line length, indentation) |
| 2. Lint | Catch bugs, security issues, style violations; auto-fix where possible |
| 3. Typecheck | Static type verification (Python, TypeScript) |
| 4. Test | Unit/integration tests |

## Python (ruff + basedpyright)

- **Linter/Formatter**: `ruff` (replaces pylint, black, isort, flake8)
- **Type Checker**: `basedpyright` (stricter pyright fork)

### Execution Order

1. `ruff format .` -- formatting (quotes, line length)
2. `ruff check --fix .` -- linting + isort via `I` rule, auto-fixes
3. `basedpyright src/` -- type checking

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

See [linter-configs.md](references/linter-configs.md) for the full `pyproject.toml` config, basedpyright setup, and noxfile sessions.

## Go (golangci-lint)

```just
format:
    gofmt -s -w .
    goimports -w .

lint:
    golangci-lint run ./...
```

See [linter-configs.md](references/linter-configs.md) for the full `.golangci.yml` configuration.

## TypeScript/JavaScript (biome)

See [linter-configs.md](references/linter-configs.md) for the full `biome.json` configuration.

## Terraform (tflint + tfsec)

```just
format:
    terraform fmt -recursive

lint:
    tflint --recursive
    tfsec .
```

See [linter-configs.md](references/linter-configs.md) for the full `.tflint.hcl` configuration.

## Shell/Bash (shellcheck + shfmt)

```just
lint-shell:
    shellcheck scripts/*.sh

format-shell:
    shfmt -w scripts/
```

## YAML (yamllint)

```just
lint-yaml:
    yamllint .
```

See [linter-configs.md](references/linter-configs.md) for the `.yamllint` configuration.

## Docker (hadolint)

- **Linter**: `hadolint` (Dockerfile best practices + embedded ShellCheck)

```just
lint-docker:
    hadolint Dockerfile
```

### .hadolint.yaml

```yaml
ignored:
  - DL3008    # pin versions in apt-get (sometimes impractical)

trustedRegistries:
  - docker.io
  - ghcr.io

failure-threshold: warning
strict-labels: true
```

### Key Rules

| Rule | What it catches |
|------|----------------|
| DL3007 | Using `:latest` tag |
| DL3008 | Not pinning apt package versions |
| DL3009 | Not cleaning apt cache after install |
| DL3025 | Using shell form for CMD (should be JSON) |
| DL3015 | Not using `--no-install-recommends` with apt-get |
| DL4006 | Not setting `SHELL` with pipefail for pipe commands |

### CI Integration

```yaml
- name: Lint Dockerfile
  uses: hadolint/hadolint-action@v3.1.0
  with:
    dockerfile: Dockerfile
```

## Verification Checklist

- [ ] Python: ruff as single tool (replaces pylint, black, isort, flake8)
- [ ] Python: Execution order -- format -> lint -> typecheck
- [ ] Python: basedpyright in strict mode
- [ ] Python: Line length 120
- [ ] Go: golangci-lint with gosec enabled
- [ ] TypeScript: biome configured
- [ ] Terraform: tflint + tfsec configured
- [ ] Shell: shellcheck + shfmt
- [ ] Docker: hadolint configured (with `.hadolint.yaml` if needed)
- [ ] YAML: yamllint configured
- [ ] Quality gate: format -> lint -> typecheck -> test
- [ ] `just lint` and `just format` commands work
- [ ] CI runs `just check` (nox for Python)

## Reference Files

- [linter-configs.md](references/linter-configs.md) -- Full configuration files for all languages (pyproject.toml, .golangci.yml, biome.json, .tflint.hcl, .yamllint)
