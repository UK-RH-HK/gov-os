"""Unit tests for the launch's enforcement of the gate (W2-20 S19, P-1, P-2, P-6, S10) and W2-136's F2 line (S21).

Planted machines (the ``planted`` fixture), a recording session stand-in, a stand-in ``nvidia-smi``; no real CLI."""
from __future__ import annotations

import fcntl
import json
import os
import sys
from pathlib import Path

import pytest
import yaml

from gov.cli.errors import GovError
from gov.launch import gate as launch_gate
from gov.launch import launcher, plan_check

GIB = 1024 ** 3
SMI = """#!{python}
import json, os, sys
with open(os.environ["SMI_LOG"], "a") as log:
    log.write(json.dumps(sys.argv[1:]) + "\\n")
if any(a.startswith("--query-gpu") for a in sys.argv):
    print(os.environ.get("SMI_GPU", "0, 1000, 8000, 5"))
elif any(a.startswith("--query-compute-apps") for a in sys.argv):
    print(os.environ.get("SMI_APPS", ""))
"""


@pytest.fixture
def sessions(planted, monkeypatch):
    """The worker and lead paths reach the gate with their other checks passed; Popen records each session."""
    (planted.home / ".local" / "bin").mkdir(parents=True)
    (planted.home / launcher.CLI_REL).write_text("")
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *a: None)
    monkeypatch.setattr(launcher, "_check_ticket", lambda *a: None)
    monkeypatch.setattr(launcher, "build_settings", lambda root, role, ticket: {
        "env": {"GOV_ROLE": role, "GOV_TICKET": ticket}, "permissions": {"deny": []},
        "sandbox": {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
                    "network": {"strictAllowlist": True, "allowedDomains": []}}})
    monkeypatch.setattr(launcher.runs, "folder", lambda *a: None)
    monkeypatch.setattr(launcher.runs, "own_folder", lambda *a: None)
    monkeypatch.setattr(launcher, "check_lead", lambda root, ticket: plan_check.LeadCheck(True, "admitted"))
    started, seen = [], []

    class Session:
        pid = 777001

        def __init__(self, argv, cwd, env):
            started.append(argv)
            seen.append(sorted(p.name for p in (planted.dir / "sessions").glob("*.json"))
                        if (planted.dir / "sessions").exists() else [])

        def wait(self):
            seen.append(json.loads((planted.dir / "sessions" / "777001.json").read_text()))
            return 0

        def poll(self):
            return 0

    import types
    monkeypatch.setattr(launcher, "subprocess", types.SimpleNamespace(Popen=Session))  # the launcher's alone
    return started, seen


def _project(planted) -> Path:
    project = planted.root / "project"
    project.mkdir(exist_ok=True)
    return project


ROLES = ["engineer", "orchestrator"]


@pytest.mark.parametrize("role", ROLES)
def test_an_open_gate_starts_the_session_and_registers_it_while_it_runs(planted, sessions, role):
    started, seen = sessions
    planted.config()
    assert launcher.launch(_project(planted), role, "T-1", []) == 0
    assert len(started) == 1
    entry = seen[-1]
    assert entry["pid"] == 777001 and entry["ticket"] == "T-1"
    assert entry["role"] == ("orchestrator" if role == "orchestrator" else "engineer")
    assert not (planted.dir / "sessions" / "777001.json").exists()  # removed when it ended


SHUT = {
    "load": lambda m: m.loads(30.0, 30.0, 30.0),
    "cpu": lambda m: m.busy(20.0),
    "memory": lambda m: m.memory(available=GIB),
    "disk": lambda m: m.config(disk_floor_bytes=10 ** 18),
    "inodes": lambda m: m.config(inode_floor=10 ** 15),
    "config": lambda m: m.config(rebuild_peak_bytes=None),
}


