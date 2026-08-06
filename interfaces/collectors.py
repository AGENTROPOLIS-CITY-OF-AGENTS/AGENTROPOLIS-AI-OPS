"""Collection interfaces for HERMES Execution Discipline telemetry.

Stdlib-only contracts (typing.Protocol, runtime-checkable). No external
dependencies. Implementations may live in any runtime; these Protocols define
the shape consumers must rely on.

Canon: wiredchaos/agentropolis
  docs/HERMES_EXECUTION_DISCIPLINE_AND_CONTEXT_GOVERNOR.md
Schemas: ../schemas/*.schema.json (JSON Schema draft 2020-12)
"""

from __future__ import annotations

from typing import Any, Dict, List, Protocol, runtime_checkable

CONTEXT_TELEMETRY_SCHEMA = "https://agentropolis.local/schemas/context-telemetry.schema.json"
BENCHMARK_REGISTRY_SCHEMA = "https://agentropolis.local/schemas/benchmark-registry.schema.json"
THERMODYNAMIC_METRICS_SCHEMA = "https://agentropolis.local/schemas/thermodynamic-metrics.schema.json"
OPTIMIZATION_PROFILE_SCHEMA = "https://agentropolis.local/schemas/optimization-profile.schema.json"


@runtime_checkable
class ModelWindowDiscovery(Protocol):
    """Discovers the effective context window of a model at runtime.

    A model's advertised context window is not the same as the usable runtime
    workspace. Both limits must be discovered, never assumed from a fixed
    value such as 64,000 tokens.
    """

    advertised_context_limit: int
    runtime_context_limit: int


@runtime_checkable
class ContextTelemetryCollector(Protocol):
    """Collects a context-telemetry record for one task execution.

    The returned mapping must conform to
    https://agentropolis.local/schemas/context-telemetry.schema.json
    """

    def collect(self) -> Dict[str, Any]:
        """Return one context telemetry record (dict) matching the schema."""
        ...


@runtime_checkable
class BenchmarkRegistry(Protocol):
    """Registry of exact, hardware-specific benchmark receipts.

    Benchmarks are hardware-specific evidence, not universal guarantees.
    Community claims remain UNVERIFIED until reproduced internally.
    """

    def store(self, receipt: Dict[str, Any]) -> str:
        """Persist a benchmark receipt; returns the receipt id."""
        ...

    def lookup(self, model_version: str, hardware: str) -> List[Dict[str, Any]]:
        """Return stored receipts matching model version and hardware."""
        ...

    def mark_reproduced_internally(self, receipt_id: str) -> None:
        """Mark a receipt as reproduced internally on stated hardware."""
        ...
