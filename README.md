# Skills Library

Centralized skills for AI coding agents (Cursor and Goose). Source of truth for coding standards, workflows, and conventions harvested from 30+ projects.

## Quick Start

```bash
# Deploy all skills to Goose and Cursor
just deploy

# List all available skills
just list

# Validate all SKILL.md files
just validate
```

## Skills Catalog

### Python

| Skill | Description |
|-------|-------------|
| `python-project-structure` | Standard directory structure, `src/` layout, uv workspace monorepo pattern |
| `python-coding-style` | Naming, typing, docstring-first comments, error handling, line-length 120 |
| `python-api-structure` | FastAPI app factory, config, routers, testing patterns |
| `python-precommit-setup` | `.hooks/` + pre-commit framework, ruff hooks, yamllint, quality gates |
| `python-debugging` | Root cause analysis, common error patterns, systematic fix protocol |

### Other Languages

| Skill | Description |
|-------|-------------|
| `go-coding-style` | Error handling (alecthomas/errors), optional values, testing, golangci-lint |
| `typescript-coding-style` | React + Vite + Tailwind + shadcn UI, biome, component patterns |
| `elixir-coding-style` | GenServer patterns, `@moduledoc`/`@doc`, cyclic dep detection, codegen sync |
| `terraform-coding-style` | Plan-first workflow, quality gates, YAML-to-TF, naming, debugging |
| `shell-coding-style` | `set -euo pipefail`, shellcheck, shfmt, variable safety |

### Cross-Language

| Skill | Description |
|-------|-------------|
| `linting-standards` | ruff (Python), golangci-lint (Go), biome (TS), tflint (TF), shellcheck, yamllint |
| `testing-standards` | pytest, Go testing, vitest, fixture recording, uv workspace patterns |
| `ci-cd-patterns` | justfile, `.hooks/` pre-commit, GitHub Actions, Docker, CI preflight |
| `cross-language-comments` | Docstring-first (Python), section dividers, TODO/FIXME markers |
| `documentation-standards` | README, CONTRIBUTING, AGENTS.md, `.cursor/rules/`, skills directory |
| `git-conventions` | Conventional commits, branch naming, breaking change notation |
| `terraform-project-structure` | `global/`, `tfvars/`, providers, variables, naming conventions |

### Agent Behavior

| Skill | Description |
|-------|-------------|
| `agent-workflow` | Core principles, plan-first methodology, quality gates, session completion |
| `self-improvement` | Retrospectives, lesson extraction, pattern detection, rule evolution |
| `subagent-patterns` | When to delegate, parallel exploration, available subagent types |

## Source Mapping

Skills were harvested from conventions across these projects:

| Source Project | What was harvested |
|---------------|-------------------|
| dart-ops-bot-orchestration | `.hooks/` pre-commit setup, pylint/yamllint configs, justfile recipes |
| dart-mas | ruff config, uv workspace monorepo pattern, section divider comments |
| rootly-py | 13 `.cursor/rules` (workflow, quality gates, self-improvement, debugging, subagents) |
| tf-rootly | 6 SKILL.md files (Terraform workflow/tooling/fixing), CLAUDE.md |
| opal | 9 Claude skills (git, CI preflight, Elixir cyclic deps, codegen, docs) |
| builderbot | AGENTS.md (Go error handling, React/TS component patterns) |
| secure-drives | AGENTS.md (FastAPI patterns, "Landing the Plane" workflow) |
| csirt-ops | `.cursor/rules` (uv workspace project structure) |
| tf-dart-metrics | AGENTS.md (schema patterns, field addition workflows) |

## Deployment

Skills are deployed via symlinks to both Goose and Cursor:

```
~/.config/goose/skills/{skill-name}/ -> skills/{skill-name}/
~/.cursor/skills/{skill-name}/       -> skills/{skill-name}/
```

Run `just deploy` to create/update all symlinks.

## Adding a New Skill

1. Create `skills/{skill-name}/SKILL.md` with frontmatter:

```markdown
---
name: skill-name
description: Brief description of what this skill covers and when to use it.
---

# Skill Title

Content here...
```

2. Run `just validate` to check frontmatter
3. Run `just deploy` to install
4. Run `just list` to verify

## Key Conventions

- **Python linting**: ruff (format -> check -> basedpyright), line-length 120
- **Pre-commit**: Custom `.hooks/` + pre-commit framework
- **Comments**: Docstring-first for Python blocks, `#` for inline only
- **Commits**: Conventional commits (`type(scope): description`)
- **Workflow**: Plan-first (research -> plan -> implement -> review)
