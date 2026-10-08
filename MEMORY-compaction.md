# Compaction

> Topic file — indexed from `MEMORY.md`. Read when sessions get long, or when
> reasoning about summarisation / context limits.

- **Compaction is lossy by construction** — a summary replaces history. Raw
  entries usually remain on disk (session logs are append-only), so the loss is to
  the *model's context* and is recoverable by re-reading the session file.
- **Never rely on compaction for anything that matters — write it to a file.**
  Retention of individual facts across a compaction is **not** reliable: identical
  runs have retained nearly everything one time and dropped almost everything
  another. Anything that must survive belongs on disk (a `MEMORY-*.md` topic file,
  a notes file, or `AGENTS.md`) — never inside a summarised span.
- **Mechanics worth knowing** (names/values vary by agent and version — check your
  own config rather than assuming): the trigger is
  `contextTokens > contextWindow - reserveTokens`; `reserveTokens` also caps the
  summary's output length; a recent-token window is kept verbatim; and repeated
  compactions re-summarise from the previous kept boundary, so messages that
  survived once can be re-included.
- **Steering beats reimplementing.** If your agent supports custom compaction
  instructions, that is the supported way to preserve exact values, paths,
  versions, and open questions. Do not reimplement the summariser to get
  instructions honoured.
- **Context oscillates** in long sessions because old tool outputs get pruned — so
  you cannot force a huge context by appending tool output. Measure at real
  session sizes.
- **Bound your payloads.** Generating big output *inside* a command
  (`python3 -c "print('x'*200000)"`) works; embedding a large payload in a command
  line fails outright with `E2BIG: argument list too long` — and that failure is
  easy to miss, because it surfaces as an error response rather than as output.
