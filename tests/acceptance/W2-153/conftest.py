"""The W2-153 acceptance tests import their helpers from this folder (README); one session-wide fixture unpacks
integrate's ``src/gov`` at the baseline commit for the failure line F2."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_153_support as support  # noqa: E402


@pytest.fixture(scope="session")
def baseline_src(tmp_path_factory) -> Path:
    """integrate's ``src`` at ``support.BASELINE_COMMIT`` (blob ids checked), unpacked once per session."""
    return support.extract_baseline_src(tmp_path_factory.mktemp("w2-153-baseline"))
