"""Fixtures for the W2-58 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_58_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: starts a real worker session through gov launch on this machine (CLI, bwrap, socat, "
                   "the network); not for CI")


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR and an unrelated folder, disjoint siblings in this test's own folder."""
    return support.make_sandbox(tmp_path / "w2-58")


@pytest.fixture()
def ask(sandbox):
    """``ask(call, role, ticket=None)``: the guard's decision on one call; the ticket defaults to the role's."""

    def _ask(call, role, ticket=None):
        ticket = ticket or support.TICKET_OF[role]
        return support.ask_guard(sandbox, call.tool, call.input, role, ticket.tk, sandbox.project)

    return _ask


def _world(tmp_path_factory, name, **kwargs):
    box = support.make_sandbox(tmp_path_factory.mktemp(name))
    builder = kwargs.pop("builder", support.make_project)
    return support.World(box, builder(box, **kwargs))


@pytest.fixture(scope="module")
def open_world(tmp_path_factory):
    """A project with no ``w2/integrate`` branch: the test designer has no base, so (c) refuses it nothing."""
    return _world(tmp_path_factory, "open", base=False)


@pytest.fixture(scope="module")
def branch_world(tmp_path_factory):
    """A project whose ticket branch ``w2/W2-95`` leaves ``w2/integrate`` and changes T's files."""
    return _world(tmp_path_factory, "branch", base=True)


@pytest.fixture(scope="module")
def eval_world(tmp_path_factory):
    """A branch project whose path map declares the fixture evaluation set (measured: research, and ticket W2-93)."""
    return _world(tmp_path_factory, "eval", builder=support.make_eval_project)


@pytest.fixture()
def cli(sandbox):
    """The stand-in CLI at ``<HOME>/.local/bin/claude``: it starts no session and never a model."""
    return support.install_stand_in_cli(sandbox)
