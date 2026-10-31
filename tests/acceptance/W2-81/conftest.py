"""Fixtures for the W2-81 proving ground's self-tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_81_build as build  # noqa: E402
import w2_81_git as gitlib  # noqa: E402
from w2_81_secret import scan_history  # noqa: E402
from w2_81_words import DEFAULT_SEED  # noqa: E402


SUITE = Path(__file__).resolve().parent
porcelain_here, w2_81_artefacts = gitlib.porcelain_here, gitlib.w2_81_artefacts


@pytest.fixture(scope="module", autouse=True)
def this_repository_unchanged():
    """No W2-81 case writes in this repository (checked around each module, attributable to this suite).

    Every write of the suite is refused inside this repository before it is made (``outside_this_repository``).
    Around each module: the suite's own folder is unchanged, and no new untracked path that only a W2-81 case
    writes appears anywhere in the tree. Another suite's transient file in the same tree is not blamed here.
    """
    for tool in gitlib.TOOLS:
        gitlib.require(tool)  # a missing tool fails naming it (DEC-899 item 7), never a skip
    suite_before, tree_before = porcelain_here(str(SUITE)), w2_81_artefacts(porcelain_here())
    yield
    assert porcelain_here(str(SUITE)) == suite_before, "a W2-81 case changed the suite's own folder"
    new = w2_81_artefacts(porcelain_here()) - tree_before
    assert not new, f"a W2-81 case wrote in this repository: {sorted(new)}"


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
