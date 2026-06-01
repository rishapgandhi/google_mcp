"""Google Workspace MCP Server — minimal, secure, self-hosted."""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

from src.tools.gmail import GMAIL_TOOLS, handle_gmail
from src.tools.calendar import CALENDAR_TOOLS, handle_calendar
from src.tools.drive import DRIVE_TOOLS, handle_drive
from src.tools.docs import DOCS_TOOLS, handle_docs
from src.tools.sheets import SHEETS_TOOLS, handle_sheets
from src.tools.slides import SLIDES_TOOLS, handle_slides

app = Server("google-mcp")

ALL_TOOLS = GMAIL_TOOLS + CALENDAR_TOOLS + DRIVE_TOOLS + DOCS_TOOLS + SHEETS_TOOLS + SLIDES_TOOLS

HANDLERS = {
    **{t.name: handle_gmail for t in GMAIL_TOOLS},
    **{t.name: handle_calendar for t in CALENDAR_TOOLS},
    **{t.name: handle_drive for t in DRIVE_TOOLS},
    **{t.name: handle_docs for t in DOCS_TOOLS},
    **{t.name: handle_sheets for t in SHEETS_TOOLS},
    **{t.name: handle_slides for t in SLIDES_TOOLS},
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    return ALL_TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = HANDLERS.get(name)
    if not handler:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    try:
        result = await handler(name, arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]


async def run():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
