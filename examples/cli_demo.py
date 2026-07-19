#!/usr/bin/env python3
"""Example: drive the ``vitagraph`` CLI end-to-end from a Python script.

Usage:
    python examples/cli_demo.py --output-dir outputs/cli_demo

This is a thin wrapper that shells out to the installed ``vitagraph``
console script (equivalent to running the three commands below by
hand), then prints a short summary of the artifacts produced. It is a
good starting point if you're wiring VitaGraph into a larger shell
pipeline or a CI job.

Equivalent shell commands:
    vitagraph run --individuals 5 --days 30 --output-dir outputs/cli_demo
    vitagraph train --samples 500 --model gradient_boosting \
        --output outputs/cli_demo/standalone_model.joblib
    vitagraph predict --model-path outputs/cli_demo/standalone_model.joblib \
        --chronological-age 45 --heart-rate 74 --hrv 48 --sleep-hours 6.5 \
        --activity-level 0.5 --environmental-exposure 0.4
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print(f"\n$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/cli_demo"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_path = args.output_dir / "standalone_model.joblib"

    run(
        [
            sys.executable,
            "-m",
            "vitagraph.cli",
            "run",
            "--individuals",
            "5",
            "--days",
            "30",
            "--output-dir",
            str(args.output_dir),
        ]
    )

    run(
        [
            sys.executable,
            "-m",
            "vitagraph.cli",
            "train",
            "--samples",
            "500",
            "--model",
            "gradient_boosting",
            "--output",
            str(model_path),
        ]
    )

    run(
        [
            sys.executable,
            "-m",
            "vitagraph.cli",
            "predict",
            "--model-path",
            str(model_path),
            "--chronological-age",
            "45",
            "--heart-rate",
            "74",
            "--hrv",
            "48",
            "--sleep-hours",
            "6.5",
            "--activity-level",
            "0.5",
            "--environmental-exposure",
            "0.4",
        ]
    )

    print(f"\nArtifacts written under: {args.output_dir.resolve()}")
    for p in sorted(args.output_dir.glob("*")):
        print(f"  - {p.name}")


if __name__ == "__main__":
    main()
