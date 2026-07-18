"""Central configuration objects for VitaGraph.

Tunable constants live here as dataclasses instead of being scattered as
magic numbers through the codebase. This makes every assumption behind the
synthetic-data generators explicit, overridable in tests/notebooks, and easy
to audit.

None of the values below are derived from a clinical dataset. They are
illustrative population-level placeholders chosen to make demo output look
plausible (e.g. a resting heart rate centered around 70 bpm). They must not
be treated as medical reference ranges.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SignalBaseline:
    """Baseline mean/std/min/max used by every synthetic-signal generator."""

    heart_rate_mean: float = 70.0
    heart_rate_std: float = 8.0
    heart_rate_min: float = 40.0
    heart_rate_max: float = 180.0

    hrv_mean_ms: float = 55.0
    hrv_std_ms: float = 12.0
    hrv_min_ms: float = 10.0
    hrv_max_ms: float = 120.0

    sleep_hours_mean: float = 7.5
    sleep_hours_std: float = 1.0
    sleep_hours_min: float = 3.0
    sleep_hours_max: float = 11.0

    activity_level_mean: float = 0.6
    activity_level_std: float = 0.2
    activity_level_min: float = 0.0
    activity_level_max: float = 1.0

    environmental_exposure_mean: float = 0.4
    environmental_exposure_std: float = 0.2
    environmental_exposure_min: float = 0.0
    environmental_exposure_max: float = 1.0


@dataclass(frozen=True)
class BioAgeFormulaWeights:
    """Coefficients for the synthetic ground-truth "biological age" label.

    biological_age = chronological_age
        + hr_weight            * (heart_rate_avg - baseline.heart_rate_mean)
        + sleep_weight         * (baseline.sleep_hours_mean - sleep_hours_avg)
        + activity_weight      * (baseline.activity_level_mean - activity_level)
        + hrv_weight           * (baseline.hrv_mean_ms - hrv_avg)
        + environmental_weight * environmental_exposure
        + noise

    This is a fully deterministic, documented simulation used to produce a
    learnable synthetic label for the demo/training pipeline. It is a
    modeling convenience for generating realistic-shaped correlated data —
    not a biological or clinical claim about what drives aging.
    """

    hr_weight: float = 0.30
    sleep_weight: float = 1.50
    activity_weight: float = 5.00
    hrv_weight: float = 0.10
    environmental_weight: float = 4.00
    noise_std: float = 2.0
    max_deviation_years: float = 12.0


@dataclass(frozen=True)
class PipelineDefaults:
    """Default parameters for a full pipeline run (see vitagraph.pipeline)."""

    num_individuals: int = 5
    num_hr_samples_per_day: int = 10
    num_sleep_days: int = 30
    training_samples: int = 500
    random_seed: int = 42
    model_type: str = "gradient_boosting"
    cv_folds: int = 5
