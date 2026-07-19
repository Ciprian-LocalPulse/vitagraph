# Architecture

VitaGraph's pipeline moves through seven stages, from simulated raw
signals to exported artifacts. Every stage is synthetic and
deterministic end-to-end (given a fixed seed) — see
[Methodology and Scope](Methodology-and-Scope) for what that does and
doesn't imply.

![VitaGraph architecture diagram](https://raw.githubusercontent.com/Ciprian-LocalPulse/vitagraph/main/docs/architecture/architecture.png)

*(Editable source: [`docs/architecture/architecture.drawio`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/docs/architecture/architecture.drawio),
open at [app.diagrams.net](https://app.diagrams.net).)*

## The seven stages

1. **Simulated Wearables** — synthetic raw heart rate, HRV, sleep, and
   environmental-exposure time series.
2. **Signal Processing** — circadian modeling (heart rate dips
   overnight), rolling-window smoothing, z-score outlier clipping.
3. **Knowledge Graph** — a typed graph (`Person`, `BiometricData`,
   `EnvironmentalFactor`, `Intervention` nodes) built from the processed
   signals.
4. **Synthetic Cohort Generator** — an independent, larger-scale tabular
   dataset (hundreds–thousands of rows) used to train the ML model,
   with a documented, deterministic `biological_age` label.
5. **ML Estimator** — a pluggable scikit-learn regressor (linear,
   random forest, or gradient boosting) trained on the tabular cohort.
6. **Intervention Suggestion** — a rule-based heuristic that flags the
   feature with the largest unfavorable deviation from a population
   baseline, attached to the graph as an `Intervention` node.
7. **Visualization and Export** — a static PNG subgraph plot, plus
   JSON, GraphML, joblib+JSON, and CSV export.

## Stage → module mapping

| Stage | Module | Key class / function |
| --- | --- | --- |
| Simulated Wearables | `vitagraph.bio_signal_processor` | `BioSignalProcessor.generate_synthetic_heart_rate`, `.generate_synthetic_hrv` |
| Signal Processing | `vitagraph.bio_signal_processor` | `BioSignalProcessor.process_biometric_data` |
| Knowledge Graph | `vitagraph.knowledge_graph` | `KnowledgeGraph.build_from_processed_data` |
| Synthetic Cohort Generator | `vitagraph.synthetic_data` | `SyntheticCohortGenerator.generate` |
| ML Estimator | `vitagraph.bio_age_estimator` | `BioAgeEstimator.train` / `.predict` / `.cross_validate` |
| Intervention Suggestion | `vitagraph.pipeline` | `recommend_focus_area` |
| Visualization | `vitagraph.visualization` | `plot_person_subgraph` |
| Export | `vitagraph.knowledge_graph`, `vitagraph.bio_age_estimator` | `export_to_json`, `export_to_graphml`, `save_model` |

All seven stages are orchestrated end-to-end by
[`vitagraph.pipeline.run_pipeline`](https://ciprian-localpulse.github.io/vitagraph/api/pipeline/),
which the `vitagraph run` CLI subcommand calls directly. `vitagraph
train` and `vitagraph predict` exercise only the Synthetic Cohort
Generator → ML Estimator slice, without touching the graph or
visualization stages.

## Design principles

1. **Every random draw is seeded.** All generators accept a `seed`, so
   pipeline runs are fully reproducible given the same seed and inputs.
2. **Config, not magic numbers.** Population-level assumptions (baseline
   heart rate, sleep hours, the biological-age formula's coefficients)
   live in [`vitagraph.config`](https://ciprian-localpulse.github.io/vitagraph/api/config/)
   as frozen dataclasses — one auditable, overridable place.
3. **Rule-based, not causal.** The intervention stage is a transparent
   heuristic (standardized distance from a population baseline), not a
   causal-inference model.
4. **Structured results, not just stdout.** `run_pipeline` returns a
   `PipelineResult` dataclass (predictions, CV scores, test metrics,
   the graph object, and the model path), so the pipeline is equally
   usable as a library call or a CLI command.

## Related pages

- [Methodology and Scope](Methodology-and-Scope) — the precise
  formulas and what they do/don't represent
- [Getting Started](Getting-Started) — run this architecture end-to-end
- Full API reference: <https://ciprian-localpulse.github.io/vitagraph/api/>
