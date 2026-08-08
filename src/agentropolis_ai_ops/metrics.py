from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class RollingStatsResult:
    mean: FloatArray
    std: FloatArray
    z_score: FloatArray


@dataclass(frozen=True)
class DriftResult:
    l2: float
    cosine_distance: float
    max_abs_delta: float


@dataclass(frozen=True)
class EntropyResult:
    entropy_bits: float
    normalized_entropy: float
    effective_states: float


@dataclass(frozen=True)
class CouncilScoreResult:
    score: float
    normalized_weights: FloatArray
    contributions: FloatArray


def _as_1d(values: ArrayLike, *, name: str) -> FloatArray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a 1-D numeric sequence")
    if array.size == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def rolling_stats(values: ArrayLike, window: int) -> RollingStatsResult:
    """Compute rolling population mean/std and z-score with deterministic NumPy math.

    Positions before a full window is available are returned as NaN.
    Zero-variance windows receive a z-score of 0.0 for an unchanged observation and
    +/-inf is intentionally avoided.
    """
    x = _as_1d(values, name="values")
    if window < 2:
        raise ValueError("window must be at least 2")
    if window > x.size:
        raise ValueError("window cannot exceed the number of values")

    windows = np.lib.stride_tricks.sliding_window_view(x, window_shape=window)
    means = windows.mean(axis=1)
    stds = windows.std(axis=1, ddof=0)
    latest = windows[:, -1]
    z = np.divide(
        latest - means,
        stds,
        out=np.zeros_like(means),
        where=stds > 0,
    )

    pad = np.full(window - 1, np.nan, dtype=np.float64)
    return RollingStatsResult(
        mean=np.concatenate((pad, means)),
        std=np.concatenate((pad, stds)),
        z_score=np.concatenate((pad, z)),
    )


def drift_distance(baseline: ArrayLike, current: ArrayLike) -> DriftResult:
    """Measure vector drift without delegating arithmetic to an LLM."""
    a = _as_1d(baseline, name="baseline")
    b = _as_1d(current, name="current")
    if a.shape != b.shape:
        raise ValueError("baseline and current must have the same shape")

    delta = b - a
    l2 = float(np.linalg.norm(delta))
    max_abs_delta = float(np.max(np.abs(delta)))

    a_norm = float(np.linalg.norm(a))
    b_norm = float(np.linalg.norm(b))
    if a_norm == 0.0 and b_norm == 0.0:
        cosine_distance = 0.0
    elif a_norm == 0.0 or b_norm == 0.0:
        cosine_distance = 1.0
    else:
        similarity = float(np.dot(a, b) / (a_norm * b_norm))
        similarity = float(np.clip(similarity, -1.0, 1.0))
        cosine_distance = 1.0 - similarity

    return DriftResult(
        l2=l2,
        cosine_distance=cosine_distance,
        max_abs_delta=max_abs_delta,
    )


def normalized_entropy(probabilities: ArrayLike) -> EntropyResult:
    """Return Shannon entropy, normalized entropy, and effective state count."""
    p = _as_1d(probabilities, name="probabilities")
    if np.any(p < 0):
        raise ValueError("probabilities cannot contain negative values")

    total = float(p.sum())
    if total <= 0:
        raise ValueError("probabilities must have a positive total")
    p = p / total
    nonzero = p[p > 0]
    entropy_bits = float(-np.sum(nonzero * np.log2(nonzero)))
    max_entropy = float(np.log2(p.size)) if p.size > 1 else 0.0
    normalized = entropy_bits / max_entropy if max_entropy > 0 else 0.0
    effective_states = float(2.0**entropy_bits)

    return EntropyResult(
        entropy_bits=entropy_bits,
        normalized_entropy=normalized,
        effective_states=effective_states,
    )


def council_weighted_score(
    scores: ArrayLike,
    weights: ArrayLike,
    *,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> CouncilScoreResult:
    """Combine bounded council scores using explicit normalized weights.

    This function computes only the numeric aggregation. Authorization, approval,
    and execution remain outside this module in the policy/risk lane.
    """
    s = _as_1d(scores, name="scores")
    w = _as_1d(weights, name="weights")
    if s.shape != w.shape:
        raise ValueError("scores and weights must have the same shape")
    if maximum <= minimum:
        raise ValueError("maximum must be greater than minimum")
    if np.any((s < minimum) | (s > maximum)):
        raise ValueError("scores fall outside the configured bounds")
    if np.any(w < 0):
        raise ValueError("weights cannot contain negative values")

    weight_total = float(w.sum())
    if weight_total <= 0:
        raise ValueError("weights must have a positive total")

    normalized_weights = w / weight_total
    contributions = s * normalized_weights
    return CouncilScoreResult(
        score=float(contributions.sum()),
        normalized_weights=normalized_weights,
        contributions=contributions,
    )
