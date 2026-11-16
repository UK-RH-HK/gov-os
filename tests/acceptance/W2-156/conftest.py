"""Fixtures for the W2-156 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_156_support as t  # noqa: E402


@pytest.fixture()
def box(tmp_path):
    """HOME (planted as W2-60a plants it), TMPDIR and an unrelated folder, in this test's folder."""
    return t.b.make_sandbox(tmp_path / "w2-156")


@pytest.fixture()
def project(box):
    """W2-60a's fixture project with the extra tickets: its own git repository, its own main checkout."""
    return t.make_project(box)


@pytest.fixture()
def cli(box, project):
    """W2-60a's stand-in CLI at ``<HOME>/.local/bin/claude``: it starts no model and records how it was started."""
    return t.b.install_stand_in_cli(box)
