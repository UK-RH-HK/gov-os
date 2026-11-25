"""Shared fixtures: one published batch of four packages, built once per worker and copied for each case."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w2_211_support as S  # noqa: E402

IDS = ["DP-0042", "DP-0043", "DP-0044", "DP-0045"]


@pytest.fixture(scope="session")
def env(tmp_path_factory):
    return S.make_env(S.make_home(tmp_path_factory.mktemp("home")))


@pytest.fixture(scope="session")
def batch_template(tmp_path_factory, env):
    base = tmp_path_factory.mktemp("batch")
    packages = {
        "DP-0042": S.package_text("DP-0042", under=["DEC-1225"], options=[
            S.option("a", "Keep it"), S.option("b", "Change it", changes="DEC-1230"), S.option("c", "Drop it")]),
        "DP-0043": S.package_text("DP-0043"),
        "DP-0044": S.package_text("DP-0044"),
        "DP-0045": S.package_text("DP-0045", options=[S.option("a", "Yes"), S.option("b", "No")]),
    }
    repo = S.init_repo(base, env, "tmpl", packages)
    batch, digest, cards = S.make_batch(repo, env)
    return repo, batch, digest, cards


@pytest.fixture
def case(batch_template, env, tmp_path):
    """A copy of the published batch: ``(repo, batch, hash, cards)``."""
    repo, batch, digest, cards = batch_template
    target = tmp_path / "repo"
    shutil.copytree(repo, target, symlinks=True)
    return target, batch, digest, cards
