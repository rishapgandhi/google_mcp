# Google Workspace MCP Server — Project Steering

## Project Overview

A minimal, secure, self-hosted MCP (Model Context Protocol) server for Google Workspace. Zero third-party wrappers — only official Google libraries. ~300 lines of fully auditable code.

- **Author**: Rishap Gandhi
- **GitHub**: https://github.com/rishapgandhi/google_mcp
- **License**: MIT
- **Python**: 3.10+
- **Location**: `/var/www/html/mcp_server/google_mcp/`

## Design Philosophy

1. **Minimal** — ~300 lines total, fully readable in 10 minutes
2. **Secure** — Only official Google libraries, no third-party wrappers
3. **Self-hosted** — No SaaS dependency, no telemetry, no analytics
4. **Auditable** — Zero external network calls except to `googleapis.com`
5. **Credentials protected** — OAuth tokens stored with `chmod 600`

## Architecture

```
google_mcp/
├── pyproject.toml           # Project metadata, pinned dependencies
├── .env                     # OAuth credentials (never commit)
├── .credentials/
│   └── token.json           # OAuth token (chmod 600)
├── src/
│   ├── __init__.py
│   ├── server.py            # MCP server entry point (stdio transport)
│   ├── auth/
│   │   └── oauth.py         # OAuth2 — only talks to accounts.google.com
│   └── tools/
│       ├── __init__.py
│       ├── gmail.py         # 7 tools: search, read, send, reply, labels, modify, delete
│       ├── calendar.py      # 5 tools: list, create, update, delete, get
│       ├── drive.py         # 6 tools: search, read, create, delete, list_folder, share
│       ├── docs.py          # 3 tools: create, read, append
│       ├── sheets.py        # 3 tools: read, write, create
│       ├── slides.py        # 2 tools: create, read
│       ├── forms.py         # 4 tools: create, get, add_question, get_responses
│       ├── tasks.py         # 5 tools: list_tasklists, list, create, update, delete
│       ├── chat.py          # 4 tools: list_spaces, send_message, list_messages, create_space
│       └── meet.py          # 4 tools: create_space, get_space, end_conference, list_conferences
└── tests/
```

## Key Patterns

### Tool Registration
Each tool module exports:
- `*_TOOLS` — List of `mcp.types.Tool` objects with name, description, inputSchema
- `handle_*` — Async handler function that routes by tool name

### Server (`src/server.py`)
- Collects all tools into `ALL_TOOLS` list
- Maps tool names to handlers via `HANDLERS` dict
- Uses MCP stdio transport (`mcp.server.stdio.stdio_server`)
- Error handling wraps all tool calls with try/except

### Auth (`src/auth/oauth.py`)
- Reads `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` from environment
- Token stored at `.credentials/token.json` with `chmod 600`
- Auto-refreshes expired tokens; prompts browser login if no token exists
- `get_service(name, version)` returns authenticated Google API client

### OAuth Scopes
- `gmail.modify` — Read/write/send Gmail
- `calendar` — Full calendar access
- `drive` — Full Drive access
- `documents` — Full Docs access
- `spreadsheets` — Full Sheets access
- `presentations` — Full Slides access
- `forms.body` — Create and edit forms
- `forms.responses.readonly` — Read form responses
- `tasks` — Full Tasks access
- `chat.spaces`, `chat.messages` — Chat spaces and messaging
- `meetings.space.created` — Create and manage Meet spaces

## Dependencies (pinned)

| Package | Version | Purpose |
|---------|---------|---------|
| `mcp` | >=1.0.0 | Anthropic MCP SDK |
| `google-api-python-client` | 2.114.0 | Official Google API client |
| `google-auth-oauthlib` | 1.2.0 | OAuth2 flow |
| `google-auth` | 2.27.0 | Credentials management |
| `python-dotenv` | 1.0.1 | .env file loading |

## Running

```bash
# Direct
python3 -m src.server

# Via entrypoint
google-mcp
```

## Compatible Agents

Claude Code, Kiro, Cursor, Windsurf, Codex, GitHub Copilot, and any MCP-compatible AI agent.

## Development Guidelines

- Keep total code under 500 lines
- No third-party API wrappers — only official `google-api-python-client`
- Each new service gets its own file in `src/tools/`
- All tools must be async handlers with signature: `async def handle_*(name: str, args: dict) -> str`
- Pin dependency versions in `pyproject.toml`
- Never commit `.env` or `.credentials/`
