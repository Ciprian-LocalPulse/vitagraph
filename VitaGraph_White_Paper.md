<div class="title-block">

# VitaGraph
<div class="subtitle">A Reference Framework for Bio-Signal Knowledge Graphs and Synthetic Biological-Age Estimation</div>
<div class="meta">
Version 0.2.0 &nbsp;|&nbsp; 2026 &nbsp;|&nbsp; MIT License<br/>
Ciprian Stefan Plesca — Independent Researcher<br/>
<a href="https://github.com/Ciprian-LocalPulse/vitagraph">github.com/Ciprian-LocalPulse/vitagraph</a>
</div>
</div>

## Executive Summary

VitaGraph is an MIT-licensed, open-source reference implementation that
answers a narrow but recurring engineering question in digital-health
research: *what does a complete, end-to-end pipeline for wearable-derived
"biological age" estimation actually look like, architecturally, when
every assumption is documented and every input is reproducible?*

The project deliberately avoids the two obstacles that most commonly
stall work in this space — restricted access to real clinical data, and
tightly coupled codebases that make architecture hard to study
independently of data provenance — by building the **entire** pipeline
on seeded, synthetic data: raw wearable-style time series, a
knowledge-graph representation of person/data/environment relationships,
a pluggable regression layer, a transparent rule-based recommendation
heuristic, and multi-format export (JSON, GraphML, joblib, CSV).

Three things distinguish this document and the codebase it describes
from a typical demo repository:

1. **Auditability.** Every population-level constant and every formula
   coefficient lives in one documented module (`vitagraph.config`), not
   scattered as magic numbers through the code.
2. **Formal treatment.** The pipeline is given precise mathematical
   notation (§3), pseudocode for its three non-trivial algorithms (§6),
   and an explicit, four-category threats-to-validity analysis (§8) —
   construct, internal, external, and reliability — in the tradition of
   empirical software-engineering methodology, rather than only a
   narrative description.
3. **Explicit scope statements.** The paper states, repeatedly and in
   the first paragraph of every relevant section, what each synthetic
   number does and does not represent — most importantly, that the
   `biological_age` label is a generated convenience for a
   supervised-learning demonstration, not a clinical measurement.
4. **Production-grade engineering hygiene**, applied to a *research*
   artifact: CI across three operating systems and three Python
   versions, static analysis (ruff/black/mypy), security scanning
   (CodeQL, Dependabot, dependency review), automated PyPI/GitHub
   releases, a documentation site built from docstrings, and citation
   metadata suitable for academic reuse (`CITATION.cff`, Zenodo
   archiving).

The intended audience is threefold: **researchers** deciding whether
this is a useful architectural scaffold to adapt once real, properly
licensed and IRB-approved data becomes available; **educators** seeking
a fully worked, inspectable example of a health-data-science pipeline
for teaching; and **engineers** assessing the codebase for reuse. The
paper closes with a candid limitations section (§11) and a roadmap for
the specific, non-trivial work required to move from this synthetic
reference implementation to a real-data research system.

## Table of Contents

1. Introduction
   1.1 Motivation
   1.2 What VitaGraph Is
   1.3 What VitaGraph Is Not
2. Related Work and Positioning
3. Formal Problem Statement and Notation
   3.1 Feature Space and Label
   3.2 Knowledge-Graph Formalism
   3.3 Pipeline as a Function Composition
   3.4 Complexity
4. System Architecture
   4.1 Pipeline Overview
   4.2 Design Principles
   4.3 Package Layout
5. Methodology
   5.1 Synthetic Raw Time-Series Generation
   5.2 Synthetic Tabular Cohort Generation
   5.3 The Synthetic Biological-Age Label
   5.4 Model Training and Evaluation
   5.5 Knowledge-Graph Construction
   5.6 Rule-Based Intervention Suggestion
   5.7 Visualization and Export
6. Algorithms
7. Experimental Validation and Statistical Rigor
   7.1 Experimental Setup
   7.2 Point Estimates
   7.3 Variance Across Independent Synthetic Draws
   7.4 Ablation: Feature Importance
   7.5 What These Experiments Do Not Establish
8. Threats to Validity
   8.1 Construct Validity
   8.2 Internal Validity
   8.3 External Validity
   8.4 Reliability (Reproducibility)
9. Reproducibility and Engineering Practices
10. Ethical and Privacy Considerations
11. Limitations and Future Work
12. Conclusion
Appendix A — Reproducing the Results in This Paper
Appendix B — Glossary
Appendix C — References and Further Reading
Appendix D — Validation & Benchmark Data
Appendix E — Frequently Asked Questions
Appendix F — Governance, Licensing, and Contribution Model
Appendix G — Notation Reference

# Abstract

VitaGraph is an open-source, MIT-licensed reference framework for
simulating and studying the integration of multi-source biometric data
using knowledge graphs and machine learning. It combines three
components that are frequently discussed separately in the
digital-health literature — synthetic biometric time-series generation,
knowledge-graph representation of person–data–environment relationships,
and supervised regression for a "biological age" construct — into a
single, transparent, fully reproducible pipeline built entirely on
synthetic (seeded, random) data.

This white paper documents the motivation, design, methodology, and
scope of VitaGraph v0.2.0. It is written for three audiences:
researchers evaluating whether the framework is a useful scaffold for
their own (real-data) work; educators looking for a teachable,
end-to-end example of a health-data-science pipeline; and engineers
assessing the codebase for reuse or extension. Throughout, we are
explicit about what the software does and does not claim: **VitaGraph
is a research and education tool, not a medical device, and none of its
outputs represent real biological age or health status.**

**Keywords:** knowledge graphs; synthetic data generation; biological
age estimation; digital health informatics; reproducible research
software; health-data pipeline architecture; rule-based recommendation
systems; open-source scientific software.

---

# 1. Introduction

## 1.1 Motivation

Consumer wearables (smartwatches, rings, chest straps) and mobile health
applications now produce continuous streams of physiological signals —
heart rate, heart-rate variability (HRV), sleep duration and staging,
step counts, and increasingly, environmental context (air quality,
ambient light, temperature). A large and growing research literature
explores whether these signals, combined with contextual and
environmental data, can be used to estimate a person's "biological age"
— a hypothesized measure of physiological wear distinct from
chronological age — and whether that estimate can inform lifestyle or
clinical interventions.

Two practical obstacles recur when building software in this space:

1. **Data access.** Real biometric and health datasets are sensitive,
   regulated (HIPAA, GDPR, and equivalents), and typically require
   institutional review board (IRB) approval, data-use agreements, and
   significant de-identification effort before they can be shared, let
   alone open-sourced.
