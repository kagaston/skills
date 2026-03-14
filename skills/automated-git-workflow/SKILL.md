---
name: automated-git-workflow
description: Automated Git Flow branching workflow for AI agents -- stage, commit, push feature branches, merge to dev, monitor GitHub Actions, clean up, and propagate skill updates to sibling skill-* repos. Use when implementing a feature end-to-end, pushing code changes, merging branches, checking CI status, cleaning up branches, or syncing skills across repos.
---

# Automated Git Workflow

End-to-end Git Flow automation for AI agents. This workflow covers the full lifecycle from code change to merged branch to skill propagation -- no manual steps.

## Overview

```
Stage → Commit → Push Branch → Monitor CI → Merge to dev → Delete Branch → Sync Skills
```

The entire flow runs against a Git Flow model where `dev` is the integration branch and `main` is release-only. Feature branches are short-lived and always target `dev`.

## Workflow Steps

### 1. Start from a Clean dev

Before any work, pull the latest `dev` to avoid drift:

```bash
git checkout dev
git pull --rebase origin dev
```

Check for duplicate branches before creating a new one:

```bash
git branch -a | grep -i <keyword>
```

### 2. Create a Feature Branch

Branch from `dev` using conventional type prefixes:

```bash
git checkout -b <type>/<short-description>
```

Types: `feat/`, `fix/`, `docs/`, `refactor/`, `chore/`, `test/`, `ci/`

Keep names under 50 characters, lowercase, kebab-case. Include ticket numbers when available (e.g. `feat/42-add-scanner`).

### 3. Stage and Commit Changes

Stage files deliberately -- never blindly `git add .` without reviewing what changed:

```bash
git add <specific-files>
git status
```

Commit with conventional commit messages:

```bash
git commit -m "type(scope): description"
```

Commit rules:
- One logical change per commit
- Lowercase imperative description, no trailing period
- Body explains *why*, not *what*
- Run lint + tests before committing

### 4. Push the Branch

First push sets upstream tracking:

```bash
git push -u origin HEAD
```

Subsequent pushes:

```bash
git push
```

### 5. Work the Branch

Continue making incremental commits. Rebase onto `dev` regularly to stay current:

```bash
git fetch origin
git rebase origin/dev
```

When the work is complete and tests pass, proceed to merge.

### 6. Merge to dev

Merge the feature branch into `dev` with a merge commit for clean history:

```bash
git checkout dev
git pull --rebase origin dev
git merge --no-ff <branch-name> -m "feat: merge <description> into dev"
git push origin dev
```

The `--no-ff` flag preserves the branch topology in the commit graph.

### 7. Monitor GitHub Actions

After pushing to `dev`, check that CI passes:

```bash
gh run list --repo <owner>/<repo> --branch dev --limit 5 --json conclusion,workflowName,status
```

Poll until runs complete. Check the latest run conclusion:

```bash
gh run list --repo <owner>/<repo> --branch dev --limit 1 --json conclusion --jq '.[0].conclusion'
```

If the conclusion is `success`, proceed. If `failure`:

1. Pull the failing logs:

```bash
gh run view <run-id> --repo <owner>/<repo> --log-failed
```

2. Fix the issue on the feature branch (or a new fix branch), push, and re-merge.

If no GitHub Actions workflows exist on the repo, skip this step -- there is nothing to wait on.

### 8. Delete the Feature Branch

Once CI is green (or no CI exists), clean up:

```bash
git branch -d <branch-name>
git push origin --delete <branch-name>
```

Prune stale remote references:

```bash
git remote prune origin
```

### 9. Propagate Skills to Sibling Repos

After successful merge, check if any skills were created or updated in the project's `skills/` directory. If so, propagate them to sibling `skill-*` repos that live in the same parent directory as the project.

Discovery -- find sibling skill repos:

```bash
ls -d "$(dirname "$(pwd)")/skill"*/ "$(dirname "$(pwd)")/skills"*/ 2>/dev/null
```

For each skill repo found (e.g. `skills-external/`, `skills-internal/`):

1. Check if the skill already exists in the target repo's `skills/` directory
2. If it exists: compare content, update if changed
3. If new: copy the skill directory into the target repo's `skills/`
4. Stage, commit, and push the change in the target repo:

```bash
cd <target-skill-repo>
git checkout dev && git pull --rebase origin dev
git checkout -b chore/sync-skill-<skill-name>
cp -r <source-project>/skills/<skill-name> skills/
git add skills/<skill-name>/
git commit -m "chore(skills): sync <skill-name> from <project>"
git push -u origin HEAD
git checkout dev
git merge --no-ff chore/sync-skill-<skill-name>
git push origin dev
git branch -d chore/sync-skill-<skill-name>
git push origin --delete chore/sync-skill-<skill-name>
```

Only sync skills that are explicitly marked for external sharing. Project-specific skills (e.g. internal config loaders) stay local.

## Decision Table

| Situation | Action |
|---|---|
| No CI workflows on repo | Skip step 7, proceed to cleanup |
| CI fails | Fix on branch, re-merge, re-check |
| CI passes | Delete branch, sync skills |
| Skill already exists in target repo | Compare and update if changed |
| Skill is project-specific | Do not propagate |
| Hotfix needed on main | Branch from `main`, merge back to both `main` and `dev` |

## Anti-Patterns

- **Pushing directly to dev or main** -- always use a feature branch, even for one-line fixes
- **Skipping CI check** -- wait for green before cleaning up branches
- **Leaving zombie branches** -- delete immediately after merge
- **Blind `git add .`** -- review staged files, exclude secrets and generated artifacts
- **Skipping skill sync** -- if a skill was created or updated, propagate it so sibling repos stay current
- **Committing tool attribution** -- no "made with Cursor" or "generated by AI" in commit messages or comments; write human-readable messages

## Commit Message Examples

```
feat(scanner): add TODO plan finder with priority parsing
fix(security): upgrade requests to 2.32.0 (CVE-2025-1234)
chore(skills): sync automated-git-workflow from runner
docs(readme): update quick start instructions
refactor(config): extract repo type into enum
```
