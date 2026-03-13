---
name: implementation-plans
description: Create structured implementation plans in a TODO/ directory using .plan.md files with badges, Mermaid diagrams, phased scheduling, and actionable checklists. Use when breaking down a project into parallelizable workstreams, creating implementation roadmaps, scaffolding a TODO directory, or when someone says "create a plan", "build out plans", or "what needs to be done".
---

# Implementation Plans

Create a `TODO/` directory of `.plan.md` files that break a project into parallelizable workstreams with dependency tracking, phased scheduling, and granular implementation checklists.

## When to Use

- Breaking a project into implementable workstreams
- Creating a roadmap with dependency-aware scheduling
- Scaffolding a TODO directory for a new or existing project
- Producing plans that multiple teams/branches can work in parallel

## Workflow

### Phase 1: Discover

Scan the codebase before writing any plans. Identify:

1. **What exists** -- read config files, source code, tests, docs, docker-compose, justfile
2. **What's broken** -- silent `except: pass`, mismatched configs, dead code, stubs
3. **What's missing** -- no tests, no CI, no Dockerfile, no docs, unfinished features
4. **What's wired wrong** -- wrong method names, missing persistence, unconnected modules

Group findings into logical workstreams (5-15 is typical). Each workstream should be completable on a single feature branch.

### Phase 2: Map Dependencies

For each workstream, determine:
- What it is **blocked by** (must land first)
- What it **blocks** (depends on this)
- Its **phase** (1 = no blockers, 2 = needs phase 1, 3 = needs phase 2)

Build a Mermaid dependency graph.

### Phase 3: Write Plans

Create the `TODO/` directory with an overview and individual plan files.

## Directory Structure

```text
TODO/
├── 00-overview.plan.md          # Master plan with dependency graph
├── 01-workstream-name.plan.md   # Individual workstream
├── 02-workstream-name.plan.md
├── ...
└── NN-workstream-name.plan.md
```

Naming: `{NN}-{kebab-case-name}.plan.md` -- zero-padded number for sort order.

## Overview File Format (00-overview.plan.md)

```markdown
# Project Implementation Plan — Master Overview

![Plans](https://img.shields.io/badge/plans-N-blue) ![Phase 1](https://img.shields.io/badge/phase%201-N%20active-green)

> One-sentence summary of the overall plan.

## Status Legend

| Symbol | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Complete |
| `[B]` | Blocked (dependency not met) |

## Workstream Summary

| # | Workstream | Phase | Status | Effort | Blocked By | Blocks |
|---|-----------|-------|--------|--------|------------|--------|
| 01 | [Name](01-name.plan.md) | 1 | `[ ]` | S | — | 03 |
| 02 | [Name](02-name.plan.md) | 2 | `[B]` | M | 01 | — |

## Dependency Graph

(Mermaid graph TD showing workstream dependencies with edge labels)

## Phase Schedule

### Phase 1 — No Blockers (Start Immediately)

| Workstream | Branch Suggestion | Summary |
|------------|-------------------|---------|
| 01 Name | `fix/branch-name` | One-line summary |

### Phase 2 — After Phase 1

| Workstream | Branch Suggestion | Depends On | Summary |
|------------|-------------------|------------|---------|

## Architecture Reference

(Project directory tree or component diagram)

## How to Use These Plans

1. Check this overview for unblocked workstreams.
2. Pick one and open its plan file.
3. Create a feature branch.
4. Work through the checklist.
5. Update status when complete.
```

## Individual Plan File Format

Every `.plan.md` file follows this structure:

```markdown
# NN — Workstream Title

![Phase N](https://img.shields.io/badge/phase-N-blue) ![Effort: M](https://img.shields.io/badge/effort-M-yellow) ![Status: Not Started](https://img.shields.io/badge/status-not%20started-lightgrey)

> One-sentence summary of what this plan achieves.

## Goal

2-3 sentences expanding on the problem and the approach.

## Scheduling

- **Phase:** N (start immediately | after phase N)
- **Blocked By:** nothing | 01, 03
- **Blocks:** 05, 07 | nothing
- **Estimated Effort:** S (1-2 days) | M (2-3 days) | L (3-5 days) | XL (5-8 days)
- **Suggested Branch:** `feat/branch-name`

## Context

Why this work is needed. What's currently broken or missing.
Include relevant code references with file paths and line numbers.

## Architecture

(Mermaid diagram showing components, data flow, or relationships relevant to this workstream)

## Tasks

### 1. Task Title

Description of what needs to change and why.

- [ ] **1.1 Sub-step with specific action**
  - [ ] Open `path/to/file.py`
  - [ ] Find line N: `existing code`
  - [ ] Change to: `new code`
  - [ ] Save file

  ```python
  # BEFORE (line N)
  old_code()

  # AFTER
  new_code()
  ```

  - [ ] **Verify:** `just lint` passes
  - [ ] **Verify:** `uv run pytest path/to/tests/ -v`

---

### 2. Next Task Title

(Same pattern: description, sub-steps, code snippets, verification)

---

## Key Files

| File | Change |
|------|--------|
| `path/to/file.py` | Brief description of change |

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Quality gates pass

## Final Verification Sequence

(Project-appropriate quality gate commands)
```

