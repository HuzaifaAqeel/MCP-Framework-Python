#!/usr/bin/env python3
"""End-to-end demo: build an MCP server with @tool, then drive it with MCPClient.

Run:
    python examples/demo_mcp_roundtrip.py

Starts a Streamable-HTTP server on 127.0.0.1:8123 in the background, connects a
client, lists the tools, calls them, and prints the results.
"""

from __future__ import annotations

import asyncio

from dedalus_mcp import MCPServer, tool
from dedalus_mcp.client import MCPClient


@tool(description="Add two numbers")
def add(a: int, b: int) -> int:
    return a + b


@tool(description="Reverse a string")
def reverse_text(text: str) -> str:
    return text[::-1]


@tool(description="Count the words in a piece of text")
def word_count(text: str) -> int:
    return len(text.split())


def build_server() -> MCPServer:
    server = MCPServer("demo-server")
    server.collect(add)
    server.collect(reverse_text)
    server.collect(word_count)
    return server


def result_text(result) -> str:
    parts = []
    for block in getattr(result, "content", []) or []:
        text = getattr(block, "text", None)
        if text is not None:
            parts.append(text)
    return " ".join(parts)


async def main() -> None:
    server = build_server()
    serve_task = asyncio.create_task(
        server.serve(port=8123, verbose=False, log_level="warning")
    )
    await asyncio.sleep(2.0)  # let uvicorn boot

    try:
        client = await MCPClient.connect("http://127.0.0.1:8123/mcp")
        try:
            tools = await client.list_tools()
            names = [t.name for t in tools.tools]
            print(f"Connected. Server exposes {len(names)} tools: {names}")

            r = await client.call_tool("add", {"a": 5, "b": 3})
            print(f"add(a=5, b=3) -> {result_text(r)}")

            r = await client.call_tool("reverse_text", {"text": "model context protocol"})
            print(f"reverse_text('model context protocol') -> {result_text(r)}")

            r = await client.call_tool("word_count", {"text": "hello mcp world"})
            print(f"word_count('hello mcp world') -> {result_text(r)}")
        finally:
            await client.close()
        print("Demo complete: server + client round-trip over MCP streamable HTTP.")
    finally:
        serve_task.cancel()
        try:
            await serve_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
