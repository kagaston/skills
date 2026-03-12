# Code Review Checklist

Printable checklist for systematic code review.

## Functionality

- [ ] Code does what it's supposed to do
- [ ] Edge cases handled
- [ ] Error cases handled
- [ ] No obvious bugs

## Code Quality

- [ ] Clear, descriptive naming
- [ ] Functions are small and focused
- [ ] No code duplication
- [ ] Consistent with codebase style
- [ ] No code smells

## Security

- [ ] Input validation
- [ ] No hardcoded secrets
- [ ] Authentication/authorization
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities

## Performance

- [ ] No obvious bottlenecks
- [ ] Efficient algorithms
- [ ] Proper database queries
- [ ] Resource management

## Testing

- [ ] Tests included
- [ ] Good test coverage
- [ ] Tests are maintainable
- [ ] Edge cases tested

## Documentation

- [ ] Code is self-documenting
- [ ] Comments where needed
- [ ] Docs updated
- [ ] Breaking changes documented

---

## Common Anti-Patterns

**God class** -- one class doing everything (user management, email, payments, reports). Split by responsibility.

**Magic numbers** -- use named constants instead of bare literals:

```python
# Bad
if user.age > 18:

# Good
MINIMUM_AGE = 18
if user.age > MINIMUM_AGE:
```

**Deep nesting** -- use early returns to flatten:

```python
# Bad
if condition1:
    if condition2:
        if condition3:
            # deeply nested

# Good (early returns)
if not condition1:
    return
if not condition2:
    return
if not condition3:
    return
# flat code
```

## Common Security Vulnerabilities

**SQL Injection:**

```python
# Bad
query = f"SELECT * FROM users WHERE id = {user_id}"

# Good
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

**XSS:**

```javascript
// Bad
element.innerHTML = userInput;

// Good
element.textContent = userInput;
```

**Hardcoded secrets:**

```python
# Bad
API_KEY = "sk-1234567890abcdef"

# Good
API_KEY = os.environ.get("API_KEY")
```
