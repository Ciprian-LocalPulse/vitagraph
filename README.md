# VitaGraph: Decentralized Bio-Signal Knowledge Graph for Longevity & Precision Medicine

![VitaGraph Banner](assets/vitagraph_cover.png)

---

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![MIT License](https://img.shields.io/badge/license-MIT-green)
![Version 0.2.0](https://img.shields.io/badge/version-0.2.0-orange)
[![Donate](https://img.shields.io/badge/💝-Support%20Research-ff69b4)](DONATE.md)
[![GitHub](https://img.shields.io/badge/github-vitagraph-181717?logo=github)](https://github.com/Ciprian-LocalPulse/vitagraph)

---

## ⚠️ Important Disclaimer

**VitaGraph is a research reference implementation using entirely synthetic, seeded random data.** Nothing in this repository should be used for real medical, diagnostic, clinical, or therapeutic decision-making. The biological-age predictions produced by this system have not been validated against any clinical cohort and do not represent real biological age or health status.

For research context and future roadmap, see [docs/METHODOLOGY.md](docs/METHODOLOGY.md) and [docs/ROADMAP.md](docs/ROADMAP.md).

---

## 🔬 Project Overview

VitaGraph is an open-source reference framework for simulating and studying the integration of multi-source biometric data using knowledge graphs and machine learning. It demonstrates:

- **Synthetic biometric time-series generation** (heart rate, HRV, sleep, environmental exposure) with circadian and noise patterns
- **Knowledge-graph representation** of person–data–environment relationships using `networkx`
- **Graph-neural-network-inspired** biological-age regression on synthetic labels
- **Pluggable model backends** (linear, random forest, gradient boosting)
- **Full pipeline orchestration** from data simulation through model evaluation
- **CLI and library API** for research / educational workflows

The code is intentionally transparent and modular, designed for researchers and educators to understand every step, audit assumptions, and extend the framework.

---

## 📦 Installation

### From source (development)

```bash
git clone https://github.com/Ciprian-LocalPulse/vitagraph.git
cd vitagraph
pip install -e ".[dev]"
```

### Production install

```bash
pip install vitagraph
```

### Requirements

- Python 3.10+
- Dependencies: `numpy`, `pandas`, `networkx`, `scikit-learn`, `joblib`, `matplotlib`
- Development: `pytest`, `pytest-cov`, `ruff`, `black`, `mypy`

---

## 🚀 Quick Start

### Run the full pipeline

```bash
vitagraph run --individuals 5 --days 30 --output-dir ./outputs
```

This will:
1. Simulate 5 synthetic individuals' biometric time series (30 days each)
2. Build a knowledge graph connecting person → biometric data → environmental factors
3. Train a gradient-boosting biological-age estimator
4. Cross-validate and evaluate on a held-out split
5. Predict biological age for each simulated person
6. Attach rule-based Intervention recommendations to the graph
7. Export model, graph (JSON + GraphML), and a summary CSV

### Train a model independently

```bash
vitagraph train --samples 1000 --model random_forest --output models/bio_age.joblib
```

### Make a prediction using a saved model

```bash
vitagraph predict \
  --model-path models/bio_age.joblib \
  --chronological-age 40 \
  --heart-rate 72 \
  --hrv 50 \
  --sleep-hours 7 \
  --activity-level 0.6 \
  --environmental-exposure 0.3
```

---

## 📚 Library API

### Synthetic Data Generation

```python
from vitagraph import SyntheticCohortGenerator

gen = SyntheticCohortGenerator(seed=42)
cohort = gen.generate(num_samples=500)  # Returns DataFrame with features + biological_age label
```

### Signal Processing

```python
from vitagraph import BioSignalProcessor
from datetime import datetime

processor = BioSignalProcessor(seed=42)
hr = processor.generate_synthetic_heart_rate(
    num_samples=100,
    start_time=datetime(2026, 1, 1, 8, 0, 0)
)
# Lightly process (smooth + de-outlier)
hr_processed = processor.process_biometric_data(hr, "heart_rate", window=5)
```

### Knowledge Graph

```python
from vitagraph import KnowledgeGraph

kg = KnowledgeGraph()
kg.add_person_node("P001")
kg.build_from_processed_data("P001", hr_processed, sleep_processed, hrv_processed)

# Export
kg.export_to_json("graph.json")
kg.export_to_graphml("graph.graphml")

# Query
subgraph = kg.get_subgraph_for_person("P001")
info = kg.get_graph_info()  # Summary statistics
```

### Biological-Age Estimation

```python
from vitagraph import BioAgeEstimator
from sklearn.model_selection import train_test_split

estimator = BioAgeEstimator(model_type="gradient_boosting")

X, y = cohort[FEATURE_COLUMNS], cohort["biological_age"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

estimator.train(X_train, y_train)
metrics = estimator.evaluate(X_test, y_test)  # MAE, RMSE, R²
cv_scores = estimator.cross_validate(X, y, cv=5)
importance = estimator.feature_importance()

estimator.save_model("bio_age_model.joblib")  # + .json metadata sidecar
estimator.load_model("bio_age_model.joblib")

preds = estimator.predict(X_test)
```

### Full Pipeline

```python
from vitagraph.pipeline import run_pipeline
from vitagraph.config import PipelineDefaults

config = PipelineDefaults(
    num_individuals=5,
    num_sleep_days=30,
    training_samples=500,
    model_type="gradient_boosting",
    cv_folds=5,
)

result = run_pipeline(config=config, output_dir="./outputs")

print(result.individuals)  # Predictions + age gaps
print(result.test_metrics)
print(result.knowledge_graph.get_graph_info())
```

---

## 🏗️ Repository Structure

```
vitagraph/
├── src/vitagraph/
│   ├── __init__.py
│   ├── config.py                    # Centralized configuration (baselines, defaults)
│   ├── exceptions.py                # Custom exception types
│   ├── logging_config.py            # Logger factory
│   ├── synthetic_data.py            # SyntheticCohortGenerator
│   ├── bio_signal_processor.py      # BioSignalProcessor (generation + processing)
│   ├── knowledge_graph.py           # KnowledgeGraph class
│   ├── bio_age_estimator.py         # BioAgeEstimator (pluggable models)
│   ├── visualization.py             # Graph plotting (matplotlib)
│   ├── pipeline.py                  # run_pipeline() orchestration
│   └── cli.py                       # argparse CLI entry point
├── tests/
│   ├── conftest.py                  # pytest fixtures
│   ├── test_synthetic_data.py
│   ├── test_bio_signal_processor.py
│   ├── test_knowledge_graph.py
│   ├── test_bio_age_estimator.py
│   └── test_pipeline.py
├── docs/
│   ├── METHODOLOGY.md               # Research scope & methods
│   ├── ROADMAP.md                   # Future objectives (causal inference, GNNs, etc.)
│   └── API.md                       # Full API reference (auto-generated from docstrings)
├── data/                            # Place for sample anonymized datasets (if future)
├── models/                          # Trained model artifacts (not versioned)
├── pyproject.toml                   # PEP 517/518 build config
├── requirements.txt                 # Runtime dependencies
├── requirements-dev.txt             # Development dependencies
├── LICENSE                          # MIT
├── README.md                        # This file
├── CHANGELOG.md                     # Version history
└── CONTRIBUTING.md                  # Contribution guidelines
```

---

## 🧪 Testing

Run the full test suite:

```bash
pytest tests/ -v --cov=vitagraph
```

Run a specific test file:

```bash
pytest tests/test_bio_age_estimator.py -v
```

Generate a coverage report:

```bash
pytest tests/ --cov=vitagraph --cov-report=html
open htmlcov/index.html
```

---

## 🎯 Core Features

### 1. Synthetic Data Generation
- Reproducible, seeded random cohorts with realistic-shaped features
- Configurable population baselines (HR, HRV, sleep, activity, environmental exposure)
- Documented, deterministic biological-age label generation for supervised learning

### 2. Signal Processing
- Circadian-pattern simulation (heart rate dips overnight)
- Rolling-window smoothing (de-noising)
- Z-score-based outlier clipping
- Does not assume stationarity; suitable for short windows or irregular sampling

### 3. Knowledge Graph Construction
- **Node types**: Person, BiometricData, EnvironmentalFactor, Intervention
- **Edge relations**: HAS_DATA, EXPOSED_TO, HAS_RECOMMENDATION
- **Export formats**: JSON (networkx node-link), GraphML (Gephi/Cytoscape compatible)
- **Querying**: Per-person subgraph retrieval, type and relation filtering

### 4. Biological-Age Regression
- **Model backends**: Linear, Random Forest, Gradient Boosting (pluggable)
- **Metrics**: MAE, RMSE, R², cross-validation, feature importance
- **Persistence**: joblib model serialization + JSON metadata sidecar
- **Validation**: train/test split, k-fold CV, hold-out evaluation

### 5. Rule-Based Intervention Logic
- **Simple heuristic**: identifies the feature with the largest unfavorable deviation from population baseline
- **Not causal**: this is explicitly NOT the output of a causal-inference model
- **Future work**: see docs/ROADMAP.md for GNN + causal objectives

---

## 📖 Documentation

- **[docs/METHODOLOGY.md](docs/METHODOLOGY.md)**: What VitaGraph does and does not do; research scope; privacy & ethical considerations
- **[docs/ROADMAP.md](docs/ROADMAP.md)**: Near-term and long-term research objectives; Graph Neural Networks; causal inference
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: How to report issues, submit PRs, and contribute

---

## 🔗 Citation

If you use VitaGraph in your research or teaching, please cite:

```bibtex
@software{plesca2026vitagraph,
  author = {Plesca, Ciprian Stefan},
  title  = {VitaGraph: Synthetic-data reference framework for bio-signal knowledge graphs and biological-age estimation},
  year   = {2026},
  url    = {https://github.com/Ciprian-LocalPulse/vitagraph},
  note   = {Open-source research reference implementation, MIT License}
}
```

---

## 📄 License

VitaGraph is released under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 💝 Support VitaGraph Research

VitaGraph is an **open-source initiative** sustained by the research community. Your support directly funds:

- 🖥️ **Infrastructure**: Cloud hosting for data processing and model training
- 📊 **Data Quality**: Cleaning, annotation, and validation of biological datasets
- 🤖 **Model Development**: GPU compute for training advanced AI models
- 📚 **Open Science**: Publishing research freely and keeping knowledge accessible
- 🌍 **Community**: Supporting researchers and educators worldwide

### 🎁 Donate Now

**Choose your method:**

| Method | Speed | Privacy |
|--------|-------|---------|
| 🪙 [**Cryptocurrency**](DONATE.md#-cryptocurrency-fast--transparent) | Instant | Pseudonymous |
| 🏦 [**Bank Transfer**](DONATE.md#-bank-transfers-wise) | 1-3 days | Transparent |

➡️ **[Full Donation Guide →](DONATE.md)** (EUR, USD, GBP, RON, BTC, ETH)

Every contribution—from €5 to €1000+—makes a difference. **All donations directly fund research.**

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to report bugs or request features
- Code style and testing requirements
- Pull request workflow
- Recognition in the contributors list

---

## ❤️ Ways to Support

- **Donate**: [Support VitaGraph Research →](DONATE.md)
- **GitHub Stars**: ⭐ Star us on GitHub
- **Issues & PRs**: Report bugs, suggest features, or contribute code
- **Cite our work**: Use the BibTeX above in your papers
- **Spread the word**: Share with colleagues, communities, and social media

---

## 👨‍💼 Author

**Ciprian Stefan Plesca**  
GitHub: [@Ciprian-LocalPulse](https://github.com/Ciprian-LocalPulse)

---

## 🌟 Sponsors & Partners

VitaGraph is supported by generous donors and research partners. **[View sponsors →](SPONSORS.md)** | **[Become a sponsor →](DONATE.md)**

---

**Made for Research** | *Funded by the Research Community*
