"""Google Forms tools — create, read, add questions, get responses."""

import json

from mcp.types import Tool
from src.auth.oauth import get_service

FORMS_TOOLS = [
    Tool(
        name="forms_create",
        description="Create a new Google Form with a title and optional description",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Form title"},
                "description": {"type": "string", "default": "", "description": "Form description"},
            },
            "required": ["title"],
        },
    ),
    Tool(
        name="forms_get",
        description="Get a Google Form's content, questions, and metadata by form ID",
        inputSchema={
            "type": "object",
            "properties": {
                "form_id": {"type": "string", "description": "The form ID (from the form URL)"},
            },
            "required": ["form_id"],
        },
    ),
    Tool(
        name="forms_add_question",
        description="Add a question to a Google Form. Supported types: short_answer, paragraph, multiple_choice, checkbox, dropdown",
        inputSchema={
            "type": "object",
            "properties": {
                "form_id": {"type": "string", "description": "The form ID"},
                "title": {"type": "string", "description": "Question title/text"},
                "question_type": {
                    "type": "string",
                    "enum": ["short_answer", "paragraph", "multiple_choice", "checkbox", "dropdown"],
                    "description": "Type of question",
                },
                "required": {"type": "boolean", "default": False, "description": "Whether the question is required"},
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                    "description": "Answer options (for multiple_choice, checkbox, dropdown)",
                },
                "index": {"type": "integer", "default": 0, "description": "Position to insert (0 = beginning)"},
            },
            "required": ["form_id", "title", "question_type"],
        },
    ),
    Tool(
        name="forms_get_responses",
        description="Get all responses for a Google Form",
        inputSchema={
            "type": "object",
            "properties": {
                "form_id": {"type": "string", "description": "The form ID"},
            },
            "required": ["form_id"],
        },
    ),
]


def _build_question(question_type: str, options: list) -> dict:
    """Build the question object based on type."""
    if question_type == "short_answer":
        return {"textQuestion": {"paragraph": False}}
    elif question_type == "paragraph":
        return {"textQuestion": {"paragraph": True}}
    elif question_type in ("multiple_choice", "checkbox", "dropdown"):
        type_map = {
            "multiple_choice": "RADIO",
            "checkbox": "CHECKBOX",
            "dropdown": "DROP_DOWN",
        }
        choice_question = {
            "type": type_map[question_type],
            "options": [{"value": opt} for opt in options],
        }
        return {"choiceQuestion": choice_question}
    else:
        return {"textQuestion": {"paragraph": False}}


async def handle_forms(name: str, args: dict) -> str:
    svc = get_service("forms", "v1")

    if name == "forms_create":
        form = {"info": {"title": args["title"]}}
        result = svc.forms().create(body=form).execute()
        form_id = result["formId"]

        # Add description if provided
        if args.get("description"):
            update = {
                "requests": [
                    {
                        "updateFormInfo": {
                            "info": {"description": args["description"]},
                            "updateMask": "description",
                        }
                    }
                ]
            }
            svc.forms().batchUpdate(formId=form_id, body=update).execute()

        return (
            f"Form created: https://docs.google.com/forms/d/{form_id}/edit\n"
            f"Form ID: {form_id}\n"
            f"Responder URL: https://docs.google.com/forms/d/{form_id}/viewform"
        )

    elif name == "forms_get":
        form = svc.forms().get(formId=args["form_id"]).execute()
        info = form.get("info", {})
        items = form.get("items", [])

        output = [
            f"Title: {info.get('title', '')}",
            f"Description: {info.get('description', '')}",
            f"Form ID: {form.get('formId', '')}",
            f"Responder URI: {form.get('responderUri', '')}",
            f"Questions: {len(items)}",
            "",
        ]

        for i, item in enumerate(items, 1):
            title = item.get("title", "(untitled)")
            q = item.get("questionItem", {}).get("question", {})
            required = q.get("required", False)
            req_str = " [required]" if required else ""

            # Determine question type
            if "textQuestion" in q:
                qtype = "paragraph" if q["textQuestion"].get("paragraph") else "short_answer"
            elif "choiceQuestion" in q:
                cq = q["choiceQuestion"]
                type_map = {"RADIO": "multiple_choice", "CHECKBOX": "checkbox", "DROP_DOWN": "dropdown"}
                qtype = type_map.get(cq.get("type", ""), "unknown")
                opts = [o.get("value", "") for o in cq.get("options", [])]
                output.append(f"  Q{i}: {title}{req_str} ({qtype}) — Options: {', '.join(opts)}")
                continue
            else:
                qtype = "unknown"

            output.append(f"  Q{i}: {title}{req_str} ({qtype})")

        return "\n".join(output)

    elif name == "forms_add_question":
        question = _build_question(args["question_type"], args.get("options", []))
        question["required"] = args.get("required", False)

        update = {
            "requests": [
                {
                    "createItem": {
                        "item": {
                            "title": args["title"],
                            "questionItem": {"question": question},
                        },
                        "location": {"index": args.get("index", 0)},
                    }
                }
            ]
        }

        svc.forms().batchUpdate(formId=args["form_id"], body=update).execute()
        return f"Question '{args['title']}' added to form {args['form_id']} at index {args.get('index', 0)}"

    elif name == "forms_get_responses":
        result = svc.forms().responses().list(formId=args["form_id"]).execute()
        responses = result.get("responses", [])

        if not responses:
            return "No responses yet."

        # Get form to map question IDs to titles
        form = svc.forms().get(formId=args["form_id"]).execute()
        q_map = {}
        for item in form.get("items", []):
            qi = item.get("questionItem", {})
            qid = qi.get("question", {}).get("questionId", "")
            if qid:
                q_map[qid] = item.get("title", "Untitled")

        output = [f"Total responses: {len(responses)}", ""]
        for idx, resp in enumerate(responses, 1):
            output.append(f"--- Response {idx} ({resp.get('createTime', '')}) ---")
            answers = resp.get("answers", {})
            for qid, answer in answers.items():
                q_title = q_map.get(qid, qid)
                text_answers = answer.get("textAnswers", {}).get("answers", [])
                values = [a.get("value", "") for a in text_answers]
                output.append(f"  {q_title}: {', '.join(values)}")
            output.append("")

        return "\n".join(output)

    return "Unknown forms tool"
