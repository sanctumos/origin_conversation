# Changelog

## [Unreleased]

### Added

- **MCP server** (`origin_conversation_mcp`): conversation search over canonical ChatGPT export DB, patterned after SMCP.
  - **Tool:** `conversation_search` — same contract as Letta’s built-in tool: optional `query`, `roles` (user/assistant/tool), `start_date` / `end_date` (ISO 8601 inclusive), `limit`. Returns matching messages with timestamps and content.
  - **Dual transport:** STDIO (default) for local process configs; `--sse` for HTTP SSE (remote/shared Sanctum boxes). Options: `--port`, `--host`, `--allow-external`; env `MCP_PORT`, `MCP_HOST`.
  - **Data:** Reads SQLite from `db/` (e.g. `db/canonical-export-YYYY-MM-DD.db`). Override with `CONVERSATION_DB` or `ORIGIN_CONVERSATION_DB`.
- **Venv and gitignore:** `.venv/`, `db/`, `*.db`, and build artifacts ignored; repo uses a venv for the MCP server.

### Notes for Athena / Ada

- This MCP server exposes **one tool**, `conversation_search`, so you can search the **full canonical ChatGPT history** (the “three years from OpenAI”) in addition to Sanctum instance history. Use STDIO or SSE depending on how this server is configured on the box (see README).
