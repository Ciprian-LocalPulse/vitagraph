"""Tests for vitagraph.bio_age_estimator."""

from __future__ import annotations

from pathlib import Path

import pytest

from vitagraph.bio_age_estimator import BioAgeEstimator
from vitagraph.exceptions import InvalidModelTypeError, MissingFeatureColumnsError, ModelNotTrainedError
from vitagraph.synthetic_data import FEATURE_COLUMNS


def test_invalid_model_type_raises(cohort_generator) -> None:
    with pytest.raises(InvalidModelTypeError):
        BioAgeEstimator(model_type="invalid_model")


def test_predict_before_train_raises(empty_graph, cohort_generator) -> None:
    estimator = BioAgeEstimator()
    df = cohort_generator.generate(10)
    with pytest.raises(ModelNotTrainedError):
        estimator.predict(df)


def test_train_and_predict(cohort_generator) -> None:
    df = cohort_generator.generate(100)
    X, y = df[FEATURE_COLUMNS], df["biological_age"]

    estimator = BioAgeEstimator()
    estimator.train(X, y)
    preds = estimator.predict(X)
    assert len(preds) == len(X)


def test_missing_columns_raises(cohort_generator) -> None:
    df = cohort_generator.generate(10)
    X_bad = df[["chronological_age"]]  # missing features
    y = df["biological_age"]

    estimator = BioAgeEstimator()
    # Validarea coloanelor se face direct în timpul metodei de train()
    with pytest.raises(MissingFeatureColumnsError):
        estimator.train(X_bad, y)


def test_evaluate(cohort_generator) -> None:
    df = cohort_generator.generate(100)
    X, y = df[FEATURE_COLUMNS], df["biological_age"]

    estimator = BioAgeEstimator()
    estimator.train(X[:80], y[:80])
    metrics = estimator.evaluate(X[80:], y[80:])

    assert metrics.mae >= 0
    assert metrics.rmse >= 0
    assert -1 <= metrics.r2 <= 1


def test_cross_validate(cohort_generator) -> None:
    df = cohort_generator.generate(100)
    X, y = df[FEATURE_COLUMNS], df["biological_age"]

    estimator = BioAgeEstimator()
    scores = estimator.cross_validate(X, y, cv=3)

    assert "mae_mean" in scores
    assert "r2_mean" in scores
    assert scores["cv_folds"] == 3


def test_feature_importance(cohort_generator) -> None:
    df = cohort_generator.generate(100)
    X, y = df[FEATURE_COLUMNS], df["biological_age"]

    estimator = BioAgeEstimator(model_type="random_forest")
    estimator.train(X, y)
    importance = estimator.feature_importance()

    assert len(importance) == len(FEATURE_COLUMNS)
    assert all(imp >= 0 for imp in importance.values())


def test_save_and_load_model(cohort_generator, tmp_path: Path) -> None:
    df = cohort_generator.generate(50)
    X, y = df[FEATURE_COLUMNS], df["biological_age"]

    estimator1 = BioAgeEstimator()
    estimator1.train(X, y)
    model_path = tmp_path / "model.joblib"
    estimator1.save_model(model_path)

    estimator2 = BioAgeEstimator()
    estimator2.load_model(model_path)

    preds1 = estimator1.predict(X)
    preds2 = estimator2.predict(X)
    assert (preds1 == preds2).all()


def test_model_metadata_sidecar(cohort_generator, tmp_path: Path) -> None:
    df = cohort_generator.generate(50)
    X, y = df[FEATURE_COLUMNS], df["biological_age"]

    estimator = BioAgeEstimator(model_type="linear")
    estimator.train(X, y)
    estimator.evaluate(X, y)
    model_path = tmp_path / "model.joblib"
    estimator.save_model(model_path)

    metadata_path = model_path.with_suffix(".json")
    assert metadata_path.exists()


def test_different_model_types(cohort_generator) -> None:
    df = cohort_generator.generate(50)
    X, y = df[FEATURE_COLUMNS], df["biological_age"]

    for model_type in ["linear", "random_forest", "gradient_boosting"]:
        estimator = BioAgeEstimator(model_type=model_type)
        estimator.train(X, y)
        preds = estimator.predict(X)
        assert len(preds) == len(X)