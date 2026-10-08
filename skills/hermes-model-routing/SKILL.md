---
name: hermes-model-routing
description: >
  Configure and explain Hermes Agent model routing: auxiliary task models,
  primary fallback providers, credential rotation, and Mixture-of-Agents.
  Use when the user asks how Hermes chooses models, how to reduce side-task
  cost, how to configure vision/compression/approval/memory-review models, how
  to configure failover, or how to use MoA deliberately.
---

# Hermes model routing

Use this skill for Hermes Agent's model/provider routing configuration. Treat
these as separate mechanisms; do not describe them as one general-purpose
performance-aware router.

## 1. Establish the routing layer

Before changing anything, identify which behavior the user means:

- Main model: the model handling the ordinary conversation.
- Auxiliary model: a per-task side call such as vision, compression, title
  generation, approval, memory-query rewriting, background review, or curator.
- Primary fallback: a backup provider/model used after operational failure.
- Credential pool: rotation among credentials for the same provider.
- Mixture-of-Agents (MoA): several reference models plus an aggregator, invoked
  explicitly rather than selected spontaneously based on task difficulty.
- Delegation: full child agents configured through `delegation.*`; this is not
  an ordinary auxiliary call.

Do not claim that Hermes automatically changes models based on answer quality,
latency, perceived task needs, or context suitability unless fresh product
behavior specifically verifies that claim.

## 2. Auxiliary models

By default, `auxiliary.<task>.provider: auto` and an empty model route the
auxiliary task to the main chat provider/model. Explicitly pin a task when a
cheaper or more specialized model is appropriate:

```yaml
auxiliary:
  vision:
    provider: <provider>
    model: <multimodal-model>
    reasoning_effort: none
  compression:
    provider: <provider>
    model: <summarization-model>
    reasoning_effort: low
  title_generation:
    provider: <provider>
    model: <cheap-model>
    reasoning_effort: none
```

Common task slots include `vision`, `compression`, `approval`,
`title_generation`, `memory_query_rewrite`, `background_review`, `curator`,
`triage_specifier`, `kanban_decomposer`, `profile_describer`, `goal_judge`, and
`monitor`. Available slots can vary by Hermes version; inspect the live config
and docs rather than inventing a slot.

The universal task settings are generally `provider`, `model`, `base_url`,
`api_key`, `timeout`, and `extra_body`; auxiliary tasks additionally support
per-task `reasoning_effort` where documented. Never put credentials in
`config.yaml` or a skill/reference file; use Hermes' secret/env mechanisms.
When `base_url` is set, it takes precedence and calls the custom
OpenAI-compatible endpoint directly.

Configure interactively first:

```bash
hermes model
# choose: Configure auxiliary models
```

Use direct config only when the desired values are known and the edit is
intentional. Verify with:

```bash
hermes config get auxiliary
hermes config check
```

Cost/quality guidance:

- Keep the main model expensive/capable if desired, but use a fast inexpensive
  model for high-volume side work.
- `vision` often needs multimodal capability; verify the selected model supports
  images before pinning it.
- `compression` generally needs summarization reliability, not maximum
  reasoning depth; `low` is a reasonable starting point.
- `title_generation` usually needs little or no reasoning.
- `background_review` is special: `auto`/same model can reuse a warm prompt
  cache; routing it elsewhere can reduce token cost but uses a compact digest
  rather than the full cached transcript.
- `delegation` is configured under top-level `delegation.provider` and
  `delegation.model`, not under `auxiliary`, because delegated workers are full
  child agents.

## 3. Fallback providers

Primary fallback is failure-based. Configure a chain with:

```bash
hermes fallback add
hermes fallback list
```

The current config shape is a top-level list:

```yaml
fallback_providers:
  - provider: <provider-a>
    model: <model-a>
  - provider: <provider-b>
    model: <model-b>
```

Entries need both provider and model. They are tried in order after eligible
operational failures such as rate limits, overload/5xx, connection failures,
authentication failure, billing/credit exhaustion, safety refusal, or other
non-retryable provider errors as classified by Hermes. A rate-limit reset may
bench the primary temporarily; use the documented `min_switch_reset_seconds`
option only when the user wants to wait for a short reset instead of switching.

Fallback does not mean:

- choose a faster model because it is faster;
- choose a better model based on quality;
- choose by context length or task type;
- continuously benchmark providers.

Credential pools are a separate same-provider rotation layer and should not be
reported as a model switch unless the model/provider actually changes.

## 4. Mixture-of-Agents

MoA is an explicit multi-model pipeline:

```text
prompt -> reference model 1
       -> reference model 2  -> aggregator -> final response
       -> reference model 3
```

Configure or inspect presets with:

```bash
hermes moa configure
hermes moa list
```

The preset shape is conceptually:

```yaml
moa:
  default_preset: default
  presets:
    default:
      reference_models:
        - provider: <provider-a>
          model: <reference-model-a>
          reasoning_effort: medium
        - provider: <provider-b>
          model: <reference-model-b>
          reasoning_effort: high
      aggregator:
        provider: <provider-c>
        model: <aggregator-model>
        reasoning_effort: high
```

Reasoning settings belong per reference slot and on the aggregator, not in the
ordinary `auxiliary.moa_reference` / `auxiliary.moa_aggregator` blocks. MoA is
more expensive and slower because it makes multiple inference calls; reserve it
for difficult design comparisons, research synthesis, or high-stakes review.
Use `/moa` or the model picker according to the current Hermes interface. Do
not imply that configuring a preset automatically activates it for every turn;
check `hermes moa list` and distinguish `Active in config` from the available
preset.

## 5. Verification and reporting

After configuration:

1. Run `hermes config check`.
2. Inspect the relevant resolved section with `hermes config get ...`.
3. Run `hermes fallback list` or `hermes moa list` as applicable.
4. For a real routing test, use a harmless task that invokes the relevant
   auxiliary feature or an explicitly invoked `/moa` prompt.
5. Report whether a model was explicitly configured, inherited via `auto`, or
   activated only because of provider failure.

When investigating behavior, Hermes logs identify provider/model and API call
records. Avoid exposing API keys; redact secrets in any diagnostic excerpt.

## References

- See `references/routing-notes.md` for verified documentation excerpts and
  version-sensitive details worth re-checking during setup.
