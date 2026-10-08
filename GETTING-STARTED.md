# Getting started (no agent required)

You can do every step by hand in a terminal. Follow top to bottom: the first part
installs the tools, the second installs this pack and brings up your agent.

## 0. You need

- A Linux desktop. This pack assumes **Omarchy** (Arch + Hyprland), but any Arch
  derivative works; the commands below note the Arch/Omarchy path.

## 1. Base tools

Install git, Node.js, Python + a Python app installer, and the GitHub CLI:

```bash
# Omarchy / Arch
omarchy pkg add git nodejs npm python python-pipx github-cli
# or:  sudo pacman -S git nodejs npm python python-pipx github-cli
```

## 2. Install an agent to run

This pack targets **Hermes Agent** (the tab in the layout):

```bash
pipx install hermes-agent      # or follow Hermes' own install docs
hermes --version
```

*(Optional)* If you also want the four subagent roles, install **pi** — the
`agents/` and `extensions/subagent/` bits target pi's subagent extension.

## 3. Install herdr

Install herdr per its docs (herdr.dev), then install its built-in Hermes
integration:

```bash
herdr integration install hermes
```

## 4. GitHub (needed only if you'll clone)

Create an account at github.com, then:

```bash
gh auth login
```

If you received this pack as an archive, skip this — just unzip it.

## 5. OpenRouter

1. Create an account at **openrouter.ai**.
2. **Add credits** (the model in this pack is a paid endpoint).
3. Create an **API key**, then put it in your shell:

```bash
echo 'export OPENROUTER_API_KEY="sk-or-..."' >> ~/.bashrc
source ~/.bashrc
```

## 6. Install this pack

From the unzipped folder:

```bash
cd friends-family-agent-starter
./install.sh
```

It backs up any existing `~/.pi/agent`, overlays the pack, installs the skills to
`~/.agents/skills/`, and wires Hermes to read them. It also seeds `~/TODO.md`
with your checklist if you don't already have one.

You end up with a **layered** context in `~/.pi/agent/`: `AGENTS.md` (the always
loaded rules), `MEMORY.md` (an index), and the `MEMORY-*.md` topic files it points
to — plus any subagent/extension files this pack includes.

## 7. Bring up the Hermes tab

Apply the layout (dry-run first):

```bash
python3 herdr/apply.py            # show what it would build
python3 herdr/apply.py --apply    # build it
```

Or make one by hand: a single tab running `hermes --provider openrouter -m
deepseek/deepseek-v4.1-flash`.

## 8. Optional

- **Tailscale** — a private device mesh. See `docs/tailscale.md`.
- **Telegram bridge** — capture notes from your phone. See `docs/telegram-bridge.md`.

## If something goes wrong

- `install.sh` saved a backup at `~/.pi/agent.bak.<timestamp>` — restore by copying
  it back over `~/.pi/agent`.
- Re-run `install.sh` any time; it is idempotent and re-backups each run.
- Verify the pieces: `ls ~/.agents/skills/`, `ls ~/.pi/agent/` (you should see
  `AGENTS.md`, `MEMORY.md`, and `MEMORY-*.md`), and `hermes config get skills`.
