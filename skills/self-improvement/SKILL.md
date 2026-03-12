---
name: self-improvement
description: Continuous learning system for AI agents including retrospectives, lesson extraction, pattern detection, and rule/skill evolution. Use after completing tasks, after user corrections, when mistakes recur, or when proposing updates to project rules or skills.
---

# Self-Improvement and Retrospective System

## The Learning Loop

```
Task Execution → Retrospective → Lesson Extraction → Pattern Detection
                                                          ↓
                                              2+ occurrences? → Propose rule/skill update
                                                          ↓
                                              User approves → Update rule/skill
```

## When to Trigger

**Mandatory triggers:**

1. **User corrections** — "Actually, you should have...", "That's not right..."
2. **Task failures** — Lint errors, test failures, apply errors
3. **Inefficiencies** — Task took longer than expected, multiple attempts needed
4. **Discoveries** — Found better pattern, learned new tool capability

## Retrospective Protocol (Four Questions)

After every task, ask:

1. **What was the task?** — Brief description, components affected, files changed
2. **What went well?** — Successful approaches, efficient workflows, good decisions
3. **What went wrong?** — Mistakes, inefficiencies, user corrections
4. **What did we learn?** — Actionable lessons, patterns identified, better approaches

## Lesson Extraction

Document lessons in structured format:

```yaml
date: 2026-03-12
task: "Brief task description"
issue: "What went wrong or could be better"
root_cause: "Why it happened"
solution: "How to prevent or fix"
pattern: "pattern-identifier"
occurrences: 1
impact: "low|medium|high"
```

**Storage:** `.agents/knowledge/lessons/YYYY-MM-DD-{short-description}.yaml`

## Pattern Detection

A pattern exists when:

- Same mistake happens 2+ times
- Same type of issue across different tasks
- Similar root cause in different contexts

**Thresholds:**

| Occurrences | Action |
|-------------|--------|
| 1 | Log lesson, monitor |
| 2 | Propose rule/skill update |
| 3+ | Critical gap, urgent update |

**Common pattern categories:**

- Workflow violations (skipped lint, skipped tests)
- Code quality (repeated lint errors, formatting)
- Architecture (misunderstanding project structure)
- Tooling (incorrect commands, missing flags)

## Rule/Skill Update Process

When a pattern is detected (2+ occurrences):

1. **Identify target** — Which rule or skill file should be updated?
2. **Draft proposed change** — What specific text to add/modify? Why?
3. **Present to user:**

   ```
   Pattern detected: {pattern-name}
   Occurrences: {count}
   Issue: {what keeps happening}

   I propose updating {filename} to add:
   "{proposed text}"

   This would prevent {problem} by {solution}.
   Reply "yes" to approve or "no" to decline.
   ```

4. **Apply if approved** — Update the file, update last_updated date

## Rule File Standards

If the project uses `.cursor/rules/`:

- File naming: `NNN-topic.mdc` (numbered for load order)
- Required frontmatter: title, description, last_updated
- Include self-improvement reminder at the end
- Include closing "Remember:" takeaway

## After User Correction

```
1. Acknowledge: "You're right, I should have done X"
2. Understand why: Why is X better than Y?
3. Document lesson: Create lesson file with pattern
4. Check occurrences: Have I made this mistake before?
5. Propose rule update if pattern (2+ occurrences)
```

## Verification Checklist

- [ ] Retro run after task completion
- [ ] Lessons documented for mistakes/corrections
- [ ] Patterns checked against previous lessons
- [ ] Rule/skill update proposed when pattern detected
- [ ] User approval obtained before updating rules
