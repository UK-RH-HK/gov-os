"""Fixtures for the W2-112 acceptance tests: one box (a temporary ``HOME``) per test, and nothing left running."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_112_support as support  # noqa: E402


def pytest_report_header(config):
    refused = support.unix_sockets_refused()
    return [f"W2-112: {refused}"] if refused else []


@pytest.fixture()
def boxes():
    """Make boxes with ``boxes(environment=..., gpu=..., settings=...)``; every process that carries a box's
    ``HOME`` is ended, and its folder removed, when the test ends, however it ends."""
    made = []

    def make(**kwargs):
        try:
            box = support.Box(**kwargs)
        except support.Missing as reason:  # a case that cannot run is red, never skipped as if it passed
            pytest.fail(f"the case cannot run on this machine: {reason}", pytrace=False)
        made.append(box)
        return box

    try:
        yield make
    finally:
        for box in made:
            box.close()


@pytest.fixture()
def box(boxes):
    """A box with the stand-in reranker environment and no GPU."""
    return boxes()
