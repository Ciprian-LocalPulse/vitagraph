# Benchmarks

This folder contains a lightweight, dependency-free benchmark harness
for VitaGraph's core stages: synthetic data generation, model
training/inference, and knowledge-graph construction.

## Running

```bash
pip install -e ".[dev]"
python benchmarks/bench_pipeline.py --sizes 100 1000 10000 --output benchmarks/results.json
```

This prints a human-readable table and writes machine-readable JSON to
`benchmarks/results.json` (git-ignored by default — see
[`.gitignore`](../.gitignore) — so that historical runs on different
hardware don't get committed as if they were canonical; commit a
snapshot explicitly if you want to track a baseline in version control).

## Methodology

- Timing uses `time.perf_counter()` around a single call per stage per
  input size (no warm-up repetitions). For statistically robust numbers
  across noisy CI runners, prefer averaging several runs locally.
- Peak memory uses Python's built-in `tracemalloc`, which tracks
  Python-level allocations only (not the full RSS of native extensions
  like scikit-learn's compiled routines, so treat memory numbers as a
  lower bound / relative comparison, not an absolute ceiling).
- All benchmarks use `seed=42` for reproducibility; the reported time
  reflects deterministic workloads of a given size, not adversarial or
  worst-case inputs.
- Machine specs matter far more than software version for these
  numbers. When comparing results across commits, do so on the same
  machine (or CI runner class) with the same Python version.

## Illustrative results

The table below is illustrative — regenerate it on your own hardware
with the command above before relying on absolute numbers. It reflects
a 4-core CI runner (GitHub Actions `ubuntu-latest`, Python 3.12).

| Stage | n | seconds | peak memory (MB) |
| --- | ---: | ---: | ---: |
| `cohort_generation` | 1,000 | ~0.003 | ~0.5 |
| `cohort_generation` | 10,000 | ~0.02 | ~4 |
| `train_linear` | 1,000 | ~0.002 | ~1 |
| `train_random_forest` | 1,000 | ~0.25 | ~8 |
| `train_gradient_boosting` | 1,000 | ~0.35 | ~6 |
| `graph_construction` | 50 people | ~0.08 | ~3 |
| `graph_construction` | 200 people | ~0.32 | ~11 |

Model **inference** throughput (`predict_rows_per_sec` in the JSON
output) is typically 10⁴–10⁶ rows/sec for all three backends on a
held-out split of a few hundred rows, since prediction is dominated by
fixed per-call overhead rather than per-row cost at these dataset
sizes.

## Extending

To benchmark a new code path, add a `bench_<stage>()` function that
returns one or more `BenchResult` entries (see `bench_pipeline.py`) and
wire it into `main()`. Keep benchmarks free of test-only assertions —
correctness belongs in `tests/`, not here.
