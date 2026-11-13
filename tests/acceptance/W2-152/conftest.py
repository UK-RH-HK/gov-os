"""The W2-152 acceptance tests import their helpers from this folder (README); each case builds its own repository."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_152_support as s  # noqa: E402


@pytest.fixture
def repo(tmp_path):
    """A fixture repository with the planted templates and the planted facts, holding the READY ticket."""
    return s.Repo(tmp_path / "repo", templates="planted")


@pytest.fixture
def real_repo(tmp_path):
    """A fixture repository with this tree's kernel templates and facts file, holding the READY ticket."""
    return s.Repo(tmp_path / "repo", templates="real")
