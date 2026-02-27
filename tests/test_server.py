# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for origin_conversation_mcp.server."""
import pytest

pytest.importorskip("mcp")

from origin_conversation_mcp.server import (
    ALLOWED_ROLES,
    CONVERSATION_SEARCH_SCHEMA,
    TOOLS,
    create_server,
    register_tools,
)

from mcp.types import CallToolParams, CallToolRequest, ListToolsRequest


def test_create_server():
    s = create_server()
    assert s is not None
    assert s.name == "origin-conversation-mcp"


def test_schema_has_limit_default():
    assert CONVERSATION_SEARCH_SCHEMA["properties"]["limit"]["default"] == 50


def test_allowed_roles():
    assert ALLOWED_ROLES == {"user", "assistant", "tool"}


@pytest.mark.asyncio
async def test_list_tools():
    server = create_server()
    register_tools(server)
    handler = server.request_handlers.get(ListToolsRequest)
    assert handler is not None
    result = await handler(None)
    tools = result.result.tools
    assert len(tools) == 1
    assert tools[0].name == "conversation_search"
    assert tools[0].inputSchema == CONVERSATION_SEARCH_SCHEMA


@pytest.mark.asyncio
async def test_call_tool_unknown_tool():
    server = create_server()
    register_tools(server)
    from mcp.types import CallToolRequest

    req = CallToolRequest(params=CallToolParams(name="unknown_tool", arguments={}))
    handler = server.request_handlers.get(CallToolRequest)
    assert handler is not None
    result = await handler(req)
    content = result.result.content
    assert len(content) == 1
    assert content[0].type == "text"
    assert "Unknown tool" in content[0].text


@pytest.mark.asyncio
async def test_call_tool_invalid_roles():
    server = create_server()
    register_tools(server)
    from mcp.types import CallToolRequest

    req = CallToolRequest(
        params=CallToolParams(name="conversation_search", arguments={"roles": ["admin", "user"]})
    )
    handler = server.request_handlers.get(CallToolRequest)
    assert handler is not None
    result = await handler(req)
    content = result.result.content
    assert len(content) == 1
    assert "Invalid role" in content[0].text
    assert "admin" in content[0].text


@pytest.mark.asyncio
async def test_call_tool_database_not_found(monkeypatch):
    from mcp.types import CallToolRequest

    def raise_not_found(*, query=None, roles=None, start_date=None, end_date=None, limit=50):
        raise FileNotFoundError("Database not found: /nope.db")

    import origin_conversation_mcp.server as server_mod
    monkeypatch.setattr(server_mod, "conversation_search", raise_not_found)
    server = create_server()
    register_tools(server)
    req = CallToolRequest(params=CallToolParams(name="conversation_search", arguments={}))
    handler = server.request_handlers.get(CallToolRequest)
    assert handler is not None
    result = await handler(req)
    content = result.result.content
    assert len(content) == 1
    assert "not found" in content[0].text.lower()


@pytest.mark.asyncio
async def test_call_tool_logs_exception_on_generic_error(monkeypatch, caplog):
    from mcp.types import CallToolRequest

    def raise_error(*, query=None, roles=None, start_date=None, end_date=None, limit=50):
        raise RuntimeError("internal error")

    import origin_conversation_mcp.server as server_mod
    monkeypatch.setattr(server_mod, "conversation_search", raise_error)
    import logging
    caplog.set_level(logging.ERROR, logger=server_mod.logger.name)
    server = create_server()
    register_tools(server)
    req = CallToolRequest(params=CallToolParams(name="conversation_search", arguments={}))
    handler = server.request_handlers.get(CallToolRequest)
    result = await handler(req)
    content = result.result.content
    assert len(content) == 1
    assert "Error:" in content[0].text
    assert "internal error" in content[0].text
    assert any("call_tool" in r.message and "internal error" in r.message for r in caplog.records)
