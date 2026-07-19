# Getting Started

This page gets you from zero to a completed VitaGraph pipeline run in
under five minutes.

## 1. Install

**Production install:**

```bash
pip install vitagraph
```

**From source (for development, examples, notebooks, docs):**

```bash
git clone https://github.com/Ciprian-LocalPulse/vitagraph.git
cd vitagraph
pip install -e ".[dev]"
```

Requirements: Python 3.10+. Runtime dependencies (`numpy`, `pandas`,
`networkx`, `scikit-learn`, `joblib`, `matplotlib`) are installed
automatically.

**Or use Docker** — no local Python setup needed:

```bash
docker build -t vitagraph .
docker run --rm -v "$(pwd)/outputs:/home/vitagraph/outputs" vitagraph run --individuals 5
```

## 2. Run the full pipeline (CLI)

```bash
vitagraph run --individuals 5 --days 30 --output-dir ./outputs
```

This single command:

1. Simulates 5 synthetic individuals' biometric time series (30 days each)
2. Builds a knowledge graph connecting person → biometric data → environmental factors
3. Trains a gradient-boosting biological-age estimator
4. Cross-validates and evaluates on a held-out split
5. Predicts biological age for each simulated person
6. Attaches rule-based intervention recommendations to the graph
7. Exports the model, the graph (JSON + GraphML), and a summary CSV to `./outputs/`

Check `./outputs/individuals_summary.csv` for the per-person results.

## 3. Train and predict independently

```bash
# Train a standalone model
vitagraph train --samples 1000 --model random_forest --output models/bio_age.joblib

# Predict for one synthetic person
vitagraph predict \
  --model-path models/bio_age.joblib \
  --chronological-age 40 \
  --heart-rate 72 \
  --hrv 50 \
  --sleep-hours 7 \
  --activity-level 0.6 \
  --environmental-exposure 0.3
```

## 4. Use it as a library

```python
from vitagraph import SyntheticCohortGenerator, BioAgeEstimator
from sklearn.model_selection import train_test_split

# Generate synthetic data
cohort = SyntheticCohortGenerator(seed=42).generate(num_samples=500)
X, y = cohort.drop(columns=["biological_age"]), cohort["biological_age"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train and evaluate
estimator = BioAgeEstimator(model_type="gradient_boosting")
estimator.train(X_train, y_train)
print(estimator.evaluate(X_test, y_test))
```

See the [Architecture](Architecture) page for how this fits together,
and the repository's [`README.md`](https://github.com/Ciprian-LocalPulse/vitagraph#-library-api)
for the complete library API (knowledge graph, signal processing, full
pipeline orchestration).

## 5. Explore interactively

```bash
pip install -e ".[dev]"
jupyter notebook notebooks/Tutorial.ipynb
```

The three notebooks under [`notebooks/`](https://github.com/Ciprian-LocalPulse/vitagraph/tree/main/notebooks)
are executed and committed with outputs, so you can read them
statically on GitHub or run them yourself:

- **`Tutorial.ipynb`** — guided walkthrough of every component
- **`Research.ipynb`** — model comparison, learning curves, seed sensitivity
- **`Examples.ipynb`** — notebook mirror of the `examples/` scripts

## 6. Run the test suite (development)

```bash
pytest tests/ -v --cov=vitagraph
```

## 7. Build the docs site locally

```bash
pip install -e ".[docs]"
mkdocs serve
# open http://127.0.0.1:8000
```

or via Docker: `docker compose --profile docs up docs`.

## Next steps

- **[Architecture](Architecture)** — understand how the pieces connect
- **[Methodology and Scope](Methodology-and-Scope)** — understand exactly
  what each number means (and doesn't mean)
- **[FAQ and Troubleshooting](FAQ-and-Troubleshooting)** — common
  questions and common errors
