---
name: cross-language-comments
description: Consistent comment standards across Python, Go, TypeScript, Elixir, Terraform, and Shell
---

# Cross-Language Comment Standards

Apply these comment standards consistently across all languages. Good comments explain *why*, not *what*.

## Universal Principles

1. **Comments Explain Why, Not What** - The code should be self-documenting for the *what*
2. **Keep Comments Updated** - Outdated comments are worse than no comments
3. **Delete Commented-Out Code** - Use version control instead

## Standard Markers

Use these markers consistently across all languages:

| Marker | Meaning | When to Use |
|--------|---------|-------------|
| `TODO:` | Task to complete | Planned work, include ticket if available |
| `FIXME:` | Known bug/issue | Needs attention, explain the problem |
| `HACK:` | Workaround | Temporary solution, explain why needed |
| `NOTE:` | Important info | Non-obvious behavior or context |
| `WARN:` | Caution | Dangerous operation or side effects |

## Python

```python
# Single line comment

# Multi-line comments use
# multiple single-line comments

"""
Docstrings are for documentation,
not comments. Use for modules,
classes, and functions.
"""

# TODO: Add retry logic for transient failures (JIRA-123)
# FIXME: This breaks when user_id is None
# NOTE: Rate limit requires delay between requests
```

## Go

```go
// Single line comment

/*
Multi-line comment for longer
explanations.
*/

// Package user provides user management functionality.
package user

// GetByID retrieves a user by their unique identifier.
// Returns ErrNotFound if the user doesn't exist.
//
// TODO: Add caching layer
func GetByID(id int64) (*User, error) {
    // NOTE: This query uses an index on id column
    return nil, nil
}
```

## TypeScript/JavaScript

```typescript
// Single line comment

/**
 * JSDoc comment for documentation.
 * 
 * @param userId - The user's unique identifier
 * @returns The user object or null if not found
 * @throws {NotFoundError} When user doesn't exist
 */
async function getUser(userId: number): Promise<User | null> {
    // TODO: Add caching layer
    return null;
}

// HACK: Browser quirk requires this delay
// See: https://bugs.chromium.org/p/chromium/issues/detail?id=12345
await sleep(100);
```

## Elixir

```elixir
# Single line comment

@moduledoc """
Module documentation goes in @moduledoc.
Supports Markdown formatting.
"""

@doc """
Function documentation goes in @doc.

## Parameters
  * `id` - The user's unique identifier

## Returns
  * `{:ok, user}` - Success with user struct
  * `{:error, :not_found}` - User doesn't exist
"""
def get_user(id) do
  # NOTE: Pattern matching handles the error case
  case Repo.get(User, id) do
    nil -> {:error, :not_found}
    user -> {:ok, user}
  end
end
```

## Terraform

```hcl
# Single line comment

/*
Multi-line comment for longer
explanations.
*/

# NOTE: This role is used by the Lambda function for S3 access
resource "aws_iam_role" "lambda_role" {
  name = "lambda-s3-access"
  
  # TODO: Restrict to specific S3 buckets (SEC-456)
  assume_role_policy = jsonencode({...})
}

# WARN: Changing this will recreate all dependent resources
variable "environment" {
  description = "Deployment environment"
  type        = string
}
```

## Shell/Bash

```bash
#!/bin/bash
# Script description at the top

# NOTE: This script requires root privileges
# WARN: Will overwrite existing configuration

# Function documentation
# Usage: backup_database <database_name> <output_path>
# Args:
#   database_name - Name of the database to backup
#   output_path   - Directory for backup file
backup_database() {
    local db_name="$1"
    local output_path="$2"
    
    # TODO: Add compression option
    pg_dump "$db_name" > "$output_path/$db_name.sql"
}
```

## Section Comments

Use section comments to organize large files:

```python
# =============================================================================
# Configuration
# =============================================================================

CONFIG = {...}

# =============================================================================
# Helper Functions
# =============================================================================

def helper():
    pass
```

## When NOT to Comment

```python
# Bad - explains what (obvious from code)
# Increment counter by 1
counter += 1

# Good - explains why
# Rate limit requires delay between requests to avoid 429 errors
counter += 1

# Bad - commented-out code (use version control)
# old_function()
# another_old_function()

# Bad - redundant docstring
def get_name(self) -> str:
    """Get the name."""  # Unnecessary
    return self.name
```

## Verification Checklist

- [ ] Comments explain *why*, not *what*
- [ ] TODO/FIXME/HACK markers include context
- [ ] No commented-out code (deleted, using version control)
- [ ] Docstrings on public APIs
- [ ] Section comments for large files
- [ ] No redundant comments on self-explanatory code
