---
name: agent-workflow
description: Standard workflow for AI coding agents including core principles, plan-first methodology, quality gates, execution flow, and session completion. Use when starting tasks, planning changes, or establishing development workflow.
---

# Agent Workflow

## Core Principles

1. **Clarity Over Cleverness** — Write code that is easy to understand. Prefer explicit over implicit.
2. **Simplicity First** — Solve problems with the simplest solution. Add complexity only when justified.
3. **Correctness Above All** — Always verify with lint and tests before committing. Never skip quality checks.
4. **Maintainability Matters** — Code is read more often than written. Document the "why", not the "what".
5. **Incremental Progress** — Small, focused changes are safer. Change → Lint → Test → Repeat.

## Plan-First Methodology

Every task follows four phases:

1. **Research** — Understand the codebase, gather context, read relevant files
2. **Plan** — Break down the task, identify dependencies, estimate blast radius
3. **Implement** — Make changes incrementally, verify after each step
4. **Review** — Run quality gate, verify all changes, clean up

## Quality Gates

EVERY change MUST pass quality checks before committing. No exceptions.

```
Read relevant code → Check baseline (lint + test) → Make changes →
Run lint → Run tests → Review results → Clean? → Commit
                                          ↓ No
                                     Debug & fix → Re-verify
```

**Re-check triggers** (must re-run lint and tests after):

- Any code change, even small edits
- Lint fixes
- Import changes
- Dependency changes
- Test changes
- Merge conflict resolution

## Execution Flow

1. **Read** relevant source files — understand before changing
2. **Baseline** — run lint + tests to ensure clean starting point
3. **Change** — make one focused change at a time
4. **Verify** — run lint + tests after each change
5. **Iterate** — repeat until done, then commit

## Task Planning Framework

1. **Understand the request**: What is being asked? Which components? What files?
2. **Gather context**: Read relevant code, check existing patterns, review tests
3. **Break down**: Identify smallest atomic changes, order by dependency
4. **Plan verification**: What should lint report? What should tests show?

## Task Size Guidelines

| Size | Examples | Approach |
|------|----------|----------|
| Small (<30 min) | Single function, bug fix, new script | Single session |
| Medium (30 min - 2 hr) | New module, refactor, multiple related changes | 3-5 incremental steps |
| Large (>2 hr) | Major rewrite, new feature with tests, breaking changes | 10+ steps, plan carefully |

## Session Completion ("Landing the Plane")

Before ending a session:

1. All changes are committed with descriptive messages
2. All lint and tests pass
3. Working directory is clean (`git status` shows nothing)
4. Push changes to remote (`git push`)
5. Summarize what was done and any follow-up items

## Agent Communication Style

- Be direct and technical
- Focus on facts, not validation
- Disagree when something is wrong
- Ask clarifying questions when requirements are ambiguous
- Never create documentation files unless explicitly asked

## Never Do / Always Do

**Never**: Skip lint or tests. Commit without verifying. Make multiple unrelated changes together. Assume code works without testing.

**Always**: Read before editing. Lint after changes. Test after changes. Make small focused changes. Clean up temporary artifacts.

## Verification Checklist

- [ ] Read relevant code before editing
- [ ] Baseline lint + tests pass
- [ ] Changes are incremental and focused
- [ ] Lint passes after each change
- [ ] Tests pass after each change
- [ ] Commit message is descriptive
- [ ] Working directory is clean
- [ ] Changes pushed to remote
