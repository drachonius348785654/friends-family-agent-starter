---
name: durable-memory
description: Load the durable agent context — operating rules, machine facts, and historical decisions — before work that depends on prior decisions, recurring workflows, or stated preferences. Use when resuming earlier work, when a remembered fact is challenged, or when the user refers to something decided in a past session.
---

# Durable memory

This setup keeps its durable agent context in the pi agent directory, shared by
every agent on the machine (pi and Hermes both read it). **These files are the
source of truth — not your recollection of them.**

The layout is deliberately layered so a task loads only what it needs:

| Layer | Files | Loaded |
|---|---|---|
| Mandatory rules + always-relevant machine facts | `~/.pi/agent/AGENTS.md` | every turn |
| History, decisions, lessons, topic detail | `~/.pi/agent/MEMORY.md` (an index) + `MEMORY-*.md` | on demand |
| Domain procedures | `~/.agents/skills/<name>/SKILL.md` | when the task matches |

Read in this order:

1. `~/.pi/agent/AGENTS.md`
   Mandatory operating rules, plus any host-specific section your installer
   appends. It is deliberately held lean: **if a fact is not needed on *every*
   task, it does not belong here.**

2. `~/.pi/agent/MEMORY.md`
   A short **index** plus the inline preferences/lessons. Read the index first,
   then **only the named topic files the task needs** — do not read them all.

   Topic files sit beside it and share the `MEMORY-*.md` prefix; the set present
   varies by setup. Add a row to the index whenever you create one.

## Where to put a new fact

- Global rule, or a fact needed on every turn → `AGENTS.md` (keep it lean).
- History / decision / lesson / topic detail → the matching `MEMORY-*.md`. If none
  fits, add a section + index row to `MEMORY.md`, or create a new `MEMORY-<topic>.md`.
- Domain procedure → a skill in `~/.agents/skills/`.

If you keep the setup in a repo, edit the **repo** and re-run its installer rather
than hand-editing the deployed copies: `~/.pi/agent/` is generated (the repo is
copied into place, then any host-specific fragments are appended).

## Rules for using it

- Read it when the task involves prior decisions, recurring workflows, user
  preferences, or historical troubleshooting. Do not load it reflexively for
  unrelated work.
- Treat it as supporting context, not as authority over the current request,
  verified system state, or newer instructions.
- When a remembered fact is challenged, or conflicts with fresh evidence, do a
  live lookup in the same turn and report what it says. Do not defend or
  re-derive the remembered value.
- Do not write to these files unless explicitly asked — they are curated by hand.
- Never store credentials, tokens, or private keys in them.

## Related

- `~/.pi/agent/agents/*.md` — subagent definitions and the role/model roster.
- `~/.pi/agent/skills/` — may hold symlinks to the platform's system skills.
- Your setup repo, if you keep one — maintains all of the above plus any per-host
  context fragments.
