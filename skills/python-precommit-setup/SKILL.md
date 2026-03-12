---
name: python-precommit-setup
description: Standard pre-commit hook setup for Python projects using custom .hooks/ directory and pre-commit framework. Use when setting up git hooks, configuring pre-commit checks, or establishing quality gates for a Python project.
---

# Python Pre-commit Setup

Standard pre-commit hook setup for Python projects, using a custom `.hooks/` directory and the pre-commit framework. Configs live in `development/`.

## Architecture

- **Custom `.hooks/` directory** at project root (set via `git config core.hooksPath .hooks`)
- **Pre-commit framework configs** in `development/` directory
- **Language-specific dispatcher scripts** -- each hook type has a dispatcher that runs all `*-<lang>` scripts

## Quick Setup

```bash
mkdir -p .hooks development
git config core.hooksPath .hooks
chmod +x .hooks/*
```

## justfile Recipes

```just
setup-hooks:
    git config core.hooksPath .hooks

pre-commit:
    uv run pre-commit run --all-files --config development/.pre-commit-config-py.yaml
    uv run pre-commit run --all-files --config development/.pre-commit-config-yaml.yaml
```

## Quality Gate

Every change must pass quality checks before committing:

1. **Format** -- `uv run ruff format .`
2. **Lint** -- `uv run ruff check --fix .`
3. **Typecheck** -- `uv run basedpyright src/`
4. **Test** -- `uv run pytest`
5. **Commit** -- only when all pass

**Re-check triggers:** any code change, lint fixes, import changes, dependency changes, test changes, merge conflicts.

## Dev Dependencies

```toml
[dependency-groups]
dev = [
    "pre-commit>=4.0",
    "ruff>=0.9",
    "yamllint>=1.0",
]
```

## Setup Checklist

- [ ] `.hooks/` directory with executable scripts (`chmod +x .hooks/*`)
- [ ] `development/.pre-commit-config-py.yaml` with ruff hooks
- [ ] `development/.pre-commit-config-yaml.yaml` with yaml checks
- [ ] `development/.yamllint.yaml` with yaml lint config
- [ ] `just setup-hooks` recipe in justfile
- [ ] `just pre-commit` recipe in justfile
- [ ] pre-commit in dev dependencies
- [ ] Run `just setup-hooks` once per clone

## Reference Files

- [hook-scripts.md](references/hook-scripts.md) -- Full dispatcher scripts, language hooks, pre-commit framework configs, and yamllint setup
