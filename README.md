# Google Workspace MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)

**Minimal, secure, self-hosted MCP server for Google Workspace.** Zero third-party wrappers — only official Google libraries. ~300 lines of fully auditable code.

Works with **Claude Code**, **Kiro**, **Cursor**, **Windsurf**, **Codex**, **GitHub Copilot**, and any MCP-compatible AI coding agent.

## Why This Exists

Most Google Workspace MCP servers use third-party wrappers with thousands of lines of code and dozens of dependencies you can't audit. This server:

- **~300 lines total** — you can read every line in 10 minutes
- **Only official Google libraries** — `google-api-python-client`, `google-auth-oauthlib`
- **Zero external network calls** — data flows only to `googleapis.com`
- **Credentials stored locally** with `chmod 600` permissions
- **No telemetry, no analytics, no SaaS dependency**

## Services & Tools (14 tools)

| Service | Tools | Description |
|---------|-------|-------------|
| **Gmail** | `gmail_search`, `gmail_read`, `gmail_send` | Search, read, and send emails |
| **Calendar** | `calendar_list_events`, `calendar_create_event` | List and create calendar events |
| **Drive** | `drive_search`, `drive_read_file`, `drive_create_file` | Search, read, and create files |
| **Docs** | `docs_create`, `docs_read`, `docs_append` | Create, read, and edit documents |
| **Sheets** | `sheets_read`, `sheets_write`, `sheets_create` | Read, write, and create spreadsheets |
| **Slides** | `slides_create`, `slides_read` | Create and read presentations |

## Quick Start

### 1. Google Cloud Console Setup (Free)

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create a new project
3. Go to **APIs & Services → Credentials → Create OAuth Client ID**
   - Application type: **Desktop Application**
   - Note your `Client ID` and `Client Secret`
4. Go to **APIs & Services → Library** and enable:
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Docs API
   - Google Sheets API
   - Google Slides API

### 2. Install

```bash
git clone https://github.com/rishapgandhi/google_mcp.git
cd google_mcp
cp .env.example .env
# Edit .env with your Client ID and Secret

pip install -e .
```

### 3. First-time Authentication

```bash
python3 -m src.server
# Opens browser for Google OAuth consent
# Token saved to .credentials/token.json (chmod 600)
```

### 4. Connect to Your AI Agent

#### Kiro CLI
```json
{
  "mcpServers": {
    "google_workspace": {
      "command": "python3",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/google_mcp",
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "your-client-id",
        "GOOGLE_OAUTH_CLIENT_SECRET": "your-secret"
      }
    }
  }
}
```

#### Claude Code
```bash
claude mcp add google_workspace -- python3 -m src.server --cwd /path/to/google_mcp
```

#### Cursor / Windsurf
Add to `.cursor/mcp.json` or `.windsurf/mcp.json`:
```json
{
  "mcpServers": {
    "google_workspace": {
      "command": "python3",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/google_mcp",
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "your-client-id",
        "GOOGLE_OAUTH_CLIENT_SECRET": "your-secret"
      }
    }
  }
}
```

## Security

| Aspect | Implementation |
|--------|---------------|
| Dependencies | Only 4 official packages, all pinned |
| Network | Only connects to `googleapis.com` |
| Credentials | OAuth tokens stored with `chmod 600` |
| Code | ~300 lines, fully auditable |
| Telemetry | None — zero external reporting |
| Data flow | Your machine → Google APIs (nothing else) |

## Dependencies

| Package | Publisher | Purpose |
|---------|-----------|---------|
| `mcp` | Anthropic | MCP protocol SDK |
| `google-api-python-client` | Google | Official API client |
| `google-auth-oauthlib` | Google | OAuth2 authentication |
| `python-dotenv` | — | .env file loading |

## Project Structure

```
google_mcp/
├── pyproject.toml
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── src/
    ├── server.py          # MCP server (stdio transport)
    ├── auth/
    │   └── oauth.py       # OAuth2 — only talks to accounts.google.com
    └── tools/
        ├── gmail.py       # Search, read, send
        ├── calendar.py    # List events, create event
        ├── drive.py       # Search, read, create files
        ├── docs.py        # Create, read, append
        ├── sheets.py      # Read, write, create
        └── slides.py      # Create, read
```

## Contributing

PRs welcome. Keep it minimal — the goal is a small, auditable codebase.

## License

[MIT](LICENSE) — use commercially, fork, modify, redistribute freely.
