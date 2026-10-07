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
    """A temporary project built from the template's .rulesync/ sources."""
    support.init_git(tmp_path)
    support.build_project_from_template(tmp_path)
    return tmp_path


@pytest.fixture()
def generated_project(project):
    """A temporary project with ``rulesync generate`` already run."""
    result = support.run_rulesync_generate(project)
    assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
    return project
