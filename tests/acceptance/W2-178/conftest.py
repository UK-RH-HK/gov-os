"""Fixtures for the W2-178 acceptance tests: W2-149's planted repository once per session, the launch script as it
stood at the ticket's base once per session, and W2-149's planted world per case.

No real session, model, network or GPU: the stub ``claude`` plays every session (the dry builds start none); HOME, the
sets root, the runs and trees folders and the repository lie under pytest's temporary folder (W2-149's
``World.check_planted`` fails a launch otherwise).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_178_support as s178  # noqa: E402
from w2_178_support import support  # noqa: E402


@pytest.fixture(scope="session")
def planted_repo_178(tmp_path_factory):
    return support.build_repo(tmp_path_factory.mktemp("w2-178-repo") / "repo")


@pytest.fixture(scope="session")
def base_script(tmp_path_factory):
    """The launch script at the base commit, next to its schemas (out of git)."""
    return s178.extract_base_script(tmp_path_factory.mktemp("w2-178-base") / "base")


@pytest.fixture()
def world(tmp_path, tmp_path_factory, planted_repo_178):
    w = support.World(tmp_path / "w", planted_repo_178, base=tmp_path_factory.getbasetemp())
    w.plant()
    yield w
    support.make_writable(tmp_path)
