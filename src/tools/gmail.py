"""Gmail tools — search, read, send, reply, list labels, delete."""

import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

from mcp.types import Tool
from src.auth.oauth import get_service

GMAIL_TOOLS = [
    Tool(name="gmail_search", description="Search emails using Gmail query syntax (e.g. 'from:x subject:y is:unread')", inputSchema={"type": "object", "properties": {"query": {"type": "string", "description": "Gmail search query"}, "max_results": {"type": "integer", "default": 10}}, "required": ["query"]}),
    Tool(name="gmail_read", description="Read a specific email by message ID", inputSchema={"type": "object", "properties": {"message_id": {"type": "string"}}, "required": ["message_id"]}),
    Tool(name="gmail_send", description="Send an email (supports cc, bcc)", inputSchema={"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}, "cc": {"type": "string", "default": ""}, "bcc": {"type": "string", "default": ""}}, "required": ["to", "subject", "body"]}),
    Tool(name="gmail_reply", description="Reply to an email thread", inputSchema={"type": "object", "properties": {"message_id": {"type": "string"}, "body": {"type": "string"}}, "required": ["message_id", "body"]}),
    Tool(name="gmail_list_labels", description="List all Gmail labels", inputSchema={"type": "object", "properties": {}, "required": []}),
    Tool(name="gmail_modify_labels", description="Add or remove labels from a message (e.g. mark read/unread, archive)", inputSchema={"type": "object", "properties": {"message_id": {"type": "string"}, "add_labels": {"type": "string", "description": "Comma-separated label IDs to add", "default": ""}, "remove_labels": {"type": "string", "description": "Comma-separated label IDs to remove", "default": ""}}, "required": ["message_id"]}),
    Tool(name="gmail_delete", description="Trash a Gmail message", inputSchema={"type": "object", "properties": {"message_id": {"type": "string"}}, "required": ["message_id"]}),
]


async def handle_gmail(name: str, args: dict) -> str:
    svc = get_service("gmail", "v1")

    if name == "gmail_search":
        results = svc.users().messages().list(userId="me", q=args["query"], maxResults=args.get("max_results", 10)).execute()
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
        parts = msg.get("payload", {}).get("parts", [])
        body = ""
        if parts:
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode()
                    break
        elif msg.get("payload", {}).get("body", {}).get("data"):
            body = base64.urlsafe_b64decode(msg["payload"]["body"]["data"]).decode()
        return f"From: {headers.get('From', '')}\nTo: {headers.get('To', '')}\nSubject: {headers.get('Subject', '')}\nDate: {headers.get('Date', '')}\nThread ID: {msg.get('threadId','')}\n\n{body}"

    elif name == "gmail_send":
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

    elif name == "gmail_reply":
        # Get original message for thread ID and headers
        orig = svc.users().messages().get(userId="me", id=args["message_id"], format="metadata", metadataHeaders=["From", "Subject", "Message-ID"]).execute()
        headers = {h["name"]: h["value"] for h in orig.get("payload", {}).get("headers", [])}
        thread_id = orig.get("threadId", "")
        subject = headers.get("Subject", "")
        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"
        message = MIMEText(args["body"])
        message["to"] = headers.get("From", "")
        message["subject"] = subject
        message["In-Reply-To"] = headers.get("Message-ID", "")
        message["References"] = headers.get("Message-ID", "")
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent = svc.users().messages().send(userId="me", body={"raw": raw, "threadId": thread_id}).execute()
        return f"Reply sent. Message ID: {sent['id']}"

    elif name == "gmail_list_labels":
        results = svc.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        return "\n".join(f"ID: {l['id']} | {l['name']}" for l in labels)

    elif name == "gmail_modify_labels":
        body = {}
        if args.get("add_labels"):
            body["addLabelIds"] = [l.strip() for l in args["add_labels"].split(",")]
        if args.get("remove_labels"):
            body["removeLabelIds"] = [l.strip() for l in args["remove_labels"].split(",")]
        svc.users().messages().modify(userId="me", id=args["message_id"], body=body).execute()
        return f"Labels modified on {args['message_id']}"

    elif name == "gmail_delete":
        svc.users().messages().trash(userId="me", id=args["message_id"]).execute()
        return f"Message {args['message_id']} moved to trash"

    return "Unknown gmail tool"
