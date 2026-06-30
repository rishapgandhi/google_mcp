"""Google Meet tools — create/get meeting spaces, end conference, list conferences."""

from mcp.types import Tool
from src.auth.oauth import get_service

MEET_TOOLS = [
    Tool(
        name="meet_create_space",
        description="Create a new Google Meet meeting space (generates a meeting link)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="meet_get_space",
        description="Get details about a Google Meet meeting space",
        inputSchema={
            "type": "object",
            "properties": {
                "space_name": {"type": "string", "description": "Space resource name (e.g. spaces/abc-defg-hij)"},
            },
            "required": ["space_name"],
        },
    ),
    Tool(
        name="meet_end_conference",
        description="End an active conference in a Google Meet space",
        inputSchema={
            "type": "object",
            "properties": {
                "space_name": {"type": "string", "description": "Space resource name (e.g. spaces/abc-defg-hij)"},
            },
            "required": ["space_name"],
        },
    ),
    Tool(
        name="meet_list_conferences",
        description="List past conference records from Google Meet",
        inputSchema={
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "default": 10, "description": "Max conferences to return"},
            },
            "required": [],
        },
    ),
]


async def handle_meet(name: str, args: dict) -> str:
    svc = get_service("meet", "v2")

    if name == "meet_create_space":
        result = svc.spaces().create(body={}).execute()
        meeting_uri = result.get("meetingUri", "")
        space_name = result.get("name", "")
        meeting_code = result.get("meetingCode", "")
        return (
            f"Meeting created!\n"
            f"Join URL: {meeting_uri}\n"
            f"Meeting code: {meeting_code}\n"
            f"Space: {space_name}"
        )

    elif name == "meet_get_space":
        result = svc.spaces().get(name=args["space_name"]).execute()
        config = result.get("config", {})
        active = result.get("activeConference", {})
        return (
            f"Space: {result.get('name', '')}\n"
            f"Meeting URI: {result.get('meetingUri', '')}\n"
            f"Meeting Code: {result.get('meetingCode', '')}\n"
            f"Access Type: {config.get('accessType', '')}\n"
            f"Entry Point Access: {config.get('entryPointAccess', '')}\n"
            f"Active Conference: {active.get('conferenceRecord', 'None')}"
        )

    elif name == "meet_end_conference":
        svc.spaces().endActiveConference(
            name=args["space_name"], body={}
        ).execute()
        return f"Active conference ended for {args['space_name']}"

    elif name == "meet_list_conferences":
        result = svc.conferenceRecords().list(
            pageSize=args.get("max_results", 10)
        ).execute()
        records = result.get("conferenceRecords", [])
        if not records:
            return "No conference records found."
        output = []
        for rec in records:
            start = rec.get("startTime", "")
            end = rec.get("endTime", "ongoing")
            space = rec.get("space", "")
            output.append(f"{rec['name']} | Start: {start} | End: {end} | Space: {space}")
        return "\n".join(output)

    return "Unknown meet tool"
