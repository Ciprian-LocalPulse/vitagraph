#!/usr/bin/env python3
"""Example: generate a synthetic cohort dataset and write it to CSV.

Usage:
    python examples/generate_dataset.py --samples 1000 --seed 42 \
        --output outputs/synthetic_cohort.csv

This demonstrates the lowest-level building block of VitaGraph:
``SyntheticCohortGenerator``, which produces a fully synthetic,
reproducible tabular dataset (features + a simulated biological-age
label) with no dependency on real wearable or clinical data.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from vitagraph import SyntheticCohortGenerator
from vitagraph.synthetic_data import FEATURE_COLUMNS, TARGET_COLUMN


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=1000, help="Number of synthetic rows")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/synthetic_cohort.csv"),
        help="Destination CSV path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    generator = SyntheticCohortGenerator(seed=args.seed)
    cohort = generator.generate(num_samples=args.samples)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cohort.to_csv(args.output, index=False)

    print(f"Generated {len(cohort)} synthetic rows -> {args.output}")
    print(f"Feature columns: {FEATURE_COLUMNS}")
    print(f"Target column:   {TARGET_COLUMN}")
    print("\nPreview:")
    print(cohort.head())
    print("\nSummary statistics:")
    print(cohort.describe().round(2))


if __name__ == "__main__":
    main()