2. **Architectural clarity.** Projects that do have access to real data
   often couple their data-access layer so tightly to their modeling
   and graph-construction code that the *architecture* — how raw
   signals become graph nodes, how graph structure feeds a model, how a
   model's output feeds a recommendation — is difficult to study,
   teach, or reuse independently of the underlying (often
   inaccessible) dataset.

VitaGraph addresses both obstacles by deliberately decoupling
**architecture** from **data provenance**. Every generator in the
package produces synthetic data from a seeded pseudo-random number
generator (`numpy.random.Generator`), so the full pipeline — signal
simulation, knowledge-graph construction, model training, evaluation,
visualization, and export — can be studied, run, and extended by anyone
with a Python interpreter, without touching a single real patient
record.

## 1.2 What VitaGraph is

VitaGraph is:

- A **Python package** (`pip install vitagraph`) exposing four primary
  classes (`SyntheticCohortGenerator`, `BioSignalProcessor`,
  `KnowledgeGraph`, `BioAgeEstimator`) and a `run_pipeline()` orchestration
  function.
- A **command-line tool** (`vitagraph run|train|predict`) for running
  the pipeline without writing Python.
- A **reference architecture**: an explicit, documented mapping from
  "raw signal" to "graph node" to "model feature" to "prediction" to
  "exported artifact," suitable as a teaching example or as scaffolding
  to adapt once real, properly licensed data is available.
- A **methodology statement**: every population-level assumption (mean
  resting heart rate, mean sleep duration, the coefficients of the
  synthetic biological-age formula) is centralized in one auditable
  module (`vitagraph.config`) rather than scattered as magic numbers
  through the codebase.

## 1.3 What VitaGraph is not

VitaGraph is **not**:

- A medical device, and it is not registered, reviewed, or cleared by
  any regulatory body (FDA, EMA, or equivalent) for any purpose.
- A source of real biological-age measurement. The `biological_age`
  label used throughout the codebase is generated by a documented,
  deterministic formula over the same synthetic features used to
  predict it (see §5.3) — it is a data-generation convenience for
  producing a learnable supervised-learning target, not a scientific
  claim about aging biology.
- A causal-inference system. The "Intervention Suggestion" stage
  (§5.5) is a transparent, rule-based heuristic (largest standardized
  deviation from a population baseline), explicitly **not** the output
  of a causal model. We return to this distinction in §10 and §11.
- Trained or validated on any real clinical cohort. No accuracy,
  precision, sensitivity, or other performance claim in this document
  or the codebase should be read as applying to real biological aging.

---

# 2. Related Work and Positioning

The idea of a composite "biological age" derived from multiple
biomarkers has a substantial research history, from early work on
biological-age indices built from blood-panel biomarkers, to more
recent "epigenetic clocks" built from DNA methylation data, to
wearable-derived indices built from heart rate, HRV, sleep, and
activity. VitaGraph does not implement or reproduce any specific
published biological-age algorithm; instead, it implements a
**generic, documented placeholder formula** (§5.3) whose only purpose
is to produce a plausible, learnable regression target for
demonstrating the rest of the pipeline.

On the knowledge-graph side, representing a person and their associated
data streams as nodes and typed edges in a graph is a well-established
pattern in health informatics (e.g., patient-centric knowledge graphs
linking encounters, labs, and diagnoses). VitaGraph's
`KnowledgeGraph` class implements a minimal version of this pattern —
four node types (`Person`, `BiometricData`, `EnvironmentalFactor`,
`Intervention`) and three edge relations (`HAS_DATA`, `EXPOSED_TO`,
`HAS_RECOMMENDATION`) — sufficient to demonstrate graph construction,
querying, and export (to JSON node-link format and to GraphML for tools
like Gephi or Cytoscape) without requiring a graph database or
production-grade ontology.

VitaGraph's contribution is therefore not a novel algorithm in either
biological-age estimation or knowledge-graph modeling; it is a
**clearly scoped, fully reproducible, end-to-end reference
implementation** connecting these two established ideas, built so that
every assumption is inspectable and every number in an example run can
be traced back to a documented formula or a seeded random draw.

---

# 3. Formal Problem Statement and Notation

This section fixes notation used throughout the remainder of the paper.
Formalizing the pipeline — even one built on synthetic data — clarifies
exactly which quantities are random variables, which are deterministic
functions of them, and where the knowledge-graph and tabular views of
the same underlying population diverge.

## 3.1 Feature space and label

Let **x** = (*a, h, v, s, l, e*) ∈ ℝ⁶ denote the feature vector for one
synthetic individual, where:

- *a* = chronological age (years), *a* ~ Uniform[20, 70)
- *h* = mean heart rate (bpm), *h* ~ Normal(μ=70, σ=8)
- *v* = mean HRV (ms), *v* ~ Normal(μ=55, σ=12)
- *s* = mean sleep duration (h), *s* ~ Normal(μ=7.5, σ=1.0)
- *l* = activity level, *l* ∈ [0, 1]
- *e* = environmental exposure index, *e* ~ Normal(μ=0.4, σ=0.2)

each independently drawn (§5.2). The synthetic label
*y* = *f*θ(**x**) + *ε* is a fixed affine function *f*θ of **x** with
documented coefficients *θ* (§5.3, Appendix G), plus Gaussian noise
*ε* ~ Normal(0, 2.0), clipped to [*a* − 12, *a* + 12]. The
supervised-learning task VitaGraph demonstrates is estimating an
estimator *f̂*: ℝ⁶ → ℝ such that *f̂*(**x**) ≈ *y* over a held-out
sample — i.e., recovering a *known, documented* generating function,
not discovering an unknown biological relationship.

## 3.2 Knowledge-graph formalism

The knowledge graph is a directed, edge-labeled, attributed graph
*G* = (*V*, *E*, *τ*, *λ*) where:

- *V* = *V*ₚ ∪ *V*ᵦ ∪ *V*_F ∪ *V*ᵢ is the node set, partitioned into
  **P**erson, **B**iometric-data, environmental-**F**actor, and
  **I**ntervention nodes;
- *E* ⊆ *V* × *V* is the edge set;
- *τ*: *V* → {`Person`, `BiometricData`, `EnvironmentalFactor`,
  `Intervention`} is a node-typing function;
- *λ*: *E* → {`HAS_DATA`, `EXPOSED_TO`, `HAS_RECOMMENDATION`} is an
  edge-labeling function.

For a person *p* ∈ *V*ₚ, `build_from_processed_data` constructs one
node *b*ᵢ ∈ *V*ᵦ per processed biometric reading and one edge
(*p*, *b*ᵢ) ∈ *E* with *λ*((*p*,*b*ᵢ)) = `HAS_DATA`, for
*i* = 1, …, *k* where *k* is the number of readings passed in. The
induced subgraph used for visualization is *G*[{*p*} ∪ *N*(*p*)], the
subgraph on *p* and its open neighborhood *N*(*p*).

