# agentropolis-ai-ops
AI operations layer for AGENTROPOLIS: context usage tracking, model routing, benchmark awareness, cost visibility, and agent performance dashboards.
AI operations control plane for AGENTROPOLIS: Hermes runtime supervision, context and token tracking, model routing, benchmark awareness, provider health, cost visibility, agent performance, queues, telemetry, alerts, recovery, and operational dashboards.

## HERMES Execution Discipline telemetry

Telemetry contracts for the HERMES Execution Discipline doctrine (canon:
`wiredchaos/agentropolis` `docs/HERMES_EXECUTION_DISCIPLINE_AND_CONTEXT_GOVERNOR.md`).
This repository owns context telemetry, benchmark receipts, model-window
discovery, and cost/performance analytics.

**What exists (this branch):**

- `schemas/` — JSON Schema (draft 2020-12) contracts:
  - `thermodynamic-metrics.schema.json` — token energy, context churn,
    coordination friction, semantic drift, correction load, compression loss,
    useful work ratio, compute energy, memory entropy, tool failure heat.
  - `benchmark-registry.schema.json` — exact, hardware-specific benchmark
    receipts; community claims remain UNVERIFIED until reproduced internally.
  - `context-telemetry.schema.json` — per-task context usage and model
    intelligence record (effective context budget is discovered, never assumed).
  - `optimization-profile.schema.json` — governed profile classes, policy
    flags, and routing receipts.
- `interfaces/` — stdlib-only collection contracts (`typing.Protocol`):
  `ModelWindowDiscovery`, `ContextTelemetryCollector`, `BenchmarkRegistry`,
  plus canonical metric definitions and no-unsupported-claims guard notes in
  `metric_definitions.py`.
- `tests/` — unittest suite validating every schema against positive and
  negative instances, and verifying the interface Protocols are
  runtime-checkable via in-test fake collectors.

**Run the validation suite** (requires only `uv`; `jsonschema` is provisioned
ephemerally — no dependency files are added to the repo; `python` is 3.11):

```bash
uv run --with jsonschema python -m unittest discover -s tests -v
```

**Backlog (not implemented):** live ingestion, durable storage, and
dashboards — see `docs/IMPLEMENTATION_BACKLOG.md`.
