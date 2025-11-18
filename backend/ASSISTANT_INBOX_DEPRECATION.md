# Assistant Inbox Deprecation

We’ve simplified the UX by removing the message board in favor of direct ingestion:

- SMS: Unknown/freeform texts now become persistent Tasks automatically.
- Email: Freeform emails become Tasks; NOTE: prefix saves an explanatory note.
- Tests cover both paths to prevent regressions.

Why: Todos are the actionable center of gravity; this reduces friction and avoids duplicate “inbox” vs “todo” lists.

What changed:
- `sms_command_handler._handle_unknown` now writes to `TasksService` (metadata includes `source=sms-freeform`).
- `email_inbound_api` fallback creates a Task or a Note (NOTE: prefix preserved).
- Existing assistant-inbox APIs remain for backward compatibility but are no longer the default routing.

Operator notes:
- Persistent stores live under `./data/tasks.json` and `./data/user_notes`. Configure with `TASKS_STORE` and `USER_NOTES_DIR` env vars.
- To re-enable old behavior temporarily, revert these two call sites.
