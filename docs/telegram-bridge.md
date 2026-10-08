# Optional: your own Telegram -> local inbox bridge

Turn your phone into a capture tool. You message a private Telegram bot; a small
service on your computer polls the bot and appends your notes to a local Markdown
inbox. Nothing is exposed publicly, and **no commands are ever executed** from
Telegram.

## Design (recommended)

- A **private bot chat**, with a token from BotFather.
- A **local polling service** (long-poll `getUpdates`) — no public webhook, no
  open ports, no firewall changes.
- **Allowlist your own numeric Telegram user ID**; ignore everyone else.
- Store the token in a **user-only secret file** (`chmod 600`). Never put it in
  this repo, memory files, agent state, or a git remote.
- **Deduplicate update IDs** so a restart doesn't double-append.
- Append to the inbox **atomically** (write a temp file, then rename); acknowledge
  only *after* the durable write succeeds.

## Steps

1. In Telegram, message **@BotFather** -> `/newbot` -> pick a name -> copy the
   bot token.
2. Message **@userinfobot** to get **your** numeric user ID.
3. Store the token owner-only:

   ```bash
   mkdir -m 700 -p ~/.config/tg-inbox
   ( umask 077; printf '%s' 'YOUR_BOT_TOKEN' > ~/.config/tg-inbox/token )
   ```

4. Run a poller. Write a small script (or use a bridge you were given) that:
   long-polls `getUpdates`, filters by your user ID, appends the text to
   `~/notes/telegram-inbox/YYYY-MM-DD.md`, tracks the last seen update ID, and
   acknowledges only after the append.
5. Send the bot a test message and confirm it lands in the inbox file.

## Security

- The token grants full control of the bot — keep it secret. Revoke any leaked
  token with `/revoke` in BotFather and issue a new one.
- Never run shell commands that arrive via Telegram. Capture only.
