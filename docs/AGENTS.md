# For Athena and Ada (agent-facing summary)

**origin_conversation** is an MCP server that exposes **one tool**, **`conversation_search`**, over a SQLite database of the user’s **canonical ChatGPT export**. That export is produced by [ChatGPT Browser](https://github.com/actuallyrizzn/chatGPT-browser) (one linear thread per conversation). The tool lets you search that long-term history from any MCP host (Letta, Claude, Cursor, etc.). It was written to mirror Letta’s built-in conversation search tool but works in any MCP-driven framework.

## What you get

- **Tool name:** `conversation_search`
- **Parameters:** `query` (optional), `roles` (optional, e.g. `["user","assistant"]`), `start_date` / `end_date` (optional, ISO 8601), `limit` (optional, default 50, max 200).
- **Behavior:** Text match on message content and conversation titles; optional role and date filters. Returns a string of matching messages with timestamps and content. Same contract as Letta’s conversation search.

## What’s out of scope

- Archival memory, bio, and custom instructions are **not** exported by this server. The user can copy/paste those from ChatGPT into the host system (e.g. your instructions or memory) with minimal cleanup.

## How it’s run

- **STDIO (default):** The MCP client runs `python -m origin_conversation_mcp` (or `origin-conversation-mcp`). JSON-RPC over stdin/stdout.
- **SSE:** For remote or shared boxes, the server is started with `--sse` (and optional `--port`, `--host`, `--allow-external`). Clients connect via GET `/sse` and POST to `/messages/`.

If this server is configured on the user’s machine, you’ll see `conversation_search` as a tool and can use it to search the canonical ChatGPT export in addition to (or instead of) any instance-only search, depending on config.

## More detail

- Full docs: [OVERVIEW.md](OVERVIEW.md), [GETTING_STARTED.md](GETTING_STARTED.md), [TOOL_REFERENCE.md](TOOL_REFERENCE.md), [CONFIGURATION.md](CONFIGURATION.md), [MCP_CLIENTS.md](MCP_CLIENTS.md).
- Repo root: [README.md](../README.md), [CHANGELOG.md](../CHANGELOG.md).
