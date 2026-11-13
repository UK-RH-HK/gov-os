"""Fixtures for the W2-129 acceptance tests: the two planted repositories and the shared runs of ``gov links``.

The planted repositories are built once per session in a temporary folder. A test that commits, writes a mark or
applies a patch works on its own copy (``fresh``). The shared runs (``since_root``, ``every``, ``as_json``) are taken
on copies of their own, so no mark written by one run changes another. Each fixture returns the child's result
unchecked; the test that reads it fails, in its own body, where the tree under test has no ``gov links``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_129_support as support  # noqa: E402


@pytest.fixture(scope="session")
def full(tmp_path_factory):
    """Repository A, built once; tests never run ``gov links`` on it directly (they take a copy)."""
    return support.build_full(tmp_path_factory.mktemp("w2-129-full") / "repo")


@pytest.fixture(scope="session")
def bare(tmp_path_factory):
    """Repository B: no register, no tickets, no contract.yaml."""
    return support.build_bare(tmp_path_factory.mktemp("w2-129-bare") / "repo")


@pytest.fixture()
def fresh(full, tmp_path):
    """A copy of repository A for one test, with no mark."""
    return support.clone(full, tmp_path / "repo")


@pytest.fixture(scope="session")
def since_root(full, tmp_path_factory):
    """``gov links --since <root>`` on a copy of A: every record and every commit is in the range."""
    shas = support.clone(full, tmp_path_factory.mktemp("w2-129-since") / "repo")
    return shas, support.spawn(shas["repo"], "--since", shas["root"])


@pytest.fixture(scope="session")
def every(full, tmp_path_factory):
    """``gov links --all`` on a copy of A with no mark."""
    shas = support.clone(full, tmp_path_factory.mktemp("w2-129-all") / "repo")
    return shas, support.spawn(shas["repo"], "--all")


@pytest.fixture(scope="session")
def as_json(full, tmp_path_factory):
    """``gov links --since <root> --json`` on a copy of A."""
    shas = support.clone(full, tmp_path_factory.mktemp("w2-129-json") / "repo")
    return shas, support.spawn(shas["repo"], "--since", shas["root"], "--json")
