---
name: code-review
description: Systematic code review methodology covering architecture, security, performance, testing, and documentation. Use when reviewing pull requests, checking code quality, providing feedback on implementations, identifying bugs, suggesting improvements, performing security audits, or analyzing performance.
argument-hint: "[pr-url or file]"
---

# Code Review

## When to Use

- Reviewing pull requests
- Checking code quality
- Providing feedback on implementations
- Identifying potential bugs
- Suggesting improvements
- Security audits
- Performance analysis

## Step 1: Understand the Context

**Read the PR description:**

- What is the goal of this change?
- Which issues does it address?
- Are there any special considerations?

**Check the scope:**

- How many files changed?
- What type of changes? (feature, bugfix, refactor)
- Are tests included?

## Step 2: High-Level Review

**Architecture and design:**

- Does the approach make sense?
- Is it consistent with existing patterns?
- Are there simpler alternatives?
- Is the code in the right place?

**Code organization:**

- Clear separation of concerns?
- Appropriate abstraction levels?
- Logical file/folder structure?

## Step 3: Detailed Code Review

**Naming:**

- Variables: descriptive, meaningful names
- Functions: verb-based, clear purpose
- Classes: noun-based, single responsibility
- Constants: UPPER_CASE for true constants
- Avoid abbreviations unless widely known

**Functions:**

- Single responsibility
- Reasonable length (< 50 lines ideally)
- Clear inputs and outputs
- Minimal side effects
- Proper error handling

**SOLID principles:**

- Single responsibility principle
- Open/closed principle
- Liskov substitution principle
- Interface segregation
- Dependency inversion

**Error handling:**

- All errors caught and handled
- Meaningful error messages
- Proper logging
- No silent failures
- User-friendly errors for UI

**Code quality:**

- No code duplication (DRY)
- No dead code
- No commented-out code
- No magic numbers
- Consistent formatting

## Step 4: Security Review

**Input validation:** All user inputs validated (type, range, format).

**Auth:** Proper authentication checks, authorization for sensitive operations, session management, password hashing.

**Data protection:** No hardcoded secrets, sensitive data encrypted, SQL injection prevention, XSS prevention, CSRF protection.

**Dependencies:** No vulnerable packages, dependencies up-to-date, minimal dependency usage.

## Step 5: Performance Review

**Algorithms:** Appropriate choice, reasonable time/space complexity, no unnecessary loops.

**Database:** Efficient queries, proper indexing, N+1 query prevention, connection pooling.

**Resources:** Files properly closed, connections released, memory leaks prevented, caching strategy with invalidation.

## Step 6: Testing Review

**Coverage:** Unit tests for new code, integration tests if needed, edge cases and error cases covered.

**Quality:** Tests are readable, maintainable, deterministic, with no interdependencies and proper setup/teardown.

**Naming:**

```python
# Good
def test_user_creation_with_valid_data_succeeds():
    pass

# Bad
def test1():
    pass
```

## Step 7: Documentation Review

**Code comments:** Complex logic explained, no obvious comments, TODOs have tickets, comments are accurate.

**Function documentation:**

```python
def calculate_total(items: list[Item], tax_rate: float) -> Decimal:
    """Calculate the total price including tax.

    Args:
        items: List of items to calculate total for.
        tax_rate: Tax rate as decimal (e.g., 0.1 for 10%).

    Returns:
        Total price including tax.

    Raises:
        ValueError: If tax_rate is negative.
    """
```

**README/docs:** Updated if needed, API docs updated, migration guide if breaking changes.

## Step 8: Provide Feedback

**Be constructive** -- suggest alternatives, not just problems. **Be specific** -- reference line numbers and concrete fixes. **Acknowledge good work** -- positive feedback matters.

**Prioritize issues:**

- RED Critical: Security, data loss, major bugs
- YELLOW Important: Performance, maintainability
- GREEN Nice-to-have: Style, minor improvements

See [review-checklist.md](references/review-checklist.md) for the printable checklist, anti-patterns, and security vulnerability examples.

## Best Practices

- **Review promptly** -- don't make authors wait
- **Be respectful** -- focus on code, not the person
- **Explain why** -- don't just say what's wrong
- **Suggest alternatives** -- show better approaches
- **Use examples** -- code examples clarify feedback
- **Pick your battles** -- focus on important issues
- **Use automated tools** -- let linters catch style issues
- **Be consistent** -- apply same standards to all code

## Reference Files

- [review-checklist.md](references/review-checklist.md) -- Printable review checklist, common anti-patterns, and security vulnerability examples
