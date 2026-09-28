# 🔌 MCP Framework Python

**A minimal, spec-faithful Python framework for building Model Context Protocol (MCP) servers and clients.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

MCP is the open standard that lets AI agents call your tools, read your resources, and use your prompts
over a clean protocol. This framework wraps the official MCP reference SDK with ergonomic decorators,
automatic schema inference, and production-grade operational features — while staying small and
spec-faithful.

## Why this framework

- **Ergonomic registration** — write functions with `@tool`, then `server.collect(fn)`. Script-style,
  no context managers, no nesting. The same function can be collected by multiple servers; no hidden
  global state.
- **Spec-faithful** — protocol versions are typed (`ProtocolVersion`), capabilities are declared per
  version, and responses are validated against JSON schemas. You get exactly what you asked for, or an
  error — no silent misbehavior.
- **Runtime flexibility** — register or remove tools at runtime, emit `notify_tools_list_changed()`,
  and connected clients refresh.
- **Client ergonomics** — `client = await MCPClient.connect(url)` gives you a ready-to-use client.
  Explicit `close()` or optional `async with`; no nested context-manager gymnastics.
- **Small** — a fraction of the size of batteries-included alternatives. It ships code, not docs and
  screenshots.

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Quickstart

### Server

```python
from dedalus_mcp import MCPServer, tool

@tool(description="Add two numbers")
def add(a: int, b: int) -> int:
    return a + b

server = MCPServer("my-server")
server.collect(add)

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.serve())  # Streamable HTTP on :8000
```

### Client

```python
from dedalus_mcp.client import MCPClient

async def main():
    client = await MCPClient.connect("http://127.0.0.1:8000/mcp")
    tools = await client.list_tools()
    result = await client.call_tool("add", {"a": 5, "b": 3})
    print(result)  # 8
    await client.close()

import asyncio
asyncio.run(main())
```

See [`examples/`](examples/) for more: resources, prompts, progress reporting, auth, and OpenAI integration.

## Features

- `@tool`, `@resource`, `@prompt` decorators with automatic JSON-schema inference from type hints
- Streamable HTTP and stdio transports (plus a transport registry for custom ones)
- Per-protocol-version capability negotiation and response validation
- Runtime tool registration / removal with client notifications
- Auth framework (JWT validation, authorization policies) that plugs into your existing stack
- Subscriptions, progress reporting, sampling, elicitation, and logging services
- `testing.py` helpers to stub contexts in unit tests

## Testing

```bash
pip install pytest pytest-asyncio
python -m pytest tests/ -q
```

## Project Structure

```
src/dedalus_mcp/
├── __init__.py        # Public API: MCPServer, tool, MCPClient, ...
├── server/            # Server core, transports, services, auth
├── client/            # MCPClient, transports, connection handling
├── tool.py            # @tool decorator + schema inference
├── resource.py        # @resource decorator
├── prompt.py          # @prompt decorator
├── versioning.py      # Protocol version profiles
└── testing.py         # Test stubs
examples/              # Runnable servers and clients
docs/                  # Spec notes and design docs
tests/                 # pytest suite
```

## License

MIT — see [LICENSE](LICENSE).
