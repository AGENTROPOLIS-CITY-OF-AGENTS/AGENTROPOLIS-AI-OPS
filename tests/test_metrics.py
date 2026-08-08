import math

import numpy as np
import pytest

from agentropolis_ai_ops import (
    council_weighted_score,
    drift_distance,
    normalized_entropy,
    rolling_stats,
)


def test_rolling_stats_tracks_latest_point_in_each_window():
    result = rolling_stats([1, 2, 3, 4], window=3)

    assert np.isnan(result.mean[:2]).all()
    assert result.mean[2] == pytest.approx(2.0)
    assert result.mean[3] == pytest.approx(3.0)
    assert result.std[2] == pytest.approx(np.std([1, 2, 3]))
    assert result.z_score[2] == pytest.approx((3 - 2) / np.std([1, 2, 3]))


def test_rolling_stats_zero_variance_is_stable():
    result = rolling_stats([5, 5, 5], window=3)
    assert result.std[-1] == 0.0
    assert result.z_score[-1] == 0.0


def test_drift_distance_reports_zero_for_identical_vectors():
    result = drift_distance([1, 2, 3], [1, 2, 3])
    assert result.l2 == 0.0
    assert result.cosine_distance == pytest.approx(0.0)
    assert result.max_abs_delta == 0.0


def test_drift_distance_handles_zero_vector_without_nan():
    result = drift_distance([0, 0], [1, 0])
    assert result.cosine_distance == 1.0
    assert math.isfinite(result.cosine_distance)


def test_entropy_uniform_distribution_is_maximal():
    result = normalized_entropy([1, 1, 1, 1])
    assert result.entropy_bits == pytest.approx(2.0)
    assert result.normalized_entropy == pytest.approx(1.0)
    assert result.effective_states == pytest.approx(4.0)


def test_entropy_single_state_is_zero():
    result = normalized_entropy([1, 0, 0])
    assert result.entropy_bits == pytest.approx(0.0)
    assert result.normalized_entropy == pytest.approx(0.0)
    assert result.effective_states == pytest.approx(1.0)


def test_council_weighted_score_normalizes_weights():
    result = council_weighted_score([0.9, 0.6, 0.3], [2, 1, 1])
    assert result.score == pytest.approx(0.675)
    assert result.normalized_weights.tolist() == pytest.approx([0.5, 0.25, 0.25])
    assert result.contributions.tolist() == pytest.approx([0.45, 0.15, 0.075])


def test_rejects_non_finite_input():
    with pytest.raises(ValueError):
        drift_distance([1, np.nan], [1, 2])
