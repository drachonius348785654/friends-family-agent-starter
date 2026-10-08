---
name: todo-list
description: >
  Use when the user asks about their to-do list, task list, "the list",
  "what's next", "what's left", outstanding items, or asks to add/check off/
  update tasks. Maintains the master list at ~/TODO.md.
---

# To-Do List

The user's master task list lives at **`~/TODO.md`**. Read it when the user
asks what's pending; present it grouped by its section headers, with the most
time-sensitive items first.

## Related files

- Migration detail may live in a dedicated migration section of `~/TODO.md`
  plus a migration-specific skill, if the user keeps one.
- Some cleanup tasks may reference staging/backup directories. Treat any such
  data as gated: never delete it without explicit in-session user approval.

## Rules

1. When the user completes a task, **edit `~/TODO.md` to check it off**
   (`- [ ]` → `- [x]`) — keep the file current rather than just answering.
2. When the user mentions a new task, **append it** to the matching section
   (or create a section if none fits).
3. When reporting, offer the single most actionable next item, not just the list.
4. Gated items (reformats, deletions, permission-flagged steps) always require
   explicit in-session user approval before acting.
