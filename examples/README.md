# Examples

Runnable scripts demonstrating VitaGraph's library API and CLI, layered
from lowest-level to highest-level:

| Script | What it shows |
| --- | --- |
| [`generate_dataset.py`](generate_dataset.py) | `SyntheticCohortGenerator` → a reproducible synthetic tabular dataset (CSV) |
| [`train_model.py`](train_model.py) | `BioAgeEstimator` → training/cross-validating/comparing all three model backends |
| [`visualize_graph.py`](visualize_graph.py) | `BioSignalProcessor` + `KnowledgeGraph` + `visualization` → build and render one person's graph |
| [`cli_demo.py`](cli_demo.py) | The `vitagraph` console script driven end-to-end (`run` → `train` → `predict`) |

## Running

```bash
pip install -e ".[dev]"

python examples/generate_dataset.py --samples 1000 --output outputs/synthetic_cohort.csv
python examples/train_model.py --samples 1500 --output models/bio_age_demo.joblib
python examples/visualize_graph.py --person-id P001 --days 14 --output-dir outputs/graph_demo
python examples/cli_demo.py --output-dir outputs/cli_demo
```

All scripts accept `--seed` (where applicable) for fully reproducible
output, consistent with the rest of the project — see
[`docs/METHODOLOGY.md`](../docs/METHODOLOGY.md).

> **Reminder:** every input and output here is synthetic. See the
> [README disclaimer](../README.md#-important-disclaimer) before using
> any of this as a template for real health data pipelines.
