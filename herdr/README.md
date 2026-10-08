# herdr layout sync

`install.sh` syncs `~/.pi/agent/` — the agent's *rules, skills, subagents,
settings*. That is **not** the same as a herdr session's *layout*, which lives in
live server state (`~/.config/herdr/session.json`), rewritten continuously.
Committing that would snapshot a running session, not define a roster.

So instead this directory carries a **portable manifest**, applied to a target
machine using herdr's own layout API.

## Files

```
herdr/
  capture.py            # RUN ON A SOURCE MACHINE: exports the live layout
  apply.py              # RUN ON A TARGET MACHINE: builds it (dry-run by default)
  layout/starter.json   # this starter's manifest (a single Hermes tab)
```

Both scripts talk to the herdr server over its unix socket using documented API
methods (`herdr api schema --json` is authoritative). They do not need the TUI.

## The data model

A manifest is a list of workspaces -> tabs -> a pane tree -> agents:

```json
{
  "version": 1,
  "workspaces": [
    {
      "label": "hermes",
      "tabs": [
        {
          "label": "hermes",
          "cwd": "~",
          "root": { "type": "pane", "cwd": "~" },
          "agents": [
            { "name": "hermes", "kind": "hermes",
              "args": ["--provider", "openrouter", "-m", "deepseek/deepseek-v4.1-flash"] }
          ]
        }
      ]
    }
  ]
}
```

`root` is a `LayoutNode`: either a `pane` leaf or a `split` node
`{type, direction: "right"|"down", ratio, first, second}`. Agent `kind` names
match herdr's built-in integrations (`herdr integration install <kind>`), e.g.
`hermes`, `pi`, `claude`, `codex`.

## Apply it

```bash
python3 apply.py            # dry run — prints what it would build
python3 apply.py --apply    # build it
```

## Capture your own

Once you have a layout you like, run `capture.py` on that machine to write a new
manifest, then adapt it. See `../README.md` for the overall starter.
