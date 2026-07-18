# VitaGraph Research Methodology

## Executive Summary

VitaGraph is a **research reference implementation** demonstrating how synthetic multi-omic data (biometric signals, environmental exposure, chronological age) can be organized in a knowledge graph and used to train supervised regression models for "biological age" prediction. 

**Nothing in this implementation has been validated against a real clinical cohort.** The synthetic data, ground-truth labels, and resulting model predictions are illustrative demonstrations intended for educational and research-methodology purposes only. This document clarifies what the system does and does not claim to do.

---

## 1. Scope: What VitaGraph Implements

### 1.1 Data Simulation

VitaGraph generates synthetic time-series data for multiple individuals across domains:

- **Biometric signals**: heart rate, heart-rate variability (HRV), sleep duration
- **Environmental factors**: a composite environmental-exposure index (illustrative)
- **Metadata**: chronological age, activity level (proxy)

**Generation method**: Every signal is drawn from a population-level distributional baseline (e.g., HR ~ N(70, 8) bpm) with:
- Circadian modulation (e.g., lower HR during sleep hours)
- Measurement noise
- Seeded random number generation for reproducibility

**Biological-age label**: A deterministic linear combination of features (formula in [`config.py`](../src/vitagraph/config.py)) with added Gaussian noise. This is **a data-generation convenience, not a biological or clinical claim**. Real biological age depends on epigenetics, genomics, metabolism, and countless other factors not modeled here.

### 1.2 Knowledge Graph Representation

The system builds a directed property graph with:

- **Node types**: Person, BiometricData, EnvironmentalFactor, Intervention
- **Edge types**: HAS_DATA, EXPOSED_TO, HAS_RECOMMENDATION (with documented semantics)
- **Implementation**: NetworkX DiGraph

This graph layer demonstrates how to organize heterogeneous data sources for downstream analysis and export (JSON, GraphML formats).

### 1.3 Machine Learning Pipeline

VitaGraph trains standard scikit-learn regressors (Linear, Random Forest, Gradient Boosting) to predict the synthetic biological-age label from:

- Chronological age
- Heart rate average
- HRV average
- Sleep hours average
- Activity level
- Environmental exposure

**Metrics**: Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), R² score, cross-validation

The fitted model is **a function fit to synthetic data**, not a clinically validated biomarker.

### 1.4 Recommendation Logic

The system implements a simple **rule-based heuristic** for priority-setting:
- Computes the standardized deviation of each feature from its population baseline
- Identifies the feature with the largest unfavorable deviation
- Attaches an Intervention node with a label ("sleep", "cardiovascular load", etc.) and rationale

**This is not causal inference.** It does not claim that modifying feature X will improve biological age. It is a transparent, auditable prioritization heuristic for demonstration.

---

## 2. Scope: What VitaGraph Does NOT Implement

### 2.1 Real Data Integration

VitaGraph does not:
- Read from real wearable devices or IoT sensors
- Connect to electronic health records (EHRs)
- Incorporate real genomic data or lab results
- Use any actual patient or research participant data

### 2.2 Clinical Validation

VitaGraph does not:
- Make claims about real biological aging
- Validate against any clinical cohort
- Undergo FDA review or any regulatory approval
- Serve as a medical device or diagnostic tool
- Provide individualized health recommendations

### 2.3 Advanced Modeling

VitaGraph v0.2.0 does not yet implement:
- **Graph Neural Networks (GNNs)**: planned for v1.0
- **Causal Inference**: counterfactual analysis of interventions (planned)
- **Federated Learning**: distributed privacy-preserving training
- **Differential Privacy**: noise-injection for formal privacy guarantees
- **Reinforcement Learning**: dynamic treatment allocation

See [ROADMAP.md](ROADMAP.md) for the full research plan.

---

## 3. Data Integration Layer

### 3.1 Current Implementation

VitaGraph v0.2.0 constructs a knowledge graph from:

1. **Biometric time series** (simulated heart rate, HRV, sleep)
2. **Environmental factors** (simulated exposure index)
3. **Metadata** (chronological age, activity level)

The graph connects:
- Each person to their biometric data (HAS_DATA edges)
- Each person to environmental exposures they are subject to (EXPOSED_TO edges)
- Each person to rule-based intervention recommendations (HAS_RECOMMENDATION edges)

### 3.2 Future Extensions

A production system would additionally integrate:
- **Genomic variants**: SNPs linked to longevity and disease susceptibility
- **Phenotypic longitudinal data**: changes in lab markers over time
- **Lifestyle & behavioral**: dietary patterns, exercise types, stress
- **Geospatial data**: climate, pollution, urban density, time zone
- **Multi-omic integration**: transcriptomics, proteomics, metabolomics

See [ROADMAP.md](ROADMAP.md).

---

## 4. Machine Learning Framework

### 4.1 Current Model Family

Scikit-learn regressors:
- **Linear Regression**: Fast baseline, interpretable coefficients
- **Random Forest**: Non-linear, feature importance via out-of-bag error
- **Gradient Boosting**: State-of-the-art regression performance on tabular data

### 4.2 Evaluation Methodology

VitaGraph follows standard ML practices:

1. **Train/test split** (80/20) on synthetic cohort
2. **k-fold cross-validation** (default k=5) to reduce variance
3. **Held-out test set** evaluation (MAE, RMSE, R²)
4. **Feature importance** extraction for model introspection

### 4.3 Future Modeling Directions

Graph Neural Networks (GNNs):
- Leverage the knowledge graph structure (node and edge types)
- Learn node and edge embeddings end-to-end
- Capture relationships between biometric signals and environment

