# VitaGraph Wiki

Welcome to the VitaGraph wiki — the narrative, browsable companion to
the [repository](https://github.com/Ciprian-LocalPulse/vitagraph) and
the [generated API documentation](https://ciprian-localpulse.github.io/vitagraph/).

> **VitaGraph** is an MIT-licensed reference framework for simulating
> and studying the integration of multi-source biometric data using
> knowledge graphs and machine learning — built entirely on synthetic,
> seeded random data. It is a research/education tool, **not** a
> medical device, and none of its outputs represent real biological
> age or health status.

## Wiki pages

| Page | What's in it |
| --- | --- |
| **[Getting Started](Getting-Started)** | Install VitaGraph, run the pipeline, first CLI commands, first library calls |
| **[Architecture](Architecture)** | The seven pipeline stages, the diagram, module-by-module mapping |
| **[Methodology and Scope](Methodology-and-Scope)** | Exactly what each synthetic number does and doesn't mean; the biological-age formula |
| **[FAQ and Troubleshooting](FAQ-and-Troubleshooting)** | Common questions, common errors, how to get help |

## Quick links

- 📦 **Install**: `pip install vitagraph`
- 🚀 **Run**: `vitagraph run --individuals 5 --days 30 --output-dir ./outputs`
- 📖 **Full docs site**: <https://ciprian-localpulse.github.io/vitagraph/>
- 📄 **White paper**: [`docs/whitepaper/VitaGraph_White_Paper.pdf`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/docs/whitepaper/VitaGraph_White_Paper.pdf)
- 🧪 **Notebooks**: [`notebooks/`](https://github.com/Ciprian-LocalPulse/vitagraph/tree/main/notebooks)
- 🐛 **Report an issue**: [GitHub Issues](https://github.com/Ciprian-LocalPulse/vitagraph/issues)
- 🔒 **Report a vulnerability**: see [`SECURITY.md`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/SECURITY.md) — please do **not** open a public issue for security reports
- 🤝 **Contribute**: [`CONTRIBUTING.md`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/CODE_OF_CONDUCT.md)

## What VitaGraph demonstrates

- **Synthetic biometric time-series generation** — heart rate, HRV,
  sleep, and environmental exposure, with circadian and noise patterns.
- **Knowledge-graph representation** of person–data–environment
  relationships using `networkx`, exportable to JSON and GraphML.
- **Pluggable ML backends** (linear, random forest, gradient boosting)
  for regression on a documented, synthetic `biological_age` label.
- **A transparent, rule-based intervention heuristic** — explicitly
  *not* a causal-inference model (see [Methodology and Scope](Methodology-and-Scope)).
- **A CLI and a library API**, both fully reproducible via seeded
  random generation.

## Project status

| | |
| --- | --- |
| Version | `0.2.0` |
| License | MIT |
| CI | [![CI](https://github.com/Ciprian-LocalPulse/vitagraph/actions/workflows/ci.yml/badge.svg)](https://github.com/Ciprian-LocalPulse/vitagraph/actions/workflows/ci.yml) |
| Security scanning | [![CodeQL](https://github.com/Ciprian-LocalPulse/vitagraph/actions/workflows/codeql.yml/badge.svg)](https://github.com/Ciprian-LocalPulse/vitagraph/actions/workflows/codeql.yml) |
| Docs site | [![Docs](https://github.com/Ciprian-LocalPulse/vitagraph/actions/workflows/docs.yml/badge.svg)](https://ciprian-localpulse.github.io/vitagraph/) |

---

*This wiki is maintained alongside the codebase. If something here is
out of date, please open an issue or a PR against the wiki — see
[Contributing](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/CONTRIBUTING.md).*
