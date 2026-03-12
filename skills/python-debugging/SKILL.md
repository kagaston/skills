---
name: python-debugging
description: Systematic debugging and fixing of Python issues including root cause analysis, common error patterns, and fix protocols. Use when encountering Python errors, debugging issues, or fixing broken code.
---

# Python Debugging

## Philosophy

1. **Understand** before fixing
2. **Fix root cause**, not symptoms
3. **Verify** the fix works
4. **Learn** from the issue

## Root Cause Analysis

When encountering an issue, ask:

1. **What failed?** — Lint? Test? Import? Runtime? What's the exact error?
2. **What changed?** — Recent code changes? Dependency update? Python version?
3. **What's the expected behavior?** — What should happen vs what's actually happening?
4. **What's the blast radius?** — One file? Multiple? One module? All?

## Common Issue Categories

### Lint Errors

- **Diagnosis**: `ruff check .`
- **Common**: unused imports, naming violations, line too long, missing docstrings
- **Fix**: read error, fix specific issue, re-run lint

### Test Failures

- **Diagnosis**: `pytest -v --tb=long tests/test_specific.py::test_name`
- **Common**: logic errors, changed API responses, missing fixtures, env-dependent tests
- **Fix**: read failing test, compare expected vs actual, fix code or update test

### Import Errors

- **Diagnosis**: `python -c "from mypackage import module"`
- **Common**: wrong import path, missing `__init__.py`, package not installed, circular imports
- **Fix**: verify paths match file structure, ensure `__init__.py` exists, run `uv sync`

### Dependency Issues

- **Diagnosis**: `uv pip check` or `pip check`
- **Common**: conflicting versions, missing dependencies, wrong virtualenv
- **Fix**: update `pyproject.toml`, run `uv sync`, verify virtualenv

## Systematic Fix Protocol

```
1. Identify the error        → Read error message carefully
2. Reproduce the issue       → Run the failing command
3. Locate root cause         → Which file? Which line?
4. Understand the context    → Read surrounding code
5. Fix the root cause        → Not just the symptom
6. Verify the fix            → Run lint + tests
7. Ensure no side effects    → All tests pass, no new lint errors
```

**CRITICAL**: Never commit without verifying lint and tests after a fix.

## Common Fixes

**Unused import**: Remove it, or add `# noqa: F401` if intentional re-export

**Line too long**: Break logically:

```python
result = some_function(
    argument_one,
    argument_two,
    argument_three,
)
```

**Missing error handling**: Add explicit exception handling:

```python
try:
    response = client.get(url)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    logger.error("Request failed: %s", e)
    raise AppError("API request failed") from e
```

## Error Message Patterns

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `ModuleNotFoundError` | Package not installed | `uv sync` or fix import path |
| `ImportError` | Wrong import path | Check module structure |
| `AttributeError: module has no attribute` | Circular import or typo | Check import order |
| `TypeError: unexpected keyword argument` | API signature changed | Update caller to match |

## Prevention > Cure

- Run lint after every change
- Run tests after every change
- Read existing code before modifying
- Follow established patterns
- Handle errors explicitly

## Verification Checklist

- [ ] Error message read carefully
- [ ] Root cause identified (not just symptom)
- [ ] Fix addresses root cause
- [ ] Lint passes after fix
- [ ] Tests pass after fix
- [ ] No new errors introduced
