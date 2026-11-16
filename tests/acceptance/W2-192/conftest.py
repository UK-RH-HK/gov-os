"""W2-192 fixtures: one planted project carried through A0-A2 per session; AS run once on a copy; copies per case."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = str(Path(__file__).resolve().parent)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import w2_192_support as support  # noqa: E402


@pytest.fixture(scope="session")
def prepared(tmp_path_factory):
    """The planted project after A0, A1 and A2 (built once; no case touches it, each copies it)."""
    return support.prepare(tmp_path_factory.mktemp("w2-192-prepared"))


@pytest.fixture(scope="session")
def audited(prepared, tmp_path_factory):
    """A copy of the prepared project on which ``--stage AS`` ran once. Read-only for the cases that read the record;
    a case that changes the project copies ``audited.root`` first. The run's outcome is not asserted here."""
    return support.run_as(prepared, tmp_path_factory.mktemp("w2-192-audited"))


@pytest.fixture
def adoption(prepared, tmp_path):
    """An ``Adoption`` on a copy of the prepared project (A0, A1, A2 done; AS not run), with a box of its own."""
    root = support.copy_of(prepared, tmp_path / "project")
    return support.Adoption(root, support.base.make_box(tmp_path / "box"))


@pytest.fixture
def after_as(audited, tmp_path):
    """An ``Adoption`` on a copy of the project after AS ran. The AS run's outcome is not asserted here (a fixture that
    asserts errors instead of failing): ``adoption.as_done`` holds it, and a case that needs it calls ``support.as_ran``."""
    root = support.copy_of(audited.root, tmp_path / "project")
    adoption = support.Adoption(root, support.base.make_box(tmp_path / "box"))
    adoption.as_done = audited.done
    return adoption
