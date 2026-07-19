# VitaGraph

Reference framework for simulating and studying the integration of
multi-source biometric data using knowledge graphs and machine
learning — on **entirely synthetic, seeded random data**.

!!! warning "Research reference implementation"
    VitaGraph is not a medical device. Its biological-age predictions are
    not validated against any real clinical cohort. See
    [Methodology](METHODOLOGY.md) for the full scope statement.

## What's here

- **[Methodology](METHODOLOGY.md)** — precise statement of what is and
  is not implemented, and what every synthetic number does/doesn't mean.
- **[Architecture](architecture.md)** — the data flow from simulated
  wearables through to export, as a diagram.
- **[Roadmap](ROADMAP.md)** — the longer-term research vision, including
  what would be required to move from synthetic to real data.
- **[API Reference](api/index.md)** — auto-generated from docstrings for
  every public module.
- **[Benchmarks](https://github.com/Ciprian-LocalPulse/vitagraph/tree/main/benchmarks)** —
  performance characteristics of each pipeline stage.

## Quick start

```bash
pip install vitagraph
vitagraph run --individuals 5 --days 30 --output-dir ./outputs
```

See the [project README](https://github.com/Ciprian-LocalPulse/vitagraph#-quick-start)
for the full quick-start guide, or open
[`notebooks/Tutorial.ipynb`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/notebooks/Tutorial.ipynb)
for an interactive walkthrough.
