"""Fixtures for the W2-201 acceptance tests: W2-184's launch fixtures (its fixture project, the stand-in CLI)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_201_support as k  # noqa: E402


@pytest.fixture()
def sandbox(tmp_path):
    """HOME (planted as W2-60a plants it), TMPDIR and an unrelated folder, in this test's folder."""
    return k.s.b.make_sandbox(tmp_path / "w2-201")


@pytest.fixture()
def project(sandbox):
    """W2-184's fixture project: a role file with a fixture table per worker role, a criticality.yaml (C3
    ``src/critical``, C2 ``src/product``, C1 ``docs``, default C0), experiment folders."""
    return k.s.make_project(sandbox)


@pytest.fixture()
def cli(sandbox):
    """The stand-in CLI at ``<HOME>/.local/bin/claude``: it starts no session and never a model."""
    return k.s.b.install_stand_in_cli(sandbox)


@pytest.fixture()
def launch(sandbox, project, cli):
    """``launch(role, ticket_id, *cli_args)``: one ``gov launch`` in the project, through the console script."""

    def _launch(role, tk, *cli_args, **options):
        return k.s.launch(sandbox, cli, role, tk, *cli_args, **options)

    return _launch


@pytest.fixture()
def hook_base(tmp_path):
    return tmp_path / "hook"
