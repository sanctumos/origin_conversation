# For Athena and Ada

**origin_conversation** now runs an MCP server that exposes **conversation_search** over the canonical ChatGPT export DB (the long-term history in `db/`).

## What you get

- **Tool name:** `conversation_search`
- **Parameters:** `query` (optional), `roles` (optional, e.g. `["user","assistant"]`), `start_date` / `end_date` (optional, ISO 8601), `limit` (optional, default 50).
- **Behavior:** Same as the built-in Letta conversation search: text match on content and titles, optional role and date filters. Returns a string of matching messages with timestamps and content.

## How it’s run

- **STDIO:** Default. The process is started by the MCP client (e.g. Letta config runs `python -m origin_conversation_mcp`).
- **SSE:** For remote or shared boxes, the server is started with `--sse` (and optional `--port`, `--host`, `--allow-external`). Clients connect via GET `/sse` and POST to `/messages/`.

If your Sanctum box runs this server, you’ll see `conversation_search` as a tool; you can use it to search the canonical export history in addition to (or instead of) the built-in instance-only search, depending on config.

See **README.md** and **CHANGELOG.md** in the repo root for details.
