#!/usr/bin/env python3
"""Micro-benchmarks for VitaGraph's core stages.

Measures wall-clock time and peak memory (via ``tracemalloc``) for:
  1. Synthetic cohort generation (SyntheticCohortGenerator.generate)
  2. Model training (BioAgeEstimator.train) for each backend
  3. Model inference/predict throughput (rows/second)
  4. Knowledge-graph construction + export (JSON and GraphML)

Usage:
    python benchmarks/bench_pipeline.py --sizes 100 1000 10000 \
        --output benchmarks/results.json

Results are written as JSON (machine-readable, for tracking regressions
across commits/CI) and printed as a human-readable table. This is a
lightweight, dependency-free harness intentionally kept separate from
`pytest` — benchmarks measure performance, not correctness, and are run
on demand rather than on every CI push (see docs/architecture for where
this fits in the pipeline).
"""

from __future__ import annotations

import argparse
import json
import time
import tracemalloc
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from sklearn.model_selection import train_test_split

from vitagraph import (
    BioAgeEstimator,
    BioSignalProcessor,
    KnowledgeGraph,
    SyntheticCohortGenerator,
)
from vitagraph.synthetic_data import FEATURE_COLUMNS, TARGET_COLUMN

MODEL_TYPES = ["linear", "random_forest", "gradient_boosting"]


@dataclass
class BenchResult:
    stage: str
    n: int
    seconds: float
    peak_memory_mb: float
    extra: dict


def timed(fn, *args, **kwargs):
    tracemalloc.start()
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak / (1024 * 1024)


def bench_generation(n: int) -> BenchResult:
    gen = SyntheticCohortGenerator(seed=42)
    _, elapsed, peak_mb = timed(gen.generate, num_samples=n)
    return BenchResult("cohort_generation", n, elapsed, peak_mb, {})


def bench_training(n: int) -> list[BenchResult]:
    cohort = SyntheticCohortGenerator(seed=42).generate(num_samples=n)
    X, y = cohort[FEATURE_COLUMNS], cohort[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    results = []
    for model_type in MODEL_TYPES:
        estimator = BioAgeEstimator(model_type=model_type)
        _, elapsed, peak_mb = timed(estimator.train, X_train, y_train)

        _, predict_elapsed, _ = timed(estimator.predict, X_test)
        throughput = len(X_test) / predict_elapsed if predict_elapsed > 0 else float("inf")

        results.append(
            BenchResult(
                f"train_{model_type}",
                n,
                elapsed,
                peak_mb,
                {"predict_rows_per_sec": round(throughput, 1)},
            )
        )
    return results


def bench_graph(n: int) -> BenchResult:
    processor = BioSignalProcessor(seed=42)
    start_time = datetime(2026, 1, 1)

    def build():
        kg = KnowledgeGraph()
        for i in range(n):
            person_id = f"P{i:05d}"
            hr_df = processor.generate_synthetic_heart_rate(10, start_time)
            sleep_df = processor.generate_synthetic_sleep_data(5, start_time.date())
            kg.build_from_processed_data(person_id, hr_df, sleep_df)
        return kg

    kg, elapsed, peak_mb = timed(build)
    info = kg.get_graph_info()
    return BenchResult("graph_construction", n, elapsed, peak_mb, info)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=[100, 1000, 10000])
    parser.add_argument("--graph-sizes", type=int, nargs="+", default=[10, 50, 200])
    parser.add_argument("--output", type=Path, default=Path("benchmarks/results.json"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    all_results: list[BenchResult] = []

    for n in args.sizes:
        all_results.append(bench_generation(n))
        all_results.extend(bench_training(n))

    for n in args.graph_sizes:
        all_results.append(bench_graph(n))

    print(f"\n{'stage':<24}{'n':>10}{'seconds':>12}{'peak MB':>12}  extra")
    for r in all_results:
        print(f"{r.stage:<24}{r.n:>10}{r.seconds:>12.4f}{r.peak_memory_mb:>12.2f}  {r.extra}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": [asdict(r) for r in all_results],
    }
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nWrote machine-readable results to {args.output}")


if __name__ == "__main__":
    main()
