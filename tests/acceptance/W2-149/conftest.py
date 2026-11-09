"""Fixtures for the W2-149 acceptance tests: one planted repository per session, one planted world per case.

The repository is only read by the script (``git show``, ``git archive``, ``git diff``, ``git ls-tree``), so the cases
share it. Each case gets its own HOME (with its runs and trees folders), its own sets root, a stub ``claude`` first on
``PATH`` (a tripwire that fails any session a case did not expect) and its own records. Live cases (marked ``live``) run
only with ``GOV_W2_149_LIVE=1`` (the CTO, outside the sandbox).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_149_support as support  # noqa: E402

LIVE = os.environ.get("GOV_W2_149_LIVE") == "1"


def pytest_configure(config):
    config.addinivalue_line("markers", "live: a real claude session (the CTO, outside the sandbox; GOV_W2_149_LIVE=1)")


def pytest_collection_modifyitems(config, items):
    skip = pytest.mark.skip(reason="live: run by the CTO outside the sandbox with GOV_W2_149_LIVE=1")
    here = str(Path(__file__).resolve().parent)
    for item in items:
        if item.get_closest_marker("live") and str(item.path).startswith(here) and not LIVE:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def planted_repo(tmp_path_factory):
    return support.build_repo(tmp_path_factory.mktemp("w2-149-repo") / "repo")


@pytest.fixture()
def world(tmp_path, tmp_path_factory, planted_repo):
    w = support.World(tmp_path / "w", planted_repo, base=tmp_path_factory.getbasetemp())
    w.plant()
    yield w
    support.make_writable(tmp_path)
