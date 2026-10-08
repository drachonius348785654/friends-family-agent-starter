# TODO — getting started

Follow top to bottom. The first three are prerequisites for the rest.

## Before you install (do these first)

- [ ] **Create a GitHub account** (github.com) — needed if you'll clone the repo
      or use `gh`.
- [ ] **Install and authenticate `gh`** → `gh auth login`.
- [ ] **Create an OpenRouter account** (openrouter.ai), **add credits**, and
      create an **API key**. Put it where your shell can see it:

      ```bash
      echo 'export OPENROUTER_API_KEY="sk-or-..."' >> ~/.bashrc
      ```

## Install this starter

- [ ] **Get the starter** — unzip the archive you received, or clone the private
      repo (needs the GitHub access above).
- [ ] **Run the installer**: `./install.sh`
- [ ] **Verify**: skills appear in `~/.agents/skills/`, and Hermes'
      `~/.hermes/config.yaml` lists that dir under `skills.external_dirs`.

## Bring up your agent

- [ ] **Install herdr**, then install its Hermes integration:

      ```bash
      herdr integration install hermes
      ```

- [ ] **Open the Hermes tab** (provider `openrouter`, model
      `deepseek/deepseek-v4.1-flash`). If a layout manifest was provided:
      `python3 herdr/apply.py --apply`.

## Optional

- [ ] **Tailscale** — private device mesh. See `docs/tailscale.md`.
- [ ] **Telegram bridge** — capture notes from your phone. See
      `docs/telegram-bridge.md`.

## Make it yours

- [ ] Edit `~/.pi/agent/AGENTS.md` — keep it **short**; it is loaded every turn.
- [ ] Put longer notes in `~/.pi/agent/MEMORY.md` (the index) and add a
      `MEMORY-<topic>.md` file for each subject, then add a row for it in the
      index. Topic files are only read when a task needs them.
- [ ] Add skills under `~/.agents/skills/<name>/SKILL.md` as you find reusable
      procedures.
