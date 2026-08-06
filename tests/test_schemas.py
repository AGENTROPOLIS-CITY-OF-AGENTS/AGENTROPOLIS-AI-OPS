"""Schema validation tests for HERMES Execution Discipline telemetry schemas.

Run from the repository root:

    uv run --with jsonschema python -m unittest discover -s tests -v

Requires only `uv`; jsonschema is provisioned ephemerally by uv and no
dependency files are added to the repository.
"""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"


def load_schema(name):
    with (SCHEMAS_DIR / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


class SchemaTestCase(unittest.TestCase):
    """Base class: load a schema and build a draft 2020-12 validator."""

    schema_file = None

    @classmethod
    def setUpClass(cls):
        assert cls.schema_file, "subclass must set schema_file"
        cls.schema = load_schema(cls.schema_file)
        cls.validator = Draft202012Validator(cls.schema)

    def assert_valid(self, instance, msg=None):
        errors = sorted(self.validator.iter_errors(instance), key=lambda e: list(e.path))
        self.assertEqual(errors, [], msg or f"expected valid, got: {[e.message for e in errors]}")

    def assert_invalid(self, instance, msg=None):
        errors = list(self.validator.iter_errors(instance))
        self.assertNotEqual(errors, [], msg or "expected invalid, but instance validated")


class TestThermodynamicMetricsSchema(SchemaTestCase):
    schema_file = "thermodynamic-metrics.schema.json"

    def make_measure(self, value=1.0, unit="tokens", state="NOMINAL", provenance="test"):
        return {"value": value, "unit": unit, "state": state, "provenance": provenance}

    def valid_instance(self):
        return {
            "schema_version": "1.0.0",
            "token_energy": self.make_measure(1200, "tokens"),
            "compute_energy": self.make_measure(45.2, "s"),
            "context_churn": self.make_measure(0.4, "ratio", "ELEVATED"),
            "coordination_friction": self.make_measure(0.2, "ratio"),
            "semantic_drift": self.make_measure(0.05, "ratio"),
            "memory_entropy": self.make_measure(0.1, "ratio"),
            "correction_load": self.make_measure(3, "retries"),
            "compression_loss": self.make_measure(0.02, "ratio"),
            "tool_failure_heat": self.make_measure(2, "calls"),
            "useful_work_ratio": self.make_measure(0.85, "ratio"),
        }

    def test_positive_instance_valid(self):
        self.assert_valid(self.valid_instance())

    def test_positive_all_states_valid(self):
        instance = self.valid_instance()
        for state in ("NOMINAL", "ELEVATED", "CRITICAL", "UNKNOWN"):
            instance["token_energy"]["state"] = state
            self.assert_valid(instance, f"state {state} should be valid")

    def test_negative_non_numeric_value(self):
        instance = self.valid_instance()
        instance["token_energy"]["value"] = "lots"
        self.assert_invalid(instance)

    def test_negative_unknown_health_state(self):
        instance = self.valid_instance()
        instance["token_energy"]["state"] = "SPARKLY"
        self.assert_invalid(instance)

    def test_negative_extra_property_rejected(self):
        instance = self.valid_instance()
        instance["magic_number"] = 42
        self.assert_invalid(instance)

    def test_negative_missing_measure(self):
        instance = self.valid_instance()
        del instance["useful_work_ratio"]
        self.assert_invalid(instance)

    def test_negative_bad_schema_version(self):
        instance = self.valid_instance()
        instance["schema_version"] = "2.0.0"
        self.assert_invalid(instance)


class TestBenchmarkRegistrySchema(SchemaTestCase):
    schema_file = "benchmark-registry.schema.json"

    def valid_instance(self, **overrides):
        instance = {
            "schema_version": "1.0.0",
            "checkpoint": "wan2.1-14b-720p",
            "model_version": "wan2.1-14b",
            "adapter_version": "none",
            "quantization": "bf16",
            "pruning": "none",
            "attention_backend": "flash-attn2",
            "cache_method": "vllm-paged",
            "steps": 28,
            "resolution": "1280x720",
            "frame_count": 121,
            "duration": 5.0,
            "audio_mode": "mute",
            "gpu": "RTX 4090",
            "vram": 24,
            "host_ram": 64,
            "runtime": "comfyui",
            "software_versions": {"torch": "2.4.0", "diffusers": "0.30.0"},
            "measured_latency": 42.5,
            "quality_evidence": "CLIP score 0.78, VBench 0.71",
            "reproduced_internally": False,
            "benchmark_state": "UNVERIFIED",
        }
        instance.update(overrides)
        return instance

    def test_positive_instance_valid(self):
        self.assert_valid(self.valid_instance())

    def test_positive_reproduced_internally_valid(self):
        self.assert_valid(
            self.valid_instance(reproduced_internally=True, benchmark_state="VERIFIED")
        )

    def test_negative_missing_required_benchmark_field(self):
        instance = self.valid_instance()
        del instance["checkpoint"]
        self.assert_invalid(instance)

    def test_negative_reproduced_internally_omitted(self):
        instance = self.valid_instance()
        del instance["reproduced_internally"]
        self.assert_invalid(instance)

    def test_negative_community_claim_not_unverified(self):
        # Rule: community claims remain UNVERIFIED until reproduced internally.
        instance = self.valid_instance(reproduced_internally=False, benchmark_state="VERIFIED")
        self.assert_invalid(instance)

    def test_negative_unknown_benchmark_state(self):
        instance = self.valid_instance(benchmark_state="MAYBE")
        self.assert_invalid(instance)

    def test_negative_non_numeric_latency(self):
        instance = self.valid_instance(measured_latency="fast")
        self.assert_invalid(instance)

    def test_negative_extra_property_rejected(self):
        instance = self.valid_instance()
        instance["hallucinated_metric"] = True
        self.assert_invalid(instance)


class TestContextTelemetrySchema(SchemaTestCase):
    schema_file = "context-telemetry.schema.json"

    def valid_instance(self, **overrides):
        instance = {
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
        instance.update(overrides)
        return instance

    def test_positive_instance_valid(self):
        self.assert_valid(self.valid_instance())

    def test_negative_non_numeric_value(self):
        instance = self.valid_instance(token_input="many")
        self.assert_invalid(instance)

    def test_negative_missing_required_field(self):
        instance = self.valid_instance()
        del instance["effective_context_budget"]
        self.assert_invalid(instance)

    def test_negative_extra_property_rejected(self):
        instance = self.valid_instance()
        instance["vibe"] = "excellent"
        self.assert_invalid(instance)

    def test_negative_unknown_verification_state(self):
        instance = self.valid_instance(benchmark_verification_state="TRUST_BRO")
        self.assert_invalid(instance)


class TestOptimizationProfileSchema(SchemaTestCase):
    schema_file = "optimization-profile.schema.json"

    def valid_instance(self, **overrides):
        instance = {
            "schema_version": "1.0.0",
            "optimization_policy": {
                "canonical_profile_required": True,
                "change_one_variable_at_a_time": True,
                "compare_against_baseline": True,
                "benchmark_per_device": True,
                "reject_unverified_quality_regressions": True,
            },
            "profiles": [
                {
                    "profile_id": "P-001",
                    "profile_class": "CANONICAL_FINAL",
                    "model_family": "wan2.1-14b",
                    "quality": "reference",
                    "speed": "baseline",
                    "hardware": "dgx-spark",
                    "policy_tradeoffs": "none",
                    "approval_state": "APPROVED",
                    "benchmark_state": "VERIFIED",
                }
            ],
            "routing_receipts": [
                {
                    "routing_receipt_id": "RR-001",
                    "selected_profile": "P-001",
                    "model_family": "wan2.1-14b",
                    "execution_location": "LOCAL",
                    "effective_limits": "88000 tokens",
                    "fallback_reason": "",
                    "hardware_snapshot": "dgx-spark",
                    "benchmark_state": "VERIFIED",
                    "policy_state": "compliant",
                    "approval_state": "APPROVED",
                    "routed_at": "2026-08-05T12:00:00Z",
                }
            ],
        }
        instance.update(overrides)
        return instance

    def test_positive_instance_valid(self):
        self.assert_valid(self.valid_instance())

    def test_negative_unknown_profile_class(self):
        instance = self.valid_instance()
        instance["profiles"][0]["profile_class"] = "SUPER_FAST"
        self.assert_invalid(instance)

    def test_negative_unknown_execution_location(self):
        instance = self.valid_instance()
        instance["routing_receipts"][0]["execution_location"] = "THE_CLOUD_OF_DREAMS"
        self.assert_invalid(instance)

    def test_negative_missing_required_profile_field(self):
        instance = self.valid_instance()
        del instance["profiles"][0]["model_family"]
        self.assert_invalid(instance)

    def test_negative_extra_property_rejected(self):
        instance = self.valid_instance()
        instance["profiles"][0]["lucky_number"] = 7
        self.assert_invalid(instance)

    def test_negative_missing_policy_flag(self):
        instance = self.valid_instance()
        del instance["optimization_policy"]["benchmark_per_device"]
        self.assert_invalid(instance)


if __name__ == "__main__":
    unittest.main()
