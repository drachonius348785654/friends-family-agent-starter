# Friends & Family — agent starter

A generic starting pack for a fresh **Omarchy + herdr + Hermes** setup: portable
agent rules and memory, a small set of tool-agnostic skills, four subagent
definitions, the subagent extension, and a **single-tab herdr layout** running
Hermes on OpenRouter.

Nothing here is specific to any one person's hardware or services.

## What's inside

| Path | What |
|---|---|
| `AGENTS.md` | Always-loaded agent rules — kept short (~800 words) |
| `MEMORY.md` | The memory **index**: preferences/lessons + a table of topic files |
| `MEMORY-*.md` | Topic files (`MEMORY-subagents.md`, `MEMORY-compaction.md`) — loaded only when needed |
| `settings.json` | Generic steering / compaction config |
| `skills/` | Tool-agnostic skills (cross-tool Agent Skills standard) |
| `agents/`, `extensions/subagent/` | Four subagent roles + the `subagent` extension (pi) |
| `herdr/` | Layout capture/apply tooling + `layout/starter.json` (one Hermes tab) |
| `docs/` | Telegram-bridge and Tailscale setup guides |
| `install.sh` | Overlays the pack onto `~/.pi/agent/` + `~/.agents/skills/` |
| `TODO.md` | Your getting-started checklist |

### Skills included

`evidence-discipline`, `look-before-build`, `delegation-discipline`, `todo-list`,
`durable-memory`, `hermes-model-routing`, `aur-install`.

## The memory model (worth understanding)

The context is deliberately layered so a task loads only what it needs — long
memory is expensive because it is re-sent on every turn:

| Layer | Files | Loaded |
|---|---|---|
| Mandatory rules + always-relevant facts | `AGENTS.md` | every turn |
| History, decisions, lessons, topic detail | `MEMORY.md` (index) + `MEMORY-*.md` | on demand |
| Domain procedures | `~/.agents/skills/<name>/SKILL.md` | when the task matches |

So: keep `AGENTS.md` short (if a fact isn't needed on *every* task, it does not
belong there), let `MEMORY.md` act as an index, and put the bulk in topic files it
points to. Add new rows to the index as you create topic files — that is the whole
trick, and it is the same idea the skills use when they push long detail into a
`references/` file.

## Start here

See **`GETTING-STARTED.md`** — a full, no-agent walkthrough (install the tools,
then this pack).

## Design notes

- Skills install to `~/.agents/skills/` — one shared copy read by pi natively and
  by Hermes via `skills.external_dirs` (which `install.sh` wires for you).
- The herdr manifest launches **only** a Hermes tab (`kind: "hermes"`), provider
  `openrouter`, model `deepseek/deepseek-v4.1-flash`.
- The subagents target the pi `subagent` extension; if you use Hermes, treat them
  as reference for the roles rather than a drop-in config.

## What is deliberately NOT here

Browser-session tooling, any personal bot/Telegram config, game-migration or
monitor tooling, per-machine monitor maps, and all personal history/memories.
Add your own to `MEMORY.md` (and its topic files) as you go.

## Sharing

It is written as a portable archive — zip the folder and send it. It contains **no
secrets**; keep it that way (never add an API key, token, or tailnet name).
