"""W2-190 fixtures: one planted project carried through A0-A2 per session, copied for each case."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = str(Path(__file__).resolve().parent)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import w2_190_support as support  # noqa: E402


@pytest.fixture(scope="session")
def prepared(tmp_path_factory):
    """The planted project after A0, A1 and A2 (built once; no case touches it, each copies it)."""
    return support.prepare(tmp_path_factory.mktemp("w2-190-prepared"))


@pytest.fixture
def adoption(prepared, tmp_path):
    """An ``Adoption`` on a copy of the prepared project, with a box (HOME, TMPDIR) of its own."""
    root = support.copy_of(prepared, tmp_path / "project")
    return support.base.Adoption(root, support.base.make_box(tmp_path / "box"))
