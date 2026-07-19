#!/usr/bin/env python3
"""Example: train, cross-validate, and compare BioAgeEstimator backends.

Usage:
    python examples/train_model.py --samples 1500 --seed 42 \
        --output models/bio_age_demo.joblib

This trains all three available model backends (linear, random_forest,
gradient_boosting) on the same synthetic split, prints a comparison
table of cross-validated MAE / R^2, and saves the best-performing model
to disk (with its JSON metadata sidecar).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sklearn.model_selection import train_test_split

from vitagraph import BioAgeEstimator, SyntheticCohortGenerator
from vitagraph.synthetic_data import FEATURE_COLUMNS, TARGET_COLUMN

MODEL_TYPES = ["linear", "random_forest", "gradient_boosting"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--output", type=Path, default=Path("models/bio_age_demo.joblib"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    cohort = SyntheticCohortGenerator(seed=args.seed).generate(num_samples=args.samples)
    X, y = cohort[FEATURE_COLUMNS], cohort[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed
    )

    results = {}
    trained_estimators = {}
    for model_type in MODEL_TYPES:
        estimator = BioAgeEstimator(model_type=model_type)
        cv_scores = estimator.cross_validate(X_train, y_train, cv=args.cv_folds)
        estimator.train(X_train, y_train)
        test_metrics = estimator.evaluate(X_test, y_test)
        results[model_type] = {"cv": cv_scores, "test": test_metrics.as_dict()}
        trained_estimators[model_type] = estimator

    print("\nModel comparison (cross-validated on training split):")
    print(f"{'model':<20}{'CV MAE':>12}{'CV R2':>12}{'Test MAE':>12}{'Test R2':>12}")
    for model_type, r in results.items():
        print(
            f"{model_type:<20}{r['cv']['mae_mean']:>12.3f}{r['cv']['r2_mean']:>12.3f}"
            f"{r['test']['mae']:>12.3f}{r['test']['r2']:>12.3f}"
        )

    best_model_type = min(results, key=lambda m: results[m]["test"]["mae"])
    print(f"\nBest model by held-out MAE: {best_model_type}")

    best_estimator = trained_estimators[best_model_type]
    saved_path = best_estimator.save_model(args.output)
    print(f"Saved best model -> {saved_path} (+ {saved_path.with_suffix('.json')})")

    print("\nFeature importance (best model):")
    for feature, importance in best_estimator.feature_importance().items():
        print(f"  {feature:<24} {importance:.4f}")


if __name__ == "__main__":
    main()
