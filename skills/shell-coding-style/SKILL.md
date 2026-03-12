---
name: shell-coding-style
description: Shell and Bash coding standards including error handling, formatting, documentation, and linting with shellcheck and shfmt. Use when writing or reviewing shell scripts.
---

# Shell Coding Style

Apply these Shell/Bash standards when writing or reviewing shell scripts.

## Error Handling

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- `set -e`: Exit on error
- `set -u`: Error on undefined variables
- `set -o pipefail`: Catch pipe failures
- Always use these three together as the first line after shebang

## Script Header

```bash
#!/usr/bin/env bash
set -euo pipefail

# Brief description of what this script does.
# Usage: script-name.sh <arg1> <arg2>
```

## Function Documentation

```bash
# Backs up a database to the specified directory.
# Usage: backup_database <database_name> <output_path>
# Args:
#   database_name - Name of the database
#   output_path   - Directory for backup file
backup_database() {
    local db_name="$1"
    local output_path="$2"
    # ...
}
```

## Variable Safety

- Always quote variables: `"$variable"` not `$variable`
- Use `local` for function variables: `local my_var="value"`
- Use `readonly` for constants: `readonly MAX_RETRIES=3`
- Default values: `${VAR:-default}`
- Required variables: `${VAR:?'VAR is required'}`

## Naming Conventions

- Scripts: lowercase with hyphens (`backup-database.sh`)
- Functions: lowercase with underscores (`backup_database`)
- Local variables: lowercase with underscores (`local db_name`)
- Constants: SCREAMING_SNAKE_CASE (`readonly MAX_RETRIES=3`)
- Environment variables: SCREAMING_SNAKE_CASE (`ROOTLY_API_TOKEN`)

## Conditional Patterns

```bash
# Use [[ ]] for conditionals (not [ ])
if [[ -f "$file" ]]; then
    echo "File exists"
fi

# String comparison
if [[ "$status" == "active" ]]; then ...

# Numeric comparison
if (( count > 10 )); then ...
```

## Linting (shellcheck + shfmt)

```bash
# Lint
shellcheck scripts/*.sh

# Format (Google style: 2-space indent, redirect after operator)
shfmt -i 2 -ci -w scripts/
```

### justfile

```just
lint-shell:
    shellcheck scripts/*.sh

format-shell:
    shfmt -i 2 -ci -w scripts/
```

## Common Patterns

```bash
# Safe temporary files
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

# Iterate over files safely
while IFS= read -r -d '' file; do
    echo "$file"
done < <(find . -name "*.sh" -print0)

# Check command exists
if ! command -v jq &>/dev/null; then
    echo "Error: jq is required" >&2
    exit 1
fi
```

## Verification Checklist

- [ ] `set -euo pipefail` at top
- [ ] All variables quoted
- [ ] `local` used in functions
- [ ] shellcheck passes
- [ ] shfmt passes
- [ ] Script header with usage comment
