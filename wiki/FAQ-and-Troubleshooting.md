# FAQ and Troubleshooting

## General

**Is VitaGraph a medical device, or validated for clinical use?**
No. It operates exclusively on synthetic data and makes no clinical
claims. See [Methodology and Scope](Methodology-and-Scope).

**Can I use VitaGraph's biological-age numbers for real health
decisions?**
No — see the disclaimer on [Home](Home) and in the repository
[`README.md`](https://github.com/Ciprian-LocalPulse/vitagraph#-important-disclaimer).

**Why is held-out model accuracy (R²) so high in the examples?**
Because the synthetic `biological_age` label is generated from a
documented formula over the same features used to predict it. See
[Methodology and Scope § Why held-out model accuracy looks so good](Methodology-and-Scope#why-held-out-model-accuracy-looks-so-good).

**Does the "Intervention Suggestion" give medical advice?**
No — it's a transparent, rule-based heuristic, not a causal or clinical
recommendation system. See
[Methodology and Scope § The intervention heuristic is not causal inference](Methodology-and-Scope#the-intervention-heuristic-is-not-causal-inference).

**Can I plug in real wearable/clinical data?**
Architecturally yes, but there are ethical/legal prerequisites (consent,
IRB approval, de-identification) the codebase does not itself enforce.
See [Methodology and Scope § If you plan to plug in real data](Methodology-and-Scope#if-you-plan-to-plug-in-real-data).

## Installation & environment

**`pip install vitagraph` fails with a build error.**
Confirm you're on Python 3.10+ (`python --version`). If a specific
dependency fails to build (e.g., on an unusual platform), try
`pip install --upgrade pip setuptools wheel` first, then retry.

**I want to develop locally — what's the right install command?**
`pip install -e ".[dev]"` (adds pytest, ruff, black, mypy, pre-commit).
Add `".[docs]"` too if you're working on documentation
(`pip install -e ".[dev,docs]"`).

**Docker build is slow / large.**
The provided `Dockerfile` is a multi-stage build (wheel build stage +
minimal runtime stage), so the final image only contains the installed
package, not the full build toolchain. If you only need to run the CLI
occasionally, `pip install vitagraph` locally is usually simpler than
Docker.

## Running the pipeline

**`vitagraph run` succeeds but I can't find my results.**
Check `--output-dir` (default varies by version — pass it explicitly).
Look for `individuals_summary.csv`, the exported model (`.joblib` +
`.json` metadata), and the graph exports (`.json`, `.graphml`).

**My results differ between two runs with the same `--seed`.**
This shouldn't happen for identical package versions, inputs, and
platform. If you see this, please check whether any input parameters
differ (e.g., `--individuals`, `--days`) and, if not, open an issue with
your exact command and environment (`python --version`, `pip show
vitagraph`, OS).

**`vitagraph predict` raises `MissingFeatureColumnsError`.**
Make sure you're passing all six required flags: `--chronological-age`,
`--heart-rate`, `--hrv`, `--sleep-hours`, `--activity-level`,
`--environmental-exposure`. See [Getting Started](Getting-Started) for
a full example.

**`ModelNotTrainedError` when calling `.predict()`.**
Call `.train(X, y)` (or `.load_model(path)`) before `.predict()`. See
the [Architecture](Architecture) page for the `BioAgeEstimator` API
shape.

## Documentation & tooling

**How do I build the docs site locally?**
```bash
pip install -e ".[docs]"
mkdocs serve
```
or `docker compose --profile docs up docs`, then open
<http://localhost:8000>.

**How do I regenerate the architecture diagram or white paper PDF?**
- Diagram: edit `docs/architecture/architecture.drawio` at
  [app.diagrams.net](https://app.diagrams.net), export as SVG/PNG into
  `docs/architecture/`.
- White paper: edit `docs/whitepaper/VitaGraph_White_Paper.md`, then run
  `docs/whitepaper/build_pdf.sh` (requires `pandoc` + `wkhtmltopdf`).

**Where do I report a bug or request a feature?**
[GitHub Issues](https://github.com/Ciprian-LocalPulse/vitagraph/issues).
See [`CONTRIBUTING.md`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/CONTRIBUTING.md)
for the PR workflow and code-style requirements.

**Where do I report a security vulnerability?**
**Not** as a public issue — see
[`SECURITY.md`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/SECURITY.md)
for the private disclosure process (GitHub Security Advisories or
direct maintainer contact) and expected response timelines.

**How do I cite VitaGraph?**
See the Citation section of the repository
[`README.md`](https://github.com/Ciprian-LocalPulse/vitagraph#-citation)
and the machine-readable [`CITATION.cff`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/CITATION.cff).
A DOI will be added once the repository is archived on Zenodo.

## Still stuck?

Open a [GitHub Discussion or Issue](https://github.com/Ciprian-LocalPulse/vitagraph/issues)
with:
1. The exact command or code you ran
2. The full error message/traceback
3. `python --version` and `pip show vitagraph`
4. Your operating system

## Related pages

- [Home](Home)
- [Getting Started](Getting-Started)
- [Architecture](Architecture)
- [Methodology and Scope](Methodology-and-Scope)
