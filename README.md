# agentropolis-ai-ops

AI operations layer for AGENTROPOLIS: context usage tracking, model routing, benchmark awareness, cost visibility, provider health, agent performance, queues, telemetry, alerts, recovery, and operational dashboards.

## Deterministic numerical compute lane

AGENTROPOLIS uses NumPy below the model layer for numerical work that should not depend on probabilistic language-model arithmetic.

```text
Model / Council
  -> requests analysis
  -> deterministic NumPy primitive
  -> Policy / Risk validation
  -> model interprets structured result
  -> receipt + telemetry
```

The model decides **what** needs analysis. The deterministic lane performs the calculation. Policy and risk systems decide whether a result may influence execution. This package does not grant execution authority.

### Initial primitives

- `rolling_stats(values, window)` — rolling population mean, standard deviation, and z-score for telemetry and anomaly baselines.
- `drift_distance(baseline, current)` — L2 distance, cosine distance, and maximum absolute delta for agent/model/system drift.
- `normalized_entropy(probabilities)` — Shannon entropy, normalized entropy, and effective-state count for thermodynamic observability.
- `council_weighted_score(scores, weights)` — explicit weighted numerical aggregation for council scoring without conflating scoring with authorization.

### Example

```python
from agentropolis_ai_ops import (
    council_weighted_score,
    drift_distance,
    normalized_entropy,
    rolling_stats,
)

telemetry = rolling_stats([100, 101, 99, 150], window=3)
drift = drift_distance([0.2, 0.4, 0.4], [0.1, 0.3, 0.6])
entropy = normalized_entropy([0.70, 0.20, 0.10])
council = council_weighted_score([0.9, 0.7, 0.4], [3, 2, 1])
```

Every primitive validates dimensionality and finite numeric inputs. Numerical outputs should be wrapped by the calling service with provenance, input hashes or references, model/tool identity, policy state, and timestamps before becoming an AGENTROPOLIS action receipt.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
```

## Architecture boundary

`wiredchaos/agentropolis-ai-ops` owns model intelligence, context usage, benchmark awareness, cost analytics, and agent-performance measurement. Runtime supervision and broader operational authority remain in `wiredchaos/AGENTROPOLIS-OPS`; policy and assurance remain in the appropriate governed lanes.
