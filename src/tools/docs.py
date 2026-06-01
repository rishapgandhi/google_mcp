"""Google Docs tools — create, read, edit."""

from mcp.types import Tool
from src.auth.oauth import get_service

DOCS_TOOLS = [
    Tool(name="docs_create", description="Create a new Google Doc", inputSchema={"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string", "default": ""}}, "required": ["title"]}),
    Tool(name="docs_read", description="Read content of a Google Doc by ID", inputSchema={"type": "object", "properties": {"document_id": {"type": "string"}}, "required": ["document_id"]}),
    Tool(name="docs_append", description="Append text to a Google Doc", inputSchema={"type": "object", "properties": {"document_id": {"type": "string"}, "text": {"type": "string"}}, "required": ["document_id", "text"]}),
]


async def handle_docs(name: str, args: dict) -> str:
    svc = get_service("docs", "v1")

    if name == "docs_create":
        doc = svc.documents().create(body={"title": args["title"]}).execute()
        doc_id = doc["documentId"]
        if args.get("content"):
            svc.documents().batchUpdate(documentId=doc_id, body={
                "requests": [{"insertText": {"location": {"index": 1}, "text": args["content"]}}]
            }).execute()
        return f"Doc created: https://docs.google.com/document/d/{doc_id}/edit"

    elif name == "docs_read":
        doc = svc.documents().get(documentId=args["document_id"]).execute()
        text = ""
        for element in doc.get("body", {}).get("content", []):
            if "paragraph" in element:
                for elem in element["paragraph"].get("elements", []):
                    text += elem.get("textRun", {}).get("content", "")
        return f"Title: {doc.get('title', '')}\n\n{text}"

    elif name == "docs_append":
        doc = svc.documents().get(documentId=args["document_id"]).execute()
        end_index = doc["body"]["content"][-1]["endIndex"] - 1
        svc.documents().batchUpdate(documentId=args["document_id"], body={
            "requests": [{"insertText": {"location": {"index": end_index}, "text": args["text"]}}]
        }).execute()
        return f"Text appended to doc {args['document_id']}"

    return "Unknown docs tool"
