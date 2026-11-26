"""Fixtures for the W2-213 slice 1 acceptance tests: the planted repositories, built once per worker and never changed
by a case (a case that changes one works on its own copy)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import w2_213_support as support  # noqa: E402


@pytest.fixture(scope="session")
def clean_repo(tmp_path_factory):
    """The planted owned repository the clean plan fits. Never changed."""
    return support.build_repository(tmp_path_factory.mktemp("w2-213-clean") / "meadow")


@pytest.fixture(scope="session")
def clean_run(clean_repo, tmp_path_factory):
    """``gov layout check <clean plan> --root <clean repository> --json``, once; the repository's state before it."""
    before = support.snapshot(clean_repo)
    run, _numbers = support.check_lines(tmp_path_factory.mktemp("w2-213-clean-run"), clean_repo, support.clean_lines())
    return run, before, support.snapshot(clean_repo)


@pytest.fixture(scope="session")
def dirty_repo(clean_repo, tmp_path_factory):
    """The clean repository plus hidden-set and secret files in the tree. Never changed."""
    return support.build_dirty(clean_repo, tmp_path_factory.mktemp("w2-213-dirty") / "meadow")


@pytest.fixture(scope="session")
def moved_repo(clean_repo, tmp_path_factory):
    """The correctly restructured copy of the clean repository. Never changed."""
    return support.build_moved(clean_repo, tmp_path_factory.mktemp("w2-213-moved") / "meadow")


@pytest.fixture()
def own_repo(clean_repo, tmp_path):
    """This case's own copy of the clean repository."""
    return support.copy_repository(clean_repo, tmp_path / "meadow")


@pytest.fixture()
def work(tmp_path):
    """Where this case's plans and run sandboxes go, outside every planted repository."""
    folder = tmp_path / "work"
    folder.mkdir()
    return folder
