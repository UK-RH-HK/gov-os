"""Unit tests for the launch's enforcement of the gate (W2-20 S19, P-1, P-2, P-6, S10) and W2-136's F2 line (S21).

Planted machines (the ``planted`` fixture), a recording session stand-in, a stand-in ``nvidia-smi``; no real CLI."""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path

import pytest
import yaml

from gov.cli.errors import GovError
from gov.launch import launcher, plan_check

GIB = 1024 ** 3


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

        def wait(self):
            seen.append(json.loads((planted.dir / "sessions" / "777001.json").read_text()))
            return 0

        def poll(self):
            return 0

    import types
    monkeypatch.setattr(launcher, "subprocess", types.SimpleNamespace(Popen=Session))  # the launcher's alone
    return started, seen


def _plant_templates(root: Path) -> None:
    """Every role's template copy a session starts with (W2-153 S1, DEC-1112 (3)), so the gate's refusal is the one
    tested: any content will do."""
    for stem in set(launcher.ROLE_TEMPLATES.values()):
        path = root / launcher.TEMPLATES_REL / f"{stem}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {stem}\n")


def _project(planted) -> Path:
    project = planted.root / "project"
    project.mkdir(exist_ok=True)
    _plant_templates(project)
    return project


ROLES = ["engineer", "orchestrator"]


@pytest.mark.parametrize("role", ROLES)
def test_an_open_gate_starts_the_session_and_registers_it_while_it_runs(planted, sessions, role):
    started, seen = sessions
    planted.config()
    assert launcher.launch(_project(planted), role, "T-1", []) == 0
    assert len(started) == 1
    entry = seen[-1]
    assert entry["pid"] == 777001 and entry["ticket"] == "T-1" and entry["role"] == role
    assert not (planted.dir / "sessions" / "777001.json").exists()  # removed when it ended


SHUT = {
    "load": (lambda m: m.loads(30.0, 30.0), "load: reading 30.0, limit 20"),
    "cpu": (lambda m: m.busy(20.0), "cpu: reading 21.0, limit 20"),
    "memory": (lambda m: m.memory(available=GIB), "memory: reading 1073741824, limit "),
    "disk": (lambda m: m.disk(GIB, 50_000_000), "disk: reading 1073741824, limit 107374182400"),
    "inodes": (lambda m: m.disk(500 * GIB, 7), "inodes: reading 7, limit 10000000"),
    "config": (lambda m: m.config(rebuild_peak_bytes=None), "rebuild_peak_bytes"),
}


@pytest.mark.parametrize("role", ROLES)
@pytest.mark.parametrize("condition", sorted(SHUT))
def test_each_reading_shut_refuses_the_launch_naming_it_and_starts_nothing(planted, sessions, role, condition):
    started, _ = sessions
    planted.config()
    plant, named = SHUT[condition]
    plant(planted)
    with pytest.raises(GovError) as refused:
        launcher.launch(_project(planted), role, "T-1", [])
    assert refused.value.code == "LAUNCH_REFUSED"
    assert refused.value.message.startswith("the resource gate is shut: ") and named in refused.value.message
    assert started == []


@pytest.mark.parametrize("role", ROLES)
def test_an_override_starts_it_anyway_with_one_line_in_the_launch_log_and_on_stderr(planted, sessions, role, capfd):
    started, _ = sessions
    planted.config()
    planted.memory(available=GIB)
    assert launcher.launch(_project(planted), role, "T-1", [], gate_override="DEC-1088") == 0
    assert len(started) == 1
    [line] = (planted.dir / "launch.log").read_text().splitlines()
    assert f"OVERRIDE gate_override: DEC-1088: {role} T-1 started with the resource gate shut: memory: reading " \
           "1073741824" in line
    err = capfd.readouterr().err
    assert [x for x in err.splitlines() if "OVERRIDE" in x] == [line.split(" ", 1)[1]]  # the same line, less its time


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


def test_a_full_set_of_slots_never_refuses_a_session(planted, sessions):
    planted.config()
    folder = planted.dir / "slots"
    folder.mkdir(parents=True, exist_ok=True)
    held = []
    for slot in (1, 2, 3):
        fd = os.open(folder / f"slot-{slot}.lock", os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX)
        (folder / f"slot-{slot}.json").write_text(json.dumps({"slot": slot, "pid": os.getpid(), "kind": "test"}))
        held.append(fd)
    try:
        from gov.resources.gate import read
        assert len(read(True)["slots"]["held"]) == 3
        assert launcher.launch(_project(planted), "engineer", "T-1", []) == 0
    finally:
        for fd in held:
            os.close(fd)


@pytest.mark.parametrize("value", [None, 0])
def test_the_slots_refuse_a_launch_only_when_their_reading_cannot_be_taken(planted, sessions, value):
    planted.config(heavy_slots=value)
    with pytest.raises(GovError) as refused:
        launcher.launch(_project(planted), "engineer", "T-1", [])
    assert "heavy_slots" in refused.value.message


# --- the GPU (S10, P-6) ---------------------------------------------------------------------------------------------

def test_a_start_with_no_declared_need_never_reads_the_gpu(planted, sessions):
    planted.config()
    calls = planted.smi()
    assert launcher.launch(_project(planted), "engineer", "T-1", []) == 0
    assert calls() == []


def test_a_start_with_a_need_opens_only_with_the_need_plus_the_margin_free(planted, sessions):
    planted.config(gpu_shares={"value": {"embedder_mib": 0, "reranker_mib": 0}, "date": "2026-11-09", "source": "t"})
    calls = planted.smi(gpu="8000, 7000, 1000, 10")  # 1000 MiB free
    with pytest.raises(GovError) as refused:
        launcher.launch(_project(planted), "engineer", "T-1", [], gpu_need_mib=910)  # 1001 > 1000
    assert "gpu: reading 1000, limit 1001" in refused.value.message
    assert launcher.launch(_project(planted), "engineer", "T-1", [], gpu_need_mib=909) == 0  # 999.9 <= 1000
    assert len([c for c in calls() if any(a.startswith("--query-gpu") for a in c)]) == 2  # once per check


def test_no_nvidia_smi_shuts_a_start_that_declares_a_need(planted, sessions):
    planted.config()
    with pytest.raises(GovError) as refused:
        launcher.launch(_project(planted), "engineer", "T-1", [], gpu_need_mib=100)
    assert "gpu: reading null" in refused.value.message and "nvidia-smi" in refused.value.message


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
    _plant_templates(lead)
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
    assert "plan_override" in line and "DEC-899" in line and "T-3" in line
    err = [x for x in capfd.readouterr().err.splitlines() if "OVERRIDE" in x]
    assert err == ["gov launch: OVERRIDE DEC-899: plan_override DEC-899 admits ticket T-3 despite: "
                   + err[0].split(" despite: ", 1)[1]]


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
