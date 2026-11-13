"""W2-20 S18: the product's own pools are as wide as the CPUs the process may use, never the machine's count."""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

import gov.codeintel as codeintel  # noqa: E402
import gov.secrets as secrets  # noqa: E402


def test_the_pool_follows_the_cpu_set_not_the_machine(monkeypatch):
    monkeypatch.delenv("GOV_HEAVY_THREAD_BUDGET", raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: {3, 4})
    monkeypatch.setattr(os, "cpu_count", lambda: 64)
    assert secrets.pool_size() == 2


def test_the_pool_stays_within_the_slots_thread_budget(monkeypatch):
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(8)))
    monkeypatch.setenv("GOV_HEAVY_THREAD_BUDGET", "3")
    assert secrets.pool_size() == 3
    monkeypatch.setenv("GOV_HEAVY_THREAD_BUDGET", "lots")
    assert secrets.pool_size() == 8


def test_the_code_index_sizes_its_pool_to_the_cpu_set(monkeypatch, tmp_path):
    widths = []

    class Pool:
        def __init__(self, max_workers=None):
            widths.append(max_workers)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def map(self, function, items):
            return [function(item) for item in items]

    monkeypatch.setattr(codeintel, "ThreadPoolExecutor", Pool)
    monkeypatch.setattr(codeintel, "pool_size", lambda: 2)
    monkeypatch.setattr(codeintel, "_checked", lambda root: tmp_path)
    monkeypatch.setattr(codeintel, "indexable", lambda root, rels: [])
    monkeypatch.setattr(codeintel, "_tool", lambda *a, **k: None)
    monkeypatch.setattr(codeintel.subprocess, "run", lambda *a, **k: type("R", (), {"stdout": ""})())
    codeintel.index(tmp_path)
    assert widths == [2]
