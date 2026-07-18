"""Custom exception types used across VitaGraph.

Using specific exception types (instead of letting bare ``ValueError`` /
``KeyError`` leak from deep inside sklearn or networkx) gives callers a
stable, documented contract to catch against.
"""

from __future__ import annotations


class VitaGraphError(Exception):
    """Base class for all VitaGraph-specific errors."""


class InvalidModelTypeError(VitaGraphError):
    """Raised when an unsupported model_type is requested from BioAgeEstimator."""


class ModelNotTrainedError(VitaGraphError):
    """Raised when predict()/evaluate()/save_model() is called before training."""


class MissingFeatureColumnsError(VitaGraphError):
    """Raised when an input DataFrame is missing required feature columns."""


class GraphNodeNotFoundError(VitaGraphError):
    """Raised when an operation references a node id that does not exist in the graph."""
