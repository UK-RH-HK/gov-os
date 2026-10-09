"""Fixtures for the W1-41 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W1-07"))

import w1_41_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: clones a dev tier (GOV_DEV_TIERS) into a temporary folder; "
                                       "not for CI")


@pytest.fixture(scope="session")
def interface():
    """The envelope and the exit codes of API-0002, read from this worktree's interface file."""
    return support.base.load_interface(support.REPO_ROOT)


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR, the launcher's folder and the bytecode cache, outside the project."""
    return support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(tmp_path):
    """The legacy project, committed: a git repository of its own in the case's temporary folder."""
    return support.build_project(tmp_path / "harbour")


@pytest.fixture()
def adoption(project, sandbox, interface):
    """An adoption of the case's own project."""
    return support.Adoption(project, sandbox, interface)


@pytest.fixture()
def adopt_in(sandbox, interface):
    """An adoption of a project the case built itself (a variant of the legacy project)."""
    return lambda root: support.Adoption(root, sandbox, interface)
