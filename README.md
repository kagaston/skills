# Skills Library

Centralized skills for AI coding agents (Cursor, Goose, Claude Code, and Amp). Source of truth for coding standards, workflows, and conventions harvested from 30+ projects.

## Quick Start

```bash
# Deploy all skills to Goose, Cursor, Claude Code, and Amp
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
| `frontend-design` | Distinctive, production-grade UI with bold aesthetic direction |

### MCP / Integrations

| Skill | Description |
|-------|-------------|
| `mcp-server` | Python MCP server creation with FastMCP: tools, resources, prompts, testing |

### Cross-Language

| Skill | Description |
|-------|-------------|
| `linting-standards` | ruff (Python), golangci-lint (Go), biome (TS), tflint (TF), shellcheck, yamllint |
| `testing-standards` | pytest, Go testing, vitest, fixture recording, uv workspace patterns |
| `ci-cd-patterns` | justfile, `.hooks/` pre-commit, GitHub Actions, Docker, CI preflight |
| `cross-language-comments` | Docstring-first (Python), section dividers, TODO/FIXME markers |
| `documentation-standards` | README, CONTRIBUTING, AGENTS.md, `.cursor/rules/`, skills directory |
| `terraform-project-structure` | `global/`, `tfvars/`, providers, variables, naming conventions |

### Git

| Skill | Description |
|-------|-------------|
| `git-conventions` | Conventional commits, branch naming, breaking change notation |
| `git-branching` | Trunk-based development, branch lifecycle, planning workflow |
| `git-pull-requests` | PR workflow, project-scoped templates, `gh` CLI commands |
| `project-templates` | Creating PR/issue templates, CODEOWNERS, CONTRIBUTING when missing |

### Documentation

| Skill | Description |
|-------|-------------|
| `readme-blueprint-generator` | Generate comprehensive README.md by analyzing project files, structure, and docs |

### Agent Behavior

| Skill | Description |
|-------|-------------|
| `agent-workflow` | Core principles, plan-first methodology, quality gates, session completion |
| `self-improvement` | Retrospectives, lesson extraction, pattern detection, rule evolution |
| `subagent-patterns` | When to delegate, parallel exploration, available subagent types |
| `skill-creator` | Creating and iterating on skills with test cases and eval loops |
| `code-review` | Systematic review covering architecture, security, performance, testing |

## Skill Structure

Each skill lives in `skills/{skill-name}/` with this layout:

```
skills/{skill-name}/
├── SKILL.md              # Required: main skill definition
└── references/           # Optional: supplementary docs
    ├── config.md         # Config templates, schemas
    └── patterns.md       # Extended examples, checklists
```

### SKILL.md Frontmatter

```yaml
---
name: skill-name                    # Required: matches directory name
description: What it does and when  # Required: primary trigger mechanism
argument-hint: "[parameter]"        # Optional: slash-command hint
---
```

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Skill identifier, must match directory name |
| `description` | Yes | What the skill does and when to use it; drives auto-triggering |
| `argument-hint` | No | Hint for slash-command invocation (e.g. `"[branch-name]"`) |

### Progressive Disclosure

1. **Metadata** (name + description) -- always loaded (~100 words)
2. **SKILL.md body** -- loaded when skill triggers (<500 lines ideal)
3. **references/** -- loaded on demand (unlimited size)

Keep SKILL.md lean. Extract large config blocks, checklists, and schema definitions into `references/*.md` and link to them from the main file.

## Deployment

Skills are deployed via symlinks to all four agent platforms:

```
~/.config/goose/skills/{skill-name}/ -> skills/{skill-name}/
~/.cursor/skills/{skill-name}/       -> skills/{skill-name}/
~/.claude/skills/{skill-name}/       -> skills/{skill-name}/
~/.config/amp/skills/{skill-name}/   -> skills/{skill-name}/
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

2. Optionally add `references/` for supplementary docs
3. Run `just validate` to check frontmatter
4. Run `just deploy` to install
5. Run `just list` to verify

## Key Conventions

- **Python linting**: ruff (format -> check -> basedpyright), line-length 120
- **Pre-commit**: Custom `.hooks/` + pre-commit framework
- **Comments**: Docstring-first for Python blocks, `#` for inline only
- **Commits**: Conventional commits (`type(scope): description`)
- **Branching**: Trunk-based development with short-lived feature branches
- **Workflow**: Plan-first (research -> plan -> implement -> review)
