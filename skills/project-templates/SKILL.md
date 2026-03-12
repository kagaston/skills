---
name: project-templates
description: Creating GitHub project templates for PRs, issues, CODEOWNERS, and CONTRIBUTING when none exist. Use when scaffolding a new project, adding PR templates, adding issue templates, creating CODEOWNERS, setting up CONTRIBUTING.md, or when a project is missing standard GitHub community files.
argument-hint: "[template-type]"
---

# Project Templates

When a project is missing standard GitHub community files, create them. This skill provides the canonical templates derived from the team's best projects.

## Detection

Check what exists before creating anything:

```bash
ls -la .github/pull_request_template.md \
       .github/PULL_REQUEST_TEMPLATE.md \
       .github/ISSUE_TEMPLATE/ \
       .github/CODEOWNERS \
       CONTRIBUTING.md 2>/dev/null
```

If the `.github/` directory doesn't exist at all, create it:

```bash
mkdir -p .github/ISSUE_TEMPLATE
```

## PR Template

Create `.github/pull_request_template.md`. This auto-populates every new PR on GitHub.

Adapt the template to the project type. Below are two proven patterns -- pick the one that fits, then customize the sections.

### Standard Template (most projects)

```markdown
## Summary
<!-- 1-3 sentences describing the change -->

## Changes
- [ ] New feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation
- [ ] Tests

## Test Plan
- [ ] Unit tests pass
- [ ] Integration tested locally

## Security Considerations
<!-- Does this change handle secrets, auth, or user input? Describe measures taken. -->
```

### Checklist Template (stricter workflow)

```markdown
**Checklist**

- [ ] This PR is not a duplicate of any other [existing PRs](../pulls)
- [ ] I have reviewed and followed the [contributing](../CONTRIBUTING.md) guidelines
- [ ] My code follows the code style of this project
- [ ] Pre-commit and pre-push checks pass locally

---

**What kind of change(s) does this PR introduce?**

| Type | Applies? |
|---|---|
| Bug fix | |
| New feature | |
| Breaking change | |
| Documentation | |
| Refactor | |

**Change log**
<!-- Describe what changed and why -->

**Breaking changes** _(if applicable)_
<!-- What must consumers update? -->
```

### Language-Specific Additions

Add project-specific sections as needed:

- **Python**: "Pre-commit checks pass (`just pre-commit`)"
- **Terraform**: "terraform validate passes", "terraform plan reviewed", "`tflint` clean"
- **Monorepo**: "Packages affected" checklist

## Issue Templates

Create templates in `.github/ISSUE_TEMPLATE/`. Each template gets its own file with YAML frontmatter.

### Bug Report -- `.github/ISSUE_TEMPLATE/bug_report.md`

```markdown
---
name: Bug Report
about: Something isn't working as expected
title: "[BUG]: "
labels: ["bug"]
---

**Describe the bug**

_A clear and concise description of what the bug is._

**Steps to reproduce**

1.

**Expected behavior**

_What you expected to happen._

**Environment**

- OS:
- Version:

**Additional context**

_Screenshots, logs, or other relevant information._
```

### Feature Request -- `.github/ISSUE_TEMPLATE/feature_request.md`

```markdown
---
name: Feature Request
about: Suggest an idea for this project
title: "[FR]: "
labels: ["enhancement"]
---

**Is your feature request related to a problem?**

_A clear description of the problem._

**Describe the solution you'd like**

_What you want to happen._

**Describe alternatives you've considered**

_Any alternative solutions or features you've considered._

**Additional information**

_Any other context or screenshots._
```

### General Issue -- `.github/ISSUE_TEMPLATE/issue.md`

```markdown
---
name: Issue
about: General issue related to this project
title: ""
labels: ""
assignees: ""
---

**Description**

_A clear and concise description of the issue._

**Potential solution**

_Any workarounds or solutions you've considered._

**Additional information**

_Any other context or screenshots._
```

## CODEOWNERS

Create `.github/CODEOWNERS` to auto-assign reviewers. The format is gitignore-style patterns mapped to GitHub teams or users.

```
# Default owners for everything
* @org/team-name

# Language-specific ownership
*.py @org/python-team
*.go @org/go-team
*.tf @org/infra-team

# Critical paths requiring senior review
src/auth/ @org/security-team
.github/ @org/platform-team
```

## CONTRIBUTING.md

Create `CONTRIBUTING.md` at the repo root. Tailor the commands to the project's actual tooling.

```markdown
# Contributing to {project-name}

## Setup

```bash
uv sync          # or: npm install, mix deps.get, go mod download
```

## Development Commands

| Command | Purpose |
|---|---|
| `just format` | Format code |
| `just lint` | Lint code |
| `just test` | Run tests |
| `just typecheck` | Type check |
| `just check` | Run all checks |

## Workflow

1. Create a branch: `git checkout -b feat/description`
2. Make changes with conventional commits
3. Run `just check` before pushing
4. Open a PR using the project template
5. Address review feedback
6. Squash-merge after approval

## Adding Dependencies

- `uv add <package>` -- runtime dependency
- `uv add --dev <package>` -- dev dependency

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(scope): add new capability
fix(scope): correct broken behavior
docs: update README
```
```

## Scaffold Command

To create all missing templates at once, run from the project root:

```bash
mkdir -p .github/ISSUE_TEMPLATE

# Only create files that don't already exist
[ ! -f .github/pull_request_template.md ] && echo "Create PR template"
[ ! -f .github/ISSUE_TEMPLATE/bug_report.md ] && echo "Create bug report template"
[ ! -f .github/ISSUE_TEMPLATE/feature_request.md ] && echo "Create feature request template"
[ ! -f .github/ISSUE_TEMPLATE/issue.md ] && echo "Create general issue template"
[ ! -f .github/CODEOWNERS ] && echo "Create CODEOWNERS"
[ ! -f CONTRIBUTING.md ] && echo "Create CONTRIBUTING.md"
```

Never overwrite existing templates -- they may have project-specific customizations.

## Verification Checklist

- [ ] `.github/pull_request_template.md` exists and has project-relevant sections
- [ ] `.github/ISSUE_TEMPLATE/` has at least bug_report.md and feature_request.md
- [ ] Issue templates have YAML frontmatter with `name`, `about`, `title`, `labels`
- [ ] `CODEOWNERS` maps critical paths to the right teams
- [ ] `CONTRIBUTING.md` documents setup, commands, and workflow
- [ ] Templates reference the project's actual tools (`just`, `uv`, `npm`, etc.)
