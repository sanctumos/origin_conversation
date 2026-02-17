# Tool reference: conversation_search

The MCP server exposes a single tool, **`conversation_search`**, which searches the canonical ChatGPT export SQLite database for messages matching your criteria. The tool is designed to mirror the [LettaAI](https://www.letta.ai) conversation search tool contract so it can be used as a drop-in for (or alongside) Letta’s built-in search, and works with any MCP client.

---

## Tool name

`conversation_search`

---

## Description (as seen by the LLM)

> Search prior conversation history (canonical ChatGPT export). Hybrid-style: text match on content and titles. Optional filters: roles (user/assistant/tool), start_date and end_date (ISO 8601 inclusive). Returns matching messages with timestamps and content.

---

## Parameters

All parameters are **optional**. The tool accepts a single JSON object with the following properties:

| Parameter     | Type     | Default | Description |
|---------------|----------|---------|-------------|
| `query`       | string   | —       | Text to match in **message content** and **conversation titles**. Uses SQL `LIKE` with `%query%` (case-sensitive in SQLite). |
| `roles`       | string[] | —       | Restrict results to messages with these roles. Allowed values: `"user"`, `"assistant"`, `"tool"`. Example: `["user", "assistant"]`. |
| `start_date`  | string   | —       | Start of date range (inclusive), ISO 8601. Date-only (e.g. `"2024-01-15"`) is interpreted as start of that day UTC. With time (e.g. `"2024-01-15T14:30:00"`), no timezone suffix is treated as UTC. |
| `end_date`    | string   | —       | End of date range (inclusive), ISO 8601. Date-only is interpreted as **end of that day** UTC (23:59:59.999). Same timezone rules as `start_date`. |
| `limit`       | integer  | 50      | Maximum number of messages to return. Server enforces a minimum of 1 and a maximum of 200; values outside that range are clamped. |

- **Required:** none.  
- **Additional properties:** not allowed (`additionalProperties: false`).  
- If the client omits a parameter, the server applies the default or “no filter” as above.

---

## Behavior

- **Data source:** The SQLite database configured via `db/` (newest `*.db`) or the `CONVERSATION_DB` / `ORIGIN_CONVERSATION_DB` environment variable. The schema is expected to have `messages` (e.g. `id`, `conversation_id`, `role`, `content`, `create_time`, `position`) and `conversations` (e.g. `id`, `title`). This matches the canonical-only export from [ChatGPT Browser](https://github.com/actuallyrizzn/chatGPT-browser).
- **Search:** If `query` is provided, it is applied as a `LIKE '%query%'` on both message content and conversation title. Combined with optional `roles` and optional date range (`start_date` / `end_date`). Results are ordered by `create_time` descending.
- **Date handling:** Dates are parsed as ISO 8601; date-only strings are normalized to start (or end) of day UTC. Timestamps stored in the DB (numeric or ISO string) are compared in a way consistent with that parsing. Date filtering may be applied in-process after a bounded fetch (see implementation).
- **Output:** A single **text** result containing matching messages, one per block, with format:
  - `[YYYY-MM-DD HH:MM] role (conv: title_or_id)\ncontent`
  - Long content is truncated (e.g. to 2000 characters) with `...`.
  - Blocks are separated by `\n\n---\n\n`. If no messages match, the string is `"No matching messages."`

---

## Example inputs (JSON)

**Search for “asyncio” in all messages, max 20:**

```json
{
  "query": "asyncio",
  "limit": 20
}
```

**Only user and assistant messages in January 2025:**

```json
{
  "roles": ["user", "assistant"],
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "limit": 50
}
```

**All assistant messages (no text filter, no date):**

```json
{
  "roles": ["assistant"]
}
```

**Date-only range (full days in UTC):**

```json
{
  "start_date": "2024-06-01",
  "end_date": "2024-06-15",
  "limit": 100
}
```

---

## Example output (conceptually)

The tool returns a single MCP `TextContent` with `type: "text"` and a string body, e.g.:

```text
[2025-02-10 14:30] user (conv: Python asyncio help)
How do I run two coroutines in parallel with asyncio?

---

[2025-02-10 14:32] assistant (conv: Python asyncio help)
You can use asyncio.gather() to run multiple coroutines concurrently...
```

If nothing matches:

```text
No matching messages.
```

---

## Errors (returned as tool result text)

- **Database not found:** If the configured DB path is missing or `db/` has no `*.db` file, the tool returns a message like `"Database not found: ..."` (no exception to the client).
- **Other errors:** Any other server-side error is returned as a short message `"Error: ..."` so the client can show something to the user. Details are not exposed in the tool response; check server logs for tracebacks.

---

## Compatibility with Letta

The tool name, parameter names, types, and semantics are intended to match Letta’s built-in conversation search tool. You can:

- Use this server **instead of** Letta’s built-in search (e.g. to search your full canonical ChatGPT export).
- Use it **in addition to** Letta’s search (e.g. one tool for instance history, this one for the long-term export), depending on how you register MCP servers in Letta.

No changes are required to the tool contract when switching between Letta’s native search and this server.
