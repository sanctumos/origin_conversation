# SPDX-License-Identifier: AGPL-3.0-only
# origin_conversation MCP server - dual transport: stdio (default) and SSE.
"""Run MCP server over stdio or SSE (for varying Sanctum box configs)."""
import argparse
import asyncio
import logging
import os
import signal
import sys

# Minimal logging to stderr so stdout stays clean for JSON-RPC in stdio mode
logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
    stream=sys.stderr,
    force=True,
)
logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Origin Conversation MCP server (conversation_search over canonical DB)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Transport:
  Default (no --sse)     STDIO for Letta/Cursor local process configs.
  --sse                 SSE over HTTP for remote or shared Sanctum boxes.

Examples:
  python -m origin_conversation_mcp
  python -m origin_conversation_mcp --sse
  python -m origin_conversation_mcp --sse --port 9000 --host 127.0.0.1
  python -m origin_conversation_mcp --sse --allow-external
        """,
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="Use SSE transport (HTTP). Default is STDIO.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MCP_PORT", "8000")),
        help="Port for SSE (default: 8000 or MCP_PORT)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("MCP_HOST", "127.0.0.1"),
        help="Host for SSE (default: 127.0.0.1 or MCP_HOST)",
    )
    parser.add_argument(
        "--allow-external",
        action="store_true",
        help="Bind SSE to 0.0.0.0 (allow external connections).",
    )
    return parser.parse_args()


async def _run_stdio() -> None:
    from mcp.server.stdio import stdio_server

    from .server import create_server, register_tools

    server = create_server()
    register_tools(server)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


async def _run_sse(args: argparse.Namespace) -> None:
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.responses import Response
    from starlette.routing import Mount, Route

    from .server import create_server, register_tools

    host = "0.0.0.0" if args.allow_external else args.host
    if args.allow_external:
        logger.warning("External connections allowed (--allow-external).")
    elif host == "127.0.0.1":
        logger.info("SSE bound to localhost only. Use --allow-external for network access.")

    server = create_server()
    register_tools(server)
    sse_transport = SseServerTransport("/messages/")

    async def sse_endpoint(request):
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options(),
            )
        return Response()

    async def sse_post_endpoint(request):
        body = await request.body()
        if body:
            return Response(
                "POST to /sse not supported. Use GET /sse to connect, POST to /messages/ to send.",
                status_code=400,
                media_type="text/plain",
            )
        return Response("Empty POST", status_code=400)

    app = Starlette(
        routes=[
            Route("/sse", sse_endpoint, methods=["GET"]),
            Route("/sse", sse_post_endpoint, methods=["POST"]),
            Mount("/messages/", app=sse_transport.handle_post_message),
        ]
    )

    import uvicorn

    config = uvicorn.Config(app, host=host, port=args.port, log_level="info")
    server_instance = uvicorn.Server(config)

    def on_signal(signum, frame):
        logger.info("Shutting down SSE server.")
        server_instance.should_exit = True

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    logger.info("Starting origin-conversation MCP SSE on %s:%s", host, args.port)
    await server_instance.serve()


def main() -> None:
    args = _parse_args()
    try:
        if args.sse:
            asyncio.run(_run_sse(args))
        else:
            asyncio.run(_run_stdio())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error("Server error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
