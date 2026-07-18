"""Shared pytest fixtures for the VitaGraph test suite."""

from __future__ import annotations

from datetime import datetime

import pytest

from vitagraph.bio_signal_processor import BioSignalProcessor
from vitagraph.config import SignalBaseline
from vitagraph.knowledge_graph import KnowledgeGraph
from vitagraph.synthetic_data import SyntheticCohortGenerator


@pytest.fixture
def baseline() -> SignalBaseline:
    return SignalBaseline()


@pytest.fixture
def processor(baseline: SignalBaseline) -> BioSignalProcessor:
    return BioSignalProcessor(seed=42, baseline=baseline)


@pytest.fixture
def cohort_generator(baseline: SignalBaseline) -> SyntheticCohortGenerator:
    return SyntheticCohortGenerator(baseline=baseline, seed=42)


@pytest.fixture
def empty_graph() -> KnowledgeGraph:
    return KnowledgeGraph()


@pytest.fixture
def start_time() -> datetime:
    return datetime(2026, 1, 1, 8, 0, 0)
