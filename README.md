# origin_conversation

**SanctumOS · Athena**

Conversation and export tooling for the SanctumOS stack.

## MCP server (conversation search)

An MCP server (patterned after SMCP) exposes a **conversation_search** tool over stdio so agents (e.g. Letta’s Athena) can search the canonical ChatGPT export history.

**Tool: `conversation_search`**

- **query** (optional): Text to match in message content and conversation titles.
- **roles** (optional): Filter by `["user"]`, `["assistant"]`, `["tool"]` or combinations.
- **start_date** / **end_date** (optional): ISO 8601 inclusive range (e.g. `"2024-01-15"`, `"2024-01-15T14:30"`).
- **limit** (optional): Max results (default 50, cap 200).

Searches the SQLite DB in **`db/`** (e.g. `db/canonical-export-YYYY-MM-DD.db`). Set `CONVERSATION_DB` or `ORIGIN_CONVERSATION_DB` to override the path.

**Run (dual transport, like SMCP):**

- **STDIO** (default)—for Letta/Cursor and local process configs:
  ```bash
  python -m origin_conversation_mcp
  # or: origin-conversation-mcp
  ```
  Configure your MCP client to run this command; it speaks JSON-RPC over stdin/stdout.

- **SSE**—for remote or shared Sanctum boxes (HTTP):
  ```bash
  python -m origin_conversation_mcp --sse
  python -m origin_conversation_mcp --sse --port 9000 --host 127.0.0.1
  python -m origin_conversation_mcp --sse --allow-external   # bind 0.0.0.0
  ```
  Use `MCP_PORT` and `MCP_HOST` env vars for port/host. Clients connect via GET `/sse` and POST to `/messages/`.

## License

This project uses **dual licensing**:

- **Source code** (e.g. application code, scripts, schema): **GNU Affero General Public License v3.0 (AGPL-3.0)**. See [LICENSE](LICENSE).
- **Documentation and other non-code materials** (e.g. this README, docs, screenshots): **Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA 4.0)**. See [LICENSES/CC-BY-SA-4.0.txt](LICENSES/CC-BY-SA-4.0.txt). Summary: https://creativecommons.org/licenses/by-sa/4.0/

Short notice: [NOTICE](NOTICE). Details: [LICENSES/README.md](LICENSES/README.md).
