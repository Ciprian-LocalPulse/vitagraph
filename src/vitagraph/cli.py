"""Command-line interface for VitaGraph.

Examples:
    vitagraph run --individuals 5 --output-dir outputs/
    vitagraph train --samples 1000 --model random_forest --output models/bio_age_model.joblib
    vitagraph predict --model-path models/bio_age_model.joblib --chronological-age 40 \\
        --heart-rate 72 --hrv 50 --sleep-hours 7 --activity-level 0.6 --environmental-exposure 0.3
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from vitagraph import __version__
from vitagraph.bio_age_estimator import BioAgeEstimator
from vitagraph.config import PipelineDefaults
from vitagraph.logging_config import get_logger
from vitagraph.pipeline import run_pipeline
from vitagraph.synthetic_data import FEATURE_COLUMNS, TARGET_COLUMN, SyntheticCohortGenerator

logger = get_logger(__name__)

_MODEL_CHOICES = ["linear", "random_forest", "gradient_boosting"]

_DISCLAIMER = (
    "NOTE: all data above is synthetic. This is a research/education demo, "
    "not a medical device, and not a source of real health guidance."
)


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="vitagraph", description="VitaGraph synthetic-data research pipeline CLI")
    parser.add_argument("--version", action="version", version=f"vitagraph {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_p = subparsers.add_parser("run", help="Run the full simulate -> graph -> train -> predict pipeline")
    run_p.add_argument("--individuals", type=int, default=PipelineDefaults.num_individuals)
    run_p.add_argument("--days", type=int, default=PipelineDefaults.num_sleep_days)
    run_p.add_argument("--hr-samples-per-day", type=int, default=PipelineDefaults.num_hr_samples_per_day)
    run_p.add_argument("--training-samples", type=int, default=PipelineDefaults.training_samples)
    run_p.add_argument("--model", choices=_MODEL_CHOICES, default=PipelineDefaults.model_type)
    run_p.add_argument("--seed", type=int, default=PipelineDefaults.random_seed)
    run_p.add_argument("--cv-folds", type=int, default=PipelineDefaults.cv_folds)
    run_p.add_argument("--output-dir", type=Path, default=None)

    train_p = subparsers.add_parser("train", help="Train (and save) a model on synthetic cohort data only")
    train_p.add_argument("--samples", type=int, default=PipelineDefaults.training_samples)
    train_p.add_argument("--model", choices=_MODEL_CHOICES, default=PipelineDefaults.model_type)
    train_p.add_argument("--seed", type=int, default=PipelineDefaults.random_seed)
    train_p.add_argument("--output", type=Path, default=Path("models/bio_age_model.joblib"))

    predict_p = subparsers.add_parser(
        "predict", help="Predict biological age for one feature vector using a saved model"
    )
    predict_p.add_argument("--model-path", type=Path, required=True)
    predict_p.add_argument("--chronological-age", type=float, required=True)
    predict_p.add_argument("--heart-rate", type=float, required=True)
    predict_p.add_argument("--hrv", type=float, required=True)
    predict_p.add_argument("--sleep-hours", type=float, required=True)
    predict_p.add_argument("--activity-level", type=float, required=True)
    predict_p.add_argument("--environmental-exposure", type=float, required=True)

    return parser


def _cmd_run(args: Namespace) -> int:
    config = PipelineDefaults(
        num_individuals=args.individuals,
        num_hr_samples_per_day=args.hr_samples_per_day,
        num_sleep_days=args.days,
        training_samples=args.training_samples,
        random_seed=args.seed,
        model_type=args.model,
        cv_folds=args.cv_folds,
    )
    result = run_pipeline(config=config, output_dir=args.output_dir)

    print("\n=== VitaGraph Pipeline Summary ===")
    print(result.individuals.to_string(index=False))
    print(f"\nCross-validation ({config.cv_folds}-fold): {result.cv_scores}")
    print(f"Held-out test metrics: {result.test_metrics.as_dict()}")
    print(f"\nKnowledge graph: {result.knowledge_graph.get_graph_info()}")
    if args.output_dir:
        print(f"\nArtifacts written under: {args.output_dir}")
    print(f"\n{_DISCLAIMER}")
    return 0


def _cmd_train(args: Namespace) -> int:
    generator = SyntheticCohortGenerator(seed=args.seed)
    cohort = generator.generate(num_samples=args.samples)

    X, y = cohort[FEATURE_COLUMNS], cohort[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=args.seed)

    estimator = BioAgeEstimator(model_type=args.model)
    estimator.train(X_train, y_train)
    metrics = estimator.evaluate(X_test, y_test)
    estimator.save_model(args.output)

    print(f"Trained {args.model} on {args.samples} synthetic samples.")
    print(f"Held-out test metrics: {metrics.as_dict()}")
    print(f"Model saved to: {args.output}")
    print(f"\n{_DISCLAIMER}")
    return 0


def _cmd_predict(args: Namespace) -> int:
    estimator = BioAgeEstimator()
    estimator.load_model(args.model_path)

    row = pd.DataFrame(
        [
            {
                "chronological_age": args.chronological_age,
                "heart_rate_avg": args.heart_rate,
                "hrv_avg": args.hrv,
                "sleep_hours_avg": args.sleep_hours,
                "activity_level": args.activity_level,
                "environmental_exposure": args.environmental_exposure,
            }
        ]
    )
    predicted = estimator.predict(row)[0]
    print(f"Predicted (synthetic-model) biological age: {predicted:.2f}")
    print(_DISCLAIMER)
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code (0 = success)."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    handlers = {"run": _cmd_run, "train": _cmd_train, "predict": _cmd_predict}
    try:
        return handlers[args.command](args)
    except Exception as exc:  # noqa: BLE001 - top-level CLI error boundary
        logger.error("vitagraph %s failed: %s", args.command, exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
