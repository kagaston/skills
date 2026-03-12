---
name: git-pull-requests
description: Pull request workflow including using project-scoped PR templates, writing PR descriptions, and pushing PRs via CLI. Use when creating a pull request, pushing a PR, writing a PR description, reviewing PR templates, or preparing code for review.
argument-hint: "[pr-title or branch]"
---

# Git Pull Requests

## Before Creating a PR

1. **Check for project templates** -- look for existing PR templates before writing a description from scratch:

   ```bash
   # Check for PR template (common locations)
   ls .github/pull_request_template.md .github/PULL_REQUEST_TEMPLATE.md .github/PULL_REQUEST_TEMPLATE/ 2>/dev/null
   ```

2. **Run quality gates** -- ensure CI will pass before pushing:

   ```bash
   just check        # or the project's equivalent
   just pre-commit   # if pre-commit hooks exist
   ```

3. **Rebase onto main** -- keep a clean diff:

   ```bash
   git fetch origin && git rebase origin/main
   ```

## Using Project-Scoped Templates

When a project has a PR template, **always use it**. The template lives in one of these locations:

| Location | Behavior |
|---|---|
| `.github/pull_request_template.md` | Auto-populates every new PR |
| `.github/PULL_REQUEST_TEMPLATE.md` | Same (case-insensitive on GitHub) |
| `.github/PULL_REQUEST_TEMPLATE/` | Multiple templates; select via query param |

### Reading the Template

Before creating a PR via CLI, read the project's template and fill it in:

```bash
cat .github/pull_request_template.md
```

Then use the template structure as the PR body. Fill in every section -- don't leave placeholders like `...` or `{type}`.

### Multiple Templates

If the project has a `PULL_REQUEST_TEMPLATE/` directory with multiple templates, pick the one that matches your change type:

```bash
ls .github/PULL_REQUEST_TEMPLATE/
# feature.md  bugfix.md  docs.md
```

Use it with `gh pr create --template feature.md`.

## Creating a PR

### Via GitHub CLI (preferred)

```bash
git push -u origin HEAD

gh pr create \
  --title "feat(auth): implement JWT-based authentication" \
  --body "$(cat <<'EOF'
## Summary
Implement JWT authentication for the API, replacing session-based auth.

## Changes
- [x] New feature

## Test Plan
- [x] Unit tests pass (`just test`)
- [x] Integration tested locally

## Security Considerations
Tokens expire after 1 hour. Refresh tokens stored in httpOnly cookies.
EOF
)"
```

### Draft PRs

Open a draft PR early to signal intent and get CI feedback:

```bash
gh pr create --draft --title "feat(auth): implement JWT auth"
```

Mark ready when complete:

```bash
gh pr ready
```

## PR Title Format

PR titles follow conventional commit format -- they become the merge commit message:

```
<type>(<scope>): <description>
```

Examples:

```
feat(api): add user search endpoint
fix(parser): handle empty CSV rows
docs(readme): update installation steps
refactor(core): extract validation into module
```

## PR Description Structure

When no project template exists, use this structure:

```markdown
## Summary
<!-- 1-3 sentences: what changed and why -->

## Changes
- Added X to support Y
- Refactored Z for clarity
- Fixed edge case in W

## Test Plan
- [ ] Unit tests pass
- [ ] Manual testing done
- [ ] Edge cases verified

## Breaking Changes
<!-- If applicable: what consumers need to update -->
```

### Adapt to the Project Template

If the project has a template with sections like "Change log", "Analysis Packages Affected", or "Security Considerations", fill those in instead of using the generic structure. The project template takes precedence.

## PR Best Practices

### Size

- **Aim for < 400 lines changed** -- smaller PRs get faster, more thorough reviews
- If a feature is large, break it into stacked PRs or sequential PRs behind a feature flag
- Split refactoring from feature work into separate PRs

### Commits

- Each commit is one logical change with a conventional commit message
- Squash fixup commits before requesting review (or use GitHub's squash-merge)
- Keep a linear commit history with rebase

### Review Readiness

- All CI checks pass
- Self-review the diff before requesting review (`gh pr diff`)
- Add reviewers: `gh pr edit --add-reviewer @teammate`
- Link related issues: `Closes #42` in the PR body or via `gh pr edit --add-label bug`

### After Merge

```bash
git checkout main
git pull --rebase origin main
git branch -d feat/my-branch
git remote prune origin
```

## Common `gh` Commands

| Command | Purpose |
|---|---|
| `gh pr create` | Create a PR |
| `gh pr create --draft` | Create a draft PR |
| `gh pr ready` | Mark draft as ready for review |
| `gh pr list` | List open PRs |
| `gh pr view` | View current branch's PR |
| `gh pr diff` | Show the PR diff |
| `gh pr checks` | Show CI check status |
| `gh pr merge --squash` | Squash-merge the PR |
| `gh pr edit --add-reviewer @user` | Add a reviewer |
| `gh pr edit --add-label enhancement` | Add a label |

## Linking Issues

Reference issues in the PR body to auto-close them on merge:

```markdown
Closes #42
Fixes #123
Resolves #456
```

For cross-repo references: `Closes org/repo#42`.

## Anti-Patterns

- **Ignoring the project template** -- if a template exists, use it; don't write a freeform description
- **Leaving template placeholders** -- fill in or remove every `...`, `{type}`, and `<!-- comment -->`
- **Giant PRs** -- a 2000-line PR will get rubber-stamped, not reviewed
- **No test plan** -- reviewers need to know how you verified the change
- **Force-pushing after review** -- add fixup commits instead so reviewers can see incremental changes
