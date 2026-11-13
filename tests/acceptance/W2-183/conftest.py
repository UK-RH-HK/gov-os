"""Fixtures for the W2-183 acceptance tests (this folder only)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_183_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: needs a live local embedder (Ollama and the pinned model) or this tree's own store; "
                   "not for CI")


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    return support.Api(tmp_path_factory.mktemp("w2-183-api"))


@pytest.fixture(scope="module")
def small(api, tmp_path_factory):
    """A small ticket and one charter record; no lexical index, so nothing supplementary. facts.yaml is absent."""
    project = support.build_project(tmp_path_factory.mktemp("w2-183-small") / "repo", support.small_files())
    api.build(project.root, index=False)
    return project


@pytest.fixture(scope="module")
def big(api, tmp_path_factory):
    """A ticket whose own text and mandatory inputs come to about 10,000 tokens; no index. facts.yaml is absent."""
    project = support.build_project(tmp_path_factory.mktemp("w2-183-big") / "repo", support.big_files())
    api.build(project.root, index=False)
    return project


@pytest.fixture(scope="module")
def ledger(api, tmp_path_factory):
    """The ledger: a small ticket with 80 matching pages (about 24,000 tokens of supplementary evidence), indexed and
    loaded; cases only read it (facts.yaml is absent except inside ``Project.setting``)."""
    project = support.build_project(tmp_path_factory.mktemp("w2-183-ledger") / "repo", support.ledger_files())
    api.build(project.root, index=True)
    return project
