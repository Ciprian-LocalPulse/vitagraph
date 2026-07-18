"""Tests for vitagraph.pipeline."""

from __future__ import annotations

from pathlib import Path

from vitagraph.config import PipelineDefaults
from vitagraph.pipeline import run_pipeline


def test_run_pipeline_returns_result() -> None:
    config = PipelineDefaults(
        num_individuals=2,
        num_sleep_days=5,
        num_hr_samples_per_day=5,
        training_samples=50,
    )
    result = run_pipeline(config=config)

    assert len(result.individuals) == 2
    assert "predicted_biological_age" in result.individuals.columns
    assert result.knowledge_graph.graph.number_of_nodes() > 0
    assert result.test_metrics.r2 >= -1


def test_run_pipeline_writes_artifacts(tmp_path: Path) -> None:
    config = PipelineDefaults(
        num_individuals=2,
        num_sleep_days=3,
        training_samples=30,
    )
    run_pipeline(config=config, output_dir=tmp_path)

    assert (tmp_path / "models" / "bio_age_model.joblib").exists()
    assert (tmp_path / "models" / "bio_age_model.json").exists()
    assert (tmp_path / "knowledge_graph.json").exists()
    assert (tmp_path / "knowledge_graph.graphml").exists()
    assert (tmp_path / "individuals_summary.csv").exists()


def test_run_pipeline_individuals_have_interventions() -> None:
    config = PipelineDefaults(
        num_individuals=1,
        num_sleep_days=2,
        training_samples=20,
    )
    result = run_pipeline(config=config)

    person_id = result.individuals.iloc[0]["person_id"]
    subgraph = result.knowledge_graph.get_subgraph_for_person(person_id)

    intervention_nodes = [
        n for n, d in subgraph.nodes(data=True) if d.get("type") == "Intervention"
    ]
    assert len(intervention_nodes) >= 1


def test_run_pipeline_cv_scores_in_result() -> None:
    config = PipelineDefaults(
        num_individuals=2,
        training_samples=40,
        cv_folds=3,
    )
    result = run_pipeline(config=config)

    assert "mae_mean" in result.cv_scores
    assert "r2_mean" in result.cv_scores
    assert result.cv_scores["cv_folds"] == 3
