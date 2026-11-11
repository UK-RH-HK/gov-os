"""Fixtures for the W2-04 acceptance tests (this folder only)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_04_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: needs a live local embedder (Ollama and the pinned model) or this tree's own store; "
                   "not for CI")


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    return support.Api(tmp_path_factory.mktemp("w2-04-api"))


@pytest.fixture(scope="session")
def retrieval_api(api):
    """The api, where the lexical index can be built (its secret filter needs gitleaks, DEC-287)."""
    if not api.has_gitleaks():
        pytest.skip("gitleaks is not on PATH on this machine: the lexical index's secret filter cannot run (DEC-287)")
    return api


@pytest.fixture(scope="session")
def ledger(retrieval_api, tmp_path_factory):
    """The ledger project (README, "The planted projects"), indexed and loaded; cases only read it."""
    project = support.build_project(tmp_path_factory.mktemp("w2-04-ledger") / "repo", support.ledger_files())
    retrieval_api.build(project.root)
    return project
