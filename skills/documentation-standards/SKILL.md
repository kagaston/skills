---
name: documentation-standards
description: Standards for README, CONTRIBUTING, AGENTS.md and project documentation
---

# Documentation Standards

Apply these documentation standards to ensure consistent, useful documentation across all projects.

## Required Files

Every repository must have these files:

### README.md

```markdown
# Project Name

Brief one-line description of what this project does.

## Overview

2-3 paragraphs explaining:
- What problem this solves
- Who uses it
- Key features

## Quick Start

\`\`\`bash
# Installation
uv pip install project-name

# Basic usage
project-name --help
\`\`\`

## Installation

Detailed installation instructions including:
- Prerequisites
- Step-by-step setup
- Environment variables needed

## Usage

Common use cases with examples.

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | API authentication key | Required |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## License

[License type] - See [LICENSE](LICENSE) for details.
```

### CONTRIBUTING.md

```markdown
# Contributing to Project Name

## Development Setup

### Prerequisites
- Python 3.11+
- uv package manager

### Setup Steps
\`\`\`bash
git clone https://github.com/org/project-name
cd project-name
uv sync
just test
\`\`\`

## Code Style

- Follow project style guide
- Run `just lint` before committing
- Run `just format` to auto-format code

## Testing

- Write tests for new features
- Maintain >80% coverage
- Run `just test` to execute test suite

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Run `just lint test`
4. Submit PR with clear description
5. Address review feedback

## Commit Messages

Follow conventional commits:
\`\`\`
type(scope): description

feat(auth): add OAuth2 support
fix(api): handle null response
docs(readme): update installation
\`\`\`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
```

### AGENTS.md (For AI-assisted repos)

```markdown
# AI Agent Instructions

## Project Context

This project is a [brief description]. Key things to know:
- Primary language: Python 3.11
- Framework: FastAPI
- Database: PostgreSQL

## Code Conventions

- Use type hints everywhere
- Follow existing patterns in codebase
- Run `just lint` before suggesting changes

## Common Tasks

### Adding a New Endpoint
1. Create route in `app/api/routes/`
2. Add service method in `app/services/`
3. Add tests in `tests/`

### Modifying Database Schema
1. Update model in `app/models/`
2. Create migration: `alembic revision --autogenerate`
3. Test migration: `alembic upgrade head`

## Files to Avoid Modifying

- `alembic/versions/` - Generated migrations
- `*.lock` - Lock files
- `.env*` - Environment files

## Testing Requirements

- All new code needs tests
- Run `just test` to verify
- Coverage must not decrease
```

## Documentation Directory Structure

For projects with extensive documentation:

```
docs/
├── index.md                 # Documentation home
├── getting-started.md       # Quick start guide
├── installation.md          # Detailed installation
├── configuration.md         # Configuration reference
├── api/                     # API documentation
├── guides/                  # How-to guides
├── architecture/            # Technical architecture
└── development/             # Developer docs
```

## Markdown Standards

### Headers
```markdown
# Page Title (H1 - one per page)
## Major Section (H2)
### Subsection (H3)
```

### Code Blocks
Always specify language:
```markdown
\`\`\`python
def example():
    pass
\`\`\`
```

### Tables
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
```

## API Documentation

```markdown
## GET /users/{id}

Retrieve a user by their unique identifier.

### Parameters

| Name | Type | In | Description |
|------|------|-----|-------------|
| `id` | integer | path | User's unique ID |

### Response

#### 200 OK
\`\`\`json
{
  "id": 123,
  "name": "John Doe"
}
\`\`\`

#### 404 Not Found
\`\`\`json
{
  "error": "User not found"
}
\`\`\`
```

## Verification Checklist

- [ ] README.md has Overview, Quick Start, Installation, Usage sections
- [ ] CONTRIBUTING.md has Setup, Code Style, Testing, PR Process sections
- [ ] AGENTS.md exists for AI-assisted projects
- [ ] Code blocks specify language
- [ ] Tables are properly formatted
- [ ] All links are valid
