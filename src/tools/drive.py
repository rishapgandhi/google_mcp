"""Google Drive tools — search, upload, download."""

from mcp.types import Tool
from src.auth.oauth import get_service

DRIVE_TOOLS = [
    Tool(name="drive_search", description="Search files in Google Drive", inputSchema={"type": "object", "properties": {"query": {"type": "string", "description": "Drive search query (e.g. name contains 'report')"}, "max_results": {"type": "integer", "default": 10}}, "required": ["query"]}),
    Tool(name="drive_read_file", description="Read content of a Google Drive file (text-based)", inputSchema={"type": "object", "properties": {"file_id": {"type": "string"}}, "required": ["file_id"]}),
    Tool(name="drive_create_file", description="Create a text file in Google Drive", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "content": {"type": "string"}, "mime_type": {"type": "string", "default": "text/plain"}, "folder_id": {"type": "string", "default": ""}}, "required": ["name", "content"]}),
]


async def handle_drive(name: str, args: dict) -> str:
    svc = get_service("drive", "v3")

    if name == "drive_search":
        result = svc.files().list(
            q=args["query"], pageSize=args.get("max_results", 10),
            fields="files(id,name,mimeType,modifiedTime)"
        ).execute()
        files = result.get("files", [])
        if not files:
            return "No files found."
        return "\n".join(f"ID: {f['id']} | {f['name']} | {f['mimeType']} | {f.get('modifiedTime', '')}" for f in files)

    elif name == "drive_read_file":
        meta = svc.files().get(fileId=args["file_id"], fields="mimeType,name").execute()
        mime = meta["mimeType"]
        if mime.startswith("application/vnd.google-apps"):
            export_mime = "text/plain"
            if "document" in mime:
                export_mime = "text/plain"
            elif "spreadsheet" in mime:
                export_mime = "text/csv"
            elif "presentation" in mime:
                export_mime = "text/plain"
            content = svc.files().export(fileId=args["file_id"], mimeType=export_mime).execute()
            return content.decode() if isinstance(content, bytes) else content
        else:
            content = svc.files().get_media(fileId=args["file_id"]).execute()
            return content.decode(errors="replace") if isinstance(content, bytes) else str(content)

    elif name == "drive_create_file":
        from googleapiclient.http import MediaInMemoryUpload
        metadata = {"name": args["name"]}
        if args.get("folder_id"):
            metadata["parents"] = [args["folder_id"]]
        media = MediaInMemoryUpload(args["content"].encode(), mimetype=args.get("mime_type", "text/plain"))
        f = svc.files().create(body=metadata, media_body=media, fields="id,webViewLink").execute()
        return f"File created: {f.get('webViewLink', f['id'])}"

    return "Unknown drive tool"
