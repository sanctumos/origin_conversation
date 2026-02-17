# MCP client integration

This page describes how to add the origin_conversation MCP server to various MCP-capable clients. The server exposes the **`conversation_search`** tool; once the client is configured, your assistant can search your canonical ChatGPT export from within that environment.

---

## General: STDIO vs SSE

- **STDIO:** The client runs the server as a subprocess and talks over stdin/stdout. Use this when the client runs on the **same machine** as where you want to run the server. You configure a **command** (and optional **args** / **env**).
- **SSE:** The server runs as a long-lived HTTP process; the client connects to a URL. Use this when the client is on a **different machine** or you want a shared server. You configure an **SSE URL** (and sometimes headers). See [Configuration](CONFIGURATION.md) for how to run the server with `--sse`.

Below, “stdio” configs assume the server is started by the client; “SSE” configs assume you have already started `python -m origin_conversation_mcp --sse` (and optionally `--allow-external`) somewhere reachable.

---

## Claude Desktop

Claude Desktop uses a JSON config file for MCP servers.

**Config file locations:**

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

You can open it via **Settings → Developer → Edit Config**.

### STDIO (recommended for local use)

Use the Python from the virtualenv where you installed origin_conversation so the server has the right dependencies. Replace the path with your actual venv Python.

**Windows (PowerShell):** typical path style:

```json
{
  "mcpServers": {
    "origin-conversation": {
      "command": "C:\\projects\\sanctum\\origin_conversation\\.venv\\Scripts\\python.exe",
      "args": ["-m", "origin_conversation_mcp"],
      "env": {}
    }
  }
}
```

**macOS/Linux:** use your venv Python:

```json
{
  "mcpServers": {
    "origin-conversation": {
      "command": "/path/to/origin_conversation/.venv/bin/python",
      "args": ["-m", "origin_conversation_mcp"],
      "env": {}
    }
  }
}
```

If the DB is not in `db/` and you want to point at a specific file:

```json
"env": {
  "CONVERSATION_DB": "C:\\data\\canonical-export-2025-02-17.db"
}
```

(Adjust path for your OS.)

### SSE (remote server)

If the server is already running with `--sse` (e.g. on `http://myserver:8000`), you would add an SSE entry. Claude Desktop’s exact format for SSE may vary by version; refer to Anthropic’s docs. Typically you need the base URL of the SSE endpoint (e.g. `http://myserver:8000` or the `/sse` URL). Check the latest [Claude Desktop MCP documentation](https://modelcontextprotocol.io/docs/develop/connect-local-servers) for the current schema.

**After editing:** Restart Claude Desktop fully (quit and reopen) so it reloads the config. The MCP server indicator (e.g. hammer icon) should appear when the server is connected.

---

## Cursor

Cursor supports MCP servers via its settings. Exact UI and config location can change; the following is the typical idea.

### STDIO

1. Open Cursor **Settings** and find **MCP** or **Features → MCP**.
2. Add a new server. You’ll specify a **command** that runs the server:
   - **Command:** Full path to the Python interpreter in your origin_conversation venv (e.g. `C:\...\origin_conversation\.venv\Scripts\python.exe` on Windows, or `.../origin_conversation/.venv/bin/python` on macOS/Linux).
   - **Args:** `-m`, `origin_conversation_mcp` (or leave args empty if the UI runs “command” as a single executable and you use a wrapper script that runs `python -m origin_conversation_mcp`).
3. If Cursor allows environment variables for the server, set `CONVERSATION_DB` (or `ORIGIN_CONVERSATION_DB`) if your DB is not in `db/`.

### SSE

If your origin_conversation server is running with `--sse` (e.g. on another machine or a shared host), add an MCP server in Cursor that uses the **SSE** transport and the server’s URL (e.g. `http://host:8000` or the `/sse` endpoint, per Cursor’s current MCP SSE docs).

Refer to Cursor’s in-app MCP documentation or **Cursor Settings → MCP** for the current fields (URL, headers, etc.).

---

## Letta (Athena / Ada)

Letta supports MCP servers so that agents (e.g. Athena) can call tools. The **`conversation_search`** tool is designed to mirror Letta’s built-in conversation search; you can use this server to search your **canonical ChatGPT export** instead of or in addition to Letta’s instance history.

### STDIO

In your Letta project or agent configuration, add an MCP server that runs the origin_conversation process:

- **Command:** Path to the Python in your venv, e.g. `C:\...\origin_conversation\.venv\Scripts\python.exe` or `.../.venv/bin/python`.
- **Args:** `["-m", "origin_conversation_mcp"]`.
- **Env (if needed):** `CONVERSATION_DB` or `ORIGIN_CONVERSATION_DB` if the DB is not in `db/`.

Once the server is connected, the agent will see `conversation_search` and can call it like the built-in conversation search (same parameters and behavior).

### SSE

If you run origin_conversation with `--sse` (e.g. on a shared “Sanctum” box), add an MCP server in Letta that uses the **SSE** transport and the server URL. The agent will get the same `conversation_search` tool over the network.

See Letta’s docs for the exact MCP server configuration format (YAML/JSON and fields for stdio vs SSE).

---

## Other MCP clients (generic)

Any client that supports the [Model Context Protocol](https://modelcontextprotocol.io/) and can start a **stdio** subprocess or connect to an **SSE** endpoint can use this server.

### STDIO

- **Command:** The executable that runs the server. Use the **full path** to the Python interpreter in the virtualenv where you ran `pip install -e .` (or `pip install origin-conversation`).
- **Args:** `["-m", "origin_conversation_mcp"]` (or equivalent for your OS).
- **Env:** Optional. Set `CONVERSATION_DB` or `ORIGIN_CONVERSATION_DB` to the full path of your canonical export SQLite file if it is not in `db/`.
- The client must start this process and connect its stdin/stdout to the MCP JSON-RPC channel. No `--sse` flag.

### SSE

- Start the server yourself:  
  `python -m origin_conversation_mcp --sse [--port PORT] [--host HOST] [--allow-external]`
- Client configuration:
  - **Transport:** SSE (or “HTTP SSE”).
  - **URL:** Base URL of the server (e.g. `http://localhost:8000`). The client will use **GET** `/sse` to open the stream and **POST** to `/messages/` to send requests (standard MCP SSE layout).
- If the client requires a single “SSE URL,” use the endpoint that opens the event stream (e.g. `http://localhost:8000/sse`), and ensure the client is configured to POST to the same host’s `/messages/` path as per MCP SSE.

---

## Verifying the tool is available

After configuring the client and restarting (if needed):

1. Start a conversation and ask the assistant to **list its tools** or to **search your conversation history** for a known phrase.
2. If the assistant can call `conversation_search` and return results from your canonical export, the integration is working.

If the tool does not appear, check:

- The server process is starting (stdio: check client logs for the command and any errors; SSE: ensure the server process is running and the URL is reachable).
- DB path: either a `db/*.db` file exists or `CONVERSATION_DB` / `ORIGIN_CONVERSATION_DB` is set to a valid file path.
- Client-specific docs for MCP (config syntax, required restart, and whether the client supports stdio vs SSE).
