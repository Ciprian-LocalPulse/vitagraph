"""Construction, querying, and export of the VitaGraph knowledge graph.

The graph is a ``networkx.DiGraph`` with a small, explicit set of node
types (``Person``, ``BiometricData``, ``EnvironmentalFactor``,
``Intervention``) and typed edges (``relation`` attribute). It is a
demonstration knowledge-graph layer over synthetic data — see
docs/METHODOLOGY.md for what is and is not implemented today.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd

from vitagraph.exceptions import GraphNodeNotFoundError
from vitagraph.logging_config import get_logger

logger = get_logger(__name__)


class KnowledgeGraph:
    """Constructs and manages the VitaGraph knowledge graph."""

    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()

    # ------------------------------------------------------------------ #
    # Node / edge construction
    # ------------------------------------------------------------------ #
    def add_person_node(self, person_id: str, attributes: dict[str, Any] | None = None) -> None:
        """Adds a Person node to the graph (no-op if it already exists)."""
        if not self.graph.has_node(person_id):
            self.graph.add_node(person_id, type="Person", **(attributes or {}))

    def add_biometric_data_node(
        self,
        data_id: str,
        person_id: str,
        data_type: str,
        value: Any,
        timestamp: datetime,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Adds a BiometricData node and links it to a person via HAS_DATA."""
        if not self.graph.has_node(data_id):
            self.graph.add_node(
                data_id,
                type="BiometricData",
                data_type=data_type,
                value=value,
                timestamp=timestamp.isoformat(),
                **(attributes or {}),
            )
            self.graph.add_edge(person_id, data_id, relation="HAS_DATA")

    def add_environmental_factor_node(
        self,
        factor_id: str,
        factor_type: str,
        value: Any,
        timestamp: datetime,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Adds an EnvironmentalFactor node."""
        if not self.graph.has_node(factor_id):
            self.graph.add_node(
                factor_id,
                type="EnvironmentalFactor",
                factor_type=factor_type,
                value=value,
                timestamp=timestamp.isoformat(),
                **(attributes or {}),
            )

    def link_person_to_environmental_factor(
        self,
        person_id: str,
        factor_id: str,
        relation_type: str = "EXPOSED_TO",
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Links a person to an environmental factor."""
        if self.graph.has_node(person_id) and self.graph.has_node(factor_id):
            self.graph.add_edge(person_id, factor_id, relation=relation_type, **(attributes or {}))

    def add_intervention_node(
        self,
        intervention_id: str,
        person_id: str,
        focus_area: str,
        rationale: str,
        timestamp: datetime,
    ) -> None:
        """Adds a rule-based Intervention suggestion node, linked via HAS_RECOMMENDATION.

        This is a simple heuristic suggestion (see
        ``vitagraph.pipeline.recommend_focus_area``), not the output of a
        causal-inference model. The Causal Inference objective described in
        docs/ROADMAP.md is not implemented yet.
        """
        if not self.graph.has_node(intervention_id):
            self.graph.add_node(
                intervention_id,
                type="Intervention",
                focus_area=focus_area,
                rationale=rationale,
                timestamp=timestamp.isoformat(),
            )
            self.graph.add_edge(person_id, intervention_id, relation="HAS_RECOMMENDATION")

    def build_from_processed_data(
        self,
        person_id: str,
        hr_df: pd.DataFrame,
        sleep_df: pd.DataFrame,
        hrv_df: pd.DataFrame | None = None,
    ) -> None:
        """Builds a subgraph for one person from processed biometric DataFrames."""
        self.add_person_node(person_id, {"name": f"Person {person_id}"})

        for index, row in hr_df.iterrows():
            data_id = f"HR_{person_id}_{index}"
            self.add_biometric_data_node(
                data_id, person_id, "HeartRate", row["heart_rate"], row["timestamp"]
            )

        if hrv_df is not None:
            for index, row in hrv_df.iterrows():
                data_id = f"HRV_{person_id}_{index}"
                self.add_biometric_data_node(
                    data_id, person_id, "HRV", row["hrv_ms"], row["timestamp"]
                )

        for index, row in sleep_df.iterrows():
            data_id = f"Sleep_{person_id}_{index}"
            sleep_date_time = datetime.combine(row["date"], datetime.min.time())
            self.add_biometric_data_node(
                data_id, person_id, "SleepHours", row["sleep_hours"], sleep_date_time
            )

    # ------------------------------------------------------------------ #
    # Querying
    # ------------------------------------------------------------------ #
    def get_graph_info(self) -> dict[str, Any]:
        """Returns summary statistics about the graph."""
        node_types = nx.get_node_attributes(self.graph, "type")
        type_counts: dict[str, int] = {}
        for node_type in node_types.values():
            type_counts[node_type] = type_counts.get(node_type, 0) + 1

        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "node_type_counts": type_counts,
            "edge_relations": list({d.get("relation") for _, _, d in self.graph.edges(data=True)}),
        }

    def get_subgraph_for_person(self, person_id: str) -> nx.DiGraph:
        """Returns the induced subgraph of a person and everything directly linked to them.

        Raises:
            GraphNodeNotFoundError: If ``person_id`` is not in the graph.
        """
        if not self.graph.has_node(person_id):
            raise GraphNodeNotFoundError(f"Person node '{person_id}' not found in graph")
        neighbor_ids = set(self.graph.successors(person_id)) | set(self.graph.predecessors(person_id))
        node_ids = {person_id} | neighbor_ids
        return self.graph.subgraph(node_ids).copy()

    # ------------------------------------------------------------------ #
    # Export
    # ------------------------------------------------------------------ #
    def export_to_json(self, path: str | Path) -> Path:
        """Exports the graph in node-link JSON format (``networkx.node_link_data``)."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = nx.node_link_data(self.graph, edges="edges")
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info("Exported graph to %s (JSON, %d nodes)", path, self.graph.number_of_nodes())
        return path

    def export_to_graphml(self, path: str | Path) -> Path:
        """Exports the graph in GraphML format, after sanitizing attribute types.

        GraphML does not support ``None`` values or arbitrary Python
        objects, so every attribute is coerced to ``str``/``int``/``float``/
        ``bool`` (or dropped, if it is ``None``) on a copy of the graph
        before writing.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        sanitized = nx.DiGraph()
        for node_id, attrs in self.graph.nodes(data=True):
            sanitized.add_node(node_id, **_sanitize_attrs(attrs))
        for source, target, attrs in self.graph.edges(data=True):
            sanitized.add_edge(source, target, **_sanitize_attrs(attrs))

        nx.write_graphml(sanitized, path)
        logger.info("Exported graph to %s (GraphML, %d nodes)", path, self.graph.number_of_nodes())
        return path


def _sanitize_attrs(attrs: dict[str, Any]) -> dict[str, Any]:
    """Coerces a node/edge attribute dict to GraphML-safe primitive types."""
    sanitized: dict[str, Any] = {}
    for key, value in attrs.items():
        if value is None:
            continue
        if isinstance(value, bool | int | float | str):
            sanitized[key] = value
        else:
            sanitized[key] = str(value)
    return sanitized
