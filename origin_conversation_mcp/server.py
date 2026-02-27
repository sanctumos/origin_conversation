# SPDX-License-Identifier: AGPL-3.0-only
# origin_conversation MCP server - SMCP-style tool registration.
"""MCP server with conversation_search tool; uses mcp.server.Server and stdio transport."""
import logging

from mcp.server import Server
from mcp.types import TextContent, Tool

from .search import conversation_search

logger = logging.getLogger(__name__)

# Server enforces default limit 50 and max 200 regardless of client; schema default is advisory.
CONVERSATION_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Search string (natural language or phrase). Searches message content and conversation title (text match).",
        },
        "roles": {
            "type": "array",
            "items": {"type": "string", "enum": ["user", "assistant", "tool"]},
            "description": "Filter by message role(s). e.g. [\"user\"], [\"assistant\"], or [\"user\", \"assistant\"].",
        },
        "start_date": {
            "type": "string",
            "description": "Start of date range (ISO 8601), inclusive. e.g. \"2024-01-15\" or \"2024-01-15T14:30\".",
        },
        "end_date": {
            "type": "string",
            "description": "End of date range (ISO 8601), inclusive; full day if date-only. e.g. \"2024-01-20\".",
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of results to return.",
            "default": 50,
        },
    },
    "required": [],
    "additionalProperties": False,
}

ALLOWED_ROLES = {"user", "assistant", "tool"}

TOOLS: list[Tool] = [
    Tool(
        name="conversation_search",
        description=(
            "Search prior conversation history (canonical ChatGPT export). "
            "Hybrid-style: text match on content and titles. Optional filters: roles (user/assistant/tool), "
            "start_date and end_date (ISO 8601 inclusive). Returns matching messages with timestamps and content."
        ),
        inputSchema=CONVERSATION_SEARCH_SCHEMA,
    ),
]


def create_server() -> Server:
    """Create MCP server instance (no tools registered yet)."""
    return Server(name="origin-conversation-mcp", version="0.1.0")


def register_tools(server: Server) -> None:
    """Register conversation_search and list_tools / call_tool handlers."""

    @server.list_tools()
    async def list_tools():
        return TOOLS

    @server.call_tool()
    async def call_tool(tool_name: str, arguments: dict):
        if tool_name != "conversation_search":
            return [TextContent(type="text", text=f"Unknown tool: {tool_name}")]
        try:
            query = arguments.get("query") or None
            roles = arguments.get("roles")
            if roles is not None and not isinstance(roles, list):
                roles = [roles]
            if roles:
                invalid = set(roles) - ALLOWED_ROLES
                if invalid:
                    return [
                        TextContent(
                            type="text",
                            text=f"Invalid role(s): {sorted(invalid)}. Allowed: user, assistant, tool.",
                        )
                    ]
            start_date = arguments.get("start_date") or None
            end_date = arguments.get("end_date") or None
            limit = arguments.get("limit")
            if limit is not None:
                try:
                    limit = int(limit)
                except (TypeError, ValueError):
                    limit = 50
            else:
                limit = 50
            result = conversation_search(
                query=query,
                roles=roles,
                start_date=start_date,
                end_date=end_date,
                limit=max(1, min(limit, 200)),
            )
            return [TextContent(type="text", text=result)]
        except FileNotFoundError as e:
            return [TextContent(type="text", text=f"Database not found: {e}")]
        except Exception as e:
            logger.error("call_tool conversation_search failed: %s", e, exc_info=True)
            return [TextContent(type="text", text=f"Error: {e}")]