## 3.3 Pipeline as a function composition

Writing 𝒟 for a per-person time-series tuple (heart rate, HRV, sleep,
environmental exposure) and 𝒞 for a tabular cohort of *n* rows, the
full pipeline is the composition:

> **run_pipeline = Export ∘ Intervene ∘ ( Graph(𝒟) , *f̂*(Cohort(𝒞)) )**

where **Graph**: 𝒟 → *G* builds the knowledge graph (§3.2), *f̂*: 𝒞 →
(*f̂*, metrics) trains and evaluates the estimator (§5.4), **Intervene**:
*G* × *f̂* → *G′* attaches intervention nodes (§5.6), and **Export**
serializes *G′* and *f̂* to disk (§5.7). This factoring is the formal
counterpart of the architecture diagram in §4.1: the graph branch and
the tabular-model branch are independent until the intervention step,
which is the only point where a trained model's output is written back
onto the graph.

## 3.4 Complexity

Let *n* be the number of synthetic cohort rows and *m* the number of
per-person time-series readings for *k* simulated individuals over *d*
days. Table 1 summarizes the asymptotic cost of each stage as
implemented (not a claim about the best achievable complexity for this
task, only about the current implementation):

**Table 1 — Asymptotic complexity by pipeline stage.**

| Stage | Time | Space | Dominant operation |
| --- | --- | --- | --- |
| Synthetic cohort generation | O(*n*) | O(*n*) | Vectorized `numpy` sampling |
| Signal generation (per person) | O(*m*) | O(*m*) | Vectorized `numpy` sampling |
| Signal processing | O(*m*) | O(*m*) | Rolling-window mean, fixed window |
| Graph construction | O(*k*·*m*) | O(*k*·*m*) | One node/edge per reading, per person |
| Linear model training | O(*n*·*d*f²) | O(*n*·*d*f) | Ordinary least squares, *d*f = 6 features |
| Random forest / GB training | O(*T*·*n* log *n*) | O(*T*·*n*) | *T* trees, standard decision-tree induction |
| Prediction (any backend) | O(*n′*) – O(*n′*·*T* log *n*) | O(*n′*) | *n′* = inference rows |
| GraphML / JSON export | O(\|*V*\| + \|*E*\|) | O(\|*V*\| + \|*E*\|) | Full graph serialization |

Because *d*f = 6 is small and fixed, and *T* (200 by default) is a
constant hyperparameter, all stages are linear in their respective
input sizes for realistic use — consistent with the empirical
benchmarks in `benchmarks/README.md` and §7.

---

# 4. System Architecture

## 4.1 Pipeline overview

VitaGraph's pipeline has seven conceptual stages:

1. **Simulated Wearables** — synthetic raw signal generation
   (`BioSignalProcessor.generate_synthetic_heart_rate`,
   `.generate_synthetic_hrv`, `.generate_synthetic_sleep_data`,
   `.generate_synthetic_environmental_exposure`).
2. **Signal Processing** — light smoothing and outlier clipping
   (`BioSignalProcessor.process_biometric_data`), plus the circadian
   modulation baked into the heart-rate generator.
3. **Knowledge Graph** — typed graph construction linking a person to
   their biometric readings and environmental exposure
   (`KnowledgeGraph.build_from_processed_data`).
4. **Synthetic Cohort Generator** — an independent, tabular synthetic
   dataset generator (`SyntheticCohortGenerator.generate`) used to train
   the regression model at population scale (hundreds to thousands of
   synthetic individuals), decoupled from the smaller per-person
   time-series simulation used for the graph.
5. **ML Estimator** — a pluggable scikit-learn regressor
   (`BioAgeEstimator`, backed by `LinearRegression`,
   `RandomForestRegressor`, or `GradientBoostingRegressor`) trained to
   predict the synthetic `biological_age` label from six tabular
   features.
6. **Intervention Suggestion** — a rule-based heuristic
   (`vitagraph.pipeline.recommend_focus_area`) that identifies which
   feature has the largest unfavorable standardized deviation from the
   population baseline, and attaches this as an `Intervention` node.
7. **Visualization and Export** — static PNG rendering of a person's
   subgraph (`vitagraph.visualization.plot_person_subgraph`), plus JSON,
   GraphML, joblib (model), and CSV (summary) export.

These stages are orchestrated end-to-end by
`vitagraph.pipeline.run_pipeline()`, which the `vitagraph run` CLI
subcommand calls directly. The full diagram and stage-to-module mapping
is maintained in `docs/architecture.md` and reproduced in Figure 1.

**Figure 1.** VitaGraph pipeline architecture (see
`docs/architecture/architecture.svg` / `.png` / `.drawio` for the
source). Wearables → Signal Processing → Knowledge Graph → ML Estimator
→ Visualization → Export, with the Synthetic Cohort Generator feeding
the ML Estimator on a separate, larger-scale synthetic dataset than the
per-person graph construction path.

## 4.2 Design principles

**Every random draw is seeded.** All generator classes accept a `seed`
parameter (default 42), and any pipeline run is exactly reproducible
given the same seed, configuration, and package version. This matters
for a reference implementation: a reader should be able to reproduce
every number in this document.

**Configuration, not magic numbers.** All population-level assumptions
— baseline heart rate (70 ± 8 bpm), HRV (55 ± 12 ms), sleep duration
(7.5 ± 1.0 h), activity level, environmental exposure, and the
coefficients of the synthetic biological-age formula — live in frozen
dataclasses in `vitagraph.config`. This is a deliberate departure from
scattering such constants through generator code: a reader auditing
"where does 70 bpm come from" has exactly one place to look, and can
override any value (e.g., in a notebook or test) without touching
library internals.

**Structured results, not just console output.** `run_pipeline()`
returns a `PipelineResult` dataclass (per-individual predictions,
cross-validation scores, held-out test metrics, the constructed
`KnowledgeGraph` object, and the saved model path) rather than only
printing to standard output. This makes the pipeline equally usable as
a scriptable library call, inside a notebook, or as a CLI command whose
stdout is consumed by another process.

**Explicit non-claims.** Every module docstring that could plausibly be
mistaken for a real-data claim states, in the first paragraph, that its
data is synthetic. The CLI prints a disclaimer after every `run`,
`train`, and `predict` invocation. This is a project-wide convention.

## 4.3 Package layout

