"""Fixtures for the W2-55 acceptance tests (this folder only)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_55_support as support  # noqa: E402


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    return support.Api(tmp_path_factory.mktemp("w2-55-api"))


@pytest.fixture(scope="session")
def retrieval_api(api):
    """The api, where the lexical index can be built (its secret filter needs gitleaks, DEC-287)."""
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH on this machine: the lexical index's secret filter cannot run (DEC-287)")
    return api
