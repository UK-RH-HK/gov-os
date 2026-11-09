"""S9: enforcement at launch (DEC-1088 (5)(a)). gov launch refuses a lead (GOV_ROLE orchestrator with a GOV_TICKET)
for a ticket not in the approved ready list's batches, or whose waits (depends_on, needs, waits_on) are not met when
checked at launch time against the current tickets; the refusal names what it waits for and starts no session; a
plan_override with its decision id lets it start, written in the launch log. The check is one function in
src/gov/launch/plan_check.py that the launcher calls at its argument checks.

The function is ``check_lead(root, ticket_id, *, ready=<path>)`` (README, "The interface"); its answer reads
``admitted``, ``reason`` and ``override`` (as keys or attributes). No session is ever started: the launcher's own
cases replace ``subprocess.Popen`` and the check itself, as the launcher's unit tests do."""

from __future__ import annotations

import datetime
import importlib
import json
import os
import sys
import types

import pytest

import w2_136_support as support
from w2_136_support import T

A = T("PLN-k001", "W2-901", status="in_progress", priority=1, writes=("src/ka/core.py",))
B = T("PLN-k002", "W2-902", status="in_progress", writes=("src/kb/**",), depends_on=("PLN-k001",))
C = T("PLN-k003", "W2-903", status="in_progress", writes=("src/kc/**",), needs=("src/ka/core.py",))
E = T("PLN-k005", "W2-905", status="in_progress", writes=("src/ke/**",), waits_on=("PLN-k001",))
F = T("PLN-k006", "W2-906", status="in_progress", writes=("src/kf/**",))
X = T("PLN-k007", "W2-907", status="in_progress", writes=("src/kx/**",), depends_on=("PLN-k001",),
      plan_override="DEC-899")
STORE = (A, B, C, E, F, X)
APPROVED = [[A], [B, C, E, X]]  # F is in no batch


def _get(answer, key):
    return answer.get(key) if isinstance(answer, dict) else getattr(answer, key, None)


@pytest.fixture
def check(planted, tmp_path):
    """``check(ticket_id, approved=APPROVED, store=None)``: the real check on a planted store and ready list."""
    made = {}

    def _check(tid, approved=APPROVED, store=None):
        plan_check = importlib.import_module("gov.launch.plan_check")  # in the test's call: a failure, not an error
        store = store or made.setdefault("store", planted(STORE, ("src/ka/core.py",)))
        ready = tmp_path / "ready.txt"
        ready.write_text(support.ready_text(approved), encoding="utf-8")
        return plan_check.check_lead(store.root, tid, ready=ready), store

    return _check


def test_s9_a_lead_not_in_the_approved_batches_is_refused_naming_it(check):
    answer, store = check("PLN-k006")
    assert _get(answer, "admitted") is False, answer
    reason = _get(answer, "reason") or ""
    assert store.mentions(reason, "PLN-k006"), answer


def test_s9_a_lead_in_a_batch_with_no_waits_is_admitted(check):
    answer, _ = check("PLN-k001")
    assert _get(answer, "admitted") is True and not _get(answer, "override"), answer


@pytest.mark.parametrize("tid, path", [("PLN-k002", None), ("PLN-k003", "src/ka/core.py"), ("PLN-k005", None)],
                         ids=["depends_on", "needs", "waits_on"])
def test_s9_a_wait_unmet_at_launch_time_is_refused_naming_what_it_waits_for(check, tid, path):
    answer, store = check(tid)
    assert _get(answer, "admitted") is False, answer
    reason = _get(answer, "reason") or ""
    assert store.mentions(reason, "PLN-k001"), answer  # the ticket it waits for
    if path:
        assert path in reason, answer                  # and the path


@pytest.mark.parametrize("tid", ["PLN-k002", "PLN-k003", "PLN-k005"], ids=["depends_on", "needs", "waits_on"])
def test_s9_a_wait_met_at_launch_time_is_admitted(check, planted, tid):
    store = planted((A.but(status="closed"), *STORE[1:]), ("src/ka/core.py",), name="met")
    answer, _ = check(tid, store=store)
    assert _get(answer, "admitted") is True, answer


def test_s9_the_waits_are_read_from_the_current_tickets_not_the_list(check):
    """The list was approved when PLN-k002 had no dependency and put it in batch 1; it has one now."""
    answer, store = check("PLN-k002", approved=[[A, B, C, E, X]])
    assert _get(answer, "admitted") is False, answer
    assert store.mentions(_get(answer, "reason") or "", "PLN-k001"), answer


def test_s9_a_plan_override_admits_the_lead_with_its_decision_id(check):
    answer, _ = check("PLN-k007")
    assert _get(answer, "admitted") is True, answer
    assert "DEC-899" in str(_get(answer, "override") or ""), answer


# --- the launcher's path, with the check and the session replaced ------------------------------------------------------

GIB = 1024 ** 3


