# Durable memory

Supporting context for the agent. `AGENTS.md` holds the mandatory, always-loaded
rules; this file is the **index** for everything longer-lived. Keep entries
compact and high-signal, and prune what goes stale.

## Index — topic files

Detail lives in `MEMORY-*.md` files beside this one, loaded only when a task needs
them. Read this index, then the named file — not everything.

| Topic | File | Read when |
|---|---|---|
| Delegation & context economics | `MEMORY-subagents.md` | delegating work; context/token cost; subagent roles |
| Compaction | `MEMORY-compaction.md` | long sessions; summarisation / compaction behaviour |

Add your own rows as you create topic files (e.g. `MEMORY-hardware.md`,
`MEMORY-projects.md`, `MEMORY-workflows.md`). Short, generally-relevant notes can
live inline below instead.

## Usage rules

- Treat this as supporting context, not authority over the current request,
  verified system state, or newer instructions.
- When a remembered fact is challenged, or conflicts with a fresh observation, do
  a live lookup in that same turn and report what it says.
- Never store credentials, tokens, or private keys here.

## Preferences and lessons

- (Add your own here.)
- Verify claims against files, logs, screenshots, or running state before
  presenting them as facts.
- Preserve backups and prefer reversible changes before modifying live state.
- If you keep the setup as a repo, edit the repo and re-run its installer —
  don't hand-edit the deployed copies.