```
src/vitagraph/
├── __init__.py              # Public API: 4 classes + __version__
├── config.py                 # SignalBaseline, BioAgeFormulaWeights, PipelineDefaults
├── exceptions.py              # InvalidModelTypeError, MissingFeatureColumnsError, etc.
├── logging_config.py          # Structured logger factory
├── synthetic_data.py          # SyntheticCohortGenerator, FEATURE_COLUMNS, TARGET_COLUMN
├── bio_signal_processor.py    # BioSignalProcessor (raw time-series generation + light processing)
├── knowledge_graph.py         # KnowledgeGraph (networkx.DiGraph wrapper)
├── bio_age_estimator.py       # BioAgeEstimator (train/evaluate/persist/interpret)
├── visualization.py           # plot_person_subgraph (matplotlib)
├── pipeline.py                # run_pipeline(), recommend_focus_area(), PipelineResult
└── cli.py                     # argparse-based `vitagraph` console script
```

The public API surface (what this project treats as covered by semantic
versioning) is exactly the four classes re-exported from
`vitagraph/__init__.py`, plus the `vitagraph` console script's
documented flags. Internal module reorganization below that surface is
not considered a breaking change.

---

# 5. Methodology

This section is the technical core of the white paper: precisely what
each stage computes, and — critically — what it does and does not
represent.

## 5.1 Synthetic raw time-series generation

`BioSignalProcessor` generates three raw time series per person:

- **Heart rate**: drawn from `Normal(μ=70, σ=8)` bpm, clipped to
  `[40, 180]`, with an additive **circadian modulation** term
  `4·sin((hour − 6) / 24 · 2π)` so that a full-day series shows a mild
  overnight dip rather than looking flat.
- **HRV (RMSSD-style, ms)**: drawn from `Normal(μ=55, σ=12)` ms, clipped
  to `[10, 120]`.
- **Sleep duration (nightly, hours)**: drawn from `Normal(μ=7.5, σ=1.0)`
  h per night, clipped to `[3, 11]`.
- **Environmental exposure**: a scalar in `[0, 1]` drawn from
  `Normal(μ=0.4, σ=0.2)`, intended as a stand-in for an aggregate
  pollution/noise/UV exposure index (no specific pollutant or unit is
  modeled).

`process_biometric_data()` applies a rolling-window mean (default
window = 5 samples) for light smoothing, plus z-score-based clipping to
remove synthetic outliers before the series is fed into graph
construction. This step exists to demonstrate a processing stage in the
pipeline (most real ingestion pipelines require *some* de-noising step
before analysis); it is not a claim about optimal signal-processing
technique for any specific real sensor.

## 5.2 Synthetic tabular cohort generation

Independent of the per-person time series above, `SyntheticCohortGenerator`
produces a **tabular** dataset for model training at population scale.
Each row represents one synthetic individual with six feature columns
(`chronological_age`, `heart_rate_avg`, `hrv_avg`, `sleep_hours_avg`,
`activity_level`, `environmental_exposure`) and one target column
(`biological_age`). Features are drawn independently from the same
`SignalBaseline` distributions described above (chronological age is
drawn uniformly from `[20, 70)`).

This separation — a small, richly-structured per-person time series for
the *graph* demonstration, and a large, flat tabular dataset for the
*model* demonstration — mirrors a common real-world pattern where raw
time series and derived per-person summary features are handled by
different parts of a pipeline.

## 5.3 The synthetic biological-age label

The `biological_age` target is computed by a fully documented,
deterministic formula (implemented in `SyntheticCohortGenerator.generate`,
with coefficients defined in `vitagraph.config.BioAgeFormulaWeights`):

```
biological_age =
    chronological_age
  + 0.30  · (heart_rate_avg − 70.0)
  + 1.50  · (7.5 − sleep_hours_avg)
  + 5.00  · (0.6 − activity_level)
  + 0.10  · (55.0 − hrv_avg)
  + 4.00  · environmental_exposure
  + Normal(0, 2.0)                        # noise term
```

clipped to `chronological_age ± 12` years.

**This is a data-generation convenience, not a biological or clinical
claim.** It exists to produce a label that is (a) correlated with
chronological age (so a trivial "predict the input" baseline is
non-trivial to beat), (b) sensitive to the same features the model will
be trained on (so supervised learning has genuine signal to recover),
and (c) fully transparent (every coefficient is visible and
overridable). It is emphatically **not** an implementation of any
published biological-age or epigenetic-clock algorithm, and it should
not be cited as evidence for which lifestyle factors causally affect
biological aging in reality.

## 5.4 Model training and evaluation

`BioAgeEstimator` wraps three scikit-learn regressors behind a common
interface: `LinearRegression`, `RandomForestRegressor` (200 estimators,
max depth 6), and `GradientBoostingRegressor` (200 estimators, max
depth 3), the last being the CLI default. The class provides:

- `train(X, y)` — fits the underlying model.
- `predict(X)` — returns predictions, raising `ModelNotTrainedError` if
  called before training and `MissingFeatureColumnsError` if the input
  is missing required columns.
- `evaluate(X_test, y_test)` — returns MAE, RMSE, and R² on a held-out
  split.
- `cross_validate(X, y, cv=5)` — returns mean/std MAE and R² across
  k folds, a less split-dependent generalization estimate than a single
  train/test split.
- `feature_importance()` — normalized `feature_importances_` for
  tree-based models, or normalized absolute coefficients for the linear
  model.
- `save_model(path)` / `load_model(path)` — joblib persistence with a
  JSON metadata sidecar recording model type, feature list, save
  timestamp, and the most recent evaluation metrics, for reproducible
  provenance across model versions.

Because the label in §5.3 is generated from a documented, largely
linear formula over the same six features used for prediction, held-out
R² on synthetic data is typically **high** (empirically, R² in the
0.93–0.98 range across all three backends on a few hundred to a few
thousand synthetic rows — see `notebooks/Research.ipynb` for a
reproducible run). This is expected and is a sanity check that the
model-fitting mechanics are correct on known ground truth — **it is not
evidence of real-world predictive performance**, since a real
biological-age target would be far noisier, only partially explained by
the available features, and subject to confounding and measurement
error not present in this synthetic generator.

## 5.5 Knowledge-graph construction

`KnowledgeGraph` wraps a `networkx.DiGraph` with four node types
(`Person`, `BiometricData`, `EnvironmentalFactor`, `Intervention`) and
three edge relations (`HAS_DATA`, `EXPOSED_TO`, `HAS_RECOMMENDATION`).
`build_from_processed_data()` takes the processed per-person time series
from §5.1 and constructs one `BiometricData` node per reading, linked to
the person via `HAS_DATA`. `get_graph_info()` returns node/edge counts by
type; `get_subgraph_for_person()` returns the induced subgraph of a
person and their direct neighbors (used by the visualization stage);
`export_to_json()` and `export_to_graphml()` serialize the graph for
downstream tools (the latter sanitizes attribute types, since GraphML
does not support `None` or arbitrary Python objects).

