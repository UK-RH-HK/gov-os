"""Fixtures for the W2-87 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_87_support as support  # noqa: E402


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH on this machine: the lexical index's secret filter cannot run (DEC-287)")
    return support.Api(tmp_path_factory.mktemp("w2-87-api"))


@pytest.fixture(scope="session")
def planted(api, tmp_path_factory):
    """``planted(config, register_text=...)``: a project built once per path-map block and register, its lexical
    index and record graph loaded. A retrieval only reads, so the tests share them."""
    built = {}

    def make(config, register_text=support.REGISTER_TEXT):
        key = (config, register_text)
        if key not in built:
            root = support.build_project(tmp_path_factory.mktemp(f"w2-87-{config}") / "repo",
                                         support.CONFIGS[config], register_text)
            api.build(root)
            built[key] = root
        return built[key]

    return make