@pytest.mark.parametrize("role", ROLES)
@pytest.mark.parametrize("condition", sorted(SHUT))
def test_each_reading_shut_refuses_the_launch_naming_it_and_starts_nothing(planted, sessions, role, condition):
    started, _ = sessions
    planted.config()
    SHUT[condition](planted)
    with pytest.raises(GovError) as refused:
        launcher.launch(_project(planted), role, "T-1", [])
    assert refused.value.code == launch_gate.GATE_SHUT and refused.value.exit_code == launch_gate.EXIT_GATE_SHUT
    assert "gov launch refuses" in refused.value.message and condition in refused.value.message
    assert started == []


@pytest.mark.parametrize("role", ROLES)
def test_an_override_starts_it_anyway_with_one_line_in_the_launch_log_and_on_stderr(planted, sessions, role, capfd):
    started, _ = sessions
    planted.config()
    planted.memory(available=GIB)
    assert launcher.launch(_project(planted), role, "T-1", [], gate_override="DEC-1088") == 0
    assert len(started) == 1
    [line] = (planted.dir / "launch.log").read_text().splitlines()
    assert "OVERRIDE gate DEC-1088" in line and "memory" in line
    err = capfd.readouterr().err
    assert line.split(" ", 1)[1] in err  # the same line, less its time


def test_an_override_on_an_open_gate_is_not_logged(planted, sessions):
    planted.config()
    assert launcher.launch(_project(planted), "engineer", "T-1", [], gate_override="DEC-1088") == 0
    assert not (planted.dir / "launch.log").exists()


@pytest.mark.parametrize("value", ["1088", "DEC-", "dec-12", "DEC-12; rm"])
def test_an_override_that_names_no_decision_is_refused(planted, sessions, value):
    planted.config()
    with pytest.raises(GovError) as refused:
        launcher.launch(_project(planted), "engineer", "T-1", [], gate_override=value)
    assert refused.value.code == "LAUNCH_REFUSED" and sessions[0] == []


def test_an_override_whose_log_cannot_be_written_refuses(planted, sessions):
    planted.config()
    planted.memory(available=GIB)
    (planted.dir / "launch.log").mkdir()
    with pytest.raises(GovError) as refused:
        launcher.launch(_project(planted), "engineer", "T-1", [], gate_override="DEC-1088")
    assert "never left unrecorded" in refused.value.message and sessions[0] == []


def _hold_every_slot(planted, count=3):
    folder = planted.dir / "slots"
    folder.mkdir(parents=True, exist_ok=True)
    held = []
    for slot in range(1, count + 1):
        fd = os.open(folder / f"slot-{slot}.lock", os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX)
        (folder / f"slot-{slot}.json").write_text(json.dumps({"slot": slot, "pid": 10 + slot, "kind": "test"}))
        held.append(fd)
    return held


def test_a_full_set_of_slots_never_refuses_a_session(planted, sessions):
    planted.config()
    held = _hold_every_slot(planted)
    try:
        from gov.resources.gate import read
        assert read("session")["slots"]["full"]
        assert launcher.launch(_project(planted), "engineer", "T-1", []) == 0
    finally:
        for fd in held:
            os.close(fd)


def test_an_unreadable_slot_refuses_the_launch_naming_the_slots(planted, sessions):
    planted.config()
    (planted.dir / "slots").mkdir(parents=True)
    (planted.dir / "slots" / "slot-1.json").write_text("{broken")
    with pytest.raises(GovError) as refused:
        launcher.launch(_project(planted), "engineer", "T-1", [])
    assert "slots" in refused.value.message


# --- the GPU (S10, P-6) ---------------------------------------------------------------------------------------------

