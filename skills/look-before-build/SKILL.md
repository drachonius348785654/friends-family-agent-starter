---
name: look-before-build
description: >
  REQUIRED before writing any custom script, tool, wrapper, or plugin for a
  user-facing capability. Use when the user asks for a new ability, feature,
  workflow, or "can you make X do Y" — search for existing apps, plugins,
  CLI tools, or distro packages FIRST, and present them as options before
  building anything custom. Triggers: "make a script", "write a tool",
  "add a feature", "can it do X", "I wish there was", any request that
  smells like new code.
---

# Look-Before-Build — find before you build

Custom code is a last resort, not a default. Before writing ANY new script,
tool, plugin, or wrapper for a user-facing capability, search for an existing
solution and present it as an option.

## Why

- Established tools (e.g. `restic` + `systemd` timers for backups) beat a
  hand-rolled script.
- Distro/desktop helper commands already exist for many tasks — agents have
  historically rebuilt things that were already there.
- Existing tools come maintained, documented, and updated; custom scripts
  rot and only the writing agent knows them (until a skill captures them).

## Search order (check ALL before concluding nothing exists)

1. **Distro packages**: `pacman -Ss <keyword>`, then AUR (`yay -Ss`)
2. **Distro/desktop built-ins**: `ls /usr/bin/<vendor>-*` — many desktop
   abilities already exist as themed helper commands.
3. **CLI standards**: coreutils/util-linux, `jq`, `fzf`, `rsync`, `curl` —
   the ability is often one well-known flag away
4. **Ecosystem plugins** for the target app: browser extensions (Chrome Web
   Store / addons.mozilla.org), VS Code extensions, compositor plugins
   (`hyprctl plugin`), PipeWire/EasyEffects presets, rclone remotes, systemd
   units (`systemctl list-unit-files | grep -i <kw>`)
5. **Language ecosystem one-shots**: pipx, npm -g, cargo install — for small
   maintained tools
6. **Upstream feature check**: the app may already do it (an option, a
   config key, a hidden flag, a URL scheme). Read `--help` and the docs
   before assuming it can't.

## Protocol when an existing solution is found

- Present it with evidence: package name, what it does, install size/maintainer
- Note anything it does NOT cover versus what the user asked for
- Let the user choose: install it, or build custom anyway (their call —
  sometimes the custom 30-liner is right, especially for glue between their
  own tools)
- If nothing exists: say so explicitly ("searched pacman/AUR/built-ins/
  plugins — nothing covers this; custom is justified"), THEN build

## Exemptions (don't run the search when)

- One-liners and shell glue for in-session work (a `jq` filter, a for-loop)
- Glue scripts connecting the user's OWN tools (e.g. their own snapshot/
  recovery kit)
- The user explicitly says "build custom" or "don't look for a package"
- Personal-data-specific logic no general tool could know (parsing the
  user's own exported files, etc.)

## Also applies to MODIFYING existing custom tools

When changing values/behavior in the user's custom widgets/scripts, check
whether the change belongs in a config/settings surface rather than more
hardcoded values — if the tool has a `setting()` mechanism or config file,
prefer promoting the values there. And verify upstream (stock desktop shell/
plugins) doesn't already provide the feature being hand-rolled. (Lesson: an
agent once edited hardcoded values in a widget instead of checking for a
settings surface.)

## Capture rule

If a custom tool IS built anyway, it must be captured (a skill, or a
comment header with purpose + usage) so the next agent finds it instead of
building a second one. Duplicates of existing local tools are a defect.
