# Complete MCP Server Example

A working FastMCP server with system info, text analysis, and data processing tools.

## pyproject.toml

```toml
[project]
name = "mcp-server"
version = "0.1.0"
description = "Example MCP server with system info, text analysis, and data tools"
requires-python = ">=3.12"
dependencies = [
    "fastmcp>=3.1.0",
]

[dependency-groups]
dev = [
    "basedpyright>=1.38.2",
    "pytest>=9.0.2",
    "pytest-asyncio>=1.3.0",
    "ruff>=0.15.5",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mcp_server"]

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["B", "C4", "C90", "E", "F", "I", "PLR", "RUF", "S", "SIM", "T20", "UP"]
fixable = ["ALL"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "PLR2004", "T20"]

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true

[tool.basedpyright]
include = ["src"]
typeCheckingMode = "standard"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = ["-ra", "--strict-markers", "--strict-config"]
```

## server.py

```python
"""MCP server exposing system, text, and data processing tools."""

import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Set up shared state that persists for the server's lifetime."""
    logger.info("MCP server starting...")
    yield {"started_at": datetime.now(UTC).isoformat()}
    logger.info("MCP server shutting down.")


mcp = FastMCP(
    name="ToolboxServer",
    instructions=(
        "A general-purpose toolbox server providing system information, "
        "text analysis/transformation, file browsing, math calculations, "
        "statistics, CSV parsing, and JSON querying."
    ),
    lifespan=server_lifespan,
)


# === Tools ====================================================================


@mcp.tool
def system_info() -> dict[str, Any]:
    """Get detailed system information including OS, CPU, disk, and Python version."""
    import platform
    import shutil

    disk = shutil.disk_usage("/")
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count() or 0,
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "utc_time": datetime.now(UTC).isoformat(),
    }


@mcp.tool
async def text_analyze(text: str) -> dict[str, Any]:
    """Analyze text and return word count, sentence count, top words, and more."""
    import re
    from collections import Counter

    if not text.strip():
        raise ValueError("Text cannot be empty")

    ctx = get_context()
    await ctx.info(f"Analyzing text ({len(text)} chars)")

    words = re.findall(r"\b\w+\b", text.lower())
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    return {
        "characters": len(text),
        "words": len(words),
        "sentences": len(sentences),
        "top_words": Counter(words).most_common(10),
    }


@mcp.tool
def math_calculate(expression: str) -> dict[str, Any]:
    """Evaluate a mathematical expression safely.

    Supports arithmetic, sqrt, log, trig functions, pi, e, abs, round, min, max.

    Args:
        expression: Math expression to evaluate, e.g. 'sqrt(144) + 2**3'.
    """
    import math

    if not expression.strip():
        raise ValueError("Expression cannot be empty")

    safe_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sqrt": math.sqrt, "pow": pow, "log": math.log, "log10": math.log10,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "pi": math.pi, "e": math.e, "ceil": math.ceil, "floor": math.floor,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, safe_names)  # noqa: S307
    except Exception as exc:
        raise ValueError(f"Invalid expression: {exc}") from exc

    return {"expression": expression, "result": float(result)}


@mcp.tool
def csv_parse(csv_text: str, delimiter: str = ",") -> list[dict[str, str]]:
    """Parse CSV text into a list of row dictionaries.

    Args:
        csv_text: Raw CSV content.
        delimiter: Column delimiter (default: comma).
    """
    import csv
    import io

    if not csv_text.strip():
        raise ValueError("CSV text cannot be empty")
    rows = list(csv.DictReader(io.StringIO(csv_text), delimiter=delimiter))
    if not rows:
        raise ValueError("CSV contains headers but no data rows")
    return rows


@mcp.tool
def json_extract(json_text: str, path: str) -> Any:
    """Extract a value from a JSON string using dot-notation.

    Args:
        json_text: Raw JSON string.
        path: Dot-separated path to the desired value (e.g. 'users.0.name').
    """
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    current = data
    for key in path.split("."):
        if isinstance(current, list):
            try:
                current = current[int(key)]
            except (ValueError, IndexError) as exc:
                raise ValueError(f"Invalid array index '{key}' in path '{path}'") from exc
        elif isinstance(current, dict):
            if key not in current:
                raise ValueError(f"Key '{key}' not found at path '{path}'")
            current = current[key]
        else:
            raise ValueError(f"Cannot traverse into {type(current).__name__} with key '{key}'")
    return current


# === Resources ================================================================


@mcp.resource("config://server")
def server_config() -> str:
    """Current server configuration and environment."""
    return json.dumps(
        {
            "name": "ToolboxServer",
            "version": "0.1.0",
            "transport": os.environ.get("MCP_TRANSPORT", "stdio"),
            "port": os.environ.get("MCP_PORT", "8000"),
        },
        indent=2,
    )


# === Prompts ==================================================================


@mcp.prompt
def analyze_file_prompt(file_path: str) -> str:
    """Generate a prompt asking the LLM to analyze a specific file."""
    return (
        f"Please read the file at '{file_path}' using the read_file tool, "
        "then analyze its contents. Summarize what the file does, "
        "note any potential issues, and suggest improvements."
    )


@mcp.prompt
def data_exploration_prompt(description: str) -> str:
    """Generate a prompt for exploring a dataset."""
    return (
        f"I have the following data: {description}\n\n"
        "Please help me explore it by:\n"
        "1. Parsing the data using csv_parse or json_extract as appropriate\n"
        "2. Computing statistics on numeric columns\n"
        "3. Summarizing your findings with key insights"
    )


# === Entry Point ==============================================================


def main() -> None:
    """Run the MCP server. Pass --http to use HTTP transport."""
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    port = int(os.environ.get("MCP_PORT", "8000"))

    if "--http" in sys.argv:
        transport = "http"

    if transport == "http":
        logger.info("Starting HTTP server on port %d...", port)
        mcp.run(transport="http", port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

## Integration Test (test_server.py)

```python
"""Integration tests for the MCP server using FastMCP's Client."""

import pytest
from fastmcp import Client

from mcp_server.server import mcp


@pytest.fixture
def client() -> Client:
    return Client(mcp)


class TestServerIntegration:
    async def test_list_tools(self, client: Client):
        async with client:
            tools = await client.list_tools()
            tool_names = {t.name for t in tools}
            assert {"system_info", "text_analyze", "math_calculate"}.issubset(tool_names)

    async def test_system_info_tool(self, client: Client):
        async with client:
            result = await client.call_tool("system_info", {})
            assert result is not None

    async def test_math_calculate_tool(self, client: Client):
        async with client:
            result = await client.call_tool("math_calculate", {"expression": "2 + 2"})
            assert result is not None

    async def test_list_resources(self, client: Client):
        async with client:
            resources = await client.list_resources()
            uris = {str(r.uri) for r in resources}
            assert "config://server" in uris

    async def test_list_prompts(self, client: Client):
        async with client:
            prompts = await client.list_prompts()
            names = {p.name for p in prompts}
            assert "analyze_file_prompt" in names
```
