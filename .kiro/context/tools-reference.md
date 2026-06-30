# Tool Reference — Google Workspace MCP Server

## Total: 26 Tools

---

## Gmail (7 tools) — `src/tools/gmail.py`

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `gmail_search` | Search using Gmail query syntax | `query` |
| `gmail_read` | Read full email by ID | `message_id` |
| `gmail_send` | Send email (cc, bcc support) | `to`, `subject`, `body` |
| `gmail_reply` | Reply to thread (auto Re: prefix) | `message_id`, `body` |
| `gmail_list_labels` | List all labels | — |
| `gmail_modify_labels` | Add/remove labels | `message_id` |
| `gmail_delete` | Trash a message | `message_id` |

**Notes:**
- `gmail_search` uses Gmail query syntax: `from:x subject:y is:unread`
- `gmail_reply` auto-fetches thread ID and sets In-Reply-To headers
- `gmail_modify_labels` takes comma-separated label IDs

---

## Calendar (5 tools) — `src/tools/calendar.py`

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `calendar_list_events` | List upcoming events | — |
| `calendar_create_event` | Create event + send invites | `summary`, `start`, `end` |
| `calendar_update_event` | Patch event fields | `event_id` |
| `calendar_delete_event` | Delete event | `event_id` |
| `calendar_get_event` | Get full event details | `event_id` |

**Notes:**
- Datetime format: ISO 8601 (e.g. `2025-01-15T09:00:00+05:30`)
- `sendUpdates="all"` is set on create/update/delete
- Attendees passed as comma-separated emails

---

## Drive (6 tools) — `src/tools/drive.py`

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `drive_search` | Search files by query | `query` |
| `drive_read_file` | Read file content | `file_id` |
| `drive_create_file` | Create text file | `name`, `content` |
| `drive_delete_file` | Delete file | `file_id` |
| `drive_list_folder` | List folder contents | — |
| `drive_share_file` | Share with user | `file_id`, `email` |

**Notes:**
- `drive_read_file` handles Google Apps files (Docs→text, Sheets→CSV, Slides→text)
- `drive_search` uses Drive query syntax: `name contains 'report'`
- `drive_share_file` roles: `reader`, `commenter`, `writer`

---

## Docs (3 tools) — `src/tools/docs.py`

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `docs_create` | Create new Doc | `title` |
| `docs_read` | Read Doc content | `document_id` |
| `docs_append` | Append text to Doc | `document_id`, `text` |

**Notes:**
- `docs_create` optionally accepts `content` to pre-fill
- `docs_append` inserts at end of document body

---

## Sheets (3 tools) — `src/tools/sheets.py`

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `sheets_read` | Read range values | `spreadsheet_id`, `range` |
| `sheets_write` | Write values to range | `spreadsheet_id`, `range`, `values` |
| `sheets_create` | Create new spreadsheet | `title` |

**Notes:**
- Range uses A1 notation: `Sheet1!A1:D10`
- Values are 2D arrays: `[["a","b"],["c","d"]]`
- Write uses `USER_ENTERED` value input option

---

## Slides (2 tools) — `src/tools/slides.py`

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `slides_create` | Create new presentation | `title` |
| `slides_read` | Read presentation structure | `presentation_id` |

**Notes:**
- `slides_read` extracts text from all shape text runs per slide

---

## Forms (4 tools) — `src/tools/forms.py`

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `forms_create` | Create a new Google Form | `title` |
| `forms_get` | Get form content and questions | `form_id` |
| `forms_add_question` | Add a question to a form | `form_id`, `title`, `question_type` |
| `forms_get_responses` | Get all form responses | `form_id` |

**Notes:**
- Service: `forms` v1, uses discovery URL `https://forms.googleapis.com/$discovery/rest?version=v1`
- Scopes: `forms.body` (create/edit), `forms.responses.readonly` (read responses)
- `forms_create` creates form then optionally sets description via batchUpdate
- `forms_add_question` types: `short_answer`, `paragraph`, `multiple_choice`, `checkbox`, `dropdown`
- Options array required for multiple_choice, checkbox, dropdown types
- Uses `createItem` request in batchUpdate to add questions at specified index
- `forms_get_responses` maps question IDs to titles for readable output
- **2026 Note**: Forms created via API after June 30, 2026 are unpublished by default

---

## Tasks (5 tools) — `src/tools/tasks.py`

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `tasks_list_tasklists` | List all task lists | — |
| `tasks_list` | List tasks in a task list | — |
| `tasks_create` | Create a new task | `title` |
| `tasks_update` | Update/complete a task | `task_id` |
| `tasks_delete` | Delete a task | `task_id` |

**Notes:**
- Service: `tasks` v1 — scope: `tasks`
- Default task list: `@default` (user's primary list)
- Due dates in RFC 3339 format: `2025-12-31T00:00:00Z`
- `tasks_update` can mark completion by setting `completed: true`
- Status display: ✓ (completed) / ○ (needs action)

---

## Chat (4 tools) — `src/tools/chat.py`

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `chat_list_spaces` | List spaces you're in | — |
| `chat_send_message` | Send message to a space | `space_name`, `text` |
| `chat_list_messages` | List recent messages | `space_name` |
| `chat_create_space` | Create a new space | `display_name` |

**Notes:**
- Service: `chat` v1 — scopes: `chat.spaces`, `chat.messages`
- Space names format: `spaces/AAAA...`
- `chat_list_messages` ordered by `createTime desc`
- `chat_create_space` types: `SPACE` (named space) or `GROUP_CHAT`

---

## Meet (4 tools) — `src/tools/meet.py`

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `meet_create_space` | Create a meeting link | — |
| `meet_get_space` | Get space details | `space_name` |
| `meet_end_conference` | End active conference | `space_name` |
| `meet_list_conferences` | List past conferences | — |

**Notes:**
- Service: `meet` v2 — scope: `meetings.space.created`
- Space names format: `spaces/abc-defg-hij`
- `meet_create_space` returns join URL, meeting code, and space name
- `meet_list_conferences` shows start/end times and associated space
