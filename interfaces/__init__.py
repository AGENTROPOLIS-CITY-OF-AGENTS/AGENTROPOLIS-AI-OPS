"""HERMES Execution Discipline telemetry collection interfaces.

Stdlib-only (typing.Protocol) contracts for collecting context telemetry,
discovering model context windows, and recording benchmark receipts.
Canon: wiredchaos/agentropolis docs/HERMES_EXECUTION_DISCIPLINE_AND_CONTEXT_GOVERNOR.md.
"""

from interfaces.collectors import (
    BenchmarkRegistry,
    ContextTelemetryCollector,
    ModelWindowDiscovery,
)
from interfaces.metric_definitions import (
    CANONICAL_METRIC_DEFINITIONS,
    GUARD_NOTES,
    NO_UNSUPPORTED_CLAIMS_RULES,
    metric_definition,
)

__all__ = [
    "BenchmarkRegistry",
    "CANONICAL_METRIC_DEFINITIONS",
    "ContextTelemetryCollector",
    "GUARD_NOTES",
    "ModelWindowDiscovery",
    "NO_UNSUPPORTED_CLAIMS_RULES",
    "metric_definition",
]
