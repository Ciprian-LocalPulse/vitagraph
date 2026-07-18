# Changelog

All notable changes to VitaGraph are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Graph Neural Networks (GCN/GraphSAGE) for node embedding and per-person age prediction
- Causal inference methods (IV, propensity-score matching, causal forests)
- Federated learning & differential privacy
- Real wearable device integration (Apple HealthKit, Google Fit, Oura)
- Multi-omic data support (genomics, proteomics, metabolomics)
- Interactive web dashboard (Streamlit or Plotly Dash)

---

## [0.2.0] - 2026-07-18

### Added

#### Core Modules
- `synthetic_data.py`: `SyntheticCohortGenerator` with configurable population baselines, deterministic biological-age labels, reproducible seeded generation
- `bio_signal_processor.py`: Heart rate, HRV, sleep, and environmental-exposure generators; circadian-pattern simulation; rolling-window smoothing + outlier clipping
- `knowledge_graph.py`: NetworkX-backed knowledge graph with Person, BiometricData, EnvironmentalFactor, Intervention node types; HAS_DATA, EXPOSED_TO, HAS_RECOMMENDATION edges; JSON/GraphML export; per-person subgraph retrieval
- `bio_age_estimator.py`: Pluggable ML models (Linear, Random Forest, Gradient Boosting); cross-validation; feature importance; metadata-tracked save/load; error handling (InvalidModelTypeError, ModelNotTrainedError, MissingFeatureColumnsError)
- `pipeline.py`: `run_pipeline()` orchestration function; rule-based intervention prioritization heuristic; end-to-end simulation → graph → training → prediction flow
- `cli.py`: Command-line interface with `run`, `train`, `predict` subcommands; argparse-based argument parsing; comprehensive help text

#### Configuration & Logging
- `config.py`: Centralized dataclass-based configuration (SignalBaseline, BioAgeFormulaWeights, PipelineDefaults)
- `logging_config.py`: Idempotent logger factory (get_logger)
- `exceptions.py`: Custom exception types (VitaGraphError, InvalidModelTypeError, ModelNotTrainedError, MissingFeatureColumnsError, GraphNodeNotFoundError)

#### Visualization
- `visualization.py`: `plot_person_subgraph()` matplotlib-based knowledge-graph rendering

#### Testing
- `tests/conftest.py`: pytest fixtures for baseline, processor, cohort_generator, empty_graph, start_time
- `tests/test_synthetic_data.py`: 6 tests covering generation, reproducibility, bounds-checking
- `tests/test_bio_signal_processor.py`: 10 tests for HR/HRV/sleep/environmental generators, signal processing, error handling
- `tests/test_knowledge_graph.py`: 10 tests for node/edge construction, subgraph retrieval, JSON/GraphML export
- `tests/test_bio_age_estimator.py`: 9 tests for model training, evaluation, cross-validation, feature importance, save/load
- `tests/test_pipeline.py`: 4 tests for end-to-end pipeline execution and artifact generation
- Target coverage: ≥80%

#### Documentation
- `README.md`: Project overview, quick-start examples, library API, repository structure, testing, features, citation
- `DONATE.md`: Comprehensive donation guide (cryptocurrency, bank transfers, impact levels)
- `SPONSORS.md`: Recognition page for donors and institutional partners
- `docs/METHODOLOGY.md`: Comprehensive scope statement, ethical considerations, reproducibility, validation requirements
- `docs/ROADMAP.md`: Release-by-release vision (GNNs, causal inference, federated learning, real data, multi-omics)
- `CONTRIBUTING.md`: Contribution guidelines, development setup, code style, PR workflow, testing requirements
- `CHANGELOG.md`: This file
- `.gitignore`: Python build artifacts, caches, coverage, virtualenvs, OS files

#### Assets
- `assets/vitagraph_cover.png`: Professional banner image (multi-omic knowledge graph visualization)

#### Configuration Files
- `pyproject.toml`: PEP 517/518 build configuration, package metadata, tool configurations (ruff, black, mypy, pytest)
- `requirements.txt`: Runtime dependencies (numpy, pandas, networkx, scikit-learn, joblib, matplotlib)
- `requirements-dev.txt`: Development dependencies (pytest, pytest-cov, ruff, black, mypy)
- `LICENSE`: MIT License

#### Package Metadata
- `src/vitagraph/__init__.py`: Public API exports, `__version__`

### Changed
- (Initial release; no prior versions to change)

### Deprecated
- (None)

### Removed
- (Eliminated from original submission: duplicate files in root vs. src/, placeholder bio_age_estimator.py with no model-type flexibility, no-op placeholder in bio_signal_processor.process_biometric_data, inconsistent main.py implementations, vague donation-linked README)

### Fixed
- (Initial release; no prior bugs to fix)

### Security
- No security updates in initial release

---

## [0.1.0] - 2026-01-01

### Added
- Initial repository structure with duplicate/placeholder code
- Basic bio_age_estimator.py, bio_signal_processor.py, knowledge_graph.py, main.py
- README.md with fundraising focus
- No tests, limited documentation

### Removed (in v0.2.0)
- Duplicate source files (root vs. src/ copies)
- Incomplete docstrings and type hints
- Placeholder process_biometric_data implementation
- Inconsistent pipeline implementations

---

## Notes

### Versioning

- **0.x.y**: Alpha releases; API may change
- **1.0.0+**: Stable API; semantic versioning

### When to file an issue vs. PR

- **Bug report**: File an Issue, optionally include a PR with a fix
- **Feature request**: File an Issue to discuss, then a PR if approved
- **Documentation**: PR directly, or Issue if you'd like feedback first
- **Question**: Use Discussions or Issues (GitHub will guide you)

### Release schedule

- Target quarterly releases (v0.3.0 Q3 2026, v1.0.0 Q4 2026, etc.)
- Critical security patches released immediately
- See [docs/ROADMAP.md](docs/ROADMAP.md) for feature timelines

---

## Contributors

### v0.2.0

- **Ciprian Stefan Plesca**: Project lead, core implementation, documentation, testing

---

**Made for Research** | *Transparency & Progress*

Last updated: 2026-07-18
