---
name: skill-creator
description: Guides creation and iterative improvement of AI agent skills. Use when creating a new skill, improving an existing skill, writing SKILL.md files, setting up skill test cases, evaluating skill quality, or optimizing skill trigger descriptions. Also use when someone says "turn this into a skill" or asks about skill best practices.
argument-hint: "[skill-name]"
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

1. Decide what you want the skill to do and roughly how it should do it
2. Write a draft of the skill
3. Create a few test prompts and run them with the skill active
4. Help the user evaluate the results both qualitatively and quantitatively
5. While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, you can either use as-is or modify). Then explain them to the user
6. Rewrite the skill based on feedback from the user's evaluation of the results (and also if there are any glaring flaws from quantitative benchmarks)
7. Repeat until satisfied
8. Expand the test set and try again at larger scale

Your job is to figure out where the user is in this process and help them progress. Maybe they say "I want to make a skill for X" -- help narrow it down, write a draft, write test cases, figure out evaluation, run prompts, and iterate. Or maybe they already have a draft -- go straight to eval/iterate.

Always be flexible. If the user says "I don't need to run a bunch of evaluations, just vibe with me", do that instead.

## Communicating with the User

Pay attention to context cues to understand how to phrase communication. In the default case:

- "evaluation" and "benchmark" are borderline, but OK
- For "JSON" and "assertion", look for cues that the user knows what those are before using them without explaining
- Briefly explain terms if in doubt; clarify with a short definition if unsure

## Creating a Skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from conversation history first -- the tools used, sequence of steps, corrections the user made, input/output formats observed. The user may need to fill gaps, and should confirm before proceeding.

Key questions:

- What should this skill enable the agent to do?
- When should this skill trigger? (what user phrases/contexts)
- What's the expected output format?
- Should we set up test cases? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them.

### Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier
- **description**: When to trigger, what it does. This is the primary triggering mechanism -- include both what the skill does AND specific contexts for when to use it. Make descriptions a little "pushy" to combat undertriggering.
- **argument-hint**: Optional hint for slash-command invocation (e.g. `"[skill-name]"`)
- **compatibility**: Required tools, dependencies (optional, rarely needed)
- The rest of the skill body

## Skill Writing Guide

### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

### Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) -- Always in context (~100 words)
2. **SKILL.md body** -- In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** -- As needed (unlimited, scripts can execute without loading)

Key patterns:

- Keep SKILL.md under 500 lines; if approaching this limit, add hierarchy with clear pointers about where the model should go next
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>300 lines), include a table of contents
- **Domain organization**: When a skill supports multiple domains/frameworks, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

### Writing Style

Explain to the model *why* things are important in lieu of heavy-handed MUSTs. Use theory of mind and try to make the skill general rather than super-narrow to specific examples. Start by writing a draft, then look at it with fresh eyes and improve it.

If you find yourself writing ALWAYS or NEVER in all caps, first ask whether explaining the *why* would be more effective. For hard constraints (security rules, data-loss prevention, breaking API contracts), firm directives are fine -- but pair them with the reasoning. For preferences and style guidance, explain why the pattern matters instead of mandating it.

## Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts -- the kind of thing a real user would actually say. Share them with the user for review.

See [schemas.md](references/schemas.md) for the JSON structures for `evals.json`, `eval_metadata.json`, `timing.json`, `grading.json`, and the workspace directory layout.

## Running and Evaluating Test Cases

### Step 1: Spawn all runs in the same turn

For each test case, spawn two runs -- one with the skill, one without (baseline). Launch everything at once so it finishes around the same time.

### Step 2: While runs are in progress, draft assertions

Draft quantitative assertions for each test case and explain them to the user. Good assertions are objectively verifiable and have descriptive names that read clearly in results. Subjective skills are better evaluated qualitatively.

### Step 3: Capture timing data

When each run completes, save timing data immediately -- this is the only opportunity to capture it.

### Step 4: Grade and aggregate

1. Grade each run against assertions, save to `grading.json`
2. Aggregate into benchmark (`benchmark.json` and `benchmark.md`)
3. Analyst pass -- surface patterns: non-discriminating assertions, high-variance evals, time/token tradeoffs

### Step 5: Review with the user

Present results for the user to review: prompt, output, formal grades, and feedback collection. Empty feedback means the user thought it was fine.

## Improving the Skill

**Generalize from the feedback.** Rather than put in fiddly overfitty changes, if there's a stubborn issue, try branching out with different metaphors or recommending different patterns.

**Keep the prompt lean.** Remove things that aren't pulling their weight. Read the transcripts, not just final outputs.

**Explain the why.** Today's LLMs are smart. They have good theory of mind and when given a good harness can go beyond rote instructions.

**Look for repeated work across test cases.** If all test cases result in the agent writing similar helper scripts, bundle that script in `scripts/`.

### The Iteration Loop

1. Apply improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory
3. Present results with comparison to previous iteration
4. Wait for user to review, read feedback, repeat

## Description Optimization

The `description` field is the primary mechanism that determines whether the agent invokes a skill. After creating or improving a skill, offer to optimize the description.

1. Generate 20 trigger eval queries (8-10 should-trigger, 8-10 should-not-trigger) -- realistic, detailed, with edge cases
2. Review with user
3. Run optimization loop: split 60/40 train/test, evaluate 3x per query, iterate up to 5 times, select by test score
4. Apply the best description to SKILL.md frontmatter

## Core Loop Summary

1. Figure out what the skill is about
2. Draft or edit the skill
3. Run the agent with the skill on test prompts
4. Evaluate the outputs with the user (qualitative review + quantitative evals)
5. Repeat until satisfied
6. Package the final skill

## Reference Files

- [schemas.md](references/schemas.md) -- JSON structures for evals, grading, timing, benchmarks, and workspace directory layout
