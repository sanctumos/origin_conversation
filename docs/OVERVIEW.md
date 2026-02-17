# Overview: origin_conversation

## What this is

**origin_conversation** is an MCP (Model Context Protocol) server that exposes a single tool, **`conversation_search`**, over a SQLite database of your **canonical ChatGPT conversation export**. Any MCP-capable framework—Claude Desktop, Cursor, Letta (Athena), or others—can use this tool to search your long-term ChatGPT history so that assistants can reference your past conversations, style, and context without leaving their own environment.

In short: **export your ChatGPT “persona” and conversation history into any MCP-driven assistant.**

---

## Companion to ChatGPT Browser

This project is designed to work with **[ChatGPT Browser](https://github.com/actuallyrizzn/chatGPT-browser)** (by the same author). ChatGPT Browser is a Flask app that lets you:

- Import your **full** ChatGPT export (JSON) and store it in a SQLite database.
- Browse conversations in “Nice” mode (one clean thread) or “Dev” mode (full tree with branches).
- Export a **canonical-only** SQLite database from Settings: one linear thread per conversation, with branches removed.

### What “canonical” means (from ChatGPT Browser)

ChatGPT exports **full conversation trees**: every branch (e.g. “regenerate” or “new branch”) is included. ChatGPT Browser stores **all of that** in its DB. The **canonical path** is the single main thread you were last on:

- **Stored in the DB:** Every message and every branch (parent/child links)—the full tree.
- **Canonical path (computed when you read):** For each conversation, the app finds the **canonical endpoint**—the message with **no children** (the leaf of the main branch). It then walks **back** via `parent_id` to the root. That ordered path is the “canonical” thread.
- **Nice mode** shows only that path. **Export canonical-only** writes a new SQLite file with **one linear thread per conversation**, no branches—ideal for search and for feeding into other tools.

So: **one source of truth in ChatGPT Browser (full tree), one interpreted view (canonical path) when you read or export.** origin_conversation consumes that **canonical-only** export so agents search a clean, single-thread history.

---

## Why use it

- **Use ChatGPT history in any MCP framework.** Claude, Cursor, Letta, or any client that speaks MCP can call `conversation_search` and get back matching messages from your canonical ChatGPT export. Your assistant can “remember” your past ChatGPT conversations within its own context.
- **Mirrors Letta’s conversation_search.** The tool name, parameters, and behavior are written to match [LettaAI](https://www.letta.ai)’s built-in conversation search tool. If you use Letta (e.g. Athena), you can point it at this server to search your **full** ChatGPT export instead of (or in addition to) instance-only history. The same tool works in other MCP hosts with no change.
- **One export, many assistants.** Export once from ChatGPT Browser; put the DB where origin_conversation can read it. Then configure as many MCP clients as you want (local or remote via SSE) to search that same history.

---

## What’s in scope (and what isn’t)

### In scope

- **Conversation history:** User and assistant (and tool) messages from your **canonical** ChatGPT export. The MCP tool searches message **content** and conversation **titles**, with optional filters by role and date range.
- **Compatibility:** Any MCP client that can run a stdio server or connect to an SSE endpoint. No lock-in to a single framework.

### Out of scope (by design)

- **Archival memory / bio memory / custom instructions.** This server does **not** export or search ChatGPT’s archival memory, bio, or custom instructions. Those are not stored in the conversation export. To reuse them in another framework:
  - Copy the text from ChatGPT (Settings → Personalization / Custom instructions / Memory).
  - Paste into the target system (e.g. Claude’s custom instructions, Letta’s memory, or a Cursor rule) and clean up formatting as needed.
- **Live sync with ChatGPT.** The DB is a **snapshot** you create by exporting from ChatGPT and then importing + re-exporting from ChatGPT Browser. To refresh, repeat the export/import/canonical-export flow and point origin_conversation at the new DB (or replace the file in `db/`).

---

## High-level flow

1. **Export from ChatGPT** (ChatGPT → Export data → download JSON).
2. **Import into ChatGPT Browser** (Settings → Import JSON). ChatGPT Browser stores the full tree in its own SQLite DB.
3. **Export canonical-only DB** from ChatGPT Browser (Settings → “Download canonical-only database”). This produces a single-thread-per-conversation SQLite file.
4. **Place that file** in origin_conversation’s `db/` directory (e.g. `db/canonical-export-2025-02-17.db`), or set `CONVERSATION_DB` to its path.
5. **Run the MCP server** (stdio for local clients, or `--sse` for remote/shared use).
6. **Configure your MCP client** (Claude, Cursor, Letta, etc.) to use this server. The client then has access to the `conversation_search` tool over your canonical ChatGPT history.

Detailed steps are in [Getting started](GETTING_STARTED.md).

---

## License

- **Source code:** [GNU Affero General Public License v3.0 (AGPL-3.0)](../LICENSE).
- **Documentation and non-code materials:** [Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA 4.0)](../LICENSES/CC-BY-SA-4.0.txt). Summary: <https://creativecommons.org/licenses/by-sa/4.0/>.

See [NOTICE](../NOTICE) and [LICENSES/README.md](../LICENSES/README.md) for details.
