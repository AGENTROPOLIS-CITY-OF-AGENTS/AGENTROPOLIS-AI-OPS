# Hermes v2026.7.30 Telemetry Profile

**Runtime:** `NousResearch/hermes-agent@v2026.7.30`  
**Lifecycle:** CANARY

## Required dimensions

- `runtime_version`
- `runtime_lane`
- `backend_identity`
- `agent_id`
- `session_id`
- `mandate_id`
- `district_id`
- `model_provider`
- `model_id`
- `capability_id`
- `receipt_id`

## Required measures

### Runtime

- gateway availability and restart count;
- session start, resume, compression, and failure counts;
- queue depth, wait time, retries, and cancellation latency;
- active, completed, failed, cancelled, and orphaned subagents.

### Model and context

- input, output, cached, and compressed context units;
- model latency and failure rate;
- provider rate-limit events;
- estimated and settled cost per completed task;
- retries and model-lane changes.

### Capability bus

- discovery count;
- policy approvals and denials;
- tool latency and error class;
- receipt completion latency;
- duplicate-write and idempotency warnings.

### Specialized transports

Track voice, Telegram media, Buzz/Nostr, FLUX3, and remote-runtime metrics only when those lanes are enabled.

## Guardrails

Telemetry must not contain raw credentials, private prompt material beyond approved retention, unredacted personal data, or unrestricted tool payloads. Evidence references should point to controlled storage rather than duplicating sensitive content.

## Promotion dashboard

A CANARY-to-LIMITED recommendation requires:

- no unresolved critical incidents;
- zero orphaned authority leases;
- complete receipt correlation for sampled writes;
- successful rollback evidence;
- stable cost and context behavior against the prior baseline.

Performance improvement cannot override failed authority or evidence controls.