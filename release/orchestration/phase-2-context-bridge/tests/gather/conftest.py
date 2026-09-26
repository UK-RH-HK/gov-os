"""Shared fixtures for ``tests/gather/`` (REPAIR_DAG.yaml node R1-GA1). ``FakeRouteSet``/``make_hit`` and the
synthetic fixture repo builder live under ``tests/fixtures/gather/`` (imported directly, the same convention
``tests/route/test_task_exclusions.py`` already uses for its own fixture builder) -- this file only holds the
per-test isolation fixture every test here needs (R1-T1: hermetic, no GOVBRIDGE_* leaked from another test, no
process-cwd dependency)."""
from __future__ import annotations

import pytest

from govbridge.core import taskctx as taskctxmod
from govbridge.gather import facets as facetsmod


@pytest.fixture(autouse=True)
def _isolated_gather_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    facetsmod.clear_cache()
    taskctxmod.reset()
    yield
    taskctxmod.reset()
    facetsmod.clear_cache()
