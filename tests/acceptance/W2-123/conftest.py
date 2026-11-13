"""Fixtures for the W2-123 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_123_support as support  # noqa: E402


@pytest.fixture()
def stage(tmp_path):
    """This test's HOME, planted executable and endpoints. Every stand-in is ended afterwards."""
    stage = support.Stage(tmp_path / "stage")
    try:
        yield stage
    finally:
        stage.close()


@pytest.fixture()
def ollama():
    """The module under test, as the pytest process imports it (README, "How the suite runs the code under test")."""
    from gov.retrieval import ollama
    return ollama
