# Configuration

This document covers environment variables, database path resolution, transport options, and security notes for the origin_conversation MCP server.

---

## Database path

The server reads from a **single** SQLite database. That database should be the **canonical-only** export produced by [ChatGPT Browser](https://github.com/actuallyrizzn/chatGPT-browser) (Settings → Download canonical-only database).

### Resolution order

1. **Environment variable**  
   If `CONVERSATION_DB` or `ORIGIN_CONVERSATION_DB` is set and the value is the path to an **existing file**, that path is used.  
   - If the env is set but the file does **not** exist, the server **falls back** to the next step (it does not error on the env path alone).

2. **Default: `db/` directory**  
   The server looks for a directory named `db` next to the package (typically the repo root). It then uses the **newest** file matching `*.db` in that directory (by modification time).  
   - If `db/` does not exist or contains no `*.db` files, the tool will return a “Database not found” error when `conversation_search` is called.

### Environment variables (DB)

| Variable                  | Purpose |
|---------------------------|--------|
| `CONVERSATION_DB`         | Full path to the SQLite conversation DB. Checked first. |
| `ORIGIN_CONVERSATION_DB`  | Alternative name for the same path. Used if `CONVERSATION_DB` is not set. |

Example (Windows PowerShell):

```powershell
$env:CONVERSATION_DB = "C:\data\canonical-export-2025-02-17.db"
```

Example (macOS/Linux):

```bash
export CONVERSATION_DB=/home/me/data/canonical-export-2025-02-17.db
```

### Recommended layout

- Put your canonical export in `origin_conversation/db/`, e.g. `db/canonical-export-YYYY-MM-DD.db`.  
- To refresh: replace or add a newer `*.db`; the server will use the newest by default.  
- If you use a path outside the repo, set `CONVERSATION_DB` (or `ORIGIN_CONVERSATION_DB`) so the server can find it.

---

## Transport: STDIO vs SSE

The server supports two transports. Your MCP client will use one or the other.

### STDIO (default)

- **Use case:** Local MCP clients (e.g. Claude Desktop, Cursor, Letta on the same machine). The client starts the server as a subprocess and communicates over stdin/stdout using JSON-RPC.
- **How to run:** The client runs the command (e.g. `python -m origin_conversation_mcp` or `origin-conversation-mcp`). You do not need to pass any transport flag.
- **Port/host:** Not used. No network listen.

### SSE (HTTP)

- **Use case:** Remote or shared setups where the MCP client connects over HTTP (e.g. a Cursor/Claude config pointing at a server on another machine or a shared “Sanctum” box).
- **How to run:**
  ```bash
  python -m origin_conversation_mcp --sse
  ```
- **Endpoints:**
  - **GET** `/sse` — client opens the SSE connection here.
  - **POST** `/messages/` — client sends JSON-RPC messages here.
- **Options and env:**

| Option / Env   | Default     | Description |
|---------------|-------------|-------------|
| `--port`      | 8000        | Port to bind. Override with `MCP_PORT`. |
| `--host`      | 127.0.0.1   | Host to bind. Override with `MCP_HOST`. |
| `--allow-external` | —   | If set, bind to `0.0.0.0` so the server is reachable from other machines. |

Examples:

```bash
python -m origin_conversation_mcp --sse --port 9000 --host 127.0.0.1
MCP_PORT=9000 MCP_HOST=0.0.0.0 python -m origin_conversation_mcp --sse --allow-external
```

---

## Environment variables (SSE)

| Variable   | Used when | Purpose |
|------------|-----------|---------|
| `MCP_PORT` | `--sse`   | Default port for `--port` (e.g. `8000`). Must be a valid integer. |
| `MCP_HOST` | `--sse`   | Default host for `--host` (e.g. `127.0.0.1`). Ignored if `--allow-external` is set (then host is `0.0.0.0`). |

---

## Logging

- **STDIO mode:** Logging is configured to **stderr** at level **WARNING** so that stdout is reserved for JSON-RPC. Application DEBUG/INFO messages will not appear unless you lower the log level (e.g. for the `origin_conversation_mcp` logger).
- **SSE mode:** Uvicorn is run with `log_level="info"`, so you get INFO from the HTTP server. Application logs still follow the same WARNING default unless you change the Python logging configuration.

---

## Security

- **STDIO:** The server only talks to the process that started it (stdin/stdout). No network exposure.
- **SSE:**  
  - With default `--host 127.0.0.1`, the server is only reachable from the same machine.  
  - With `--allow-external`, the server binds to `0.0.0.0` and is reachable from the network. There is **no built-in authentication or TLS**.  
  - **Recommendation:** Use SSE with `--allow-external` only on **trusted networks**, or put the server behind a **reverse proxy** that enforces TLS and authentication (e.g. nginx, Caddy, or a cloud load balancer). Document this for anyone deploying the server.

---

## Quick reference

| What you want                         | What to do |
|--------------------------------------|------------|
| Use a specific DB file               | Set `CONVERSATION_DB` (or `ORIGIN_CONVERSATION_DB`) to its path. |
| Use newest DB in repo               | Put `*.db` in `db/`; don’t set the env. |
| Run for local MCP client            | Client runs `python -m origin_conversation_mcp` (no flags). |
| Run SSE on port 9000                | `python -m origin_conversation_mcp --sse --port 9000` or `MCP_PORT=9000 ... --sse`. |
| Allow external connections (SSE)    | `python -m origin_conversation_mcp --sse --allow-external`. Protect with proxy/auth. |
