"""Fixtures for the W2-20 acceptance tests (the machine-wide resource gate)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_20_support as support  # noqa: E402


@pytest.fixture
def machine(tmp_path):
    """A temporary home folder, reading files and child processes, all removed at the end of the test."""
    m = support.Machine(tmp_path)
    try:
        yield m
    finally:
        m.cleanup()


@pytest.fixture
def repo(machine):
    """This repository: a git repository built from scratch."""
    return machine.repo("this-repo")
