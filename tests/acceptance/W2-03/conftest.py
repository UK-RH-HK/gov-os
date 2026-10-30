"""Fixtures for the W2-03 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_03_support as support  # noqa: E402


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    """The store, the record query and the decision checker of this worktree."""
    return support.Api(tmp_path_factory.mktemp("w2-03-api"))
