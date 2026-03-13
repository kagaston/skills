---
name: python-api-structure
description: FastAPI application structure patterns for Python APIs based on secure-drives
---

# Python API Structure

When creating or reviewing FastAPI applications, follow this structure derived from Block's secure-drives project.

## Directory Structure

All Python projects use the `app/{name}/src/{name}/` monorepo layout:

```
project-name/
├── app/
│   └── project_name/
│       ├── src/
│       │   └── project_name/
│       │       ├── __init__.py
│       │       ├── app.py              # FastAPI app factory
│       │       ├── main.py             # Entry point (uvicorn)
│       │       ├── config.py           # Pydantic settings
│       │       ├── auth/               # Authentication
│       │       ├── clients/            # External API clients
│       │       ├── database/           # DB connection, session
│       │       ├── dependencies/       # FastAPI dependencies
│       │       ├── middleware/         # Custom middleware
│       │       ├── migrations/         # Alembic migrations
│       │       ├── models/             # SQLAlchemy models
│       │       ├── repositories/       # Data access layer
│       │       ├── routers/            # API endpoints
│       │       │   ├── __init__.py
│       │       │   ├── status.py       # Health check
│       │       │   └── v1/             # Versioned API
│       │       ├── schemas/            # Pydantic schemas
│       │       ├── services/           # Business logic
│       │       ├── utils/              # Shared utilities
│       │       └── workers/            # Background workers
│       ├── tests/
│       │   ├── __init__.py
│       │   ├── conftest.py
│       │   ├── unit/
│       │   ├── integration/
│       │   └── e2e/
│       └── pyproject.toml
├── pyproject.toml                      # Root workspace config
├── uv.lock
└── justfile
```

## App Factory Pattern

### app.py
```python
"""FastAPI application definition."""
import truststore
truststore.inject_into_ssl()

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from project_name.config import settings
from project_name.routers import status
from project_name.routers.v1 import router as v1_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """FastAPI lifespan hook for startup/shutdown tasks."""
    # Startup logic here
    yield
    # Shutdown logic here


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    app = FastAPI(root_path="/api-prefix", lifespan=lifespan)

    # Add middleware (order matters - last added runs first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.CORS_ALLOWED_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    # Include routers
    app.include_router(status.router)
    app.include_router(v1_router)
    return app
```

### main.py
```python
"""Application entry point."""
import uvicorn
from project_name.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("project_name.main:app", host="0.0.0.0", port=8000, reload=True)
```

## Configuration Pattern

### config.py
```python
"""Application configuration using Pydantic settings."""
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "app"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: SecretStr = SecretStr("")

    # Application
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # External Services
    SLACK_BOT_TOKEN: SecretStr | None = None
    SLACK_ENABLED: bool = False


settings = Settings()
```

## Router Pattern

### routers/v1/__init__.py
```python
"""V1 API router."""
from fastapi import APIRouter

from project_name.routers.v1 import items, users

router = APIRouter(prefix="/v1")
router.include_router(items.router, prefix="/items", tags=["items"])
router.include_router(users.router, prefix="/users", tags=["users"])
```

### routers/status.py
```python
"""Health check endpoints."""
from fastapi import APIRouter

router = APIRouter(tags=["status"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
```

## Testing Pattern

### conftest.py
```python
"""Pytest configuration and fixtures."""
import pytest


def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require external services",
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless flag is passed."""
    run_integration = config.getoption("--run-integration")
    skip_integration = pytest.mark.skip(reason="Need --run-integration option to run")

    for item in items:
        if "integration" in item.keywords and not run_integration:
            item.add_marker(skip_integration)
```

### pyproject.toml pytest config (member)

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
addopts = ["-ra", "--strict-markers", "--strict-config", "--cov=src/project_name", "--cov-report=term-missing", "--cov-fail-under=80"]
filterwarnings = ["error"]
asyncio_mode = "auto"
markers = [
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
    "slow: marks tests as slow",
]
```

## justfile Commands

```just
[private]
default:
    @just --list --unsorted

format:
    uv run ruff format .

lint:
    uv run ruff check --fix .

test pkg="*" *args="":
    uv run pytest app/{{pkg}}/tests/ --ignore=app/{{pkg}}/tests/e2e -v --tb=short {{args}}

test-integration pkg="*" *args="":
    uv run pytest app/{{pkg}}/tests/ --ignore=app/{{pkg}}/tests/e2e --run-integration {{args}}

test-e2e pkg="*" *args="":
    uv run pytest app/{{pkg}}/tests/e2e --run-e2e --no-cov {{args}}

typecheck:
    uv run basedpyright app/*/src/

check:
    uv run nox

# Start local database
mysql:
    @docker start app-mysql 2>/dev/null || docker run -d --name app-mysql -p 3306:3306 -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -e MYSQL_DATABASE=app mysql:8.0

# Generate OpenAPI spec
openapi output="openapi.json":
    uv run ./script/generate-openapi {{ output }}

# Interactive console
console:
    uv run python -m project_name.console
```

## AGENTS.md Template

Include in every API project:

```markdown
# AGENTS.md - Project Documentation Hub

## Quick Reference

### Essential Commands
\`\`\`bash
uv sync                    # Install dependencies
just test                  # Run tests
just check                 # Run all CI checks
just lint                  # Lint code
just format                # Format code
\`\`\`

## Code Style & Conventions
- **Linting**: Ruff with Google-style docstrings
- **Line Length**: 120 characters
- **Type Checking**: basedpyright strict mode

## Architecture Overview
[Include a diagram of your service architecture]

## Getting Help
1. Check docs/ directory
2. Review test files for usage examples
3. Check justfile for available commands
```

## Verification Checklist

- [ ] Uses app factory pattern (`create_app()`)
- [ ] Config uses Pydantic settings with `SecretStr` for secrets
- [ ] Routers are versioned (`/v1/`)
- [ ] Health check endpoint exists (`/health`)
- [ ] Tests use pytest markers for integration/e2e
- [ ] `--run-integration` flag for integration tests
- [ ] `AGENTS.md` documents quick reference commands
- [ ] justfile has mysql/services commands for local dev
