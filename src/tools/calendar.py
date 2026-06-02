"""Google Calendar tools — list events, create events."""

from mcp.types import Tool
from src.auth.oauth import get_service

CALENDAR_TOOLS = [
    Tool(name="calendar_list_events", description="List upcoming calendar events", inputSchema={"type": "object", "properties": {"max_results": {"type": "integer", "default": 10}, "calendar_id": {"type": "string", "default": "primary"}}, "required": []}),
    Tool(name="calendar_create_event", description="Create a calendar event", inputSchema={"type": "object", "properties": {"summary": {"type": "string"}, "start": {"type": "string", "description": "ISO datetime (e.g. 2025-01-15T09:00:00+05:30)"}, "end": {"type": "string", "description": "ISO datetime"}, "description": {"type": "string", "default": ""}, "attendees": {"type": "string", "description": "Comma-separated emails", "default": ""}}, "required": ["summary", "start", "end"]}),
]


async def handle_calendar(name: str, args: dict) -> str:
    svc = get_service("calendar", "v3")

    if name == "calendar_list_events":
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        result = svc.events().list(
            calendarId=args.get("calendar_id", "primary"),
            timeMin=now, maxResults=args.get("max_results", 10),
            singleEvents=True, orderBy="startTime"
        ).execute()
        events = result.get("items", [])
        if not events:
            return "No upcoming events."
        output = []
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date"))
            output.append(f"{start} | {e.get('summary', '(No title)')} | ID: {e['id']}")
        return "\n".join(output)

    elif name == "calendar_create_event":
        event = {
            "summary": args["summary"],
            "start": {"dateTime": args["start"]},
            "end": {"dateTime": args["end"]},
        }
        if args.get("description"):
            event["description"] = args["description"]
        if args.get("attendees"):
            event["attendees"] = [{"email": e.strip()} for e in args["attendees"].split(",")]
        created = svc.events().insert(calendarId="primary", body=event, sendUpdates="all").execute()
        return f"Event created: {created.get('htmlLink')}"

    return "Unknown calendar tool"
