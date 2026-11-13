"""Fixtures of the W2-32 acceptance tests (README, "The fixtures")."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_32_support as s  # noqa: E402


@pytest.fixture(autouse=True)
def _the_code_under_test():
    s.assert_code_under_test()


@pytest.fixture
def standin():
    stand_in = s.OllamaStandIn({s.PIN_MODEL: s.PIN_DIGEST, s.SWAP_MODEL: s.SWAP_DIGEST})
    yield stand_in
    stand_in.close()


@pytest.fixture
def box(tmp_path, standin):
    """The children's places and environment; every case fails if a child tried to start an embedder."""
    the_box = s.Box(tmp_path / "box", standin.host)
    yield the_box
    the_box.assert_no_embedder_started()


@pytest.fixture
def needs_vectors():
    missing = s.lacking()
    if missing:
        pytest.skip(missing)


@pytest.fixture
def project(tmp_path, needs_vectors):
    """A planted project (``NOTES``), not yet rebuilt."""
    return s.plant(tmp_path / "project")
