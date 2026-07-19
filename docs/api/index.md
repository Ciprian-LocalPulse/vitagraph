# API Reference

Auto-generated from docstrings (Google style) in `src/vitagraph/` via
[mkdocstrings](https://mkdocstrings.github.io/). This is the canonical,
always-up-to-date reference — narrative usage guides live in the
[Tutorial notebook](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/notebooks/Tutorial.ipynb)
and [`examples/`](https://github.com/Ciprian-LocalPulse/vitagraph/tree/main/examples).

## Modules

| Module | Purpose |
| --- | --- |
| [`pipeline`](pipeline.md) | End-to-end orchestration: simulate → graph → train → predict |
| [`synthetic_data`](synthetic_data.md) | `SyntheticCohortGenerator` — tabular synthetic cohort + label |
| [`bio_signal_processor`](bio_signal_processor.md) | Synthetic raw time-series (heart rate, HRV, sleep) |
| [`knowledge_graph`](knowledge_graph.md) | `KnowledgeGraph` — typed graph construction, query, export |
| [`bio_age_estimator`](bio_age_estimator.md) | `BioAgeEstimator` — train/evaluate/persist regression models |
| [`visualization`](visualization.md) | Static PNG rendering of a person's subgraph |
| [`config`](config.md) | Central, documented dataclasses for every tunable constant |
| [`cli`](cli.md) | The `vitagraph` command-line interface |

## Public package-level exports

```python
from vitagraph import (
    BioAgeEstimator,
    BioSignalProcessor,
    KnowledgeGraph,
    SyntheticCohortGenerator,
)
```

These four classes are the intended entry points for library usage; see
[`vitagraph/__init__.py`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/src/vitagraph/__init__.py)
for the exact `__all__` contract that this project treats as its public
API surface for semantic-versioning purposes (see
[`CHANGELOG.md`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/CHANGELOG.md)).
