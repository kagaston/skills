# Eval and Benchmark Schemas

JSON structures for test cases, grading results, and benchmark data.

## evals.json

Main eval set saved at the skill level:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

## eval_metadata.json

Per-test-case metadata saved in each eval directory:

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": [
    {
      "name": "output-contains-header",
      "check": "Output file contains an H1 header"
    }
  ]
}
```

## timing.json

Captured from subagent completion notifications:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

## grading.json

Assertion results per run:

```json
{
  "expectations": [
    {
      "text": "Output contains an H1 header",
      "passed": true,
      "evidence": "Found '# Dashboard Report' at line 1"
    },
    {
      "text": "No hardcoded API keys",
      "passed": true,
      "evidence": "Searched output files, no API key patterns found"
    }
  ]
}
```

The `expectations` array must use the fields `text`, `passed`, and `evidence` -- the viewer depends on these exact field names.

## Trigger Eval Set

For description optimization:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

## Workspace Directory Structure

```
<skill-name>-workspace/
├── iteration-1/
│   ├── eval-descriptive-name/
│   │   ├── eval_metadata.json
│   │   ├── with_skill/
│   │   │   ├── outputs/
│   │   │   ├── timing.json
│   │   │   └── grading.json
│   │   └── without_skill/
│   │       ├── outputs/
│   │       ├── timing.json
│   │       └── grading.json
│   ├── benchmark.json
│   └── benchmark.md
├── iteration-2/
│   └── ...
└── feedback.json
```
