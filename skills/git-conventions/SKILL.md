---
name: git-conventions
description: Git conventions including conventional commits, commit message format, branching, and hygiene. Use when creating commits, preparing PRs, or performing git operations.
---

## Conventional Commits

Every commit MUST follow this format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types (required)

| Type | When to use | Version bump |
|------|-------------|--------------|
| `feat` | New feature or capability | minor |
| `fix` | Bug fix | patch |
| `docs` | Documentation only | none |
| `style` | Formatting, whitespace -- no logic change | none |
| `refactor` | Code change that neither fixes bug nor adds feature | none |
| `perf` | Performance improvement | patch |
| `test` | Adding or correcting tests | none |
| `build` | Build system or dependency changes | none |
| `ci` | CI configuration changes | none |
| `chore` | Maintenance tasks (deps, tooling, releases) | none |

### Scopes (recommended)

Use a scope to identify the affected area. Define project-specific scopes in CONTRIBUTING.md. Common patterns:

- By component: `auth`, `api`, `cli`, `core`, `db`
- By language: `python`, `go`, `terraform`
- By layer: `model`, `service`, `router`, `middleware`

Omit scope only when the change truly spans the entire project.

### Rules

1. Always use conventional commit format. Never bare messages like "fix stuff" or "updates"
2. Description: lowercase, imperative mood, no period at end
3. Body: optional but encouraged for non-trivial changes -- explain why, not what
4. One logical change per commit. Don't bundle unrelated changes
5. Breaking changes: append `!` after type/scope or add `BREAKING CHANGE:` footer

   ```
   feat(api)!: change response envelope format

   BREAKING CHANGE: Response now wraps data in { data: ... } envelope.
   Clients must update parsing logic.
   ```

### Examples

```
feat(auth): implement JWT-based authentication
fix(api): handle null response from upstream service
docs(readme): update installation instructions
refactor(core): extract token counting into dedicated module
test(users): add edge case tests for email validation
chore(deps): upgrade pydantic to 2.6
ci: add Python 3.13 to test matrix
feat(rpc)!: switch wire format from JSON to msgpack
```

### Branch Naming

Use the same type prefixes as commits: `feat/short-description`, `fix/42-null-response`, `docs/api-guide`. See the **git-branching** skill for full naming conventions and trunk-based workflow.

## Related Skills

- **git-branching** -- branching strategies, branch lifecycle, trunk-based development
- **git-pull-requests** -- PR workflow, using project templates, pushing PRs via CLI
- **project-templates** -- creating PR/issue templates and CODEOWNERS when none exist

### Verification Checklist

- [ ] Commit follows `type(scope): description` format
- [ ] Description is lowercase imperative mood
- [ ] One logical change per commit
- [ ] Breaking changes marked with `!` or footer
- [ ] Body explains "why" for non-trivial changes
- [ ] Branch name uses type prefix (`feat/`, `fix/`, etc.)
