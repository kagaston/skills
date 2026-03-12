---
name: typescript-coding-style
description: TypeScript and React coding standards including component patterns, state management, linting with biome, and UI conventions. Use when writing or reviewing TypeScript, React, or JavaScript code.
---

# TypeScript Coding Style

Apply these TypeScript and React coding standards when writing or reviewing TypeScript, React, or JavaScript code.

## Stack

- React + Vite + Tailwind CSS + shadcn UI + pnpm

## Component Patterns

- Use functional components with hooks (no class components)
- Do NOT use `FC` or `React.FC` for component types:

```typescript
// Good
export const MyComponent = ({ name }: Props) => {
  return <div>{name}</div>;
};

// Bad
export const MyComponent: FC<Props> = ({ name }) => {
  return <div>{name}</div>;
};
```

## State Management

- `useState` and `useEffect` for local state and side effects
- React Query for server state and data fetching
- Use React-idiomatic patterns; avoid setTimeout and animation-frame hacks

## UI Components

- Use shadcn UI components for consistent styling
- Never use raw `<button>`, `<input>` — use `<Button>`, `<Input>` from shadcn UI
- Components live in `web/src/components/ui`

## Imports

- Don't create `index.ts` files to re-export components
- Always import components directly from their file path
- Run `just lint-fix-web` to fix lint errors and sort imports

## Linting (biome)

```json
{
  "$schema": "https://biomejs.dev/schemas/1.5.0/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "correctness": {
        "noUnusedVariables": "error",
        "noUnusedImports": "error"
      },
      "style": {
        "useConst": "error"
      }
    }
  },
  "formatter": {
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  }
}
```

## Naming Conventions

- Components: PascalCase (`UserProfile`)
- Hooks: camelCase with `use` prefix (`useAuth`)
- Utils/helpers: camelCase (`formatDate`)
- Constants: SCREAMING_SNAKE_CASE (`MAX_RETRIES`)
- Types/Interfaces: PascalCase (`UserProfile`, `AuthState`)
- Files: kebab-case for utilities, PascalCase for components

## JSDoc

```typescript
/**
 * Fetches user profile data and handles loading states.
 *
 * @param userId - The user's unique identifier
 * @returns The user profile or null during loading
 * @throws {NotFoundError} When user doesn't exist
 */
```

## Verification Checklist

- [ ] Functional components with hooks (no class components)
- [ ] No FC/React.FC usage
- [ ] shadcn UI components used (no raw HTML inputs/buttons)
- [ ] No index.ts re-exports
- [ ] biome lint passes
- [ ] React Query for data fetching
