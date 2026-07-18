"""Tests for vitagraph.bio_signal_processor."""

from __future__ import annotations

from datetime import datetime

import pytest

from vitagraph.bio_signal_processor import BioSignalProcessor


def test_heart_rate_shape_and_columns(processor: BioSignalProcessor, start_time: datetime) -> None:
    df = processor.generate_synthetic_heart_rate(50, start_time)
    assert len(df) == 50
    assert list(df.columns) == ["timestamp", "heart_rate"]


def test_heart_rate_within_baseline_bounds(
    processor: BioSignalProcessor, start_time: datetime, baseline
) -> None:
    df = processor.generate_synthetic_heart_rate(200, start_time)
    assert (df["heart_rate"] >= baseline.heart_rate_min).all()
    assert (df["heart_rate"] <= baseline.heart_rate_max).all()


def test_heart_rate_raises_on_non_positive_samples(
    processor: BioSignalProcessor, start_time: datetime
) -> None:
    with pytest.raises(ValueError):
        processor.generate_synthetic_heart_rate(0, start_time)


def test_hrv_shape_and_bounds(
    processor: BioSignalProcessor, start_time: datetime, baseline
) -> None:
    df = processor.generate_synthetic_hrv(50, start_time)
    assert len(df) == 50
    assert (df["hrv_ms"] >= baseline.hrv_min_ms).all()
    assert (df["hrv_ms"] <= baseline.hrv_max_ms).all()


def test_sleep_shape_and_bounds(
    processor: BioSignalProcessor, start_time: datetime, baseline
) -> None:
    df = processor.generate_synthetic_sleep_data(14, start_time.date())
    assert len(df) == 14
    assert (df["sleep_hours"] >= baseline.sleep_hours_min).all()
    assert (df["sleep_hours"] <= baseline.sleep_hours_max).all()


def test_sleep_raises_on_non_positive_days(
    processor: BioSignalProcessor, start_time: datetime
) -> None:
    with pytest.raises(ValueError):
        processor.generate_synthetic_sleep_data(0, start_time.date())


def test_environmental_exposure_shape_and_bounds(
    processor: BioSignalProcessor, start_time: datetime, baseline
) -> None:
    df = processor.generate_synthetic_environmental_exposure(10, start_time.date())
    assert len(df) == 10
    assert (df["environmental_exposure"] >= baseline.environmental_exposure_min).all()
    assert (df["environmental_exposure"] <= baseline.environmental_exposure_max).all()


def test_process_biometric_data_adds_smoothed_column(
    processor: BioSignalProcessor, start_time: datetime
) -> None:
    raw = processor.generate_synthetic_heart_rate(30, start_time)
    processed = processor.process_biometric_data(raw, "heart_rate", window=5)
    assert "heart_rate_smoothed" in processed.columns
    assert len(processed) == len(raw)


def test_process_biometric_data_raises_on_missing_column(
    processor: BioSignalProcessor, start_time: datetime
) -> None:
    raw = processor.generate_synthetic_heart_rate(10, start_time)
    with pytest.raises(ValueError):
        processor.process_biometric_data(raw, "does_not_exist")


def test_process_biometric_data_clips_extreme_outlier(
    processor: BioSignalProcessor, start_time: datetime
) -> None:
    raw = processor.generate_synthetic_heart_rate(30, start_time)
    raw.loc[0, "heart_rate"] = 10_000  # inject an extreme outlier
    processed = processor.process_biometric_data(raw, "heart_rate")
    assert processed["heart_rate"].max() < 10_000


def test_process_biometric_data_does_not_mutate_input(
    processor: BioSignalProcessor, start_time: datetime
) -> None:
    raw = processor.generate_synthetic_heart_rate(20, start_time)
    raw_copy = raw.copy()
    processor.process_biometric_data(raw, "heart_rate")
    assert raw.equals(raw_copy)
