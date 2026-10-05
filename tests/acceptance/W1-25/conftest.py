"""Fixtures for the W1-25 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_25_support as support  # noqa: E402

cli_support = support.cli_support


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: needs the dev tiers (GOV_DEV_TIERS) or a real session on this machine; not for CI")


@pytest.fixture(scope="session")
def live(tmp_path_factory):
    """A committed copy of the working tree with the fixture tickets. Never run a command in it."""
    target = cli_support.copy_working_tree(tmp_path_factory.mktemp("w1-25-live") / "repo")
    support.add_fixtures(target)
    return target


@pytest.fixture(scope="session")
def interface(live):
    return cli_support.load_interface(live)


@pytest.fixture(scope="session")
def built(live, tmp_path_factory):
    """The copy, once ``gov checkpoint`` is built. Until then every test of its behaviour fails here."""
    base = tmp_path_factory.mktemp("w1-25-built")
    probe = base / "repo"
    shutil.copytree(live, probe, symlinks=True)
    run = cli_support.run_gov(probe, cli_support.make_sandbox(base / "sandbox"), "checkpoint", "--json")
    if support.NOT_IMPLEMENTED in run.stdout:
        pytest.fail("gov checkpoint is not built yet: it returns NOT_IMPLEMENTED", pytrace=False)
    return live


@pytest.fixture()
def sandbox(tmp_path):
    return cli_support.make_sandbox(tmp_path / "sandbox")


def _copy(source, tmp_path):
    target = tmp_path / "repo"
    shutil.copytree(source, target, symlinks=True)
    return target


@pytest.fixture()
def raw_project(live, tmp_path):
    """This test's own copy, whether or not ``gov checkpoint`` is built."""
    return _copy(live, tmp_path)


@pytest.fixture()
def project(built, tmp_path):
    """This test's own copy of the working tree, with ``gov checkpoint`` built."""
    return _copy(built, tmp_path)


@pytest.fixture()
def raw_gov(raw_project, sandbox):
    def _gov(*args, cwd=None):
        return cli_support.run_gov(raw_project, sandbox, *args, cwd=cwd)

    return _gov


@pytest.fixture()
def gov(project, sandbox):
    """``gov(*args)`` runs the command line in this test's project."""

    def _gov(*args, cwd=None):
        return cli_support.run_gov(project, sandbox, *args, cwd=cwd)

    return _gov


@pytest.fixture()
def checkpoint(project, gov, interface):
    """``checkpoint(**write_args)`` writes one checkpoint, commits it and returns its path."""

    def _checkpoint(commit=True, **kwargs):
        result = support.succeeded(gov(*support.write_args(**kwargs)), interface)
        path = support.checkpoint_path(project, result)
        if commit:
            cli_support.commit_all(project, "checkpoint")
        return path

    return _checkpoint