Causal Inference:
- Estimate counterfactual biological-age outcomes under different interventions
- Identify causal links (not mere correlations) between modifiable risk factors and aging phenotype

---

## 5. Ethical Considerations & Privacy

### 5.1 Synthetic Data Mitigates Privacy Risk

Because VitaGraph uses **only seeded random data**, there is no real individual identifiable information, genetic data, or health records in the system. The synthetic data cannot be reverse-engineered to identify real people or health conditions.

### 5.2 Real Data Future

If VitaGraph is extended to real clinical data in the future, it must employ:

- **Differential Privacy**: formal privacy guarantees via ε-δ noise injection
- **Federated Learning**: model training without centralizing raw data
- **Data Minimization**: collect only necessary features
- **Access Controls**: role-based permissions, audit logs
- **Consent & Transparency**: informed participant consent, clear communication of study objectives
- **Fairness Audits**: test for disparate impact across demographics

### 5.3 Broader Implications

Biological-aging research carries societal risks if not conducted responsibly:

- **Ageism**: Biological-age predictions could be misused to discriminate based on age
- **Inequality**: Access to anti-aging interventions often depends on wealth
- **Over-medicalization**: Framing aging as a "disease" may increase unnecessary treatment
- **Behavioral coercion**: Guilt or shame-based wellness nudges can be psychologically harmful

VitaGraph remains an **educational tool**, not a path to individualized aging-intervention claims.

---

## 6. Reproduciblity & Transparency

### 6.1 Seeded Random Generation

Every synthetic-data generator uses a seeded `numpy.random.Generator`, making all outputs reproducible:

```python
gen = SyntheticCohortGenerator(seed=42)
cohort = gen.generate(1000)  # Always the same output given seed=42
```

### 6.2 Documented Baselines

Population-level assumptions (heart-rate mean/std, sleep hours, etc.) are centralized in [`config.py`](../src/vitagraph/config.py), making them auditable and overridable:

```python
@dataclass(frozen=True)
class SignalBaseline:
    heart_rate_mean: float = 70.0
    heart_rate_std: float = 8.0
    # ... etc
```

### 6.3 Explicit Formula for Biological Age

The synthetic ground-truth biological-age label is computed by a documented formula in [`config.py`](../src/vitagraph/config.py), not a black box. Every coefficient is justified and overridable.

### 6.4 Logging & Inspection

All major pipeline steps log their progress. Models save a JSON metadata sidecar (model type, features, training metrics) alongside the joblib artifact.

---

## 7. Validation Against Clinical Data

### 7.1 What Would Real Validation Require?

1. **Clinical cohort**: Longitudinal data on 100–10,000+ individuals with real biometric + genomic + outcome data
2. **Ground-truth biological age**: Measured via epigenetic clocks (e.g., Horvath, DunedinPace) or other validated biomarkers
3. **Held-out prospective cohort**: Predictions on new individuals, verified against later measured biological age
4. **Fairness assessment**: Validation across age, sex, ancestry, socioeconomic status
5. **Peer review & publication**: Undergo standard scientific review

### 7.2 VitaGraph's Current Status

VitaGraph has **not undergone any of the above**. It uses only synthetic data with a synthetic label. Predictions are illustrative.

---

## 8. Code Quality & Testing

VitaGraph follows software-engineering best practices:

- **Type hints**: Python 3.10+ type annotations throughout
- **Docstrings**: NumPy-style docstrings for every module and function
- **Unit tests**: 20+ tests covering synthetic data, signal processing, graph, estimator, and pipeline
- **Test coverage**: Target ≥80% via pytest + coverage.py
- **Linting**: ruff for style, mypy for static type checking
- **Documentation**: Markdown guides (METHODOLOGY, ROADMAP, API reference)

---

## 9. Contact & Questions

For questions about VitaGraph's methodology, assumptions, or limitations:

- **GitHub Issues**: Post on the project repository
- **Email**: Ciprian Stefan Plesca (@Ciprian-LocalPulse on GitHub)

---

## References & Further Reading

### Biological Aging Research

- Horvath, S. "DNA methylation age of human tissues and cell types." *Genome Biology* 14, R115 (2013).
- Belsky, D. W., et al. "DunedinPace, a molecular-aging rate in midlife predicts mortality." *Nature Aging* 2, 308–318 (2022).

### Knowledge Graphs in Biomedical Informatics

- Wilkinson, M. D., et al. "The FAIR Guiding Principles for scientific data management and stewardship." *Scientific Data* 3, 160018 (2016).
- Hripcsak, G., & Albers, D. J. "High-fidelity phenotyping with EHRs." *Nature Computational Science* 1, 268–275 (2021).

### Graph Neural Networks

- Kipf, T., & Welling, M. "Semi-supervised classification with graph convolutional networks." *ICLR* (2017).
- Hamilton, W. L., Ying, R., & Leskovec, J. "Representation learning on graphs." *ICML Tutorial* (2017).

### Causal Inference

- Pearl, J. *Causality: Models, Reasoning, and Inference*. 2nd ed., Cambridge University Press (2009).
- Cunningham, S. *Causal Inference: The Mixtape*. Yale University Press (2021).

### Ethical AI & Fairness

- Buolamwini, B., & Buolamwini, B. "Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification." *FAccT* (2018).
- Mitchell, M., et al. "Model Cards for model reporting." *FAccT* (2019).

---

**Made for Research** | *Transparency & Reproducibility*

Last updated: 2026-07-18
