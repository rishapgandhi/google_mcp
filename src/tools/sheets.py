"""Google Sheets tools — read, write."""

from mcp.types import Tool
from src.auth.oauth import get_service

SHEETS_TOOLS = [
    Tool(name="sheets_read", description="Read values from a Google Sheet range", inputSchema={"type": "object", "properties": {"spreadsheet_id": {"type": "string"}, "range": {"type": "string", "description": "A1 notation (e.g. Sheet1!A1:D10)"}}, "required": ["spreadsheet_id", "range"]}),
    Tool(name="sheets_write", description="Write values to a Google Sheet range", inputSchema={"type": "object", "properties": {"spreadsheet_id": {"type": "string"}, "range": {"type": "string"}, "values": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}, "description": "2D array of values"}}, "required": ["spreadsheet_id", "range", "values"]}),
    Tool(name="sheets_create", description="Create a new Google Spreadsheet", inputSchema={"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}),
]


async def handle_sheets(name: str, args: dict) -> str:
    svc = get_service("sheets", "v4")

    if name == "sheets_read":
        result = svc.spreadsheets().values().get(
            spreadsheetId=args["spreadsheet_id"], range=args["range"]
        ).execute()
        values = result.get("values", [])
        if not values:
            return "No data found."
        return "\n".join(" | ".join(row) for row in values)

    elif name == "sheets_write":
        svc.spreadsheets().values().update(
            spreadsheetId=args["spreadsheet_id"], range=args["range"],
            valueInputOption="USER_ENTERED", body={"values": args["values"]}
        ).execute()
        return f"Written to {args['range']}"

    elif name == "sheets_create":
        sheet = svc.spreadsheets().create(body={"properties": {"title": args["title"]}}).execute()
        return f"Spreadsheet created: https://docs.google.com/spreadsheets/d/{sheet['spreadsheetId']}/edit"

    return "Unknown sheets tool"
