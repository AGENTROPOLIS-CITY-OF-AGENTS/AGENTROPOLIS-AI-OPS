# Implementation Backlog — Telemetry Collection Pipeline

> Status: **BACKLOG** — items in this document are NOT implemented and carry no
> runtime support. Nothing here is a claim of existing behavior.

This document records the planned collection pipeline that will consume the
schemas in `schemas/` and the interfaces in `interfaces/`. Until items move out
of BACKLOG, all telemetry remains contract-only (schemas + interfaces + tests).

## BACKLOG — live ingestion

- [ ] Runtime hook that calls `ContextTelemetryCollector.collect()` at task
      completion and persists the record against `context-telemetry.schema.json`.
- [ ] `BenchmarkRegistry` implementation backed by durable storage
      (`store`, `lookup`, `mark_reproduced_internally`).
- [ ] `ModelWindowDiscovery` implementation that discovers advertised vs
      runtime context limits from the live model/runtime, not from a fixed
      value such as 64,000 tokens.
- [ ] Thermodynamic metrics batch emission (`thermodynamic-metrics.schema.json`).
- [ ] Optimization profile + routing receipt recording
      (`optimization-profile.schema.json`).

## BACKLOG — storage

- [ ] Durable telemetry store (schema-versioned, append-only) with retention
      and redaction policy per the telemetry profile guardrails
      (no raw credentials, no unredacted personal data).
- [ ] Benchmark receipt store with hardware/software-version indexing.
- [ ] Provenance-preserving store for measurement sources.

## BACKLOG — dashboards

- [ ] Context usage dashboard (effective budget vs usage, reserves).
- [ ] Thermodynamic observability dashboard (token energy, churn, friction,
      drift, correction load, compression loss, useful work ratio).
- [ ] Benchmark awareness dashboard (per-device, per-software-version, with
      verification state).
- [ ] Cost visibility dashboard (provider cost per task, per model family).

## BACKLOG — no-unsupported-claims rules

These guard notes (also defined verbatim in `interfaces/metric_definitions.py`)
are enforced by policy in any future dashboard or routing surface. They are
rules, not measurements:

- **12GB VRAM does NOT equal production readiness.**
- **Low-memory execution does NOT equal full model quality.**
- **One DGX Spark benchmark does NOT apply to other hardware.**
- **A faster preview profile is NOT equivalent to canonical final output.**
- Community benchmark claims remain **UNVERIFIED** until reproduced
  internally on the stated hardware (`benchmark-registry.schema.json`).
