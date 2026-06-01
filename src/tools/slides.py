"""Google Slides tools — create, read."""

from mcp.types import Tool
from src.auth.oauth import get_service

SLIDES_TOOLS = [
    Tool(name="slides_create", description="Create a new Google Slides presentation", inputSchema={"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}),
    Tool(name="slides_read", description="Read content/structure of a Google Slides presentation", inputSchema={"type": "object", "properties": {"presentation_id": {"type": "string"}}, "required": ["presentation_id"]}),
]


async def handle_slides(name: str, args: dict) -> str:
    svc = get_service("slides", "v1")

    if name == "slides_create":
        pres = svc.presentations().create(body={"title": args["title"]}).execute()
        return f"Presentation created: https://docs.google.com/presentation/d/{pres['presentationId']}/edit"

    elif name == "slides_read":
        pres = svc.presentations().get(presentationId=args["presentation_id"]).execute()
        slides = pres.get("slides", [])
        output = [f"Title: {pres.get('title', '')}", f"Slides: {len(slides)}", ""]
        for i, slide in enumerate(slides, 1):
            texts = []
            for element in slide.get("pageElements", []):
                shape = element.get("shape", {})
                tf = shape.get("text", {})
                for te in tf.get("textElements", []):
                    run = te.get("textRun", {})
                    if run.get("content", "").strip():
                        texts.append(run["content"].strip())
            output.append(f"Slide {i}: {' | '.join(texts) if texts else '(empty)'}")
        return "\n".join(output)

    return "Unknown slides tool"
