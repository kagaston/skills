---
name: subagent-patterns
description: When and how to delegate tasks to specialized subagents for parallel work, exploration, and specialized operations. Use when deciding whether to delegate to subagents or handle directly.
---

# Subagent Patterns

## Available Subagent Types

| Type | Use for | Strengths |
|------|---------|-----------|
| `generalPurpose` | Complex multi-step tasks, research, code search | Full tool access, autonomous decision-making |
| `explore` | Fast codebase exploration, finding files, searching code | Optimized for search, quick results |
| `shell` | Command execution, git operations, terminal tasks | Dedicated execution context |
| `browser-use` | Web testing, UI verification, browser automation | Visual testing, interaction simulation |

## When to Use Subagents

**Use for:**

1. **Parallel exploration** — Searching multiple areas simultaneously, investigating different approaches, gathering context from different components
2. **Complex exploration** — "How does module X work?", "Find all files matching pattern Y", "What patterns exist for Z?"
3. **Specialized operations** — Long-running commands, browser testing, multi-step git operations

**Don't use for:**

1. **Simple direct tasks** — Reading a known file (use Read), exact text search (use Grep), single file edit, quick command
2. **Sequential dependencies** — When you need results from step N to start step N+1
3. **Tasks you can do in 1-2 tool calls** — Reading 2-3 specific files, searching for a class definition

## Usage Patterns

**Parallel exploration** (max 4 concurrent):

```
Agent 1: "How is the auth module structured?"
Agent 2: "What CLI tools exist?"
Agent 3: "What test patterns are used?"
Wait for all → synthesize findings
```

**Thorough investigation:**

```
Launch explore agent with "very thorough":
"Find all places where incidents are filtered by status"
```

## Best Practices

- **Clear instructions**: Provide detailed context, specify exactly what to return, mention known files/directories
- **Appropriate scope**: Don't delegate 1-2 tool-call tasks. Don't over-parallelize (max 4)
- **Trust results**: Don't re-verify subagent outputs unless suspicious
- **Right tool for the job**: Use `explore` for search, `shell` for commands, `generalPurpose` for complex multi-step work

## Anti-Patterns

| Anti-Pattern | Better Approach |
|-------------|-----------------|
| Delegating single file read | Read the file directly |
| Delegating exact text search | Use Grep directly |
| Launching 1 agent for simple search | Use explore tools directly |
| Sequential agents when direct tools work | Handle directly |
| Delegating when you need immediate results | Do it yourself |

## Verification Checklist

- [ ] Task genuinely benefits from delegation (not doable in 1-2 calls)
- [ ] Instructions are detailed and specific
- [ ] Max 4 concurrent subagents
- [ ] Results synthesized for user (not raw agent output)
