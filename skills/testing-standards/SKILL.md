---
name: testing-standards
description: Testing patterns for Python (pytest), Go, and TypeScript (vitest)
---

# Testing Standards

Apply these testing standards to ensure reliable, maintainable test suites.

## Test Pyramid

```
        /\
       /  \     E2E Tests (few)
      /----\    
     /      \   Integration Tests (some)
    /--------\  
   /          \ Unit Tests (many)
  --------------
```

## Universal Principles

### 1. Descriptive Test Names
```python
# Good
def test_user_creation_with_valid_email_succeeds():
def test_user_creation_with_duplicate_email_raises_error():

# Bad
def test_user():
def test_1():
```

### 2. Arrange-Act-Assert (AAA)
```python
def test_user_full_name():
    # Arrange
    user = User(first_name="John", last_name="Doe")
    
    # Act
    result = user.full_name()
    
    # Assert
    assert result == "John Doe"
```

### 3. One Assertion Per Test (Generally)
Focus each test on one behavior.

## Python (pytest)

### Directory Structure
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/
│   ├── __init__.py
│   └── test_services.py
├── integration/
│   ├── __init__.py
│   └── test_api.py
└── e2e/
    └── test_workflows.py
```

### conftest.py Patterns
```python
import pytest

@pytest.fixture
def sample_user():
    """Provide a sample user for testing."""
    return User(id=1, name="Test User", email="test@example.com")

@pytest.fixture
async def async_client(app):
    """Provide an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### Test Examples
```python
import pytest
from app.services import UserService
from app.errors import NotFoundError

class TestUserService:
    def test_get_user_returns_user_when_exists(self, mock_db, sample_user):
        mock_db.query.return_value = sample_user
        service = UserService(db=mock_db)
        
        result = service.get_user(1)
        
        assert result == sample_user

    def test_get_user_raises_not_found_when_missing(self, mock_db):
        mock_db.query.return_value = None
        service = UserService(db=mock_db)
        
        with pytest.raises(NotFoundError):
            service.get_user(999)

    @pytest.mark.parametrize("email,expected", [
        ("JOHN@EXAMPLE.COM", "john@example.com"),
        ("  john@example.com  ", "john@example.com"),
    ])
    def test_normalize_email(self, email, expected):
        service = UserService(db=None)
        assert service.normalize_email(email) == expected
```

### pyproject.toml Configuration
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = ["-v", "--tb=short", "-ra"]
markers = [
    "slow: marks tests as slow",
    "integration: integration tests",
]

[tool.coverage.run]
source = ["app"]
branch = true

[tool.coverage.report]
fail_under = 80
```

## Go

### Test File Structure
```go
// user_test.go
package user

import (
    "testing"
    "github.com/alecthomas/assert/v2"
)

func TestUserFullName(t *testing.T) {
    user := User{FirstName: "John", LastName: "Doe"}
    
    result := user.FullName()
    
    assert.Equal(t, "John Doe", result)
}

func TestUserCreation(t *testing.T) {
    tests := []struct {
        name      string
        email     string
        wantError bool
    }{
        {"valid email", "john@example.com", false},
        {"invalid email", "invalid", true},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            _, err := NewUser(tt.email)
            if tt.wantError {
                assert.Error(t, err)
            } else {
                assert.NoError(t, err)
            }
        })
    }
}
```

## TypeScript (vitest)

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { UserService } from './user-service';

describe('UserService', () => {
  let service: UserService;
  let mockDb: MockDatabase;

  beforeEach(() => {
    mockDb = createMockDatabase();
    service = new UserService(mockDb);
  });

  describe('getUser', () => {
    it('returns user when found', async () => {
      const expectedUser = { id: 1, name: 'John' };
      mockDb.query.mockResolvedValue(expectedUser);

      const result = await service.getUser(1);

      expect(result).toEqual(expectedUser);
    });

    it('throws NotFoundError when user missing', async () => {
      mockDb.query.mockResolvedValue(null);

      await expect(service.getUser(999)).rejects.toThrow('User not found');
    });
  });
});
```

## uv Workspace Testing

For monorepos with `app/*/` package layout:

- **Test all packages:** `uv run pytest app/*/tests/ -v --tb=short`
- **Test single package:** `uv run pytest app/{pkg}/tests/ -v --tb=short`

```just
test pkg="*":
    uv run pytest app/{{pkg}}/tests/ -v --tb=short

test-cov:
    uv run pytest app/*/tests/ --cov=app --cov-report=term-missing --tb=short
```

## Fixture Recording Pattern

VCR-like pattern: record real API responses, replay for deterministic tests.

### Workflow

1. Write a "live" test that hits the real API and records responses
2. Save responses as JSON fixtures in `test/support/fixtures/` or `tests/fixtures/`
3. Write replay tests that use the fixtures (no network needed)

### Tagging Live Tests

Tag live tests so they are excluded from normal runs:

```python
# pytest
@pytest.mark.live
def test_fetch_user_from_api():
    ...
```

```bash
# Run without live tests (default)
pytest -m "not live"

# Run live tests to refresh fixtures
pytest -m live
```

### Rules

- Use constrained inputs for deterministic output
- Use descriptive fixture names (e.g. `user_123_response.json`)
- Never hand-edit fixtures; regenerate via live tests

### Language-Specific Examples

| Language | Recording | Replay |
|----------|-----------|--------|
| Python | `pytest-recording`, `responses` | Load JSON fixtures in tests |
| Elixir | ExVCR, `Tesla.Mock` | Cassette files in `test/fixtures/vcr_cassettes/` |
| Node/TS | `nock`, `msw` | Save/load fixtures in `__fixtures__/` |

## Test Data Management

### Factories
```python
from factory import Factory, Faker, LazyAttribute

class UserFactory(Factory):
    class Meta:
        model = User
    
    name = Faker("name")
    email = LazyAttribute(lambda o: f"{o.name.lower().replace(' ', '.')}@example.com")

# Usage
user = UserFactory()
user_with_name = UserFactory(name="John Doe")
```

## justfile Commands

```just
test:
    pytest tests/ -v

test-cov:
    pytest tests/ --cov=app --cov-report=term-missing

test-unit:
    pytest tests/unit/ -v

test-integration:
    pytest tests/integration/ -v -m integration
```

## Verification Checklist

- [ ] Tests follow AAA pattern
- [ ] Test names describe behavior being tested
- [ ] conftest.py has shared fixtures
- [ ] Coverage configured (>80% target)
- [ ] Unit and integration tests separated
- [ ] `just test` command works
