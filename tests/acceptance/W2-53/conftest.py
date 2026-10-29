"""Fixtures for the W2-53 acceptance tests (the probe gate's later merges; DEC-757's lists)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_53_support as support  # noqa: E402


@pytest.fixture(scope="session")
def interface():
    """The envelope fields and exit codes of ``docs/interfaces/API-0002.yaml``."""
    return support.cli_support.load_interface(support.REPO_ROOT)


@pytest.fixture(scope="session")
def code_under_test():
    """The ``gov`` the cases start is this worktree's ``src/`` (DEC-732)."""
    assert support.SRC.is_dir() and (support.SRC / "gov" / "__init__.py").is_file(), \
        f"no gov package under {support.SRC}"
    return support.SRC


@pytest.fixture()
def sandbox(tmp_path, code_under_test):
    return support.cli_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(tmp_path, code_under_test):
    """A temporary project built from scratch: its path map names its register, records no base and no list."""
    return support.project_at(tmp_path / "project")


@pytest.fixture()
def told(tmp_path):
    """A folder outside the project where the telling tests write how they ran."""
    folder = tmp_path / "told"
    folder.mkdir()
    return folder
