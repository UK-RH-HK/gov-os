"""Fixtures for the W2-184 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_184_support as s  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: starts a real worker session through gov launch on this machine; not for CI")


@pytest.fixture()
def sandbox(tmp_path):
    """HOME (planted as W2-60a plants it), TMPDIR and an unrelated folder, in this test's folder."""
    return s.b.make_sandbox(tmp_path / "w2-184")


@pytest.fixture()
def project(sandbox):
    """The fixture project: a role file with a table per worker role, a criticality.yaml, experiment folders."""
    return s.make_project(sandbox)


@pytest.fixture()
def cli(sandbox):
    """The stand-in CLI at ``<HOME>/.local/bin/claude``: it starts no session and never a model."""
    return s.b.install_stand_in_cli(sandbox)


@pytest.fixture()
def launch(sandbox, project, cli):
    """``launch(role, ticket_id, *cli_args, reason=, trial=, owner_named=)``: one launch in the project."""

    def _launch(role, tk, *cli_args, **options):
        return s.launch(sandbox, cli, role, tk, *cli_args, **options)

    return _launch
