---
name: python-coding-style
description: Python coding standards including naming, typing, docstrings, comments, and error handling
---

# Python Coding Style

Apply these Python coding standards when writing or reviewing Python code.

## General Principles

1. **Readability First**: Code is read more than written
2. **Explicit over Implicit**: Be clear about intentions
3. **Consistency**: Follow established patterns in the codebase
4. **Simplicity**: Prefer simple solutions over clever ones

## Quality Philosophy

- **Comments explain "why" not "what"**: Code should be self-documenting; comments clarify intent, edge cases, and non-obvious decisions
- **No hardcoded secrets**: Use environment variables, config, or secret managers—never commit API keys, passwords, or tokens
- **Security-first**: Validate input, sanitize output, prefer parameterized queries, avoid `eval()` and unsafe deserialization

## Formatting

- **Line Length**: Maximum 120 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Use double quotes `"` for strings
- **Formatter**: Use `ruff format` (not black)

### Import Order

```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import httpx
from pydantic import BaseModel

# Local
from app.errors import AppError
from app.settings import Settings
```

## Comment Conventions

**Docstring-first**: Use triple-quoted docstrings (`"""`) for all block-level documentation and longer explanations. Use single `#` comments only for brief inline annotations.

### When to Use Docstrings

- Module-level documentation
- Class documentation
- Function/method documentation
- Any multi-line or block-level explanation

### When to Use `#` Comments

- Single-line inline annotations
- Brief TODOs or FIXMEs
- Section dividers (see below)

### Section Dividers

Use `# ---` for subsection dividers and `# ===` for major section dividers in large files:

```python
# === Data Models ===

# --- User ---
class User(BaseModel):
    """User entity with validated fields."""
    pass

# --- Session ---
class Session(BaseModel):
    """Active session state."""
    pass

# === API Handlers ===

# --- Authentication ---
def authenticate(token: str) -> User | None:
    """Validate token and return user or None."""
    pass
```

**Never** use multi-line `#` comment blocks when a docstring would serve better.

## Naming Conventions

### Variables and Functions

```python
# Good - snake_case
user_name = "john"
def get_user_by_id(user_id: int) -> User:
    pass

# Bad - camelCase
userName = "john"
```

### Classes

```python
# Good - PascalCase
class UserRepository:
    pass

class HTTPClient:  # Acronyms capitalized
    pass
```

### Constants

```python
# Good - SCREAMING_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"
```

### Private Members

```python
class User:
    def __init__(self):
        self._internal_state = {}  # Single underscore for internal

    def _helper_method(self):  # Internal method
        pass
```

## Type Hints

Type hints are required for all public functions and methods:

```python
# Good
def process_items(items: list[str], limit: int = 10) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items[:limit]:
        result[item] = len(item)
    return result

# Bad - no type hints
def process_items(items, limit=10):
    pass
```

### Optional Types

```python
# Python 3.10+
def find_user(user_id: int) -> User | None:
    pass
```

## Docstrings

### Function Docstrings

```python
def create_user(name: str, email: str, role: str = "user") -> User:
    """
    Create a new user in the system.

    Args:
        name: The user's full name.
        email: The user's email address.
        role: The user's role. Defaults to "user".

    Returns:
        The newly created User object.

    Raises:
        ValidationError: If email format is invalid.
        DuplicateError: If user with email already exists.
    """
    pass
```

### Class Docstrings

```python
class UserRepository:
    """
    Repository for user data access operations.

    Provides CRUD operations for User entities with support for
    filtering, pagination, and bulk operations.

    Attributes:
        db: Database connection instance.
        cache: Optional cache layer for read operations.

    Example:
        repo = UserRepository(db=database)
        user = repo.get_by_id(123)
    """
    pass
```

## Error Handling

Use custom exceptions for application errors. Handle errors explicitly; avoid bare `except:`.

### Custom Exceptions

```python
# In app/errors/__init__.py
class AppError(Exception):
    """Base exception for application errors."""
    pass

class ValidationError(AppError):
    """Raised when input validation fails."""
    pass

class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
    pass
```

### Exception Handling

```python
# Good - specific exceptions
try:
    user = repository.get_by_id(user_id)
except NotFoundError:
    logger.warning(f"User {user_id} not found")
    raise
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise AppError("Failed to fetch user") from e

# Bad - bare except
try:
    user = repository.get_by_id(user_id)
except:  # Never do this
    pass
```

## Classes and Pydantic

### Dataclasses for Simple Containers

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
```

### Pydantic for Validation

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

    class Config:
        str_strip_whitespace = True
```

## Tools Configuration

### pyproject.toml

```toml
[tool.ruff]
target-version = "py311"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "C4", "PTH", "RUF"]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.11"
strict = true
```

## Verification Checklist

- [ ] All functions have type hints
- [ ] Public functions have docstrings
- [ ] Custom exceptions inherit from base AppError
- [ ] No bare `except:` clauses
- [ ] Imports are organized (stdlib, third-party, local)
- [ ] Naming follows conventions (snake_case, PascalCase, SCREAMING_SNAKE_CASE)
- [ ] No hardcoded secrets; use env/config
- [ ] Docstrings for block-level docs; `#` for brief inline only
- [ ] 4-space indent; `ruff format` used
