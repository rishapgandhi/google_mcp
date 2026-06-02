"""Google Calendar tools — list, create, update, delete events."""

from mcp.types import Tool
from src.auth.oauth import get_service

CALENDAR_TOOLS = [
    Tool(name="calendar_list_events", description="List upcoming calendar events", inputSchema={"type": "object", "properties": {"max_results": {"type": "integer", "default": 10}, "calendar_id": {"type": "string", "default": "primary"}}, "required": []}),
    Tool(name="calendar_create_event", description="Create a calendar event (sends invite emails to attendees)", inputSchema={"type": "object", "properties": {"summary": {"type": "string"}, "start": {"type": "string", "description": "ISO datetime (e.g. 2025-01-15T09:00:00+05:30)"}, "end": {"type": "string", "description": "ISO datetime"}, "description": {"type": "string", "default": ""}, "attendees": {"type": "string", "description": "Comma-separated emails", "default": ""}}, "required": ["summary", "start", "end"]}),
    Tool(name="calendar_update_event", description="Update an existing calendar event", inputSchema={"type": "object", "properties": {"event_id": {"type": "string"}, "summary": {"type": "string", "default": ""}, "start": {"type": "string", "default": ""}, "end": {"type": "string", "default": ""}, "description": {"type": "string", "default": ""}, "attendees": {"type": "string", "default": ""}}, "required": ["event_id"]}),
    Tool(name="calendar_delete_event", description="Delete a calendar event", inputSchema={"type": "object", "properties": {"event_id": {"type": "string"}}, "required": ["event_id"]}),
    Tool(name="calendar_get_event", description="Get full details of a calendar event including attendees", inputSchema={"type": "object", "properties": {"event_id": {"type": "string"}}, "required": ["event_id"]}),
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

    elif name == "calendar_update_event":
        body = {}
        if args.get("summary"):
            body["summary"] = args["summary"]
        if args.get("start"):
            body["start"] = {"dateTime": args["start"]}
        if args.get("end"):
            body["end"] = {"dateTime": args["end"]}
        if args.get("description"):
            body["description"] = args["description"]
        if args.get("attendees"):
            body["attendees"] = [{"email": e.strip()} for e in args["attendees"].split(",")]
        if not body:
            return "No fields to update."
        updated = svc.events().patch(calendarId="primary", eventId=args["event_id"], body=body, sendUpdates="all").execute()
        return f"Event updated: {updated.get('htmlLink')}"

    elif name == "calendar_delete_event":
        svc.events().delete(calendarId="primary", eventId=args["event_id"], sendUpdates="all").execute()
        return f"Event {args['event_id']} deleted"

    elif name == "calendar_get_event":
        e = svc.events().get(calendarId="primary", eventId=args["event_id"]).execute()
        attendees = "\n".join(f"  {a['email']} ({a.get('responseStatus','')})" for a in e.get("attendees", []))
        return (
            f"Summary: {e.get('summary','')}\n"
            f"Start: {e['start'].get('dateTime', e['start'].get('date'))}\n"
            f"End: {e['end'].get('dateTime', e['end'].get('date'))}\n"
            f"Description: {e.get('description','')}\n"
            f"Status: {e.get('status','')}\n"
            f"Link: {e.get('htmlLink','')}\n"
            f"Attendees:\n{attendees or '  (none)'}"
        )

    return "Unknown calendar tool"
