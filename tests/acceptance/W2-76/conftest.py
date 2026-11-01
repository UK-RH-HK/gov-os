"""Fixtures for the W2-76 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_76_support as support  # noqa: E402


@pytest.fixture()
def box(tmp_path):
    """HOME, TMPDIR, the tools folder and the lock folder of one case, in its temporary folder; removed after it."""
    made = support.make_box(tmp_path / "w2-76")
    yield made
    for folder in made.base.rglob("*"):
        if folder.is_dir() and not folder.is_symlink():
            folder.chmod(0o755)
    shutil.rmtree(made.base, ignore_errors=True)


@pytest.fixture()
def lock(box):
    """This case's temporary rebuild lock path (absent until a rebuild or a holder creates it)."""
    return box.locks / "rebuild.lock"


@pytest.fixture()
def env(box):
    return support.environment(box)
