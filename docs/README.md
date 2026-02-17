# Documentation index

Documentation for **origin_conversation**: MCP server for searching your canonical ChatGPT export in any MCP-capable framework (Claude, Cursor, Letta, etc.).

| Document | Audience | Contents |
|----------|----------|----------|
| [OVERVIEW.md](OVERVIEW.md) | Everyone | What this is, companion to [ChatGPT Browser](https://github.com/actuallyrizzn/chatGPT-browser), “canonical” export, in/out of scope (no archival/bio/custom instructions). |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Users | End-to-end: export from ChatGPT → import into ChatGPT Browser → export canonical DB → install & run origin_conversation → configure MCP client. |
| [TOOL_REFERENCE.md](TOOL_REFERENCE.md) | Users / developers | Full `conversation_search` API: parameters, behavior, examples, Letta compatibility. |
| [CONFIGURATION.md](CONFIGURATION.md) | Operators | DB path, env vars (`CONVERSATION_DB`, `MCP_PORT`, `MCP_HOST`), STDIO vs SSE, logging, security. |
| [MCP_CLIENTS.md](MCP_CLIENTS.md) | Users | How to add this server to Claude Desktop, Cursor, Letta, and other MCP clients (stdio and SSE). |
| [AGENTS.md](AGENTS.md) | Agents (Athena, Ada) | Short summary: tool name, params, behavior, how the server is run; links to full docs. |

Repo root: [README.md](../README.md) · [CHANGELOG.md](../CHANGELOG.md) · [LICENSE](../LICENSE).
