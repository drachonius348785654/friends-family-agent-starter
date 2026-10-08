# Hermes model-routing notes

Verified against the documentation during an initial routing review. These details
are **version-sensitive** — re-check them against your own install.

## Documentation findings

- Auxiliary tasks default to `auxiliary.<task>.provider: auto` with an empty model. `auto` routes to the main chat provider/model.
- The interactive path is `hermes model` → `Configure auxiliary models`; selections persist under `auxiliary.<task>.*`.
- Common documented auxiliary slots include `vision`, `compression`, `approval`, `title_generation`, `memory_query_rewrite`, `background_review`, `curator`, `triage_specifier`, `kanban_decomposer`, `profile_describer`, and others. The available set is version-sensitive.
- Auxiliary task settings commonly include `provider`, `model`, `base_url`, `api_key`, `timeout`, and `extra_body`; many also accept `reasoning_effort`.
- A custom `base_url` overrides provider routing and uses direct OpenAI-compatible endpoint behavior.
- `background_review` has a cache tradeoff: the same model can replay the full cached transcript; a different model uses a compact digest.
- `delegation` is separate from auxiliary calls and persists under top-level `delegation.provider` / `delegation.model`.
- Primary fallback is configured as top-level `fallback_providers` and managed with `hermes fallback add|list|remove|clear`. It is triggered by provider failures, not quality/performance/task suitability.
- MoA uses configured reference models followed by an aggregator. Configure/inspect with `hermes moa configure` and `hermes moa list`; reasoning effort belongs per reference slot and the aggregator.

## Check your own install

Routing values are host-specific, so verify rather than assume:

```bash
hermes config get auxiliary     # which auxiliary tasks are configured, and with what
hermes fallback list            # configured fallback providers
hermes moa list                 # MoA presets, their models, and whether active
```

## Reporting pitfalls

- Do not call an auxiliary route a spontaneous main-model switch.
- Do not say MoA is active merely because a preset exists; check the active state.
- Do not present credential rotation as a model switch; it is same-provider credential failover.
- Do not claim Hermes chooses auxiliary models by live quality, speed, or context-aware benchmarking without fresh evidence.
