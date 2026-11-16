"""Fixtures for the W2-60b acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_60b_support as t  # noqa: E402


@pytest.fixture()
def box(tmp_path):
    """HOME (planted as W2-60a plants it), TMPDIR and an unrelated folder, in this test's folder."""
    return t.b.make_sandbox(tmp_path / "w2-60b")


@pytest.fixture()
def project(box):
    """W2-184's fixture project: W2-60a's, a role file with a table per worker role, a ``criticality.yaml``."""
    return t.s.make_project(box)


@pytest.fixture()
def cli(box):
    """The planted CLI at ``<HOME>/.local/bin/claude``: it writes the planted session log and starts no model."""
    return t.install_cli(box)


@pytest.fixture()
def launch(box, project, cli):
    """``launch(role, ticket, *cli_args, options=(), cwd=None)``: one ``gov launch``."""

    def _launch(role, tk, *cli_args, **kwargs):
        return t.launch(box, cli, role, tk, *cli_args, **kwargs)

    return _launch
