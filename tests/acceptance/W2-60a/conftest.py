"""Fixtures for the W2-60a acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_60a_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: starts a real worker session through gov launch on this machine (CLI, bwrap, socat, "
                   "the network, the caller's sign-in); not for CI")


@pytest.fixture()
def sandbox(tmp_path):
    """HOME (planted with what a session must not load), TMPDIR and an unrelated folder, in this test's folder."""
    return support.make_sandbox(tmp_path / "w2-60a")


@pytest.fixture()
def project(sandbox):
    """The fixture project: every worker role's fixture role file, generated agents, loaded and kernel skills."""
    return support.make_project(sandbox)


@pytest.fixture()
def cli(sandbox):
    """The stand-in CLI at ``<HOME>/.local/bin/claude``: it starts no session and never a model."""
    return support.install_stand_in_cli(sandbox)


@pytest.fixture()
def launch(sandbox, project, cli):
    """``launch(role, ticket=None, *cli_args)``: one ``gov launch`` in the project; the ticket defaults to the
    role's."""

    def _launch(role, ticket=None, *cli_args, **kwargs):
        return support.launch(sandbox, cli, role, ticket or support.TICKET_OF[role], *cli_args, **kwargs)

    return _launch
