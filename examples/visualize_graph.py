#!/usr/bin/env python3
"""Example: build a person's knowledge graph and render/export it.

Usage:
    python examples/visualize_graph.py --person-id P001 --days 14 \
        --output-dir outputs/graph_demo

Demonstrates the KnowledgeGraph + BioSignalProcessor + visualization
layer together: simulate biometric time series for one synthetic
person, assemble them into a typed knowledge graph, attach a rule-based
intervention suggestion, then export to JSON/GraphML and a PNG plot.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

from vitagraph import BioSignalProcessor, KnowledgeGraph
from vitagraph.config import SignalBaseline
from vitagraph.pipeline import recommend_focus_area
from vitagraph.visualization import plot_person_subgraph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--person-id", default="P001")
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/graph_demo"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    processor = BioSignalProcessor(seed=args.seed)
    start = datetime.now() - timedelta(days=args.days)

    hr_df = processor.generate_synthetic_heart_rate(
        num_samples=args.days * 4, start_time=start, interval_minutes=360
    )
    hrv_df = processor.generate_synthetic_hrv(
        num_samples=args.days * 4, start_time=start, interval_minutes=360
    )
    sleep_df = processor.generate_synthetic_sleep_data(num_days=args.days, start_date=start.date())

    kg = KnowledgeGraph()
    kg.build_from_processed_data(args.person_id, hr_df, sleep_df, hrv_df)

    # Attach a rule-based intervention recommendation based on the average
    # of the simulated signals for this person (see docs/METHODOLOGY.md).
    summary_row = {
        "heart_rate_avg": hr_df["heart_rate"].mean(),
        "hrv_avg": hrv_df["hrv_ms"].mean(),
        "sleep_hours_avg": sleep_df["sleep_hours"].mean(),
        "activity_level": SignalBaseline().activity_level_mean,
        "environmental_exposure": SignalBaseline().environmental_exposure_mean,
    }
    import pandas as pd

    focus_area, rationale = recommend_focus_area(pd.Series(summary_row), SignalBaseline())
    kg.add_intervention_node(
        f"INT_{args.person_id}", args.person_id, focus_area, rationale, datetime.now()
    )

    print("Graph summary:", kg.get_graph_info())

    json_path = kg.export_to_json(args.output_dir / f"{args.person_id}_graph.json")
    graphml_path = kg.export_to_graphml(args.output_dir / f"{args.person_id}_graph.graphml")
    png_path = plot_person_subgraph(kg, args.person_id, args.output_dir / f"{args.person_id}.png")

    print(f"Exported: {json_path}, {graphml_path}, {png_path}")


if __name__ == "__main__":
    main()
