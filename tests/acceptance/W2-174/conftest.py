"""The W2-174 acceptance tests import their helpers from this folder (README); each case builds its own repository."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "src"))  # in-process imports use the tree under test, as the children do

import w2_174_support as s  # noqa: E402


@pytest.fixture
def repo(tmp_path):
    """An empty fixture repository (a ``.tickets/`` folder); a case plants its tickets."""
    return s.Repo(tmp_path)
