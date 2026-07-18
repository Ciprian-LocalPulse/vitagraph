"""Biological-age regression models trained on synthetic cohort data.

See docs/METHODOLOGY.md for an explicit statement of what this module does
and does not do. In short: it fits a standard scikit-learn regressor to
predict the synthetic ``biological_age`` label produced by
``vitagraph.synthetic_data.SyntheticCohortGenerator``. It has not been
trained or validated on any real dataset, and its predictions are not a
medical or diagnostic output.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import RegressorMixin
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_validate as sk_cross_validate

from vitagraph.exceptions import (
    InvalidModelTypeError,
    MissingFeatureColumnsError,
    ModelNotTrainedError,
)
from vitagraph.logging_config import get_logger
from vitagraph.synthetic_data import FEATURE_COLUMNS

logger = get_logger(__name__)

_MODEL_REGISTRY: dict[str, type[RegressorMixin]] = {
    "linear": LinearRegression,
    "random_forest": RandomForestRegressor,
    "gradient_boosting": GradientBoostingRegressor,
}

_DEFAULT_MODEL_KWARGS: dict[str, dict[str, Any]] = {
    "linear": {},
    "random_forest": {"n_estimators": 200, "max_depth": 6, "random_state": 42},
    "gradient_boosting": {"n_estimators": 200, "max_depth": 3, "random_state": 42},
}


@dataclass
class EvaluationMetrics:
    """Regression metrics for a held-out evaluation split."""

    mae: float
    rmse: float
    r2: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


class BioAgeEstimator:
    """Trains, evaluates, and serves a biological-age regressor.

    Args:
        model_type: One of ``"linear"``, ``"random_forest"``,
            ``"gradient_boosting"``.
        model_kwargs: Optional overrides passed to the underlying
            scikit-learn estimator constructor.
        features: Feature columns to use. Defaults to
            ``vitagraph.synthetic_data.FEATURE_COLUMNS``.

    Raises:
        InvalidModelTypeError: If ``model_type`` is not recognized.
    """

    def __init__(
        self,
        model_type: str = "gradient_boosting",
        model_kwargs: dict[str, Any] | None = None,
        features: list[str] | None = None,
    ) -> None:
        if model_type not in _MODEL_REGISTRY:
            raise InvalidModelTypeError(
                f"Unknown model_type '{model_type}'. Valid options: {sorted(_MODEL_REGISTRY)}"
            )
        self.model_type = model_type
        self.features = features or list(FEATURE_COLUMNS)
        kwargs = {**_DEFAULT_MODEL_KWARGS.get(model_type, {}), **(model_kwargs or {})}
        self.model: RegressorMixin = _MODEL_REGISTRY[model_type](**kwargs)
        self._is_trained = False
        self._last_metrics: EvaluationMetrics | None = None

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _validate_columns(self, df: pd.DataFrame) -> None:
        missing = [c for c in self.features if c not in df.columns]
        if missing:
            raise MissingFeatureColumnsError(f"Missing required feature columns: {missing}")

    def _require_trained(self) -> None:
        if not self._is_trained:
            raise ModelNotTrainedError("Call .train(...) before using this method.")

    # ------------------------------------------------------------------ #
    # Training / inference
    # ------------------------------------------------------------------ #
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> "BioAgeEstimator":
        """Fits the model on training data. Returns self for chaining."""
        self._validate_columns(X_train)
        logger.info(
            "Training %s on %d samples (%d features)",
            self.model_type,
            len(X_train),
            len(self.features),
        )
        self.model.fit(X_train[self.features], y_train)
        self._is_trained = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts biological age for new data.

        Raises:
            ModelNotTrainedError: If called before ``train()``/``load_model()``.
            MissingFeatureColumnsError: If ``X`` is missing required feature columns.
        """
        self._require_trained()
        self._validate_columns(X)
        return self.model.predict(X[self.features])

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> EvaluationMetrics:
        """Evaluates the model on a held-out split and returns MAE / RMSE / R²."""
        predictions = self.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        r2 = r2_score(y_test, predictions)
        metrics = EvaluationMetrics(mae=round(float(mae), 4), rmse=round(float(rmse), 4), r2=round(float(r2), 4))
        self._last_metrics = metrics
        logger.info("Evaluation — MAE: %.2f  RMSE: %.2f  R²: %.3f", metrics.mae, metrics.rmse, metrics.r2)
        return metrics

    def cross_validate(self, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> dict[str, float]:
        """Runs k-fold cross-validation and returns mean MAE / R² across folds.

        This gives a less optimistic, less split-dependent estimate of
        generalization error than a single train/test split.
        """
        self._validate_columns(X)
        scores = sk_cross_validate(
            self.model,
            X[self.features],
            y,
            cv=cv,
            scoring=("neg_mean_absolute_error", "r2"),
        )
        result = {
            "cv_folds": cv,
            "mae_mean": round(float(-scores["test_neg_mean_absolute_error"].mean()), 4),
            "mae_std": round(float(scores["test_neg_mean_absolute_error"].std()), 4),
            "r2_mean": round(float(scores["test_r2"].mean()), 4),
            "r2_std": round(float(scores["test_r2"].std()), 4),
        }
        logger.info(
            "%d-fold CV — MAE: %.2f ± %.2f  R²: %.3f ± %.3f",
            cv,
            result["mae_mean"],
            result["mae_std"],
            result["r2_mean"],
            result["r2_std"],
        )
        return result

    def feature_importance(self) -> dict[str, float]:
        """Returns a feature-name -> importance mapping.

        Uses ``feature_importances_`` for tree-based models and normalized
        absolute coefficients for linear models.

        Raises:
            ModelNotTrainedError: If called before training.
        """
        self._require_trained()
        if hasattr(self.model, "feature_importances_"):
            raw = self.model.feature_importances_
        elif hasattr(self.model, "coef_"):
            coefs = np.abs(np.asarray(self.model.coef_))
            total = coefs.sum() or 1.0
            raw = coefs / total
        else:  # pragma: no cover - defensive fallback for future model types
            raise NotImplementedError(f"{self.model_type} does not expose feature importances")

        return dict(sorted(zip(self.features, (float(v) for v in raw)), key=lambda kv: -kv[1]))

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def save_model(self, path: str | Path) -> Path:
        """Saves the trained model plus a JSON metadata sidecar (same stem, ``.json``).

        The metadata captures model type, feature list, and the most recent
        evaluation metrics (if ``evaluate()`` was called), which matters for
        reproducibility once more than one model version exists.
        """
        self._require_trained()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

        metadata = {
            "model_type": self.model_type,
            "features": self.features,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "metrics": self._last_metrics.as_dict() if self._last_metrics else None,
        }
        metadata_path = path.with_suffix(".json")
        with metadata_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info("Saved model to %s (+ metadata at %s)", path, metadata_path)
        return path

    def load_model(self, path: str | Path) -> "BioAgeEstimator":
        """Loads a trained model from disk. Also loads the metadata sidecar if present."""
        path = Path(path)
        self.model = joblib.load(path)
        self._is_trained = True

        metadata_path = path.with_suffix(".json")
        if metadata_path.exists():
            with metadata_path.open(encoding="utf-8") as f:
                metadata = json.load(f)
            self.features = metadata.get("features", self.features)
            self.model_type = metadata.get("model_type", self.model_type)

        logger.info("Loaded model from %s", path)
        return self
