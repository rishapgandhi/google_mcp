# Google Workspace MCP Server

Minimal, secure, self-hosted MCP server for Google Workspace. Zero third-party wrappers — only official Google libraries.

## Services & Tools

| Service | Tools |
|---------|-------|
| Gmail | `gmail_search`, `gmail_read`, `gmail_send` |
| Calendar | `calendar_list_events`, `calendar_create_event` |
| Drive | `drive_search`, `drive_read_file`, `drive_create_file` |
| Docs | `docs_create`, `docs_read`, `docs_append` |
| Sheets | `sheets_read`, `sheets_write`, `sheets_create` |
| Slides | `slides_create`, `slides_read` |

## Security

- **Only official Google libraries** — no third-party MCP wrappers
- **Zero external calls** — data flows only to `googleapis.com`
- **Pinned dependencies** — no surprise updates
- **Credentials stored locally** with `chmod 600`
- **Fully auditable** — ~300 lines of code total

## Setup

### 1. Google Cloud Console (Free)

1. Go to https://console.cloud.google.com/
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
cd /var/www/html/mcp_server/google_mcp
cp .env.example .env
# Edit .env with your Client ID and Secret

pip install -e .
# OR with uv:
uv pip install -e .
```

### 3. First-time Auth

```bash
python -m src.server
# Opens browser for Google OAuth consent on first run
# After consent, token is stored in .credentials/token.json
```

### 4. Configure in Kiro CLI

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "google_workspace": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/var/www/html/mcp_server/google_mcp",
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "your-client-id",
        "GOOGLE_OAUTH_CLIENT_SECRET": "your-secret"
      }
    }
  }
}
```

## Dependencies (all official)

| Package | Publisher | Purpose |
|---------|-----------|---------|
| `mcp` | Anthropic | MCP protocol SDK |
| `google-api-python-client` | Google | API client |
| `google-auth-oauthlib` | Google | OAuth2 flow |
| `google-auth` | Google | Credentials |
| `python-dotenv` | theskumar | .env loading |

## File Structure

```
google_mcp/
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
└── src/
    ├── server.py          # MCP server entry point
    ├── auth/
    │   └── oauth.py       # OAuth2 (official Google libs only)
    └── tools/
        ├── gmail.py       # Gmail search, read, send
        ├── calendar.py    # Events list, create
        ├── drive.py       # Search, read, create files
        ├── docs.py        # Create, read, append
        ├── sheets.py      # Read, write, create
        └── slides.py      # Create, read
```
