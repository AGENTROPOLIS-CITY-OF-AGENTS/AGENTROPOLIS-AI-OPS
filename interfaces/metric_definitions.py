"""Canonical metric definitions and guard notes for HERMES telemetry.

Definitions are verbatim from the canon doctrine:
wiredchaos/agentropolis docs/HERMES_EXECUTION_DISCIPLINE_AND_CONTEXT_GOVERNOR.md
section 'Thermodynamic observability'.

Guard notes encode the doctrine's no-unsupported-claims rules: benchmark and
quality claims are hardware-specific evidence, never universal guarantees.
"""

from __future__ import annotations

from typing import Dict

# Verbatim definitions from the canon doctrine (Thermodynamic observability).
CANONICAL_METRIC_DEFINITIONS: Dict[str, str] = {
    "token_energy": "tokens consumed per accepted result",
    "compute_energy": "CPU, GPU, accelerator time, and energy per accepted result",
    "context_churn": "repeatedly loaded and discarded context",
    "coordination_friction": "overhead spent routing and reconciling agents",
    "semantic_drift": "deviation from approved objective and constraints",
    "memory_entropy": "duplication, contradiction, staleness, and unresolved conflicts",
    "correction_load": "rework caused by preventable errors",
    "compression_loss": "decision-relevant information lost during compaction",
    "tool_failure_heat": "resource expenditure on failed calls and retries",
    "useful_work_ratio": "verified value divided by total resource expenditure",
}

# No-unsupported-claims rules. These are guard notes, not measured values:
# they exist to prevent unsupported performance or quality claims.
NO_UNSUPPORTED_CLAIMS_RULES: Dict[str, str] = {
    "vram_production_readiness": "12GB VRAM does NOT equal production readiness",
    "low_memory_quality": "low-memory execution does NOT equal full model quality",
    "benchmark_hardware_specificity": "one DGX Spark benchmark does NOT apply to other hardware",
    "preview_vs_canonical": "a faster preview profile is NOT equivalent to canonical final output",
}

# Alias kept for readability; guard notes ARE the no-unsupported-claims rules.
GUARD_NOTES: Dict[str, str] = NO_UNSUPPORTED_CLAIMS_RULES


def metric_definition(metric: str) -> str:
    """Return the canonical definition for a metric key.

    Raises KeyError for unknown metric keys.
    """
    return CANONICAL_METRIC_DEFINITIONS[metric]
