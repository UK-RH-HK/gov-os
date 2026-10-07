"""Fixtures for the W1-38 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_38_support as support  # noqa: E402


@pytest.fixture(scope="session")
def rulesync_version():
    """The installed rulesync version string, or skip if not found."""
    ver = support.rulesync_version()
    if ver is None:
        pytest.skip("rulesync is not installed")
    return ver


@pytest.fixture()
def project(tmp_path):
    """A temporary project with a .rulesync/ source tree and git init."""
    support.init_git(tmp_path)
    support.build_minimal_rulesync_tree(tmp_path)
    return tmp_path


@pytest.fixture()
def project_with_openspec_and_vendored(tmp_path):
    """A temporary project with OpenSpec commands and vendored skills in .rulesync/."""
    support.init_git(tmp_path)
    support.build_minimal_rulesync_tree(tmp_path)
    support.add_openspec_commands(tmp_path)
    support.add_vendored_skills(tmp_path)
    return tmp_path
