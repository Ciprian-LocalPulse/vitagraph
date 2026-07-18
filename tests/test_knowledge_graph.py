"""Tests for vitagraph.knowledge_graph."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import networkx as nx
import pytest

from vitagraph.exceptions import GraphNodeNotFoundError
from vitagraph.knowledge_graph import KnowledgeGraph


def test_add_person_node_is_idempotent(empty_graph: KnowledgeGraph) -> None:
    empty_graph.add_person_node("P001")
    empty_graph.add_person_node("P001")  # should not duplicate
    assert empty_graph.graph.number_of_nodes() == 1
    assert empty_graph.graph.nodes["P001"]["type"] == "Person"


def test_add_biometric_data_node_links_edge(
    empty_graph: KnowledgeGraph, start_time: datetime
) -> None:
    empty_graph.add_person_node("P001")
    empty_graph.add_biometric_data_node("HR_1", "P001", "HeartRate", 72, start_time)
    assert empty_graph.graph.number_of_edges() == 1
    assert empty_graph.graph.edges["P001", "HR_1"]["relation"] == "HAS_DATA"


def test_build_from_processed_data_counts(
    empty_graph: KnowledgeGraph, processor, start_time: datetime
) -> None:
    hr = processor.generate_synthetic_heart_rate(5, start_time)
    hrv = processor.generate_synthetic_hrv(5, start_time)
    sleep = processor.generate_synthetic_sleep_data(2, start_time.date())

    empty_graph.build_from_processed_data("P001", hr, sleep, hrv)
    info = empty_graph.get_graph_info()

    # 1 Person + 5 HR + 5 HRV + 2 Sleep = 13 nodes
    assert info["nodes"] == 13
    assert info["node_type_counts"]["BiometricData"] == 12
    assert info["node_type_counts"]["Person"] == 1


def test_get_graph_info_edge_relations(empty_graph: KnowledgeGraph, start_time: datetime) -> None:
    empty_graph.add_person_node("P001")
    empty_graph.add_environmental_factor_node("Env_1", "AirQuality", 0.4, start_time)
    empty_graph.link_person_to_environmental_factor("P001", "Env_1", "EXPOSED_TO")
    info = empty_graph.get_graph_info()
    assert "EXPOSED_TO" in info["edge_relations"]


def test_add_intervention_node(empty_graph: KnowledgeGraph, start_time: datetime) -> None:
    empty_graph.add_person_node("P001")
    empty_graph.add_intervention_node(
        "Intervention_P001", "P001", "sleep", "low sleep z-score", start_time
    )
    assert empty_graph.graph.nodes["Intervention_P001"]["type"] == "Intervention"
    assert empty_graph.graph.edges["P001", "Intervention_P001"]["relation"] == "HAS_RECOMMENDATION"


def test_get_subgraph_for_person(empty_graph: KnowledgeGraph, start_time: datetime) -> None:
    empty_graph.add_person_node("P001")
    empty_graph.add_biometric_data_node("HR_1", "P001", "HeartRate", 72, start_time)
    empty_graph.add_person_node("P002")  # unrelated node
    sub = empty_graph.get_subgraph_for_person("P001")
    assert set(sub.nodes()) == {"P001", "HR_1"}


def test_get_subgraph_raises_for_unknown_person(empty_graph: KnowledgeGraph) -> None:
    with pytest.raises(GraphNodeNotFoundError):
        empty_graph.get_subgraph_for_person("does-not-exist")


def test_export_to_json_round_trip(
    empty_graph: KnowledgeGraph, start_time: datetime, tmp_path: Path
) -> None:
    empty_graph.add_person_node("P001")
    empty_graph.add_biometric_data_node("HR_1", "P001", "HeartRate", 72, start_time)

    out_path = empty_graph.export_to_json(tmp_path / "graph.json")
    assert out_path.exists()

    with out_path.open() as f:
        data = json.load(f)
    assert "nodes" in data
    assert len(data["nodes"]) == 2


def test_export_to_graphml_is_readable(
    empty_graph: KnowledgeGraph, start_time: datetime, tmp_path: Path
) -> None:
    empty_graph.add_person_node("P001")
    empty_graph.add_biometric_data_node("HR_1", "P001", "HeartRate", 72, start_time)

    out_path = empty_graph.export_to_graphml(tmp_path / "graph.graphml")
    assert out_path.exists()

    reloaded = nx.read_graphml(out_path)
    assert reloaded.number_of_nodes() == 2