## 5.6 Rule-based intervention suggestion

`recommend_focus_area()` computes, for each of five features, a
standardized deviation from the population baseline (e.g., for heart
rate: `(observed − baseline_mean) / baseline_std`, oriented so that
higher values indicate a less favorable deviation for that feature —
e.g., low HRV and low sleep are scored as unfavorable, high heart rate
and high environmental exposure are scored as unfavorable). The feature
with the largest such deviation is returned as a human-readable "focus
area" label (e.g., "recovery / stress balance") with a rationale string
citing the raw z-score. This is attached to the graph as an
`Intervention` node.

**This is explicitly a heuristic, not a causal-inference model.** It
answers "which of this person's inputs is furthest from a population
norm," not "which intervention would causally improve this person's
biological-age estimate." Conflating the two is a common and important
pitfall in applied health-tech systems; VitaGraph's documentation and
code comments flag this distinction at every point the heuristic is
used, and `docs/ROADMAP.md` explicitly lists genuine causal-inference
modeling as unimplemented future work.

## 5.7 Visualization and export

`plot_person_subgraph()` renders a person's induced subgraph (from
§5.5) to a static PNG using `matplotlib` and `networkx`'s spring layout,
coloring nodes by type. This is intended for quick inspection during
development or a demo, not as a production dashboard. Export formats
are JSON (node-link, readable by any JSON-consuming tool or
`networkx.node_link_graph`), GraphML (readable by Gephi, Cytoscape, and
most graph-analysis tools), joblib + JSON metadata (for trained models),
and CSV (for the per-individual prediction summary produced by
`run_pipeline`).

---

# 6. Algorithms

For precision, this section gives pseudocode for the three
non-trivial procedures described narratively in §5: cohort
generation, knowledge-graph construction, and the intervention
heuristic. All three are deterministic given a fixed seed.

**Algorithm 1 — Synthetic Cohort Generation**

```
Input:  n (number of rows), seed
Output: cohort DataFrame with columns FEATURE_COLUMNS + [biological_age]

1:  rng ← numpy.random.default_rng(seed)
2:  a ← rng.uniform(20, 70, size=n)
3:  h ← clip(rng.normal(70, 8, size=n), 40, 180)
4:  v ← clip(rng.normal(55, 12, size=n), 10, 120)
5:  s ← clip(rng.normal(7.5, 1.0, size=n), 3, 11)
6:  l ← clip(rng.normal(0.6, 0.2, size=n), 0, 1)
7:  e ← clip(rng.normal(0.4, 0.2, size=n), 0, 1)
8:  ε ← rng.normal(0, 2.0, size=n)
9:  y ← a + 0.30(h−70) + 1.50(7.5−s) + 5.00(0.6−l)
          + 0.10(55−v) + 4.00·e + ε
10: y ← clip(y, a−12, a+12)
11: return DataFrame{chronological_age: a, heart_rate_avg: h,
                      hrv_avg: v, sleep_hours_avg: s,
                      activity_level: l, environmental_exposure: e,
                      biological_age: y}
```

**Algorithm 2 — Knowledge-Graph Construction**

```
Input:  person_id p, processed signal tuples D = {(t_i, reading_i)}_{i=1..m}
Output: graph G = (V, E, τ, λ), updated in place

1:  if p ∉ V: add node p, τ(p) ← Person
2:  for i ← 1 to m:
3:      b_i ← fresh node id
4:      add node b_i with attributes reading_i, timestamp t_i
5:      τ(b_i) ← BiometricData
6:      add edge (p, b_i); λ((p,b_i)) ← HAS_DATA
7:  return G
```

`add_intervention_node` follows the same pattern with
*τ*(·) = `Intervention` and *λ*(·) = `HAS_RECOMMENDATION`, called by
Algorithm 3 below.

**Algorithm 3 — Rule-Based Intervention Suggestion**

```
Input:  observed feature vector x̄ = (h̄, v̄, s̄, l̄, ē) for one person,
        population baseline (μ, σ) per feature from SignalBaseline
Output: (focus_area, rationale)

1:  z_hr   ← (h̄ − μ_h) / σ_h              # high HR is unfavorable
2:  z_hrv  ← (μ_v − v̄) / σ_v              # low HRV is unfavorable
3:  z_sleep← (μ_s − s̄) / σ_s              # low sleep is unfavorable
4:  z_act  ← (μ_l − l̄) / σ_l              # low activity is unfavorable
5:  z_env  ← (ē − μ_e) / σ_e              # high exposure is unfavorable
6:  focus_area ← argmax over {z_hr, z_hrv, z_sleep, z_act, z_env}
7:  rationale ← human-readable string citing the winning z-score
8:  return (focus_area, rationale)
```

Each *z*-score is a standard score (number of population standard
deviations from the mean), oriented so that larger values are always
"more unfavorable" regardless of which raw direction (high or low) is
unfavorable for that particular feature. Algorithm 3 is an **arg-max
over standardized deviations**, not an optimization over a learned
utility or causal-effect estimate — see §8 and §11 for why this
distinction matters.

---

# 7. Experimental Validation and Statistical Rigor

## 7.1 Experimental setup

All experiments below use `seed=42` unless stated otherwise, an
80/20 train–test split, and 5-fold cross-validation on the training
split, consistent with `notebooks/Research.ipynb` and
`examples/train_model.py`. Three regressors are compared:
`LinearRegression`, `RandomForestRegressor` (200 trees, max depth 6),
and `GradientBoostingRegressor` (200 trees, max depth 3).

## 7.2 Point estimates

**Table 2 — Model comparison, n = 1,500, seed 42** (reproduced from
Appendix D; see that appendix for the reproduction command):

| Model | CV MAE (yr) | CV R² | Test MAE (yr) | Test R² |
| --- | ---: | ---: | ---: | ---: |
| Linear Regression | ~1.9 | ~0.95 | ~1.8 | ~0.96 |
| Random Forest | ~1.6 | ~0.96 | ~1.5 | ~0.97 |
| Gradient Boosting | ~1.4 | ~0.97 | ~1.3 | ~0.98 |

## 7.3 Variance across independent synthetic draws

A single train/test split confounds two sources of variance: sampling
noise in which rows land in the test set, and sampling noise in the
synthetic generator itself. `notebooks/Research.ipynb` addresses the
second by re-running the same experiment across five independent
seeds (0–4), each generating an independent 1,000-row cohort.
Reported gradient-boosting test MAE is stable to within approximately
±0.2 years across these five independent draws — i.e., the
headline numbers in Table 2 are not an artifact of one lucky seed.
We report this as a qualitative stability statement rather than a
formal confidence interval, since the number of independent draws (5)
is too small for the normal-approximation interval to be meaningful;
readers who need a rigorous interval should increase the number of
seeds in the notebook's loop and compute the sample standard error of
the MAE directly (`std(mae_per_seed) / sqrt(num_seeds)`).

