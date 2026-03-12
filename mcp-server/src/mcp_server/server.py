"""MCP server exposing system, text, and data processing tools.

Run with:
    uv run python src/mcp_server/server.py          # stdio transport (default)
    uv run python src/mcp_server/server.py --http    # HTTP transport on port 8000
    uv run fastmcp dev src/mcp_server/server.py:mcp  # interactive inspector
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context

from mcp_server.tools.data import calculate, json_query, parse_csv, statistics_summary
from mcp_server.tools.system import get_system_info, list_directory, read_file_summary
from mcp_server.tools.text import analyze_text, hash_text, transform_text

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


# ===  System Tools ============================================================


@mcp.tool
def system_info() -> dict[str, Any]:
    """Get detailed system information including OS, CPU, disk, and Python version."""
    return get_system_info()


@mcp.tool
def list_dir(path: str = ".", pattern: str = "*", include_hidden: bool = False) -> list[dict[str, Any]]:
    """List files and directories at a given path.

    Args:
        path: Directory to list (default: current directory).
        pattern: Glob pattern to filter entries, e.g. '*.py'.
        include_hidden: Include dotfiles and dotdirs.
    """
    return list_directory(path, pattern=pattern, include_hidden=include_hidden)


@mcp.tool
def read_file(path: str, max_lines: int = 100) -> dict[str, Any]:
    """Read a file and return its metadata plus a content preview.

    Args:
        path: Path to the file.
        max_lines: Maximum number of lines in the preview (default: 100).
    """
    return read_file_summary(path, max_lines=max_lines)


# === Text Tools ===============================================================


@mcp.tool
async def text_analyze(text: str) -> dict[str, Any]:
    """Analyze text and return word count, sentence count, top words, and more.

    Args:
        text: The text to analyze.
    """
    ctx = get_context()
    await ctx.info(f"Analyzing text ({len(text)} chars)")
    return analyze_text(text)


@mcp.tool
def text_transform(
    text: str,
    operation: str,
    find: str = "",
    replace: str = "",
) -> str:
    """Transform text using the specified operation.

    Args:
        text: Input text to transform.
        operation: One of uppercase, lowercase, title, reverse, strip,
                   deduplicate_lines, sort_lines, replace.
        find: String to find (required for 'replace').
        replace: Replacement string (used with 'replace').
    """
    return transform_text(text, operation, find=find, replace=replace)


@mcp.tool
def text_hash(text: str, algorithm: str = "sha256") -> dict[str, str]:
    """Compute a cryptographic hash of the given text.

    Args:
        text: The text to hash.
        algorithm: One of md5, sha1, sha256, sha512 (default: sha256).
    """
    return hash_text(text, algorithm=algorithm)


# === Data Tools ===============================================================


@mcp.tool
def math_calculate(expression: str) -> dict[str, Any]:
    """Evaluate a mathematical expression safely.

    Supports arithmetic, sqrt, log, trig functions, pi, e, abs, round, min, max.

    Args:
        expression: Math expression to evaluate, e.g. 'sqrt(144) + 2**3'.
    """
    return calculate(expression)


@mcp.tool
async def stats_summary(numbers: list[float]) -> dict[str, Any]:
    """Compute descriptive statistics for a list of numbers.

    Returns count, sum, mean, median, mode, stdev, variance, min, and max.

    Args:
        numbers: List of numeric values.
    """
    ctx = get_context()
    await ctx.info(f"Computing statistics for {len(numbers)} values")
    return statistics_summary(numbers)


@mcp.tool
def csv_parse(csv_text: str, delimiter: str = ",") -> list[dict[str, str]]:
    """Parse CSV text into a list of row dictionaries.

    The first row is treated as column headers.

    Args:
        csv_text: Raw CSV content.
        delimiter: Column delimiter (default: comma).
    """
    return parse_csv(csv_text, delimiter=delimiter)


@mcp.tool
def json_extract(json_text: str, path: str) -> Any:
    """Extract a value from a JSON string using dot-notation.

    Supports nested keys and integer array indices (e.g. 'users.0.name').

    Args:
        json_text: Raw JSON string.
        path: Dot-separated path to the desired value.
    """
    return json_query(json_text, path)


# === Resources ================================================================


@mcp.resource("config://server")
def server_config() -> str:
    """Current server configuration and environment."""
    import json

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
        "2. Computing statistics with stats_summary on numeric columns\n"
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
