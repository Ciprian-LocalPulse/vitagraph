"""Synthetic biometric time-series simulation and lightweight signal processing.

Every generator method here produces synthetic data from a seeded
``numpy.random.Generator``. Nothing in this module reads from, or connects
to, a real wearable device, EHR system, or lab result.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from vitagraph.config import SignalBaseline
from vitagraph.logging_config import get_logger

logger = get_logger(__name__)


class BioSignalProcessor:
    """Simulates and lightly processes raw biometric time-series data."""

    def __init__(self, seed: int = 42, baseline: SignalBaseline | None = None) -> None:
        self.rng = np.random.default_rng(seed)
        self.baseline = baseline or SignalBaseline()

    def generate_synthetic_heart_rate(
        self,
        num_samples: int,
        start_time: datetime,
        interval_minutes: int = 1,
    ) -> pd.DataFrame:
        """Generates a synthetic heart-rate time series with a mild circadian pattern.

        Args:
            num_samples: Number of readings to generate.
            start_time: Timestamp of the first reading.
            interval_minutes: Spacing between consecutive readings.

        Returns:
            DataFrame with columns ``timestamp`` and ``heart_rate`` (bpm).
        """
        if num_samples <= 0:
            raise ValueError("num_samples must be positive")

        b = self.baseline
        timestamps = [
            start_time + timedelta(minutes=i * interval_minutes) for i in range(num_samples)
        ]

        # Mild circadian modulation so a full-day series doesn't look flat:
        # lower heart rate overnight, a touch higher through the day.
        hours = np.array([t.hour + t.minute / 60 for t in timestamps])
        circadian = 4.0 * np.sin((hours - 6.0) / 24.0 * 2 * np.pi)

        heart_rates = self.rng.normal(b.heart_rate_mean, b.heart_rate_std, num_samples) + circadian
        heart_rates = np.clip(heart_rates, b.heart_rate_min, b.heart_rate_max).astype(int)

        return pd.DataFrame({"timestamp": timestamps, "heart_rate": heart_rates})

    def generate_synthetic_hrv(
        self,
        num_samples: int,
        start_time: datetime,
        interval_minutes: int = 1,
    ) -> pd.DataFrame:
        """Generates synthetic heart-rate-variability readings (RMSSD-style, ms).

        Args:
            num_samples: Number of readings to generate.
            start_time: Timestamp of the first reading.
            interval_minutes: Spacing between consecutive readings.

        Returns:
            DataFrame with columns ``timestamp`` and ``hrv_ms``.
        """
        if num_samples <= 0:
            raise ValueError("num_samples must be positive")

        b = self.baseline
        timestamps = [
            start_time + timedelta(minutes=i * interval_minutes) for i in range(num_samples)
        ]
        hrv = self.rng.normal(b.hrv_mean_ms, b.hrv_std_ms, num_samples)
        hrv = np.clip(hrv, b.hrv_min_ms, b.hrv_max_ms)
        return pd.DataFrame({"timestamp": timestamps, "hrv_ms": hrv})

    def generate_synthetic_sleep_data(
        self,
        num_days: int,
        start_date: date,
    ) -> pd.DataFrame:
        """Generates synthetic nightly sleep-duration data.

        Args:
            num_days: Number of nights to generate.
            start_date: Date of the first night.

        Returns:
            DataFrame with columns ``date`` and ``sleep_hours``.
        """
        if num_days <= 0:
            raise ValueError("num_days must be positive")

        b = self.baseline
        dates = [start_date + timedelta(days=i) for i in range(num_days)]
        sleep_hours = self.rng.normal(b.sleep_hours_mean, b.sleep_hours_std, num_days)
        sleep_hours = np.clip(sleep_hours, b.sleep_hours_min, b.sleep_hours_max)
        return pd.DataFrame({"date": dates, "sleep_hours": sleep_hours})

    def generate_synthetic_environmental_exposure(
        self,
        num_days: int,
        start_date: date,
    ) -> pd.DataFrame:
        """Generates a synthetic daily environmental exposure index in [0, 1].

        Higher values represent a heavier simulated exposure load (e.g. air
        quality, noise); this is a coarse illustrative proxy, not a reading
        from any real sensor network.

        Args:
            num_days: Number of days to generate.
            start_date: Date of the first day.

        Returns:
            DataFrame with columns ``date`` and ``environmental_exposure``.
        """
        if num_days <= 0:
            raise ValueError("num_days must be positive")

        b = self.baseline
        dates = [start_date + timedelta(days=i) for i in range(num_days)]
        exposure = self.rng.normal(
            b.environmental_exposure_mean, b.environmental_exposure_std, num_days
        )
        exposure = np.clip(exposure, b.environmental_exposure_min, b.environmental_exposure_max)
        return pd.DataFrame({"date": dates, "environmental_exposure": exposure})

    def process_biometric_data(
        self,
        df: pd.DataFrame,
        value_column: str,
        window: int = 5,
        outlier_z_threshold: float = 3.0,
    ) -> pd.DataFrame:
        """Smooths a signal column and clips statistical outliers.

        Two real (if intentionally simple) processing steps are applied:

        1. A centered rolling-mean smoothing pass over ``value_column``,
           written to a new ``{value_column}_smoothed`` column.
        2. Z-score-based outlier clipping: points more than
           ``outlier_z_threshold`` standard deviations from the column mean
           are clipped back to that boundary, reducing the influence of
           sensor-noise spikes on downstream aggregation.

        Args:
            df: Input DataFrame containing ``value_column``.
            value_column: Name of the numeric column to process.
            window: Rolling window size (in samples) for smoothing.
            outlier_z_threshold: Number of standard deviations beyond which
                a point is considered an outlier and clipped.

        Returns:
            A copy of ``df`` with an added ``{value_column}_smoothed`` column
            and outliers in ``value_column`` clipped in place.
        """
        if value_column not in df.columns:
            raise ValueError(f"'{value_column}' not found in DataFrame columns: {list(df.columns)}")

        logger.info("Processing '%s' (%d rows, window=%d)", value_column, len(df), window)
        processed = df.copy()

        std = processed[value_column].std(ddof=0)
        mean = processed[value_column].mean()
        if std and std > 0:
            z_scores = (processed[value_column] - mean) / std
            lower, upper = mean - outlier_z_threshold * std, mean + outlier_z_threshold * std
            processed[value_column] = processed[value_column].where(
                z_scores.abs() <= outlier_z_threshold, processed[value_column].clip(lower, upper)
            )

        processed[f"{value_column}_smoothed"] = (
            processed[value_column].rolling(window=window, min_periods=1, center=True).mean()
        )
        return processed
