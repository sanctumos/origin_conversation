# SPDX-License-Identifier: AGPL-3.0-only
# origin_conversation MCP server: conversation_search over canonical ChatGPT export.
"""MCP server exposing conversation_search tool (SMCP-style). Transports: stdio (default) and SSE."""
__all__ = ["create_server", "register_tools"]
