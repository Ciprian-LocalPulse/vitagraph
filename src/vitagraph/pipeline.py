"""End-to-end VitaGraph pipeline: signal simulation -> knowledge graph -> bio-age estimation.

This module replaces the previous duplicated ``main.py`` (which existed
both at the repository root and under ``src/``) with a single, testable
``run_pipeline`` function that returns a structured result instead of only
printing to stdout.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from vitagraph.bio_age_estimator import BioAgeEstimator, EvaluationMetrics
from vitagraph.bio_signal_processor import BioSignalProcessor
from vitagraph.config import PipelineDefaults, SignalBaseline
from vitagraph.knowledge_graph import KnowledgeGraph
from vitagraph.logging_config import get_logger
from vitagraph.synthetic_data import FEATURE_COLUMNS, TARGET_COLUMN, SyntheticCohortGenerator

logger = get_logger(__name__)

# Human-readable focus-area labels for each feature, used by recommend_focus_area.
_FOCUS_AREA_LABELS = {
    "heart_rate_avg": "cardiovascular load",
    "hrv_avg": "recovery / stress balance",
    "sleep_hours_avg": "sleep",
    "activity_level": "physical activity",
    "environmental_exposure": "environmental exposure",
}


def recommend_focus_area(row: pd.Series, baseline: SignalBaseline) -> tuple[str, str]:
    """Rule-based heuristic: picks the feature with the largest unfavorable deviation from baseline.

    This is a simple, fully transparent heuristic (standardized distance
    from the population baseline for each feature) — it is NOT the output
    of a causal-inference model. Real causal inference is tracked as a
    future goal in docs/ROADMAP.md, not implemented here.

    Returns:
        (focus_area_label, rationale) tuple.
    """
    deviations = {
        "heart_rate_avg": (row["heart_rate_avg"] - baseline.heart_rate_mean)
        / baseline.heart_rate_std,
        "hrv_avg": (baseline.hrv_mean_ms - row["hrv_avg"]) / baseline.hrv_std_ms,
        "sleep_hours_avg": (baseline.sleep_hours_mean - row["sleep_hours_avg"])
        / baseline.sleep_hours_std,
        "activity_level": (baseline.activity_level_mean - row["activity_level"])
        / baseline.activity_level_std,
        "environmental_exposure": (
            (row["environmental_exposure"] - baseline.environmental_exposure_mean)
            / baseline.environmental_exposure_std
        ),
    }
    worst_feature = max(deviations, key=lambda k: deviations[k])
    label = _FOCUS_AREA_LABELS[worst_feature]
    rationale = (
        f"Largest unfavorable standardized deviation from baseline: "
        f"{worst_feature} (z={deviations[worst_feature]:.2f})"
    )
    return label, rationale


@dataclass
class PipelineResult:
    """Structured output of a full pipeline run."""

    individuals: pd.DataFrame
    cv_scores: dict[str, float]
    test_metrics: EvaluationMetrics
    knowledge_graph: KnowledgeGraph
    model_path: Path | None = None


def run_pipeline(
    config: PipelineDefaults | None = None,
    output_dir: str | Path | None = None,
) -> PipelineResult:
    """Runs the full VitaGraph demo pipeline end-to-end.

    Steps:
        1. Simulate per-person raw biometric time series (heart rate, HRV, sleep).
        2. Lightly process (smooth + de-outlier) those series.
        3. Build a knowledge graph from the processed data plus a synthetic
           environmental-exposure reading per person.
        4. Train a BioAgeEstimator on a larger synthetic cohort.
        5. Cross-validate and evaluate the model on a held-out split.
        6. Predict biological age for each simulated individual and attach a
           rule-based Intervention suggestion to their graph node.
        7. If ``output_dir`` is given, persist the model (+ metadata), the
           knowledge-graph export (JSON + GraphML), and a summary CSV there.

    Args:
        config: Pipeline parameters. Defaults to ``PipelineDefaults()``.
        output_dir: Optional directory to write model/graph/CSV artifacts to.

    Returns:
        A PipelineResult with per-individual predictions, cross-validation
        scores, held-out evaluation metrics, and the constructed graph.
    """
    cfg = config or PipelineDefaults()
    baseline = SignalBaseline()
    output_path = Path(output_dir) if output_dir else None

    logger.info(
        "Starting VitaGraph pipeline (model=%s, individuals=%d, seed=%d)",
        cfg.model_type,
        cfg.num_individuals,
        cfg.random_seed,
    )

    processor = BioSignalProcessor(seed=cfg.random_seed, baseline=baseline)
    kg = KnowledgeGraph()
    rng = np.random.default_rng(cfg.random_seed)

    records: list[dict[str, Any]] = []
    for i in range(cfg.num_individuals):
        person_id = f"P{i + 1:03d}"
        start_time = datetime(2026, 1, 1, 8, 0, 0)
        num_hr = cfg.num_hr_samples_per_day * cfg.num_sleep_days

        hr_raw = processor.generate_synthetic_heart_rate(num_hr, start_time)
        hrv_raw = processor.generate_synthetic_hrv(num_hr, start_time)
        sleep_raw = processor.generate_synthetic_sleep_data(cfg.num_sleep_days, start_time.date())
        env_raw = processor.generate_synthetic_environmental_exposure(
            cfg.num_sleep_days, start_time.date()
        )

        hr_processed = processor.process_biometric_data(hr_raw, "heart_rate")
        hrv_processed = processor.process_biometric_data(hrv_raw, "hrv_ms")
        sleep_processed = processor.process_biometric_data(sleep_raw, "sleep_hours")

        kg.build_from_processed_data(person_id, hr_processed, sleep_processed, hrv_processed)

        env_value = float(env_raw["environmental_exposure"].mean())
        env_id = f"Env_{person_id}"
        kg.add_environmental_factor_node(
            env_id, "EnvironmentalExposureIndex", env_value, start_time
        )
        kg.link_person_to_environmental_factor(person_id, env_id, "EXPOSED_TO")

        activity_level = float(
            np.clip(rng.normal(baseline.activity_level_mean, baseline.activity_level_std), 0.0, 1.0)
        )
        chronological_age = int(rng.integers(25, 65))

        records.append(
            {
                "person_id": person_id,
                "chronological_age": chronological_age,
                "heart_rate_avg": float(hr_processed["heart_rate"].mean()),
                "hrv_avg": float(hrv_processed["hrv_ms"].mean()),
                "sleep_hours_avg": float(sleep_processed["sleep_hours"].mean()),
                "activity_level": activity_level,
                "environmental_exposure": env_value,
            }
        )
        logger.info(
            "Built knowledge graph for %s (%d total nodes so far)",
            person_id,
            kg.graph.number_of_nodes(),
        )

    individuals_df = pd.DataFrame.from_records(records)

    # --- Train + evaluate the estimator on a larger synthetic cohort --- #
    logger.info("Generating %d-sample synthetic training cohort", cfg.training_samples)
    cohort_gen = SyntheticCohortGenerator(baseline=baseline, seed=cfg.random_seed)
    cohort = cohort_gen.generate(num_samples=cfg.training_samples)

    X, y = cohort[FEATURE_COLUMNS], cohort[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=cfg.random_seed
    )

    estimator = BioAgeEstimator(model_type=cfg.model_type)
    cv_scores = estimator.cross_validate(X_train, y_train, cv=cfg.cv_folds)
    estimator.train(X_train, y_train)
    test_metrics = estimator.evaluate(X_test, y_test)

    # --- Predict for the simulated individuals + attach recommendations --- #
    predictions = estimator.predict(individuals_df[FEATURE_COLUMNS])
    individuals_df["predicted_biological_age"] = np.round(predictions, 2)
    individuals_df["age_gap"] = np.round(
        individuals_df["predicted_biological_age"] - individuals_df["chronological_age"], 2
    )

    for _, row in individuals_df.iterrows():
        focus_area, rationale = recommend_focus_area(row, baseline)
        intervention_id = f"Intervention_{row['person_id']}"
        kg.add_intervention_node(
            intervention_id, row["person_id"], focus_area, rationale, datetime.now()
        )

    model_path: Path | None = None
    if output_path is not None:
        output_path.mkdir(parents=True, exist_ok=True)
        model_path = estimator.save_model(output_path / "models" / "bio_age_model.joblib")
        kg.export_to_json(output_path / "knowledge_graph.json")
        kg.export_to_graphml(output_path / "knowledge_graph.graphml")
        individuals_df.to_csv(output_path / "individuals_summary.csv", index=False)
        logger.info("Pipeline outputs written to %s", output_path)

    logger.info("Pipeline complete.")
    return PipelineResult(
        individuals=individuals_df,
        cv_scores=cv_scores,
        test_metrics=test_metrics,
        knowledge_graph=kg,
        model_path=model_path,
    )
