"""Fixtures for the W2-173 acceptance tests: W2-149's planted repository (with W2-173's extra briefs) once per
session, W2-149's planted world per case, and W2-173's argv recorder in front of W2-149's stub ``claude``.

No real session, model, network or GPU: the stub plays every session; HOME, the sets root, the runs and trees folders
and the repository lie under pytest's temporary folder (W2-149's ``World.check_planted`` fails a launch otherwise).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_173_support as s173  # noqa: E402
from w2_173_support import support  # noqa: E402


@pytest.fixture(scope="session")
def planted_repo_173(tmp_path_factory):
    return support.build_repo(tmp_path_factory.mktemp("w2-173-repo") / "repo", extra_briefs=s173.EXTRA_BRIEFS)


@pytest.fixture()
def world(tmp_path, tmp_path_factory, planted_repo_173):
    w = support.World(tmp_path / "w", planted_repo_173, base=tmp_path_factory.getbasetemp())
    w.plant()
    s173.install_recorder(w)
    yield w
    support.make_writable(tmp_path)