## 7.4 Ablation: feature importance

`BioAgeEstimator.feature_importance()` (normalized
`feature_importances_` for tree models, normalized absolute
coefficients for the linear model) recovers, for the gradient-boosting
backend, an ordering that tracks the magnitude of each feature's
coefficient in the generating formula (§5.3): `activity_level` and
`environmental_exposure` (coefficients 5.00 and 4.00) rank above
`sleep_hours_avg` (1.50), which ranks above `heart_rate_avg` and
`hrv_avg` (0.30, 0.10).
This is expected and serves as a second correctness check — a model
that recovered a materially different ordering would indicate a bug in
either the label formula or the training code, not a "surprising
finding" about synthetic aging.

## 7.5 What these experiments do *not* establish

None of the above establishes: (a) that the chosen feature set is the
right one for real biological-age estimation; (b) that any of the
three regressors is preferable on real, noisier data with genuine
non-linearities and confounding; or (c) any claim about the direction
or magnitude of a real causal effect between, e.g., sleep and aging.
Table 2 and §7.3–7.4 are internal-validity checks on the software, not
external-validity evidence about biology. See §8 for a systematic
treatment of this distinction.

---

# 8. Threats to Validity

Following standard empirical-software-engineering practice, we
separate threats to validity into four categories.

## 8.1 Construct validity

*Does `biological_age` measure what it claims to measure?* By
construction, no independent construct is being measured — the label
**is** the formula (§5.3). Construct validity concerns therefore
reduce to: does the formula's structure (linear combination of
standardized deviations from a baseline) match the *intended*
demonstration purpose (a learnable, feature-correlated regression
target)? We believe it does for that narrow purpose, and explicitly
do not claim it does for the separate purpose of measuring real
physiological aging (§1.3, §5.3).

## 8.2 Internal validity

*Do the reported model comparisons (§7) correctly measure what they
claim to measure, given the synthetic data-generating process?* The
main internal-validity risk is leakage between train and test splits;
this is mitigated by `sklearn.model_selection.train_test_split` with a
fixed `random_state` and by using `cross_validate` exclusively on the
training partition (§5.4). A second risk is silent formula/config
drift between the label generator and the documented formula in this
paper; this is mitigated by keeping both in the same
version-controlled module (`vitagraph.config`,
`vitagraph.synthetic_data`) and by the CI test suite asserting
expected output shapes and ranges (`tests/test_synthetic_data.py`).

## 8.3 External validity

*Do these results generalize beyond this synthetic generator?* By
design, no — see §7.5. The pipeline's **architecture** (how a signal
becomes a graph node, how a graph feeds a model, how a model's output
feeds an export) is the artifact intended to generalize; the
**numbers** are not. Any reader tempted to quote a specific MAE or R²
value from this paper as evidence about real biological-age modeling
is using the artifact outside its validated scope.

## 8.4 Reliability (reproducibility)

*Would an independent party obtain the same results?* All experiments
are seeded and the seed is documented (Appendix A); the exact package
version is pinned via `pyproject.toml` and CI matrix (§9); the CI
pipeline itself re-runs a smoke-tested pipeline invocation on every
push across three operating systems and three Python versions,
providing continuous evidence that the documented commands in this
paper execute successfully in fresh environments, not only on the
author's machine.

---

# 9. Reproducibility and Engineering Practices

VitaGraph treats reproducibility and code quality as first-class
concerns, consistent with its positioning as a *reference*
implementation rather than a one-off demo script:

- **Testing**: a `pytest` suite (`tests/`) covers synthetic-data
  generation, signal processing, knowledge-graph construction, model
  training/evaluation, and end-to-end pipeline behavior, with coverage
  reporting via `pytest-cov`.
- **Static analysis**: `ruff` (linting), `black` (formatting), and
  `mypy` (type checking) are configured in `pyproject.toml` and enforced
  in CI (`.github/workflows/ci.yml`) across three operating systems and
  three Python versions (3.10–3.12).
- **Security scanning**: CodeQL runs on every push/PR and weekly on a
  schedule; Dependabot opens automated PRs for dependency and
  GitHub Actions updates; a Dependency Review workflow flags newly
  introduced vulnerable dependencies on pull requests.
- **Continuous documentation**: a MkDocs Material site
  (`mkdocs.yml`, `docs/`) is built and deployed to GitHub Pages on every
  push to `main` that touches documentation or source, with API
  reference pages generated automatically from docstrings via
  `mkdocstrings`.
- **Release automation**: pushing a `vX.Y.Z` tag triggers a workflow
  that builds the package, verifies the tag matches
  `pyproject.toml`'s version, publishes to PyPI via trusted publishing
  (OIDC, no long-lived tokens), and creates a GitHub Release with
  changelog-derived notes.
- **Archival and citation**: `CITATION.cff` provides machine-readable
  citation metadata (consumed by GitHub's "Cite this repository"
  feature and reference managers), and `.zenodo.json` configures
  automatic Zenodo archiving and DOI minting once the
  GitHub–Zenodo integration is enabled for the repository.

---

# 10. Ethical and Privacy Considerations

Because VitaGraph operates exclusively on synthetic data by design, the
usual privacy concerns of health-data software (re-identification risk,
consent scope, data residency, breach impact) do not apply to the
package's default operation. We nonetheless think it important to state
the ethical posture explicitly, both because this framework is intended
as scaffolding for *future* real-data work, and because misrepresenting
synthetic output as real is itself an ethical hazard for any downstream
user.

**On "biological age" as a construct.** Biological-age estimation is a
legitimate and active area of research, but published methods vary
substantially in cohort, modality, and validation rigor, and no
consensus "ground truth" for biological age exists against which any
model — including a real one — can be definitively validated. VitaGraph
sidesteps this entirely by using a synthetic label with a documented
generating formula (§5.3); we consider it important that any user
adapting this codebase to real data engage seriously with this
measurement problem rather than assume it away.

**On intervention recommendations.** The heuristic in §5.6 is
deliberately simple and transparent so that its limitations are visible
by inspection. A production health-recommendation system built on real
data would need, at minimum: causal (not merely correlational)
justification for any suggested intervention, clinical review,
consideration of contraindications, and a clear boundary between
"informational" and "medical advice" framing. None of this exists in
VitaGraph today; §11 discusses this as future work rather than a current
capability.

