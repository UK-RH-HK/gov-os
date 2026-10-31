"""Fixtures for the W2-81 proving ground's self-tests."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_81_build as build  # noqa: E402
import w2_81_git as gitlib  # noqa: E402
from w2_81_secret import scan_history  # noqa: E402
from w2_81_words import DEFAULT_SEED  # noqa: E402


def porcelain_here():
    """This repository's ``git status --porcelain``: no case may change it."""
    return subprocess.run(["git", "-C", str(gitlib.REPO_ROOT), "status", "--porcelain", "--untracked-files=all"],
                          capture_output=True, text=True, env=gitlib.git_env(gitlib.REPO_ROOT.parent)).stdout


@pytest.fixture(scope="module", autouse=True)
def this_repository_unchanged():
    """Nothing is written in this repository by any case of this suite (checked around each module)."""
    for tool in gitlib.TOOLS:
        gitlib.require(tool)  # a missing tool fails naming it (DEC-899 item 7), never a skip
    before = porcelain_here()
    yield
    after = porcelain_here()
    assert after == before, "a W2-81 case changed this repository's working tree"


@pytest.fixture(scope="session")
def ground(tmp_path_factory):
    """The proving ground at the self-tests' fixed seed, built once per process and removed at the end."""
    run = tmp_path_factory.mktemp("w2-81-run")
    built = build.build_all(run, DEFAULT_SEED, build.SELF_TEST_LARGE)
    yield built
    shutil.rmtree(run)


@pytest.fixture(scope="session")
def scans(ground, tmp_path_factory):
    """The secrets scanner's findings on each built repository's history, made once."""
    scratch = tmp_path_factory.mktemp("w2-81-scan")
    made = {name: scan_history(b.root, scratch) for name, b in ground.items()}
    yield made
    shutil.rmtree(scratch)


@pytest.fixture()
def run_folder(tmp_path):
    """A run folder of the case's own (pytest removes it with its retention)."""
    folder = tmp_path / "run"
    yield folder
    if folder.exists():
        shutil.rmtree(folder)
