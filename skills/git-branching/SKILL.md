---
name: git-branching
description: Branching strategies and branch lifecycle management with a preference for trunk-based development. Use when creating branches, checking out branches, starting work on a feature or fix, planning development work, choosing a branching strategy, or discussing git workflow.
argument-hint: "[branch-name]"
---

# Git Branching

## Strategy: Trunk-Based Development

Trunk-based development is the preferred branching strategy. All work flows through short-lived feature branches that merge into a single `main` trunk.

### Why Trunk-Based

- **Smaller diffs** -- easier to review, less merge conflict risk
- **Continuous integration** -- main is always deployable
- **Faster feedback** -- changes land in hours or days, not weeks
- **Simpler model** -- no long-lived develop/release/hotfix branches to manage

### How It Works

```
main ─────●────●────●────●────●────●─────
           \  /      \  /      \  /
            ●         ●         ●
          feat/x    fix/y    feat/z
        (1-3 days) (hours)  (2 days)
```

1. `main` is the single source of truth and is always deployable
2. Feature branches are short-lived (ideally < 3 days)
3. Merge via pull request with CI checks passing
4. Delete the branch after merge
5. Use feature flags for incomplete work that must merge early

### When to Deviate

| Situation | Approach |
|---|---|
| Open-source with external contributors | Fork-based workflow; contributors PR from forks |
| Rigid release cadence (mobile apps, on-prem) | Release branches cut from main, hotfixes cherry-picked |
| Regulatory/compliance gates | Release branch for sign-off, then merge to main and tag |

Even in these cases, keep the spirit: branches are short-lived, main stays healthy.

## Branch Lifecycle

### 1. Before Creating a Branch

Always start from a clean, up-to-date main:

```bash
git checkout main
git pull --rebase origin main
```

Check for an existing branch first -- don't duplicate work:

```bash
git branch -a | grep -i <keyword>
```

### 2. Create and Checkout

Name the branch using conventional type prefixes (matching commit types):

```bash
git checkout -b feat/add-user-auth
git checkout -b fix/123-null-response
git checkout -b docs/update-api-guide
git checkout -b refactor/extract-token-module
git checkout -b chore/upgrade-dependencies
```

### 3. Push and Track

Push the branch and set upstream on first push:

```bash
git push -u origin HEAD
```

### 4. Keep Current with Main

Rebase onto main regularly to avoid drift. Do this at least daily for active branches:

```bash
git fetch origin
git rebase origin/main
```

If rebase produces conflicts, resolve them one commit at a time. If the branch has diverged significantly, consider a merge instead:

```bash
git merge origin/main
```

### 5. Clean Up After Merge

Delete the branch locally and remotely after the PR merges:

```bash
git branch -d feat/add-user-auth
git remote prune origin
```

## Branch Naming Conventions

```
<type>/<short-description>
<type>/<issue-number>-<short-description>
```

### Rules

- Use lowercase with hyphens (kebab-case) for the description
- Keep it under 50 characters total
- Include the issue/ticket number when one exists
- Use the same type prefixes as conventional commits

### Examples

| Branch | Purpose |
|---|---|
| `feat/oauth-google-login` | New Google OAuth feature |
| `fix/42-csv-parse-error` | Fix for issue #42 |
| `docs/contributing-guide` | Documentation update |
| `refactor/split-user-service` | Code restructuring |
| `chore/bump-python-313` | Dependency/tooling maintenance |
| `test/e2e-checkout-flow` | Adding test coverage |
| `ci/add-deploy-stage` | CI pipeline changes |
| `release/2.1.0` | Release branch (when needed) |

## Planning Workflow

When starting a planned piece of work (from a ticket, issue, or task list):

1. **Pull latest main** -- `git checkout main && git pull --rebase origin main`
2. **Create the branch** -- `git checkout -b <type>/<ticket>-<description>`
3. **Make an empty initial commit** (optional, useful for draft PRs):
   ```bash
   git commit --allow-empty -m "chore: begin work on <ticket> <description>"
   git push -u origin HEAD
   ```
4. **Open a draft PR immediately** -- this signals intent to the team and enables early CI feedback. Use `gh pr create --draft` if using the GitHub CLI.
5. **Work in small commits** -- each commit is one logical change, following conventional commit format
6. **Mark PR as ready** when CI passes and the work is complete

## Feature Flags for Incomplete Work

When a feature takes longer than a few days, merge partial work behind a feature flag rather than keeping a long-lived branch:

```python
if feature_flags.is_enabled("new_checkout_flow"):
    return new_checkout(cart)
return legacy_checkout(cart)
```

This keeps the branch short-lived while the feature remains hidden until ready.

## Anti-Patterns

- **Long-lived feature branches** -- branches open for weeks accumulate merge conflicts and block collaboration
- **Merging main into feature branches** -- prefer rebase to keep a linear history
- **Working directly on main** -- always use a branch, even for small fixes
- **Branch naming without type prefix** -- `my-changes` or `kevin-branch` provides no context
- **Zombie branches** -- delete branches after merge; stale branches clutter the remote
