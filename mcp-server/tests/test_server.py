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
            expected = {"system_info", "list_dir", "read_file", "text_analyze", "text_transform", "text_hash"}
            assert expected.issubset(tool_names)

    async def test_system_info_tool(self, client: Client):
        async with client:
            result = await client.call_tool("system_info", {})
            assert result is not None

    async def test_text_analyze_tool(self, client: Client):
        async with client:
            result = await client.call_tool("text_analyze", {"text": "Hello world. Goodbye world."})
            assert result is not None

    async def test_math_calculate_tool(self, client: Client):
        async with client:
            result = await client.call_tool("math_calculate", {"expression": "2 + 2"})
            assert result is not None

    async def test_csv_parse_tool(self, client: Client):
        async with client:
            result = await client.call_tool("csv_parse", {"csv_text": "a,b\n1,2\n3,4"})
            assert result is not None

    async def test_list_resources(self, client: Client):
        async with client:
            resources = await client.list_resources()
            uris = {str(r.uri) for r in resources}
            assert "config://server" in uris

    async def test_read_resource(self, client: Client):
        async with client:
            content = await client.read_resource("config://server")
            assert content is not None

    async def test_list_prompts(self, client: Client):
        async with client:
            prompts = await client.list_prompts()
            names = {p.name for p in prompts}
            assert "analyze_file_prompt" in names
            assert "data_exploration_prompt" in names