@pytest.fixture
def smi(planted, monkeypatch):
    program = planted.root / "nvidia-smi"
    program.write_text(SMI.format(python=sys.executable))
    program.chmod(0o755)
    log = planted.root / "smi.log"
    monkeypatch.setenv("GOV_RESOURCES_NVIDIA_SMI", str(program))
    monkeypatch.setenv("SMI_LOG", str(log))
    return lambda: [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


def test_a_start_with_no_declared_need_never_reads_the_gpu(planted, sessions, smi):
    planted.config()
    assert launcher.launch(_project(planted), "engineer", "T-1", []) == 0
    assert smi() == []


def test_a_start_with_a_need_opens_only_with_the_need_plus_the_margin_free(planted, sessions, smi, monkeypatch):
    planted.config(gpu_shares=[{"kind": "headroom", "bytes": 0}])
    monkeypatch.setenv("SMI_GPU", "0, 7000, 8000, 10")  # 1000 MiB free
    with pytest.raises(GovError) as refused:
        launcher.launch(_project(planted), "engineer", "T-1", [], gpu_need_mib=910)  # 910 * 1.1 = 1001 > 1000
    assert "gpu" in refused.value.message
    assert launcher.launch(_project(planted), "engineer", "T-1", [], gpu_need_mib=909) == 0  # 999.9 <= 1000
    assert len([call for call in smi() if call[0].startswith("--query-gpu")]) == 2  # once per check


def test_no_nvidia_smi_shuts_a_start_that_declares_a_need(planted, sessions, monkeypatch):
    planted.config()
    monkeypatch.setenv("GOV_RESOURCES_NVIDIA_SMI", str(planted.root / "absent"))
    with pytest.raises(GovError) as refused:
        launcher.launch(_project(planted), "engineer", "T-1", [], gpu_need_mib=100)
    assert "no nvidia-smi" in refused.value.message


def test_a_job_that_would_push_the_embedder_off_waits_and_the_room_is_stated(planted, smi, monkeypatch):
    from gov.resources.gate import read
    planted.config(gpu_shares=[{"kind": "embedder", "bytes": 3000 * 1024 ** 2},
                               {"kind": "reranker", "bytes": 2000 * 1024 ** 2},
                               {"kind": "headroom", "bytes": 500 * 1024 ** 2}])
    monkeypatch.setenv("SMI_GPU", "0, 1000, 8000, 20")  # 7000 MiB free; the embedder not loaded yet
    other = read("session", gpu_need_bytes=2000 * 1024 ** 2, gpu_kind="other")
    gpu = [r for r in other["gate"]["reasons"] if r["condition"] == "gpu"]
    assert gpu and "the GPU room it saw" in gpu[0]["why"] and "runs its model on the CPU" in gpu[0]["why"]
    assert other["gpu"]["room"]["reserved_bytes"] == 5500 * 1024 ** 2
    embedder = read("session", gpu_need_bytes=2000 * 1024 ** 2, gpu_kind="embedder")
    assert not [r for r in embedder["gate"]["reasons"] if r["condition"] == "gpu"]


def test_the_reading_measures_the_gpu_and_its_holders_once(planted, smi, monkeypatch):
    from gov.resources.gate import read
    planted.config()
    planted.process(5001, cmdline="ollama runner --model x")
    planted.process(5002, cmdline="python rerank_service.py")
    monkeypatch.setenv("SMI_APPS", "5001, 3000\n5002, 2000\n6000, 100")
    gpu = read(None)["gpu"]
    assert gpu["read"] and gpu["gpus"][0]["used_bytes"] == 1000 * 1024 ** 2 and gpu["gpus"][0]["utilization"] == 5.0
    assert [h["kind"] for h in gpu["holders"]] == ["embedder", "reranker", "other"]
    assert len([call for call in smi() if call[0].startswith("--query-gpu")]) == 1


def test_a_machine_with_no_gpu_is_named_in_the_reading_never_an_error(planted, monkeypatch):
    from gov.resources.gate import read
    planted.config()
    reading = read(None)
    assert reading["gpu"] == {"read": False, "why": "no nvidia-smi on this machine"} and reading["gate"]["open"]


# --- S21: the plan check reads the main tree ------------------------------------------------------------------------

def _tickets(root: Path, *fronts: dict) -> None:
    folder = root / ".tickets"
    folder.mkdir(parents=True, exist_ok=True)
    for front in fronts:
        base = {"status": "in_progress", "priority": 1, "role": "engineer", "allowed_paths": [], "depends_on": [],
                "deps": [], "needs": []}
        base.update(front)
        (folder / f"{base['id']}.md").write_text("---\n" + yaml.safe_dump(base) + "---\n")


@pytest.fixture
def trees(tmp_path, monkeypatch):
    """A main tree and a lead worktree of it (git's own files planted), whose tickets and ready lists differ."""
    main, lead = tmp_path / "main", tmp_path / "lead"
    gitdir = main / ".git" / "worktrees" / "lead"
    gitdir.mkdir(parents=True)
    (gitdir / "commondir").write_text("../..\n")
    lead.mkdir()
    (lead / ".git").write_text(f"gitdir: {gitdir}\n")
    # Main: T-2 waits on T-1 (open) and only T-1 is approved. The worktree's stale copy: T-1 closed, T-2 approved.
    _tickets(main, {"id": "T-1", "wbs_id": "W9-1"}, {"id": "T-2", "wbs_id": "W9-2", "depends_on": ["T-1"],
                                                     "deps": ["T-1"]})
    _tickets(lead, {"id": "T-1", "wbs_id": "W9-1", "status": "closed"},
             {"id": "T-2", "wbs_id": "W9-2", "depends_on": ["T-1"], "deps": ["T-1"]})
    for root, lines in ((main, "W9-1 T-1 a b\n"), (lead, "W9-2 T-2 a b\n")):
        ready = root / plan_check.READY_REL
        ready.parent.mkdir(parents=True)
        ready.write_text(lines)
    monkeypatch.delenv(plan_check.READY_ENV, raising=False)
    return main, lead


def test_the_check_follows_the_main_trees_tickets_and_ready_list_not_the_worktrees(trees):
    main, lead = trees
    verdict = plan_check.check_lead(lead, "T-2")
    assert not verdict.admitted
    assert "not in the approved ready list's batches" in verdict.reason and "waits for T-1" in verdict.reason
    assert str(main / plan_check.READY_REL) in verdict.reason
    assert plan_check.check_lead(lead, "T-1").admitted


def test_a_relative_ready_list_variable_is_read_against_the_main_tree(trees, monkeypatch):
    main, lead = trees
    (main / "dispatch.txt").write_text("W9-1 T-1 a b\nW9-2 T-2 a b\n")
    monkeypatch.setenv(plan_check.READY_ENV, "dispatch.txt")
    assert plan_check.ready_path(lead) == main / "dispatch.txt"


def test_a_plan_override_is_one_line_in_the_launch_log_and_the_line_on_stderr(planted, sessions, trees, monkeypatch,
                                                                                capfd):
    main, lead = trees
    _tickets(main, {"id": "T-3", "wbs_id": "W9-3", "depends_on": ["T-1"], "deps": ["T-1"],
                    "plan_override": "DEC-899"})
    monkeypatch.setattr(launcher, "check_lead", lambda root, ticket: plan_check.check_lead(root, ticket))
    planted.config()
    assert launcher.launch(lead, "orchestrator", "T-3", []) == 0
    [line] = (planted.dir / "launch.log").read_text().splitlines()
    assert "gov launch: OVERRIDE DEC-899: plan_override DEC-899 admits ticket T-3" in line
    assert line.split(" ", 1)[1] in capfd.readouterr().err


def test_gov_launch_takes_both_options(monkeypatch, tmp_path):
    from gov.launch import command
    seen = {}
    monkeypatch.setattr(launcher, "launch", lambda root, role, ticket, args, **kw: seen.update(kw) or 0)
    import argparse
    parser = argparse.ArgumentParser()
    command.add_arguments(parser)
    args = parser.parse_args(["engineer", "T-1", "--gate-override", "DEC-1", "--gpu-need-mib", "512"])
    args.passthrough = None
    assert command.run(tmp_path, args, {}) == 0
    assert seen == {"gate_override": "DEC-1", "gpu_need_mib": 512}
