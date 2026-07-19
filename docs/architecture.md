# Architecture

VitaGraph's pipeline moves through seven stages, from simulated raw
signals to exported artifacts. Every stage is synthetic/deterministic
end-to-end — see [Methodology](METHODOLOGY.md) for the scope statement.

![VitaGraph architecture diagram](architecture/architecture.png)

*(Editable source: [`architecture.drawio`](architecture/architecture.drawio),
open at [app.diagrams.net](https://app.diagrams.net). Raw SVG:
[`architecture.svg`](architecture/architecture.svg).)*

## Stage-by-module mapping

| Stage | Module | Key class / function |
| --- | --- | --- |
| Simulated Wearables | `vitagraph.bio_signal_processor` | `BioSignalProcessor.generate_synthetic_heart_rate`, `.generate_synthetic_hrv` |
| Signal Processing | `vitagraph.bio_signal_processor` | Circadian modeling + clipping baked into the same generators |
| Knowledge Graph | `vitagraph.knowledge_graph` | `KnowledgeGraph.build_from_processed_data` |
| Synthetic Cohort Generator | `vitagraph.synthetic_data` | `SyntheticCohortGenerator.generate` |
| ML Estimator | `vitagraph.bio_age_estimator` | `BioAgeEstimator.train` / `.predict` / `.cross_validate` |
| Intervention Suggestion | `vitagraph.pipeline` | `recommend_focus_area` (rule-based heuristic, **not** causal inference) |
| Visualization | `vitagraph.visualization` | `plot_person_subgraph` |
| Export | `vitagraph.knowledge_graph`, `vitagraph.bio_age_estimator` | `export_to_json`, `export_to_graphml`, `save_model` |

Everything above is orchestrated end-to-end by
[`vitagraph.pipeline.run_pipeline`](api/pipeline.md), which the `vitagraph run`
CLI subcommand calls directly. `vitagraph train` and `vitagraph predict`
exercise the `SyntheticCohortGenerator` → `BioAgeEstimator` slice of the
diagram in isolation, without touching the graph or visualization stages.

## Design principles

1. **Every random draw is seeded.** All generators accept a `seed`, and
   pipeline runs are fully reproducible given the same seed and inputs.
2. **Config, not magic numbers.** Every population-level assumption
   (baseline heart rate, sleep hours, the biological-age formula's
   coefficients) lives in [`vitagraph.config`](api/config.md) as a frozen
   dataclass, so it's auditable and overridable from one place instead
   of scattered through the codebase.
3. **Rule-based, not causal.** The "Intervention Suggestion" stage is an
   explicit, transparent heuristic (standardized distance from a
   population baseline) — it is *not* the output of a causal-inference
   model. See [`docs/ROADMAP.md`](ROADMAP.md) for that future goal.
4. **Structured results, not just stdout.** `run_pipeline` returns a
   `PipelineResult` dataclass (predictions, CV scores, test metrics, the
   graph object, and the saved model path) so the pipeline is equally
   usable as a library call or a CLI command.