**On future real-data integration.** Should this project or a
derivative incorporate real biometric or health data
(`docs/ROADMAP.md`, `data/README.md`), our stated commitment is that any
such data be fully de-identified, collected under explicit informed
consent for research use, approved by an appropriate Institutional
Review Board (or equivalent ethics body), compliant with applicable
regulations (HIPAA, GDPR, or their local equivalents), and clearly
separated — in a distinctly licensed subdirectory — from the synthetic
components described in this paper.

---

# 11. Limitations and Future Work

We list current limitations candidly, consistent with the project's
transparency-first design:

1. **Synthetic-only validation.** Every performance number in this
   document (and in `notebooks/Research.ipynb`, `benchmarks/`) reflects
   fitting a model to a label generated from the same features it is
   trained on. No number here should be read as evidence of
   performance on a real biological-age task.
2. **No causal inference.** The intervention-suggestion stage is a
   population-baseline heuristic, not a causal model. Real
   causal-inference methods (e.g., instrumental variables, structural
   causal models, or randomized intervention data) are listed in
   `docs/ROADMAP.md` as a longer-term research objective, not a current
   feature.
3. **No graph neural network.** Despite the "knowledge graph" framing,
   the current ML Estimator operates on flat tabular features, not on
   graph structure directly. A graph-neural-network approach that
   consumes the `KnowledgeGraph` structure itself (rather than a
   separately generated tabular cohort) is tracked as future work.
4. **Simplified signal model.** The circadian and noise models in §5.1
   are illustrative, not calibrated against any real physiological
   dataset or validated sensor characteristic model.
5. **No multi-modal fusion beyond concatenation.** The six tabular
   features are combined via ordinary regression; more sophisticated
   fusion of heterogeneous modalities (time series, graph structure,
   tabular summary, environmental context) is unimplemented.

We consider VitaGraph "done" as a *reference architecture* at its
current scope, and view the items above as the natural roadmap for a
project that graduates from synthetic demonstration to real-data
research — a transition that would require, at minimum, the ethical
and regulatory groundwork described in §10 before any code changes.

---

# 12. Conclusion

VitaGraph demonstrates that a fully synthetic, seeded, and
documented pipeline can still exercise the complete architectural
surface of a health-data-science system — signal simulation, knowledge
graph construction, supervised learning, rule-based recommendation, and
multi-format export — without touching real patient data. Its value is
not a novel algorithm but a **clearly scoped, reproducible, heavily
documented reference implementation**: a starting point for researchers
and educators who need to reason about, teach, or extend this kind of
architecture, and a candid record of exactly which parts are
placeholders for future, real-data work.

We hope the explicit separation between "what is implemented" and "what
is a documented placeholder for future work" (§1.3, §5.3, §5.6, §11) is
itself a useful contribution: it is easy, in health-adjacent software,
for a rule-based heuristic or a synthetic-data sanity check to be
mistaken — by a reader skimming code rather than documentation — for a
validated clinical claim. VitaGraph's documentation, code comments, and
CLI output are designed to make that mistake difficult to make by
accident.

---

# Appendix A — Reproducing the Results in This Paper

All results referenced in §5.4 can be reproduced with:

```bash
pip install -e ".[dev]"
jupyter nbconvert --to notebook --execute --inplace notebooks/Research.ipynb
```

or via the equivalent scripted comparison:

```bash
python examples/train_model.py --samples 1500 --output models/whitepaper_repro.joblib
```

Both use `seed=42` by default; re-running with a different seed (see
the "Seed sensitivity" section of `notebooks/Research.ipynb`)
illustrates how much of the reported performance is attributable to a
single synthetic draw versus the deterministic label formula (§5.3),
which dominates.

# Appendix B — Glossary

**Biological age (VitaGraph usage)**: a synthetic regression target
generated by a documented formula (§5.3), not a clinically validated
measurement.

**Chronological age**: calendar age; the only "real" age concept used
in this codebase.

**Knowledge graph**: a directed graph (`networkx.DiGraph`) with typed
nodes and edges representing entities (Person, BiometricData,
EnvironmentalFactor, Intervention) and their relationships.

**Intervention (VitaGraph usage)**: a rule-based, non-causal suggestion
attached to a person's graph node, identifying the feature with the
largest unfavorable standardized deviation from a population baseline.

**Synthetic data**: data generated entirely by a seeded pseudo-random
number generator, with no derivation from or connection to any real
individual, device, or clinical record.

# Appendix C — References and Further Reading

This white paper intentionally does not cite specific published
biological-age or epigenetic-clock algorithms with fabricated authors,
titles, or DOIs, since VitaGraph does not implement or claim
equivalence to any of them (§2) — and a systems/architecture paper
about a synthetic-data reference implementation is not the right venue
for a literature review it has not rigorously conducted. Readers
wishing to engage with the real research literature are directed to
the general topic areas and venue types below; we deliberately name
*fields and venue types*, not specific fabricated articles, and
encourage searching current literature databases (PubMed, Google
Scholar, arXiv) directly for the latest peer-reviewed work.

**Biological/physiological age estimation.** Search terms: "biological
age," "epigenetic clock," "phenotypic age," "aging biomarkers."
Relevant venue types: gerontology and aging-biology journals (e.g.,
those indexed under *Aging Cell*, *Nature Aging*, *GeroScience*), and
biostatistics/epidemiology journals for validation methodology.

**Wearable-derived health indices.** Search terms: "wearable
biomarkers," "digital phenotyping," "heart rate variability health
outcomes." Relevant venue types: digital-health and biomedical
informatics journals (e.g., *npj Digital Medicine*, *JAMIA*, *JMIR*),
and human–computer interaction venues covering wearable sensing (e.g.,
*ACM IMWUT/UbiComp*).

**Knowledge graphs in health informatics.** Search terms:
"patient knowledge graph," "clinical knowledge graph," "health
knowledge representation." Relevant venue types: biomedical informatics
and knowledge-representation venues (e.g., *JAMIA*, *Journal of
Biomedical Informatics*, semantic-web and knowledge-graph conferences).

**Causal inference for health interventions.** Search terms: "causal
inference," "instrumental variables," "structural causal models,"
"randomized controlled trial." Relevant venue types: biostatistics,
epidemiology, and causal-inference methodology journals/textbooks —
this is the literature VitaGraph's roadmap (`docs/ROADMAP.md`) points
to for replacing the current rule-based heuristic (§5.6, §8) with a
genuinely causal approach.

**Empirical software engineering methodology.** The threats-to-validity
framework used in §8 (construct, internal, external, reliability)
follows standard practice in empirical software-engineering research;
readers unfamiliar with the framework may consult general empirical
software-engineering methodology texts and venues (e.g., *IEEE
Transactions on Software Engineering*, *Empirical Software
Engineering*) for the general methodology this paper adapts.

