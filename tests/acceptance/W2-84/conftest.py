"""Fixtures for the W2-84 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_84_support as support  # noqa: E402


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    """The planted repository's five trees, each holding the hidden part, and the links (read-only cases)."""
    return support.make_world(tmp_path_factory.mktemp("w2-84-trees"))


@pytest.fixture(scope="module")
def store(tmp_path_factory):
    """A repository whose trees hold no hidden file, while a commit on another branch holds the hidden part."""
    return support.make_store_world(tmp_path_factory.mktemp("w2-84-store"))


@pytest.fixture()
def fresh_world(tmp_path):
    """A world of its own, for a case that changes it (a mode, a file); no links."""
    return support.make_world(tmp_path / "w2-84", links=False)


@pytest.fixture()
def modes():
    """Folders a case makes unreadable get their mode back at teardown, so that pytest can remove them."""
    held = support.Modes()
    yield held
    held.restore()
