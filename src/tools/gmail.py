"""Gmail tools — search, read, send."""

import json
from mcp.types import Tool
from src.auth.oauth import get_service

GMAIL_TOOLS = [
    Tool(name="gmail_search", description="Search emails using Gmail query syntax (e.g. 'from:x subject:y is:unread')", inputSchema={"type": "object", "properties": {"query": {"type": "string", "description": "Gmail search query"}, "max_results": {"type": "integer", "default": 10}}, "required": ["query"]}),
    Tool(name="gmail_read", description="Read a specific email by message ID", inputSchema={"type": "object", "properties": {"message_id": {"type": "string"}}, "required": ["message_id"]}),
    Tool(name="gmail_send", description="Send an email", inputSchema={"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}, "cc": {"type": "string", "default": ""}, "bcc": {"type": "string", "default": ""}}, "required": ["to", "subject", "body"]}),
]


async def handle_gmail(name: str, args: dict) -> str:
    svc = get_service("gmail", "v1")

    if name == "gmail_search":
        results = svc.users().messages().list(
            userId="me", q=args["query"], maxResults=args.get("max_results", 10)
        ).execute()
        messages = results.get("messages", [])
        if not messages:
            return "No messages found."
        output = []
        for msg in messages:
            detail = svc.users().messages().get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["From", "Subject", "Date"]).execute()
            headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
            output.append(f"ID: {msg['id']} | From: {headers.get('From', '')} | Subject: {headers.get('Subject', '')} | Date: {headers.get('Date', '')}")
        return "\n".join(output)

    elif name == "gmail_read":
        msg = svc.users().messages().get(userId="me", id=args["message_id"], format="full").execute()
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        # Extract body
        import base64
        parts = msg.get("payload", {}).get("parts", [])
        body = ""
        if parts:
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode()
                    break
        elif msg.get("payload", {}).get("body", {}).get("data"):
            body = base64.urlsafe_b64decode(msg["payload"]["body"]["data"]).decode()
        return f"From: {headers.get('From', '')}\nTo: {headers.get('To', '')}\nSubject: {headers.get('Subject', '')}\nDate: {headers.get('Date', '')}\n\n{body}"

    elif name == "gmail_send":
        import base64
        from email.mime.text import MIMEText
        message = MIMEText(args["body"])
        message["to"] = args["to"]
        message["subject"] = args["subject"]
        if args.get("cc"):
            message["cc"] = args["cc"]
        if args.get("bcc"):
            message["bcc"] = args["bcc"]
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent = svc.users().messages().send(userId="me", body={"raw": raw}).execute()
        return f"Email sent. Message ID: {sent['id']}"

    return "Unknown gmail tool"
