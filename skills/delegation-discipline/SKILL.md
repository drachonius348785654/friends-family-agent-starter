---
name: delegation-discipline
description: >
  Standing context-economics rule. Use BEFORE running any command whose output
  might be large, any multi-page web or documentation sweep, any whole-repo /
  whole-corpus / whole-session scan, and whenever asked whether context is being
  conserved or token costs are being wasted. Also applies when deciding between
  doing reconnaissance in the main context and delegating it to a subagent
  (scout, noise-runner, image-triage, worker).
---

# Delegation discipline — context is the budget

The user pays for context. Every large tool result that enters the main context
is re-sent on every later turn, for the rest of the session. Subagents exist to
absorb that mass in a discarded context and hand back only the distilled answer.

**The mechanism works. The practice tends to be nearly absent.** This skill
exists because agents habitually under-use delegation even when it is available,
and the gap only shows up when behavior is actually measured.

## Why it matters (measure it on your own session)

Do not take the principle on faith — measure it. A typical long session shows:

- a handful of subagent calls against hundreds of direct bash/read/edit calls;
- tool results dominating stored context mass (often the majority of bytes),
  with a small number of very large tool outputs accounting for a large share
  of that mass;
- a per-turn bill dominated by **input + cache-read tokens**, i.e. the context
  **re-sent** every turn rather than generated fresh;
- per-turn costs. Once
  the session is long, that re-sent mass is most of the cost.

The lesson is structural, not tied to one session: content mass concentrated in a
few large tool results, re-sent every turn, is the cost driver. Images are the
single largest byte consumer of stored content, and an image is likewise re-sent
on every later turn (and image bytes != token count, since the harness re-encodes
them to the model's resize limits).

Delegation buys context at the cost of **latency**, not usually much money. The
true price of reconnoitering a very large file inside a subagent is the wall-clock
time to run it — worth paying when the main-context alternative is a large mass
carried for the rest of the session.

## Rules

1. **Delegate by threshold, not by mood.** Send it to a subagent when any of
   these is true:
   - a command's output could exceed roughly **10 KB**;
   - the work is a **multi-page web or documentation sweep**;
   - it is a **whole-repo, whole-corpus, whole-session, or whole-large-file scan**;
   - it will take **many iterations to distill** (grep-and-narrow loops, log
     archaeology, "find the one line that matters").
2. **Keep it in the main context when delegation would hurt.** Do it yourself if:
   - the output is **small** (a few lines, a version string, one exit status);
   - you need the **exact bytes verbatim** — subagents return distilled answers,
     so a file you are about to edit precisely, a config you must reproduce
     character-for-character, or a diff belongs in the main context;
   - it is a **single quick check** whose result decides the next step — the
     delegation latency to save a few hundred tokens is a loss;
   - the user asked for **the raw artifact itself**.
3. **Route to the right role.** `scout` = fast recon, compressed findings for a
   handoff. `noise-runner` = high-volume commands, returns only the distilled
   answer. `image-triage` = screenshots/photos, returns compact text.
   `worker` = bulk or iterative work in an isolated context. Do not ask
   `noise-runner` for judgement, and do not ask `scout` to absorb a very large
   file when `noise-runner` is the high-volume role.
4. **Brief like the agent knows nothing — it does.** A subagent does not see this
   conversation. Give absolute paths, the exact commands or URLs, the shape of
   the answer you want, and a bound ("return only X, at most N lines, no
   transcript"). A vague brief produces a vague answer that must be redone in the
   main context, which is the worst outcome.
5. **A subagent's answer is a claim, not a fact.** It discards its context, so its
   reasoning is unauditable. Spot-check the load-bearing number or path before
   acting on it — this is evidence-discipline applied to delegation.
6. **Subagent context is discarded.** Anything worth keeping must be written to a
   file or into the parent's answer; it does not survive anywhere else.
7. **Report the trade honestly.** Delegation buys context at the cost of
   latency. Never claim a saving you did not measure; if asked whether costs are
   being conserved, answer from the numbers, not from the design.
8. **If the `subagent` tool is unavailable, say so.** The extension loads at
   session start, so a session already running when it was installed may not have
   the tool. Fall back to doing the work in-context and state that context is
   being spent — do not silently bloat.
9. **Parallel for independent sweeps, chain for dependent ones.** Several
   unrelated lookups go out in parallel; a sequence where each step needs the
   previous result goes in a chain.
10. **Images are the largest byte consumer — never `read` a large one into the
    main context.** Screenshots and photos dominate stored content bytes, and an
    image is re-sent on every later turn, like everything else. Have
    `image-triage` view it and return text (`noise-runner` and `scout` also accept
    images; be careful that text-only models cannot process them, which is why
    model choice matters here). Note bytes != tokens for images — the harness
    re-encodes per the model's resize limits — so report what was read as text,
    not as a token estimate.
11. **Session hygiene outranks delegation when the session is old.** Delegation
    reduces what *enters* context; a fresh session resets what is *carried*. A
    long-running session re-sends its whole history every turn. When a session is
    that old, suggest starting fresh for the next task rather than only delegating
    inside it.

## Related skills

- The `evidence-discipline` skill — a subagent's answer is a claim, not a fact.
