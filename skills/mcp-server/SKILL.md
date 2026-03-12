---
name: mcp-server
description: Guide for creating Python MCP servers using FastMCP with proper project structure, tools, resources, prompts, and testing. Use when building an MCP server, creating MCP tools, setting up a FastMCP project, or connecting AI agents to custom functionality.
argument-hint: "[server-name]"
---

# MCP Server (Python + FastMCP)

Create Model Context Protocol servers in Python using [FastMCP](https://gofastmcp.com/). MCP servers expose tools, resources, and prompts that LLM clients (Claude Desktop, Cursor, Goose, Amp) can invoke.

## Project Setup

```bash
uv init <server-name> --no-readme
cd <server-name>
uv add fastmcp
uv add --dev ruff basedpyright pytest pytest-asyncio
mkdir -p src/<module_name>/tools tests
```

### Project Structure

```
<server-name>/
├── src/<module_name>/
│   ├── __init__.py
│   ├── server.py              # FastMCP server definition
│   └── tools/
│       ├── __init__.py
│       └── <domain>.py        # Tool implementations
├── tests/
│   ├── __init__.py
│   ├── test_<domain>.py       # Unit tests for tools
│   └── test_server.py         # Integration tests via FastMCP Client
├── pyproject.toml
├── justfile
└── README.md
```

## Server Definition

```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="MyServer",
    instructions="Description of what this server provides.",
)

@mcp.tool
def my_tool(param: str, count: int = 10) -> dict[str, str]:
    """Tool description becomes the LLM-visible documentation.

    Args:
        param: What this parameter controls.
        count: How many results to return.
    """
    return {"result": f"Processed {param}", "count": count}

if __name__ == "__main__":
    mcp.run()
```

## Tools

Use `@mcp.tool` decorator. Type hints generate schemas automatically. Docstrings become tool descriptions.

```python
@mcp.tool
def search(query: str, max_results: int = 10) -> list[dict[str, str]]:
    """Search the knowledge base.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.
    """
    return [{"title": "Result", "snippet": "..."}]
```

### Async Tools

Use `async def` for I/O-bound operations. Sync tools run in a threadpool automatically.

```python
@mcp.tool
async def fetch_data(url: str) -> dict[str, str]:
    """Fetch data from an external API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### Context for Logging

Use `get_context()` to log back to the MCP client:

```python
from fastmcp.server.dependencies import get_context

@mcp.tool
async def process(data: str) -> dict[str, int]:
    """Process data with progress logging."""
    ctx = get_context()
    await ctx.info(f"Processing {len(data)} chars")
    result = do_work(data)
    await ctx.info("Done")
    return result
```

## Resources

Expose read-only data. Must return `str` or `bytes`:

```python
@mcp.resource("config://server")
def server_config() -> str:
    """Current server configuration."""
    import json
    return json.dumps({"version": "1.0", "status": "running"}, indent=2)
```

## Prompts

Reusable LLM prompt templates:

```python
@mcp.prompt
def analyze_prompt(file_path: str) -> str:
    """Generate a prompt to analyze a file."""
    return f"Read '{file_path}' and summarize its contents."
```

## Lifespan Management

For shared resources (database connections, HTTP clients):

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Set up shared state for the server's lifetime."""
    db = await connect_db()
    yield {"db": db}
    await db.close()

mcp = FastMCP("MyServer", lifespan=server_lifespan)
```

## Transport

### stdio (default, local)

```bash
uv run python src/<module>/server.py
uv run fastmcp dev src/<module>/server.py:mcp    # inspector
uv run fastmcp install src/<module>/server.py:mcp # Claude Desktop
```

### HTTP (remote)

```python
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
```

```bash
uv run fastmcp run src/<module>/server.py:mcp --transport http --port 8000
```

Connect clients to `http://localhost:8000/mcp`.

## Testing

### Unit Tests (test tools directly)

```python
from my_server.tools.data import calculate

def test_basic_arithmetic():
    assert calculate("2 + 3")["result"] == 5.0

def test_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        calculate("   ")
```

### Integration Tests (via FastMCP Client)

```python
from fastmcp import Client
from my_server.server import mcp

@pytest.fixture
def client() -> Client:
    return Client(mcp)

async def test_list_tools(client: Client):
    async with client:
        tools = await client.list_tools()
        assert {t.name for t in tools} >= {"my_tool", "search"}

async def test_call_tool(client: Client):
    async with client:
        result = await client.call_tool("my_tool", {"param": "test"})
        assert result is not None
```

## justfile

```just
[private]
default:
    @just --list --unsorted

format:
    uv run ruff format .

lint:
    uv run ruff check --fix .

typecheck:
    uv run basedpyright src/

test *args:
    uv run pytest tests/ {{args}}

check: format lint typecheck test

run:
    uv run python src/<module>/server.py

run-http:
    uv run python src/<module>/server.py --http

dev:
    uv run fastmcp dev src/<module>/server.py:mcp
```

## Key Rules

- **Type hints everywhere** -- they generate the MCP parameter schemas
- **Docstrings on every tool** -- they become the tool description the LLM sees
- **Log to stderr** (or use Context logging) -- stdout is the MCP transport channel
- **Resources return str or bytes** -- not dicts
- **Clean up resources** -- use lifespan for connections, files, clients
- **Validate inputs early** -- raise `ValueError` with clear messages
- **Test tools independently** before LLM integration

## Reference Files

- [server-example.md](references/server-example.md) -- Complete working server with tools, resources, prompts, lifespan, and pyproject.toml
