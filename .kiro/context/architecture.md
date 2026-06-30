# Architecture — Google Workspace MCP Server

## Data Flow

```
AI Agent (Kiro/Claude/Cursor)
    ↓ stdio (JSON-RPC)
MCP Server (src/server.py)
    ↓ routes to handler
Tool Handler (src/tools/*.py)
    ↓ calls get_service()
OAuth Module (src/auth/oauth.py)
    ↓ authenticates
googleapis.com
```

## Server Lifecycle

1. `python3 -m src.server` starts the process
2. `.env` loaded via `python-dotenv` from project root
3. MCP `Server("google-mcp")` instance created
4. All tool lists merged into `ALL_TOOLS`
5. Handler map built: `{tool_name: handler_function}`
6. stdio transport established (`stdin`/`stdout` JSON-RPC)
7. Agent sends `list_tools` → returns all 26 tool definitions
8. Agent sends `call_tool(name, args)` → dispatched to handler

## Auth Flow

1. First call to any tool triggers `get_service()`
2. `get_credentials()` checks for existing token at `.credentials/token.json`
3. If valid → use it. If expired → refresh via `creds.refresh(Request())`
4. If no token → `InstalledAppFlow.run_local_server()` opens browser
5. Token saved with `chmod 600`
6. `googleapiclient.discovery.build()` creates service client

## Error Handling

```python
try:
    result = await handler(name, arguments)
    return [TextContent(type="text", text=result)]
except Exception as e:
    return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]
```

All exceptions are caught at the server level and returned as text errors to the agent. Individual tools do not need try/except unless they need specific error recovery.

## Adding a New Service

1. Create `src/tools/{service}.py`
2. Define `{SERVICE}_TOOLS` list with `Tool(name=..., description=..., inputSchema=...)`
3. Define `async def handle_{service}(name: str, args: dict) -> str:`
4. Import in `src/server.py` and add to `ALL_TOOLS` and `HANDLERS`
5. Add OAuth scope in `src/auth/oauth.py` if needed
6. Enable the API in Google Cloud Console

## Security Model

- **No network calls** except to `*.googleapis.com` and `accounts.google.com`
- **No dependency on wrappers** — direct Google SDK usage
- **Token isolation** — chmod 600 on token file
- **Environment variables** — credentials never hardcoded
- **Minimal attack surface** — ~300 lines of auditable code
