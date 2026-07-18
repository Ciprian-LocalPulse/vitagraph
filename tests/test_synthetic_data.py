"""Tests for vitagraph.synthetic_data."""

from __future__ import annotations

import pytest

from vitagraph.synthetic_data import FEATURE_COLUMNS, TARGET_COLUMN, SyntheticCohortGenerator


def test_generate_returns_expected_columns(cohort_generator: SyntheticCohortGenerator) -> None:
    df = cohort_generator.generate(num_samples=10)
    assert set(df.columns) == set(FEATURE_COLUMNS) | {TARGET_COLUMN}


def test_generate_respects_num_samples(cohort_generator: SyntheticCohortGenerator) -> None:
    df = cohort_generator.generate(num_samples=37)
    assert len(df) == 37


@pytest.mark.parametrize("bad_value", [0, -1, -100])
def test_generate_raises_on_non_positive_samples(
    cohort_generator: SyntheticCohortGenerator, bad_value: int
) -> None:
    with pytest.raises(ValueError):
        cohort_generator.generate(num_samples=bad_value)


def test_biological_age_stays_within_clipped_bounds(cohort_generator: SyntheticCohortGenerator) -> None:
    df = cohort_generator.generate(num_samples=500)
    max_dev = cohort_generator.formula.max_deviation_years
    assert (df["biological_age"] >= df["chronological_age"] - max_dev).all()
    assert (df["biological_age"] <= df["chronological_age"] + max_dev).all()


def test_generate_is_reproducible_with_same_seed(baseline) -> None:
    gen_a = SyntheticCohortGenerator(baseline=baseline, seed=123)
    gen_b = SyntheticCohortGenerator(baseline=baseline, seed=123)
    df_a = gen_a.generate(num_samples=20)
    df_b = gen_b.generate(num_samples=20)
    assert df_a.equals(df_b)


def test_generate_differs_across_seeds(baseline) -> None:
    gen_a = SyntheticCohortGenerator(baseline=baseline, seed=1)
    gen_b = SyntheticCohortGenerator(baseline=baseline, seed=2)
    df_a = gen_a.generate(num_samples=20)
    df_b = gen_b.generate(num_samples=20)
    assert not df_a.equals(df_b)
