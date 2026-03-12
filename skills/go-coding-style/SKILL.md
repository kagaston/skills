---
name: go-coding-style
description: Go coding standards including error handling, optional values, testing patterns, and linting. Use when writing or reviewing Go code.
---

# Go Coding Style

Apply these Go coding standards when writing or reviewing Go code.

## Error Handling

- Always use `github.com/alecthomas/errors` for error handling
- Never use `fmt.Errorf()` or stdlib `errors.New()`
- Patterns:

```go
// Wrap existing error
errors.Errorf("%w: failed to fetch user", err)

// Wrap with formatting
errors.Errorf("%w: user %s not found", err, userID)

// Create new error
errors.Errorf("invalid input: %v", value)
```

## Optional Values

- Never use pointers to represent optional values
- Always use `github.com/alecthomas/types/optional.Option[T]`

```go
func FindUser(id string) (optional.Option[User], error) {
    user, err := db.Get(id)
    if err != nil {
        return optional.None[User](), err
    }
    return optional.Some(user), nil
}
```

## Testing

- Always use `github.com/alecthomas/assert/v2` for assertions
- Parameter order: `assert.Equal(t, expected, actual)`
- Always update or create tests for new changes
- After making changes, always run tests
- Table-driven tests for multiple cases:

```go
func TestExample(t *testing.T) {
    tests := []struct {
        name     string
        input    string
        expected string
    }{
        {"valid", "hello", "HELLO"},
        {"empty", "", ""},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            assert.Equal(t, tt.expected, Transform(tt.input))
        })
    }
}
```

## Environment Variables

- Never use `os.Getenv()` outside of `main()`
- Pass configuration as function parameters or struct fields

## Naming Conventions

- Packages: lowercase, single word (no underscores)
- Interfaces: verb-based (`Reader`, `Writer`, `Stringer`)
- Exported: PascalCase
- Unexported: camelCase
- Acronyms: all caps (`HTTP`, `URL`, `ID`)

## Linting (golangci-lint)

- Standard `.golangci.yml` config with errcheck, gosimple, govet, ineffassign, staticcheck, unused, gofmt, goimports, misspell, gocritic, revive, gosec
- justfile: `just lint` runs `golangci-lint run ./...`
- justfile: `just format` runs `gofmt -s -w . && goimports -w .`

## Verification Checklist

- [ ] Errors use alecthomas/errors (no fmt.Errorf)
- [ ] Optional values use optional.Option[T] (no pointers)
- [ ] Tests use assert/v2 with correct parameter order
- [ ] No os.Getenv outside main()
- [ ] golangci-lint passes
- [ ] Tests pass
