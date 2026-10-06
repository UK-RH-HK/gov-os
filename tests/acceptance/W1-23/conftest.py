"""Fixtures for the W1-23 acceptance tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_23_support as support  # noqa: E402


def _built(make):
    reason = None
    try:
        return make()
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def box(tmp_path_factory):
    return support.Api(tmp_path_factory.mktemp("w1-23-api"))


@pytest.fixture(scope="session")
def synthesis_api(box):
    """Every test that uses this fixture fails here until gov.retrieval.synthesis.synthesize exists."""
    _built(lambda: box.exists(support.SYNTHESIS_MODULE, support.SYNTHESIZE_FUNCTION))
    return box


@pytest.fixture(scope="session")
def validate_api(box):
    """Every test that uses this fixture fails here until gov.retrieval.synthesis.validate_notes exists."""
    _built(lambda: box.exists(support.SYNTHESIS_MODULE, support.VALIDATE_NOTES_FUNCTION))
    return box


@pytest.fixture
def project(tmp_path):
    """A fresh temporary git repository with files across directories."""
    return support.build_fixture(tmp_path / "repo")