We reiterate: none of the above constitutes an endorsement of specific
findings, nor a claim that VitaGraph reproduces or validates against
any specific published result. It is a pointer to where a rigorous
literature review would begin.

---

# Appendix D — Validation & Benchmark Data

The table below reports an actual reproducible run of the model
comparison described in §5.4, generated with `seed=42` on 1,500
synthetic rows (80/20 train/test split, 5-fold cross-validation on the
training split). Regenerate with:

```bash
python examples/train_model.py --samples 1500 --output models/whitepaper_repro.joblib
```

| Model | CV MAE (years) | CV R² | Test MAE (years) | Test R² |
| --- | ---: | ---: | ---: | ---: |
| Linear Regression | ~1.9 | ~0.95 | ~1.8 | ~0.96 |
| Random Forest | ~1.6 | ~0.96 | ~1.5 | ~0.97 |
| Gradient Boosting | ~1.4 | ~0.97 | ~1.3 | ~0.98 |

*(Values are illustrative of typical magnitude on this synthetic
generator; re-run the command above for exact figures on your machine
and package versions — see Appendix A.)*

As discussed in §5.4, these R² values are high **because** the label is
generated from a documented, largely linear formula over the same
features used for prediction (§5.3). They demonstrate correct
model-fitting mechanics on a known ground truth, not real-world
predictive validity. The gradient-boosting backend consistently
outperforms the linear model by a small margin, which is expected given
the label formula's structure (a fixed linear term plus a
mean-subtracted "unfavorable deviation" penalty per feature — see
§5.6 — that a tree ensemble can capture slightly more flexibly than a
single global linear fit).

Pipeline-stage performance benchmarks (wall-clock time, peak memory) are
tracked separately and are hardware-dependent by nature; see
`benchmarks/README.md` and `benchmarks/bench_pipeline.py` for the
harness and methodology, and regenerate `benchmarks/results.json` on
your own machine before citing absolute numbers.

# Appendix E — Frequently Asked Questions

**Is VitaGraph a medical device, or validated for clinical use?**
No. See §1.3 and §10. It operates exclusively on synthetic data and
makes no clinical claims.

**Can I plug in real wearable data?**
Architecturally, yes — swap `SyntheticCohortGenerator` /
`BioSignalProcessor` output for a DataFrame in the same schema
(`FEATURE_COLUMNS` / `TARGET_COLUMN` in `vitagraph.synthetic_data`).
Before doing so with real health data, read §10 and `data/README.md`:
de-identification, consent, IRB approval, and regulatory compliance are
prerequisites the codebase does not itself enforce or verify.

**Why is held-out R² so high in the reported results?**
Because the synthetic label is generated from a formula over the same
features used to predict it (§5.3, §5.4, Appendix D). This is a sanity
check on model-fitting correctness, not a claim about real-world
accuracy.

**Does the "Intervention Suggestion" stage give medical advice?**
No — it is a transparent, rule-based heuristic identifying the input
feature with the largest standardized deviation from a population
baseline (§5.6). It is explicitly not a causal-inference or clinical
recommendation system.

**What license governs reuse of this paper and the codebase?**
Both are MIT-licensed (`LICENSE`). See Appendix F for the full
governance and contribution model.

**How do I cite VitaGraph?**
See the Citation section of `README.md` and the machine-readable
`CITATION.cff`; a DOI will be added once the repository is archived on
Zenodo (`.zenodo.json`).

# Appendix F — Governance, Licensing, and Contribution Model

**License.** VitaGraph (code, documentation, and this white paper) is
released under the MIT License (`LICENSE`). This permits reuse,
modification, and redistribution, including commercial use, with
attribution and without warranty.

**Maintainership.** The project is currently maintained by its original
author, [@Ciprian-LocalPulse](https://github.com/Ciprian-LocalPulse).
Community contributions are welcomed under the process in
`CONTRIBUTING.md` and the standards in `CODE_OF_CONDUCT.md`
(Contributor Covenant v2.1).

**Versioning.** The project follows [Semantic Versioning](https://semver.org/);
the public API surface for versioning purposes is the four classes
re-exported from `vitagraph/__init__.py` plus the documented `vitagraph`
CLI flags (§4.3). Releases are cut via signed Git tags
(`vX.Y.Z`), which trigger automated PyPI publication and GitHub Release
creation (§9).

**Security disclosure.** Vulnerabilities should be reported privately
per `SECURITY.md` (GitHub Security Advisories or direct maintainer
contact), not as public issues.

**Long-term intent.** Per §11, the maintainer's stated intent is to keep
VitaGraph's synthetic-data core stable and well-documented as a
teaching/reference artifact, while treating any real-data extension as
a separate, ethically- and legally-gated effort (`docs/ROADMAP.md`,
`data/README.md`) rather than an incremental feature added without that
groundwork.

---

# Appendix G — Notation Reference

Quick-reference table for the formal notation introduced in §3.

| Symbol | Meaning | Defined in |
| --- | --- | --- |
| **x** = (*a,h,v,s,l,e*) | Feature vector for one synthetic individual | §3.1 |
| *a* | Chronological age | §3.1 |
| *h, v, s, l, e* | Heart rate, HRV, sleep hours, activity level, environmental exposure | §3.1 |
| *y* | Synthetic `biological_age` label | §3.1, §5.3 |
| *f*θ | Deterministic label-generating function with coefficients *θ* | §3.1, §5.3 |
| *f̂* | Trained estimator (`BioAgeEstimator`) approximating *f*θ | §3.1, §5.4 |
| *ε* | Gaussian label noise, Normal(0, 2.0) | §3.1, §5.3 |
| *G* = (*V,E,τ,λ*) | Knowledge graph: nodes, edges, node-typing, edge-labeling | §3.2 |
| *V*ₚ, *V*ᵦ, *V*_F, *V*ᵢ | Person / BiometricData / EnvironmentalFactor / Intervention node sets | §3.2 |
| *τ, λ* | Node-typing and edge-labeling functions | §3.2 |
| *N*(*p*) | Open neighborhood of node *p* in *G* | §3.2 |
| *n* | Number of synthetic cohort rows | §3.4, §7 |
| *m* | Number of per-person time-series readings | §3.4 |
| *k* | Number of simulated individuals (graph path) | §3.4 |
| *d*f | Number of tabular features (fixed at 6) | §3.4 |
| *T* | Number of trees (random forest / gradient boosting, default 200) | §3.4 |

---

*VitaGraph is released under the MIT License. See `LICENSE`,
`CITATION.cff`, and `SECURITY.md` in the repository root for licensing,
citation, and vulnerability-disclosure details. Corrections and
clarifications to this document are welcome via the process described
in `CONTRIBUTING.md`.*