def _plant_open_gate(home, base, monkeypatch):
    """An open resource gate for the launcher's cases (W2-20 S19 runs it on every launch; S8 shuts it when the
    configuration is missing). W2-20's README, "The configuration file": every value dated and sourced, in
    ``$HOME/.gov-os/machine/gate.json``; the readings planted through ``GOV_RESOURCES_*`` with room to spare, so
    these cases test the plan check alone, whatever the machine is doing. Code with no gate reads none of it."""
    def dated(value, source="planted for the W2-136 launcher cases (W2-20 README)"):
        return {"value": value, "date": datetime.date.today().isoformat(), "source": source}

    base.mkdir()
    cpu = str(max(os.sched_getaffinity(0)))
    values = {
        "memory_floor_bytes": dated(3 * GIB, "DEC-942 item 2 (planted)"),
        "verification_peak_bytes": dated(4 * GIB),
        "working_size_bytes": dated(1 * GIB),
        "rebuild_peak_bytes": dated(2 * GIB),
        "disk_floor_bytes": dated(100 * GIB, "DEC-898 item 1 (planted)"),
        "inode_floor": dated(10_000_000, "DEC-898 item 1 (planted)"),
        "verification_lock": dated(str(base / "verification.lock")),
        "gpu_margin": dated(0.10, "DEC-950 item 2 (planted)"),
        "oom_floor_bytes": dated(1 * GIB),
        "heavy_slots": dated(2),
        "gpu_shares": dated({"embedder_mib": 0, "reranker_mib": 0}),
        "embedding_servers": {
            "shared": {"cpus": cpu, "nice": 10, "date": datetime.date.today().isoformat(), "source": "planted"},
            "query": {"cpus": cpu, "nice": 10, "date": datetime.date.today().isoformat(), "source": "planted"},
        },
    }
    machine = home / ".gov-os" / "machine"
    machine.mkdir(parents=True)
    (machine / "gate.json").write_text(json.dumps(values, indent=1), encoding="utf-8")
    readings = {
        "GOV_RESOURCES_MEMINFO": ("meminfo", f"MemTotal: {80 * GIB // 1024} kB\nMemAvailable: {64 * GIB // 1024} kB\n"),
        "GOV_RESOURCES_LOADAVG": ("loadavg", "0.00 0.00 0.00 1/321 54321\n"),
        "GOV_RESOURCES_BUSY_CORES": ("busy", "0\n"),
        "GOV_RESOURCES_EMBEDDING_CPU": ("embedding-cpu.json", json.dumps({"shared": 0, "query": 0})),
        "GOV_RESOURCES_DISK": ("disk.json", json.dumps({"free_bytes": 1024 * GIB, "free_inodes": 100_000_000})),
    }
    for variable, (name, text) in readings.items():
        (base / name).write_text(text, encoding="utf-8")
        monkeypatch.setenv(variable, str(base / name))
    monkeypatch.setenv("GOV_RESOURCES_NPROC", "64")


@pytest.fixture
def launcher_with(planted, tmp_path, monkeypatch):
    """``launcher_with(answer)``: (launch, calls, started) with the plan check answering ``answer``."""
    from gov.launch import launcher
    import gov.launch as package

    home, temp = tmp_path / "home", tmp_path / "temp"
    (home / ".local" / "bin").mkdir(parents=True)
    temp.mkdir()
    (home / launcher.CLI_REL).write_text("", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    _plant_open_gate(home, tmp_path / "gate-readings", monkeypatch)
    monkeypatch.setattr(launcher.tempfile, "tempdir", str(temp))
    # the repository's settings are not what these cases are about (the check comes at the argument checks)
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
    store = planted(STORE, ("src/ka/core.py",))

    def _with(answer):
        calls, started = [], []

        def check_lead(*args, **kwargs):
            calls.append((args, kwargs))
            return answer

        stub = types.ModuleType("gov.launch.plan_check")
        stub.check_lead = check_lead
        monkeypatch.setitem(sys.modules, "gov.launch.plan_check", stub)
        monkeypatch.setattr(package, "plan_check", stub, raising=False)
        for name, value in (("plan_check", stub), ("check_lead", check_lead)):
            if hasattr(launcher, name):
                monkeypatch.setattr(launcher, name, value)

        class Session:  # in place of subprocess.Popen: no session is started
            def __init__(self, argv, cwd, env):
                started.append(env)
                self.returncode = 0

            def wait(self):
                return 0

            def poll(self):
                return 0

        monkeypatch.setattr(launcher.subprocess, "Popen", Session)
        return (lambda role, tid: launcher.launch(store.root, role, tid, [])), calls, started

    return _with


def test_s9_the_launcher_refuses_a_lead_the_check_refuses_and_starts_no_session(launcher_with):
    from gov.cli.errors import GovError

    reason = "STUB-W2-136: PLN-k002 waits for PLN-k001 (DEPENDS_ON PLN-k001)"
    launch, calls, started = launcher_with({"admitted": False, "reason": reason, "override": None})
    with pytest.raises(GovError) as refused:
        launch("orchestrator", "PLN-k002")
    assert refused.value.code == "LAUNCH_REFUSED" and "STUB-W2-136" in refused.value.message, refused.value.message
    assert calls and any("PLN-k002" in map(str, args) or "PLN-k002" in map(str, kw.values()) for args, kw in calls)
    assert started == []


def test_s9_the_launcher_starts_a_lead_the_check_admits(launcher_with):
    launch, calls, started = launcher_with({"admitted": True, "reason": "", "override": None})
    assert launch("orchestrator", "PLN-k001") == 0
    assert calls and len(started) == 1


def test_s9_the_launcher_writes_an_override_in_the_launch_log(launcher_with, capfd):
    launch, calls, started = launcher_with({"admitted": True, "reason": "plan_override DEC-899",
                                            "override": "DEC-899"})
    assert launch("orchestrator", "PLN-k007") == 0
    assert calls and len(started) == 1
    log = capfd.readouterr().err
    assert any("OVERRIDE" in line and "DEC-899" in line for line in log.splitlines()), log


def test_s9_guard_a_worker_launch_never_consults_the_plan(launcher_with):
    """S9 is about leads; any session's gate is W2-20's (DEC-1088 (5)(b)). A worker of a ticket starts as before."""
    launch, calls, started = launcher_with({"admitted": False, "reason": "STUB-W2-136 refused", "override": None})
    assert launch("engineer", "PLN-k006") == 0
    assert calls == [] and len(started) == 1
