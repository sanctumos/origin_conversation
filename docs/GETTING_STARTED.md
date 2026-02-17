# Getting started

This guide walks through the full path from a ChatGPT export to an MCP client that can search your canonical conversation history.

---

## Prerequisites

- **Python 3.10+**
- **[ChatGPT Browser](https://github.com/actuallyrizzn/chatGPT-browser)** installed and run at least once (so you can import and export)
- A ChatGPT data export (JSON) from [ChatGPT → Settings → Export data](https://help.openai.com/en/articles/9086558-exporting-your-chatgpt-data)

---

## Step 1: Export your data from ChatGPT

1. In ChatGPT, go to **Settings** (profile or gear).
2. Use **Export data** (or equivalent) and request an export.
3. When ready, download the ZIP. Inside you’ll have (among other files) something like `conversations.json` or a folder of conversation data.
4. Keep this file handy for the next step.

---

## Step 2: Import into ChatGPT Browser and export canonical-only DB

1. **Install and run ChatGPT Browser** (see [their README](https://github.com/actuallyrizzn/chatGPT-browser)):
   - Clone the repo, create a venv, `pip install -r requirements.txt`, `python init_db.py`, then `python app.py`.
2. Open the app (e.g. `http://localhost:5000`) and go to **Settings**.
3. In **Import JSON**, choose your ChatGPT export file (e.g. `conversations.json` from the export) and run **Import Conversations**. Wait for the import to finish.
4. In the same **Settings** page, use **Export data** → **Download canonical-only database**. This creates a SQLite file with **one linear thread per conversation** (no branches)—the “canonical truth” view.
5. Save that file somewhere you can use for origin_conversation (e.g. `canonical-export-2025-02-17.db`).

---

## Step 3: Install and configure origin_conversation

1. **Clone and install** (from this repo):
   ```bash
   git clone <this-repo-url> origin_conversation
   cd origin_conversation
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   pip install -e .
   ```
2. **Provide the canonical DB** to the server. Either:
   - **Option A:** Create a `db` directory in the repo root and put your SQLite file there, e.g.:
     ```text
     origin_conversation/
       db/
         canonical-export-2025-02-17.db
     ```
     The server will use the **newest** `*.db` file in `db/` by default.
   - **Option B:** Set the environment variable to the full path of your DB:
     ```bash
     # Windows (PowerShell)
     $env:CONVERSATION_DB = "C:\path\to\canonical-export-2025-02-17.db"
     # macOS/Linux
     export CONVERSATION_DB=/path/to/canonical-export-2025-02-17.db
     ```
     See [Configuration](CONFIGURATION.md) for `CONVERSATION_DB` and `ORIGIN_CONVERSATION_DB`.

---

## Step 4: Run the MCP server

Choose how your MCP client will connect:

### For local use (Cursor, Claude Desktop, Letta on the same machine): STDIO

Run the server as a **subprocess**; the MCP client will start it and talk over stdin/stdout:

```bash
python -m origin_conversation_mcp
# or, if installed with pip:
origin-conversation-mcp
```

Do **not** run this in the foreground for normal use—your MCP client will run this command and attach to it. You only run it manually to confirm it starts (it will wait for JSON-RPC on stdin).

### For remote or shared use: SSE (HTTP)

Run the server with HTTP SSE so clients can connect over the network:

```bash
python -m origin_conversation_mcp --sse
# Optional: custom port/host
python -m origin_conversation_mcp --sse --port 9000 --host 127.0.0.1
# Allow external connections (bind 0.0.0.0):
python -m origin_conversation_mcp --sse --allow-external
```

Clients connect via **GET** `/sse` and send messages via **POST** to `/messages/`. See [Configuration](CONFIGURATION.md) and [MCP clients](MCP_CLIENTS.md).

---

## Step 5: Configure your MCP client

Add this server to your MCP host so it gets the `conversation_search` tool. Examples:

- **Claude Desktop:** Add an entry to your MCP config file that runs `python -m origin_conversation_mcp` (stdio) or points at your SSE URL.
- **Cursor:** Add the server in Cursor’s MCP settings (command or config file); use the same command or SSE URL.
- **Letta (Athena):** Add the server in Letta’s MCP configuration; the tool contract matches Letta’s built-in conversation search.

Full examples and config snippets are in [MCP clients](MCP_CLIENTS.md).

---

## Step 6: Use the tool from your assistant

Once the client is configured, your assistant can call the tool, for example:

- “Search my ChatGPT history for conversations about Python asyncio.”
- “Find what I asked about authentication in January 2025.”
- “Look up my past discussions on recipe ideas.”

The assistant will invoke `conversation_search` with the right parameters; results are returned as text (messages with timestamps and content) and can be used as context for the next reply.

---

## Refreshing your history

To update the data the MCP server searches:

1. Export again from ChatGPT (or re-export from ChatGPT Browser if you only changed something there).
2. Re-import into ChatGPT Browser and export a new canonical-only DB.
3. Replace the file in `db/` with the new DB (or point `CONVERSATION_DB` at the new file). The server uses the newest `*.db` in `db/` by default, so replacing the file is enough if you use that method.
4. Restart the MCP server (or rely on your client restarting it) so it picks up the new DB.

---

## Copying over memory and custom instructions

origin_conversation does **not** export archival memory, bio, or custom instructions. To reuse them elsewhere:

1. In ChatGPT, open **Settings** and find **Personalization**, **Memory**, and **Custom instructions**.
2. Copy the text you care about.
3. Paste into your target system (e.g. Claude’s custom instructions, a Letta memory block, or a Cursor rule) and tidy formatting as needed.

That gives your other assistants the same high-level context; `conversation_search` then adds search over your **conversation** history.
