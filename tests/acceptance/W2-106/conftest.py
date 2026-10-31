"""W2-106 acceptance fixtures: one stand-in pin per session, built from this repository's own code (README)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_106_support as support  # noqa: E402


@pytest.fixture(scope="session")
def stand_in():
    """The stand-in pin (W2-59's form): this repository's wheel, installed non-editable in its own environment in a
    short temporary folder (so that its ``bin/gov`` names its interpreter in a direct ``#!`` line), instrumented."""
    base = support.pin_support.short_temporary_folder("w2106-pin-")
    try:
        yield support.pin_support.make_stand_in(base)
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.fixture
def pin(stand_in):
    """The stand-in, its markers emptied before the case."""
    stand_in.clear_markers()
    return stand_in


@pytest.fixture
def box(tmp_path):
    return support.make_box(tmp_path / "box")
