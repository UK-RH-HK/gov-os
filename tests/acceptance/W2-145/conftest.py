"""Fixtures for the W2-145 acceptance tests: one box (a planted ``HOME``) per case, nothing left running."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_145_support as support  # noqa: E402


def pytest_report_header(config):
    refused = support.unix_sockets_refused()
    return [f"W2-145: {refused}"] if refused else []


@pytest.fixture()
def boxes():
    """Make boxes with ``boxes(environment=..., gpu=..., settings=..., slots=...)``; every process that carries a
    box's ``HOME`` is ended, and its folder removed, when the case ends, however it ends."""
    made = []

    def make(**kwargs):
        try:
            box = support.Box(**kwargs)
        except support.base.Missing as reason:  # a case that cannot run is red, never skipped as if it passed
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
    return boxes()


@pytest.fixture(scope="session")
def project():
    """``(tools, root)``: a small project with its lexical index and record store, never written by a retrieval.
    It needs ``gitleaks`` (the lexical index's secret filter), as W2-112's bundle cases do."""
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH on this machine; the lexical index's secret filter cannot run")
    try:
        base_dir = support.base.short_base()
    except support.base.Missing as reason:
        pytest.fail(f"the case cannot run on this machine: {reason}", pytrace=False)
    try:
        yield support.build_project(base_dir)
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
