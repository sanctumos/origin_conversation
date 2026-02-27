# Changelog

## [Unreleased]

## [0.1.1] - 2026-02-27

### Fixed

- **#1** SSE: Document reliance on Starlette private API (`request._send`), add version pin `starlette<0.40.0`, TODO to revisit when public API exists.
- **#2** SSE: Chain to previous SIGINT/SIGTERM handler instead of clobbering; document in comment.
- **#3** MCP_PORT: Add `_env_port()` helper; invalid or empty value falls back to default instead of crashing.
- **#4** Add type annotations `request: Request` to SSE endpoint handlers.
- **#5** POST /sse: Single 400 response message for any POST to `/sse`.
- **#6** Log level: Documented in CONFIGURATION.md (app WARNING vs uvicorn INFO).
- **#7** [HIGH] Log exceptions in call_tool before returning generic Error (logger.error with exc_info=True).
- **#8** Comment: server enforces limit default 50 and max 200.
- **#9** Validate roles against {user, assistant, tool} before search; return clear error for invalid roles.
- **#10** Rename list_tools_handler/call_tool_handler to list_tools/call_tool for stack traces.
- **#11** Document DB path resolution in _get_db_path docstring and CONFIGURATION.md.
- **#12** Open SQLite read-only for search (`file:path?mode=ro`, uri=True).
- **#13** Document date filter strategy in module docstring (in-process after fetch).
- **#14** Named constants in search.py (_FETCH_LIMIT_*, _CONTENT_DISPLAY_MAX, _SECONDS_PER_DAY, etc.).
- **#15** Docstring in _parse_iso_to_float for optional stricter validation (see issue #15).
- **#16** Use context manager for SQLite connection (`with sqlite3.connect(...) as conn`).
- **#17** __init__.py docstring: "stdio (default) and SSE".
- **#18** Upper bound starlette<0.40.0; comment on tested versions.
- **#19** Optional: noted in audit; no change (optional-deps for SSE-only install possible later).
- **#20** SSE security: documented in CONFIGURATION.md (trusted network / reverse proxy with auth/TLS).

### Added

- Test suite (pytest, pytest-cov, pytest-asyncio); tests for search, server, __main__.

## [0.1.0]

### Added

- **MCP server** (`origin_conversation_mcp`): conversation search over canonical ChatGPT export DB, patterned after SMCP.
  - **Tool:** `conversation_search` — same contract as Letta’s built-in tool: optional `query`, `roles` (user/assistant/tool), `start_date` / `end_date` (ISO 8601 inclusive), `limit`. Returns matching messages with timestamps and content.
  - **Dual transport:** STDIO (default) for local process configs; `--sse` for HTTP SSE (remote/shared Sanctum boxes). Options: `--port`, `--host`, `--allow-external`; env `MCP_PORT`, `MCP_HOST`.
  - **Data:** Reads SQLite from `db/` (e.g. `db/canonical-export-YYYY-MM-DD.db`). Override with `CONVERSATION_DB` or `ORIGIN_CONVERSATION_DB`.
- **Venv and gitignore:** `.venv/`, `db/`, `*.db`, and build artifacts ignored; repo uses a venv for the MCP server.

### Notes for Athena / Ada

- This MCP server exposes **one tool**, `conversation_search`, so you can search the **full canonical ChatGPT history** (the “three years from OpenAI”) in addition to Sanctum instance history. Use STDIO or SSE depending on how this server is configured on the box (see README).
