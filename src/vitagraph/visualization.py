"""Static visualization helpers for the VitaGraph knowledge graph.

Kept intentionally small: a single function that renders a person's
subgraph to a PNG using matplotlib + networkx's spring layout. This is a
convenience for quick inspection during development/demos, not a
production dashboard.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless-safe backend for servers/CI/sandboxes
import matplotlib.pyplot as plt
import networkx as nx

from vitagraph.knowledge_graph import KnowledgeGraph
from vitagraph.logging_config import get_logger

logger = get_logger(__name__)

_NODE_COLORS = {
    "Person": "#2E86AB",
    "BiometricData": "#7CB518",
    "EnvironmentalFactor": "#E9724C",
    "Intervention": "#C5283D",
}
_DEFAULT_COLOR = "#999999"


def plot_person_subgraph(
    kg: KnowledgeGraph,
    person_id: str,
    save_path: str | Path,
    figsize: tuple[int, int] = (9, 7),
    seed: int = 42,
) -> Path:
    """Renders the induced subgraph around ``person_id`` to a PNG file.

    Args:
        kg: The KnowledgeGraph to visualize.
        person_id: The person whose neighborhood should be plotted.
        save_path: Where to write the PNG.
        figsize: Matplotlib figure size in inches.
        seed: Layout seed, for a reproducible node arrangement.

    Returns:
        The path the figure was saved to.
    """
    subgraph = kg.get_subgraph_for_person(person_id)
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    node_types = nx.get_node_attributes(subgraph, "type")
    colors = [_NODE_COLORS.get(node_types.get(n), _DEFAULT_COLOR) for n in subgraph.nodes()]
    labels = {n: node_types.get(n, n) for n in subgraph.nodes()}

    pos = nx.spring_layout(subgraph, seed=seed)

    fig, ax = plt.subplots(figsize=figsize)
    nx.draw_networkx_nodes(subgraph, pos, node_color=colors, node_size=600, ax=ax)
    nx.draw_networkx_edges(subgraph, pos, arrows=True, arrowsize=12, ax=ax)
    nx.draw_networkx_labels(subgraph, pos, labels=labels, font_size=7, ax=ax)
    ax.set_title(f"VitaGraph — neighborhood of {person_id}")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)

    logger.info("Saved subgraph plot for %s to %s", person_id, save_path)
    return save_path
