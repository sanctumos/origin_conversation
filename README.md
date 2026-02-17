# origin_conversation

<p align="center">
  <img src="docs/logo_inverted.png" alt="origin_conversation logo" width="240">
</p>

**SanctumOS · Athena**

MCP server that exposes **conversation search** over your **canonical ChatGPT export**, so any MCP-capable assistant (Claude, Cursor, Letta, etc.) can search your long-term ChatGPT history.

---

## What this is

- **Companion to [ChatGPT Browser](https://github.com/actuallyrizzn/chatGPT-browser).** ChatGPT Browser lets you import ChatGPT exports and export a **canonical-only** SQLite DB (one linear thread per conversation). This project uses that DB and exposes a single MCP tool, **`conversation_search`**, so agents can search that history.
- **Works with any MCP framework.** Use your ChatGPT “persona” and conversation history inside Claude, Cursor, Letta (Athena), or any client that speaks MCP. The tool contract mirrors [LettaAI](https://www.letta.ai)’s conversation search so it fits naturally there too.
- **Does not export** archival memory, bio, or custom instructions—those are copy/paste into your target system; this server is for **conversation** search only.

Full context, workflow, and scope: **[docs/OVERVIEW.md](docs/OVERVIEW.md)**.

---

## Quick start

1. **Export from ChatGPT** → import into [ChatGPT Browser](https://github.com/actuallyrizzn/chatGPT-browser) → **Settings → Download canonical-only database** in ChatGPT Browser.
2. Put that `.db` file in this repo’s **`db/`** folder (or set **`CONVERSATION_DB`** to its path).
3. **Run the MCP server:**
   - **Local (stdio):** Your MCP client runs: `python -m origin_conversation_mcp` (or `origin-conversation-mcp`).
   - **Remote (SSE):** `python -m origin_conversation_mcp --sse` (optional: `--port`, `--host`, `--allow-external`).
4. **Configure your MCP client** (Claude, Cursor, Letta) to use this server. The client gets the **`conversation_search`** tool.

Step-by-step: **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)**.  
Client-specific config: **[docs/MCP_CLIENTS.md](docs/MCP_CLIENTS.md)**.

---

## Tool: `conversation_search`

- **query** (optional): Text to match in message content and conversation titles.
- **roles** (optional): Filter by `["user"]`, `["assistant"]`, `["tool"]` or combinations.
- **start_date** / **end_date** (optional): ISO 8601 inclusive range.
- **limit** (optional): Max results (default 50, cap 200).

Full API: **[docs/TOOL_REFERENCE.md](docs/TOOL_REFERENCE.md)**.

---

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/OVERVIEW.md](docs/OVERVIEW.md) | Purpose, ChatGPT Browser and “canonical” export, scope (conversations only; no memory/instructions). |
| [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | End-to-end: export → ChatGPT Browser → canonical DB → origin_conversation → MCP client. |
| [docs/TOOL_REFERENCE.md](docs/TOOL_REFERENCE.md) | Full `conversation_search` API and examples. |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | DB path, env vars, STDIO vs SSE, security. |
| [docs/MCP_CLIENTS.md](docs/MCP_CLIENTS.md) | Wiring the server into Claude Desktop, Cursor, Letta, and other MCP clients. |
| [docs/AGENTS.md](docs/AGENTS.md) | Short summary for agent/AI readers (Athena, Ada). |

---

## License

- **Source code:** [GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE).
- **Documentation and non-code:** [Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA 4.0)](LICENSES/CC-BY-SA-4.0.txt). Summary: https://creativecommons.org/licenses/by-sa/4.0/

See [NOTICE](NOTICE) and [LICENSES/README.md](LICENSES/README.md).
