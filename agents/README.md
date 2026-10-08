# Subagent agents (user scope)

Definitions for the `subagent` extension bundled in `extensions/subagent/`
(a pi extension). Each `.md` file is one agent; frontmatter fields are `name`,
`description`, `tools`, and `model`.

| agent | model (example) | tools | purpose |
|---|---|---|---|
| `scout` | `deepseek/deepseek-v4.1-flash` | read, grep, find, ls, bash | fast recon; returns compressed findings for handoff |
| `noise-runner` | `deepseek/deepseek-v4.1-flash` | read, bash, grep, find, ls | runs high-volume commands; returns only the distilled answer |
| `image-triage` | `deepseek/deepseek-v4.1-flash` | read, bash, ls | views screenshots/photos, returns compact text |
| `worker` | `openai/gpt-6-luna` | (default set) | bulk/iterative work in an isolated context |

The models are examples routed through OpenRouter — change the `model:` lines to
whatever you have access to.

## Smoke test

```bash
pi --model deepseek/deepseek-v4.1-flash --no-session \
  -p "Use the subagent tool with the noise-runner agent to report the current \
      working directory value."
```

If the extension loaded, the subagent tool is invoked and the parent returns a
one-line answer while the noisy work happened inside the subagent's own,
discarded context.

Note: the extension loads at **session start**, so a session already running when
it was installed will not have the `subagent` tool.

## When to use which

See the `delegation-discipline` skill — it covers the thresholds for delegating,
when to keep work in the main context, and how to route to each role.

## Using these with Hermes instead of pi

These agent definitions target the pi `subagent` extension. Hermes Agent has its
own delegation mechanism; if you use Hermes, treat this directory as reference for
the roles (scout / noise-runner / image-triage / worker) and their contracts,
not as a drop-in config.

## Updating

`extensions/subagent/` was copied (not symlinked) from the pi examples directory.
To update after a pi upgrade, re-copy `index.ts` and `agents.ts` and re-run the
smoke test above.
