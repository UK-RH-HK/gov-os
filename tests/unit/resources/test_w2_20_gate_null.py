"""G-NULL-1 (DAEO-r30l fix): the resource gate shut on ``cpu: reading null`` when an embedding server's process-tree
CPU sum fell between samples (its model-runner child exited). A fall is a reset, not an unreadable reading; a pid in
no process table is still unreadable and still shuts the gate. Planted machines; no real server."""
from __future__ import annotations

import json
import time

from gov.resources import gate, machine


def reasons(reading: dict) -> dict:
    return {r["condition"]: r for r in reading["gate"]["reasons"]}


def _two_servers(planted, monkeypatch, shared_pid=900, query_pid=910):
    planted.config()
    monkeypatch.delenv("GOV_RESOURCES_EMBEDDING_CPU")
    monkeypatch.delenv("GOV_RESOURCES_EMBEDDING_CPU_NOW")
    planted.process(900, ticks=machine.TICKS * 5, cmdline="ollama serve")
    planted.process(910, ticks=machine.TICKS * 5, cmdline="ollama serve")
    ports = {11434: shared_pid, 11435: query_pid}
    monkeypatch.setattr(machine, "listener", lambda port, table=None: ports.get(port))
    return planted.dir / machine.SERVER_HISTORY


def _history(path, per_server, age_s=30):
    """Lines 30 s and older (inside KEEP_S) of each (server, pid) at its given cpu_seconds."""
    now = time.time()
    path.write_text("".join(
        json.dumps({"time": now - age_s - 30 * k, "server": server, "pid": pid, "cpu_seconds": cpu}) + "\n"
        for k in range(5) for server, pid, cpu in per_server))


def _numbers(now):
    assert isinstance(now, dict) and now
    for value in now.values():
        assert isinstance(value, float) and value >= 0


def test_g_null_1_both_trees_fell_is_a_reset_not_a_null(planted, monkeypatch):
    path = _two_servers(planted, monkeypatch)
    _history(path, (("shared", 900, 50.0), ("query", 910, 50.0)))
    reading = gate.read(True)
    _numbers(reading["embedding_cpu_now"])
    assert "cpu" not in reasons(reading) and reading["gate"]["open"]


def test_g_null_1_one_tree_fell_the_other_steady(planted, monkeypatch):
    path = _two_servers(planted, monkeypatch)
    _history(path, (("shared", 900, 50.0), ("query", 910, 5.0)))
    reading = gate.read(True)
    _numbers(reading["embedding_cpu_now"])
    assert "cpu" not in reasons(reading) and reading["gate"]["open"]


def test_g_null_1_an_unreadable_pid_still_shuts_on_cpu(planted, monkeypatch):
    path = _two_servers(planted, monkeypatch, shared_pid=999)  # 999 is in no process table
    _history(path, (("shared", 999, 50.0), ("query", 910, 50.0)))
    reading = gate.read(True)
    assert reading["embedding_cpu_now"] is None and reasons(reading)["cpu"]["reading"] is None
