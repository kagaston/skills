# Skills Library

## Official Location

Skills are stored in the official Goose skills location:
```
~/.config/goose/skills/
```

This allows them to be automatically discovered and loaded by Goose.

## Current Skills

| Skill | Description |
|-------|-------------|
| `python-project-structure` | Standard Python project layout |
| `terraform-project-structure` | Standard Terraform project layout |
| `python-coding-style` | Python naming, typing, docstrings |
| `cross-language-comments` | TODO/FIXME/NOTE markers |
| `documentation-standards` | README, CONTRIBUTING, AGENTS.md |
| `linting-standards` | ruff, golangci-lint, biome, tflint |
| `testing-standards` | pytest, Go testing, vitest patterns |
| `ci-cd-patterns` | justfile, GitHub Actions, Docker |
| `typescript-coding-style` | TypeScript/React standards |

## Skills to Create

Based on repository reviews:

- [ ] `go-coding-style` - Go coding standards
- [ ] `elixir-coding-style` - Elixir/OTP patterns
- [ ] `terraform-coding-style` - Terraform/HCL standards
- [ ] `shell-coding-style` - Shell/Bash standards

## Viewing Skills

```bash
# List all skills
ls ~/.config/goose/skills/

# View a skill
cat ~/.config/goose/skills/python-coding-style/SKILL.md
```

## Creating New Skills

1. Create a directory in `~/.config/goose/skills/{skill-name}/`
2. Create a `SKILL.md` file with frontmatter:

```markdown
---
name: skill-name
description: Brief description of what this skill covers
---

# Skill Title

Instructions and content...
```

## Reference

See [Goose Skills Documentation](https://block.github.io/goose/docs/guides/context-engineering/using-skills)
