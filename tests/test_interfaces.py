"""Contract tests for the interfaces package (runtime-checkable Protocols).

Implements tiny in-test fake collectors that must satisfy the Protocols in
interfaces/collectors.py, and verifies the canonical metric definitions and
guard notes in interfaces/metric_definitions.py.

Run from the repository root:

    uv run --with jsonschema python -m unittest discover -s tests -v
"""

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from interfaces.collectors import (  # noqa: E402
    BenchmarkRegistry,
    ContextTelemetryCollector,
    ModelWindowDiscovery,
)
from interfaces.metric_definitions import (  # noqa: E402
    CANONICAL_METRIC_DEFINITIONS,
    GUARD_NOTES,
    NO_UNSUPPORTED_CLAIMS_RULES,
    metric_definition,
)


class FakeModelWindowDiscovery:
    """Tiny in-test implementation of ModelWindowDiscovery."""

    def __init__(self, advertised=128000, runtime=96000):
        self.advertised_context_limit = advertised
        self.runtime_context_limit = runtime


class FakeContextTelemetryCollector:
    """Tiny in-test implementation of ContextTelemetryCollector."""

    def collect(self):
        return {
            "schema_version": "1.0.0",
            "model_identifier": "deepseek-v4-flash-0731",
            "model_provider": "nous",
            "runtime_context_limit": 96000,
            "advertised_context_limit": 128000,
            "effective_context_budget": 88000,
            "current_context_usage": 31000,
            "output_reserve": 8000,
            "safety_reserve": 8000,
            "token_input": 42000,
            "token_output": 6300,
            "tool_call_count": 14,
            "tool_failure_count": 1,
            "retries": 2,
            "latency": 1840.0,
            "compute_duration": 92.4,
            "provider_cost": 0.0132,
            "gpu_cpu_profile": "cpu:8c/16g",
            "semantic_drift_score": 0.03,
            "context_churn_score": 0.12,
            "coordination_friction_score": 0.07,
            "correction_load": 2,
            "compression_loss": 0.01,
            "useful_work_ratio": 0.81,
            "benchmark_verification_state": "UNVERIFIED",
        }


class FakeBenchmarkRegistry:
    """Tiny in-test implementation of BenchmarkRegistry."""

    def __init__(self):
        self._store = {}

    def store(self, receipt):
        receipt_id = receipt.get("receipt_id", f"R{len(self._store) + 1}")
        self._store[receipt_id] = receipt
        return receipt_id

    def lookup(self, model_version, hardware):
        return [
            r
            for r in self._store.values()
            if r.get("model_version") == model_version and r.get("gpu") == hardware
        ]

    def mark_reproduced_internally(self, receipt_id):
        self._store[receipt_id]["reproduced_internally"] = True


class TestProtocolContracts(unittest.TestCase):
    def test_model_window_discovery_is_runtime_checkable(self):
        fake = FakeModelWindowDiscovery(advertised=128000, runtime=96000)
        self.assertIsInstance(fake, ModelWindowDiscovery)
        self.assertEqual(fake.advertised_context_limit, 128000)
        self.assertEqual(fake.runtime_context_limit, 96000)

    def test_context_telemetry_collector_is_runtime_checkable(self):
        fake = FakeContextTelemetryCollector()
        self.assertIsInstance(fake, ContextTelemetryCollector)
        record = fake.collect()
        self.assertIsInstance(record, dict)
        self.assertEqual(record["model_identifier"], "deepseek-v4-flash-0731")
        self.assertIn("effective_context_budget", record)

    def test_benchmark_registry_is_runtime_checkable(self):
        fake = FakeBenchmarkRegistry()
        self.assertIsInstance(fake, BenchmarkRegistry)
        receipt_id = fake.store(
            {
                "receipt_id": "R-100",
                "model_version": "wan2.1-14b",
                "gpu": "RTX 4090",
                "reproduced_internally": False,
            }
        )
        self.assertEqual(receipt_id, "R-100")
        hits = fake.lookup("wan2.1-14b", "RTX 4090")
        self.assertEqual(len(hits), 1)
        fake.mark_reproduced_internally("R-100")
        self.assertTrue(fake._store["R-100"]["reproduced_internally"])

    def test_protocols_are_runtime_checkable(self):
        # Runtime-checkability is a hard requirement of the contract so
        # fakes and real collectors can be verified without external deps.
        # @runtime_checkable sets _is_runtime_protocol on the class.
        for proto in (ModelWindowDiscovery, ContextTelemetryCollector, BenchmarkRegistry):
            self.assertTrue(proto._is_runtime_protocol, f"{proto.__name__} must be runtime-checkable")


class TestMetricDefinitions(unittest.TestCase):
    def test_canonical_metric_definitions_verbatim(self):
        expected = {
            "token_energy": "tokens consumed per accepted result",
            "context_churn": "repeatedly loaded and discarded context",
            "coordination_friction": "overhead spent routing and reconciling agents",
            "correction_load": "rework caused by preventable errors",
            "compression_loss": "decision-relevant information lost during compaction",
            "useful_work_ratio": "verified value divided by total resource expenditure",
        }
        for key, definition in expected.items():
            self.assertEqual(CANONICAL_METRIC_DEFINITIONS[key], definition)
            self.assertEqual(metric_definition(key), definition)

    def test_metric_definition_unknown_key_raises(self):
        with self.assertRaises(KeyError):
            metric_definition("not_a_metric")

    def test_guard_notes_present(self):
        self.assertIn("vram_production_readiness", NO_UNSUPPORTED_CLAIMS_RULES)
        self.assertIn("low_memory_quality", NO_UNSUPPORTED_CLAIMS_RULES)
        self.assertIn("benchmark_hardware_specificity", NO_UNSUPPORTED_CLAIMS_RULES)
        self.assertIn("preview_vs_canonical", NO_UNSUPPORTED_CLAIMS_RULES)

    def test_guard_notes_assert_no_equivalences(self):
        # Guard notes must never be softened into "close enough" claims.
        for note in NO_UNSUPPORTED_CLAIMS_RULES.values():
            self.assertIn("NOT", note.upper())


class TestCollectorOutputAgainstSchema(unittest.TestCase):
    """The fake collector's output must validate against the schema."""

    def test_collect_output_validates_against_context_telemetry_schema(self):
        from jsonschema import Draft202012Validator

        with (REPO_ROOT / "schemas" / "context-telemetry.schema.json").open(
            "r", encoding="utf-8"
        ) as fh:
            schema = json.load(fh)
        validator = Draft202012Validator(schema)
        record = FakeContextTelemetryCollector().collect()
        errors = list(validator.iter_errors(record))
        self.assertEqual(errors, [], f"collect() output must match schema: {[e.message for e in errors]}")


if __name__ == "__main__":
    unittest.main()
