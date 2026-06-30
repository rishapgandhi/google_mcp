"""Google Chat tools — list spaces, send/list messages, create space."""

from mcp.types import Tool
from src.auth.oauth import get_service

CHAT_TOOLS = [
    Tool(
        name="chat_list_spaces",
        description="List Google Chat spaces (rooms, DMs, group chats) you are a member of",
        inputSchema={
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "default": 20, "description": "Max spaces to return"},
            },
            "required": [],
        },
    ),
    Tool(
        name="chat_send_message",
        description="Send a text message to a Google Chat space",
        inputSchema={
            "type": "object",
            "properties": {
                "space_name": {"type": "string", "description": "Space resource name (e.g. spaces/AAAA)"},
                "text": {"type": "string", "description": "Message text"},
            },
            "required": ["space_name", "text"],
        },
    ),
    Tool(
        name="chat_list_messages",
        description="List recent messages in a Google Chat space",
        inputSchema={
            "type": "object",
            "properties": {
                "space_name": {"type": "string", "description": "Space resource name (e.g. spaces/AAAA)"},
                "max_results": {"type": "integer", "default": 10, "description": "Max messages to return"},
            },
            "required": ["space_name"],
        },
    ),
    Tool(
        name="chat_create_space",
        description="Create a new Google Chat space (named space)",
        inputSchema={
            "type": "object",
            "properties": {
                "display_name": {"type": "string", "description": "Display name for the space"},
                "space_type": {"type": "string", "enum": ["SPACE", "GROUP_CHAT"], "default": "SPACE", "description": "Type of space"},
            },
            "required": ["display_name"],
        },
    ),
]


async def handle_chat(name: str, args: dict) -> str:
    svc = get_service("chat", "v1")

    if name == "chat_list_spaces":
        result = svc.spaces().list(pageSize=args.get("max_results", 20)).execute()
        spaces = result.get("spaces", [])
        if not spaces:
            return "No spaces found."
        output = []
        for s in spaces:
            stype = s.get("spaceType", s.get("type", ""))
            output.append(f"{s['name']} | {s.get('displayName', '(DM)')} | Type: {stype}")
        return "\n".join(output)

    elif name == "chat_send_message":
        message = {"text": args["text"]}
        result = svc.spaces().messages().create(
            parent=args["space_name"], body=message
        ).execute()
        return f"Message sent: {result.get('name', '')} | Created: {result.get('createTime', '')}"

    elif name == "chat_list_messages":
        result = svc.spaces().messages().list(
            parent=args["space_name"],
            pageSize=args.get("max_results", 10),
            orderBy="createTime desc",
        ).execute()
        messages = result.get("messages", [])
        if not messages:
            return "No messages found."
        output = []
        for msg in messages:
            sender = msg.get("sender", {}).get("displayName", msg.get("sender", {}).get("name", "Unknown"))
            text = msg.get("text", "(no text)")[:200]
            time = msg.get("createTime", "")
            output.append(f"[{time}] {sender}: {text}")
        return "\n".join(output)

    elif name == "chat_create_space":
        space = {
            "displayName": args["display_name"],
            "spaceType": args.get("space_type", "SPACE"),
        }
        result = svc.spaces().create(body=space).execute()
        return f"Space created: {result['name']} | {result.get('displayName', '')}"

    return "Unknown chat tool"
