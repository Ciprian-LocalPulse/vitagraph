"""VitaGraph: synthetic-data reference framework for bio-signal knowledge graphs
and biological-age estimation research.

This package is an educational / research reference implementation. All
data produced by its bundled generators is synthetic (seeded random data).
Nothing in this package should be used for real medical, diagnostic, or
clinical decision-making. See docs/METHODOLOGY.md for a precise statement
of current scope and docs/ROADMAP.md for the longer-term research vision.
"""

from vitagraph.bio_age_estimator import BioAgeEstimator
from vitagraph.bio_signal_processor import BioSignalProcessor
from vitagraph.knowledge_graph import KnowledgeGraph
from vitagraph.synthetic_data import SyntheticCohortGenerator

__version__ = "0.2.0"

__all__ = [
    "BioAgeEstimator",
    "BioSignalProcessor",
    "KnowledgeGraph",
    "SyntheticCohortGenerator",
    "__version__",
]
