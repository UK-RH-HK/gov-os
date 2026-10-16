"""Fixtures for the W1-42 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_42_support as support  # noqa: E402


class _Reader:
    """The support readers, with a missing file, section, table or value reported as a plain failure."""

    def __getattr__(self, name):
        target = getattr(support, name)
        if not callable(target) or isinstance(target, type):
            return target

        def call(*args, **kwargs):
            try:
                return target(*args, **kwargs)
            except support.Missing as exc:
                reason = str(exc)
            pytest.fail(reason, pytrace=False)

        return call


@pytest.fixture(scope="session")
def read():
    return _Reader()


@pytest.fixture(scope="session")
def report(read):
    """The text of ``docs/plan/wave-1-exit/EXIT-REPORT.md``."""
    return read.load_report()
