"""Fixtures for the W2-71 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_71_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: runs the gitleaks binary of this machine; not for CI")


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR and the test's own folder, in this test's temporary folder; removed after the test."""
    made = support.make_sandbox(tmp_path / "w2-71")
    yield made
    shutil.rmtree(made.base, ignore_errors=True)


@pytest.fixture(scope="module")
def module_sandbox(tmp_path_factory):
    """A sandbox shared by the cases of one file (one scene, one run of the check and of the filter); removed when
    the file's cases are done."""
    made = support.make_sandbox(tmp_path_factory.mktemp("w2-71-scene"))
    yield made
    shutil.rmtree(made.base, ignore_errors=True)
