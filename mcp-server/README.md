# MCP Toolbox Server

A Model Context Protocol (MCP) server built with [FastMCP](https://gofastmcp.com/) that exposes system information, text analysis, and data processing tools to LLM clients like Claude Desktop, Cursor, and Goose.

## Tools

| Tool | Description |
|---|---|
| `system_info` | OS, CPU, disk, Python version |
| `list_dir` | Browse directories with glob filtering |
| `read_file` | Read file metadata and content preview |
| `text_analyze` | Word/sentence/paragraph counts, top words |
| `text_transform` | Uppercase, lowercase, reverse, sort, replace, etc. |
| `text_hash` | SHA-256, SHA-512, SHA-1, MD5 hashing |
| `math_calculate` | Safe math expression evaluation |
| `stats_summary` | Descriptive statistics (mean, median, stdev, ...) |
| `csv_parse` | Parse CSV text into row dictionaries |
| `json_extract` | Dot-notation JSON querying |

## Quickstart

```bash
uv sync
just test          # run the test suite
just run           # start with stdio transport
just run-http      # start with HTTP transport on :8000
just dev           # open the MCP inspector
```

## Project Structure

```
mcp-server/
├── src/mcp_server/
│   ├── server.py           # FastMCP server (tools, resources, prompts)
│   └── tools/
│       ├── system.py       # System info and file browsing
│       ├── text.py         # Text analysis and transformation
│       └── data.py         # Math, stats, CSV, JSON
├── tests/
│   ├── test_system.py
│   ├── test_text.py
│   ├── test_data.py
│   └── test_server.py      # Integration tests via FastMCP Client
├── pyproject.toml
├── justfile
└── README.md
```

## Running

### stdio (local, default)

```bash
uv run python src/mcp_server/server.py
```

### HTTP (remote)

```bash
uv run python src/mcp_server/server.py --http
# or with custom port:
MCP_PORT=9000 uv run python src/mcp_server/server.py --http
```

Connect clients to `http://localhost:8000/mcp`.

### MCP Inspector

```bash
uv run fastmcp dev src/mcp_server/server.py:mcp
```

### Install to Claude Desktop

```bash
uv run fastmcp install src/mcp_server/server.py:mcp
```

## Development

```bash
just format      # ruff format
just lint        # ruff check --fix
just typecheck   # basedpyright
just test        # pytest
just check       # all of the above
```
