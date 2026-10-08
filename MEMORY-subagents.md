# Delegation & context economics

> Topic file — indexed from `MEMORY.md`. Read when delegating work, or when
> reasoning about context / token cost.

- **Context is the budget.** Every large tool result that enters the main context
  is re-sent on every later turn, for the rest of the session. Subagents exist to
  absorb that mass in a discarded context and hand back only the distilled answer.
- **Delegate by threshold, not by mood.** Send work to a subagent when: a
  command's output could exceed roughly 10 KB; it is a multi-page web or
  documentation sweep; it is a whole-repo, whole-file, or whole-corpus scan; or it
  takes many grep-and-narrow iterations to distil.
- **Keep it in the main context** when the output is small (a few lines, one exit
  status); when you need the exact bytes verbatim (a file you are about to edit
  precisely, a config, a diff); when a single quick check decides the next step;
  or when the user asked for the raw artifact itself.
- **Route to the right role** — fast recon, high-volume command running, image
  triage, and bulk/iterative work are different jobs; don't ask a recon role to
  absorb a huge file.
- **Brief like the agent knows nothing — it does.** A subagent does not see your
  conversation: give absolute paths, the exact command or URL, the shape of the
  answer you want, and a bound ("return only X, at most N lines, no transcript").
- **A subagent's answer is a claim, not a fact.** Its context is discarded, so its
  reasoning is unauditable — spot-check the load-bearing number or path before
  acting on it.
- **Measure your own costs.** Don't trust a rule of thumb; the agent's own
  session logs / usage reports are the source of truth for what context actually
  costs you.
