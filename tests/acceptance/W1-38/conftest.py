"""Fixtures for the W1-38 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_38_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "needs_rulesync: test requires the rulesync binary"
    )


@pytest.fixture(scope="session")
def rulesync_bin():
    """The rulesync binary path, or skip if not installed."""
    ver = support.rulesync_version()
    if ver is None:
        pytest.skip("rulesync is not installed")
    return support.RULESYNC_BIN


@pytest.fixture()
def project(tmp_path, rulesync_bin):
    """An adopted project in a temporary folder: the template's ``.rulesync/``
    sources, the kernel, the tool registry and the check's declaration."""
    root = tmp_path / "project"
    root.mkdir()
    support.init_git(root)
    support.build_project_from_template(root)
    return root


@pytest.fixture()
def generated_project(project):
    """The project with ``rulesync generate`` already run, committed."""
    result = support.run_rulesync_generate(project)
    assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
    support.commit_all(project, "generated")
    return project


@pytest.fixture()
def sandbox(tmp_path):
    """The home, temporary and launcher folders ``gov`` runs with (W1-07)."""
    return support.cli_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def mock_dir(tmp_path):
    """A folder outside the project for a stand-in rulesync binary."""
    return tmp_path / "bin"


@pytest.fixture(scope="session")
def openspec_shipped(tmp_path_factory):
    """``{name: text}`` of the command files the registered OpenSpec writes for
    Claude Code. A missing or differently versioned openspec fails the case."""
    return support.openspec_shipped_commands(tmp_path_factory.mktemp("w1-38-openspec"))
