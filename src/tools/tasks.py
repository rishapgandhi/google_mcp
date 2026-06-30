"""Google Tasks tools — list task lists, list/create/update/delete tasks."""

from mcp.types import Tool
from src.auth.oauth import get_service

TASKS_TOOLS = [
    Tool(
        name="tasks_list_tasklists",
        description="List all Google Tasks task lists",
        inputSchema={
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "default": 20, "description": "Max task lists to return"},
            },
            "required": [],
        },
    ),
    Tool(
        name="tasks_list",
        description="List tasks in a task list",
        inputSchema={
            "type": "object",
            "properties": {
                "tasklist_id": {"type": "string", "default": "@default", "description": "Task list ID (use @default for primary)"},
                "max_results": {"type": "integer", "default": 20, "description": "Max tasks to return"},
                "show_completed": {"type": "boolean", "default": True, "description": "Include completed tasks"},
            },
            "required": [],
        },
    ),
    Tool(
        name="tasks_create",
        description="Create a new task in a task list",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title"},
                "notes": {"type": "string", "default": "", "description": "Task notes/details"},
                "due": {"type": "string", "default": "", "description": "Due date (RFC 3339, e.g. 2025-12-31T00:00:00Z)"},
                "tasklist_id": {"type": "string", "default": "@default", "description": "Task list ID"},
            },
            "required": ["title"],
        },
    ),
    Tool(
        name="tasks_update",
        description="Update a task (title, notes, due date, or mark as completed)",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
                "tasklist_id": {"type": "string", "default": "@default", "description": "Task list ID"},
                "title": {"type": "string", "default": "", "description": "New title"},
                "notes": {"type": "string", "default": "", "description": "New notes"},
                "due": {"type": "string", "default": "", "description": "New due date (RFC 3339)"},
                "completed": {"type": "boolean", "default": False, "description": "Mark as completed"},
            },
            "required": ["task_id"],
        },
    ),
    Tool(
        name="tasks_delete",
        description="Delete a task from a task list",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
                "tasklist_id": {"type": "string", "default": "@default", "description": "Task list ID"},
            },
            "required": ["task_id"],
        },
    ),
]


async def handle_tasks(name: str, args: dict) -> str:
    svc = get_service("tasks", "v1")

    if name == "tasks_list_tasklists":
        result = svc.tasklists().list(maxResults=args.get("max_results", 20)).execute()
        items = result.get("items", [])
        if not items:
            return "No task lists found."
        return "\n".join(
            f"ID: {tl['id']} | {tl['title']} | Updated: {tl.get('updated', '')}"
            for tl in items
        )

    elif name == "tasks_list":
        tasklist_id = args.get("tasklist_id", "@default")
        result = svc.tasks().list(
            tasklist=tasklist_id,
            maxResults=args.get("max_results", 20),
            showCompleted=args.get("show_completed", True),
        ).execute()
        items = result.get("items", [])
        if not items:
            return "No tasks found."
        output = []
        for t in items:
            status = "✓" if t.get("status") == "completed" else "○"
            due = f" | Due: {t['due'][:10]}" if t.get("due") else ""
            notes = f" | Notes: {t['notes'][:50]}" if t.get("notes") else ""
            output.append(f"{status} {t.get('title', '(untitled)')} | ID: {t['id']}{due}{notes}")
        return "\n".join(output)

    elif name == "tasks_create":
        tasklist_id = args.get("tasklist_id", "@default")
        task = {"title": args["title"]}
        if args.get("notes"):
            task["notes"] = args["notes"]
        if args.get("due"):
            task["due"] = args["due"]
        created = svc.tasks().insert(tasklist=tasklist_id, body=task).execute()
        return f"Task created: {created['title']} | ID: {created['id']}"

    elif name == "tasks_update":
        tasklist_id = args.get("tasklist_id", "@default")
        task = svc.tasks().get(tasklist=tasklist_id, task=args["task_id"]).execute()
        if args.get("title"):
            task["title"] = args["title"]
        if args.get("notes"):
            task["notes"] = args["notes"]
        if args.get("due"):
            task["due"] = args["due"]
        if args.get("completed"):
            from datetime import datetime, timezone
            task["status"] = "completed"
            task["completed"] = datetime.now(timezone.utc).isoformat()
        updated = svc.tasks().update(tasklist=tasklist_id, task=args["task_id"], body=task).execute()
        return f"Task updated: {updated['title']} | Status: {updated.get('status', '')}"

    elif name == "tasks_delete":
        tasklist_id = args.get("tasklist_id", "@default")
        svc.tasks().delete(tasklist=tasklist_id, task=args["task_id"]).execute()
        return f"Task {args['task_id']} deleted"

    return "Unknown tasks tool"