## Badge Reference

Use shields.io badges for visual status. Place on the line after the H1 title.

| Badge | Markdown |
|-------|----------|
| Phase 1 | `![Phase 1](https://img.shields.io/badge/phase-1-blue)` |
| Phase 2 | `![Phase 2](https://img.shields.io/badge/phase-2-yellow)` |
| Phase 3 | `![Phase 3](https://img.shields.io/badge/phase-3-purple)` |
| Effort S | `![Effort: S](https://img.shields.io/badge/effort-S-green)` |
| Effort M | `![Effort: M](https://img.shields.io/badge/effort-M-yellow)` |
| Effort L | `![Effort: L](https://img.shields.io/badge/effort-L-orange)` |
| Effort XL | `![Effort: XL](https://img.shields.io/badge/effort-XL-red)` |
| Not Started | `![Status: Not Started](https://img.shields.io/badge/status-not%20started-lightgrey)` |
| Blocked | `![Status: Blocked](https://img.shields.io/badge/status-blocked-red)` |
| In Progress | `![Status: In Progress](https://img.shields.io/badge/status-in%20progress-yellow)` |
| Complete | `![Status: Complete](https://img.shields.io/badge/status-complete-brightgreen)` |

## Formatting Rules

1. **Badges** -- every `.plan.md` must have Phase, Effort, and Status badges under the H1
2. **Blockquote summary** -- one sentence after badges, before first H2
3. **Mermaid diagram** -- every plan file must have at least one, showing relevant architecture or data flow
4. **Code blocks** -- always tagged with a language (`python`, `bash`, `yaml`, `text`, `just`, `toml`, etc.)
5. **Before/after snippets** -- show the exact code change with file path and line number
6. **Verification steps** -- every task must end with concrete verify commands
7. **No placeholder text** -- no `TODO`, `...`, `your-org`, or `{variable}` in final output
8. **Heading hierarchy** -- one H1, H2 for sections, H3 for tasks, H4 for sub-tasks
9. **Horizontal rules** -- use `---` between tasks for visual separation

## Task Granularity Guide

Each task sub-step should be atomic enough for an AI agent to execute:

- Name the specific file to edit
- Quote the exact code to find (with line number if known)
- Show the replacement code
- Provide a verification command

**Too vague:**
> Fix the database connection

**Right level:**
> - [ ] Open `app/settings/src/settings/config.py`
> - [ ] Find line 26: `POSTGRES_DB = os.getenv("POSTGRES_DB", "mas")`
> - [ ] Change default from `"mas"` to `"analytics"`
> - [ ] **Verify:** `grep POSTGRES_DB app/settings/src/settings/config.py`

## Effort Sizing

| Size | Duration | Scope |
|------|----------|-------|
| S | 1-2 days | Config fixes, doc updates, small refactors |
| M | 2-3 days | New module, integration work, test expansion |
| L | 3-5 days | Major feature, security overhaul, multi-file refactor |
| XL | 5-8 days | Architecture change, new subsystem, framework migration |

## Anti-Patterns

- **Monolith plans** -- if a plan is over 500 lines, split it into sub-plans
- **Circular dependencies** -- phases must be a DAG; no workstream can block itself
- **Missing verification** -- every task must have a way to prove it worked
- **Aspirational plans** -- only plan work grounded in actual codebase findings
- **Implicit dependencies** -- always document what blocks what and why

## Verification Checklist

- [ ] `TODO/` directory exists with `00-overview.plan.md`
- [ ] Every plan file uses `{NN}-{kebab-case}.plan.md` naming
- [ ] Every `.plan.md` has Phase, Effort, and Status badges under H1
- [ ] Overview contains a Mermaid dependency graph
- [ ] Every individual plan has at least one Mermaid diagram
- [ ] Dependencies form a DAG (no circular references)
- [ ] Every task ends with a verification command
- [ ] Sub-steps are atomic: specific file, exact code, replacement, verify
- [ ] No placeholder text in final output
- [ ] Plans total 5-15 workstreams (split or merge if outside range)
