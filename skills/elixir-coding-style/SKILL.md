---
name: elixir-coding-style
description: Elixir and OTP coding standards including GenServer patterns, documentation, cyclic dependency detection, codegen sync, and linting. Use when writing or reviewing Elixir code.
---

# Elixir Coding Style

Apply these Elixir and OTP coding standards when writing or reviewing Elixir code.

## Core Philosophy

- **Everything is a Process** — Agent loops, sessions, and tools are GenServers
- **Cross-Platform** — Works on macOS, Linux, and Windows
- **Let it crash** — Use OTP supervision trees for fault tolerance

## Documentation

- `@moduledoc` for module documentation (Markdown supported)
- `@doc` for function documentation
- `@typedoc` for type documentation

```elixir
@moduledoc """
User management GenServer.

Handles user lifecycle including creation, lookup, and session management.
"""

@doc """
Looks up a user by ID.

## Parameters
  * `id` - The user's unique identifier

## Returns
  * `{:ok, user}` - User found
  * `{:error, :not_found}` - User doesn't exist
"""
def get_user(id), do: ...
```

## Pattern Matching

- Use pattern matching in function heads for control flow
- Prefer multi-clause functions over if/case when matching on argument shape

```elixir
def handle_call(:get_state, _from, state), do: {:reply, state, state}
def handle_call({:update, key, value}, _from, state) do
  new_state = Map.put(state, key, value)
  {:reply, :ok, new_state}
end
```

## Cyclic Dependency Detection

Requires Elixir 1.19+ for accurate results.

```bash
# Detect compile-connected cycles
mix xref graph --format cycles --label compile-connected --fail-above 0

# Detect compile cycles
mix xref graph --format cycles --label compile --fail-above 0
```

Strategies to break cycles:

- Extract helper module (shared logic both depend on)
- Move code down (function from A to B)
- Invert dependency (callback, option, or data structure)
- Split module (when one module has two responsibilities)

## Codegen Sync (Elixir -> TypeScript)

When Elixir types change, regenerate TypeScript:

```bash
mix run scripts/codegen_ts.exs         # Regenerate
mix run scripts/codegen_ts.exs --check # Verify current (CI)
```

Rules: never hand-edit generated files, commit codegen output with source changes.

## Lint & Format

```bash
# Elixir
mix format          # Format
mix format --check  # Check formatting (CI)
mix credo           # Static analysis

# Full check
mise run lint       # or: mix format --check && mix credo
```

## Development Commands

Elixir projects use `mise` as the task runner (other languages use `just`):

```bash
mise run dev     # Run TUI
mise run test    # Run tests
mise run lint    # Check code quality
mise run release # Release
```

## Naming Conventions

- Modules: PascalCase (`MyApp.UserManager`)
- Functions: snake_case (`get_user`)
- Variables: snake_case (`user_name`)
- Atoms: snake_case (`:ok`, `:not_found`)
- Private functions: prefix with `_` by convention or use `defp`

## Verification Checklist

- [ ] @moduledoc on every module
- [ ] @doc on public functions
- [ ] Pattern matching preferred over if/case
- [ ] No cyclic dependencies (mix xref --fail-above 0)
- [ ] mix format passes
- [ ] Codegen in sync (if applicable)
