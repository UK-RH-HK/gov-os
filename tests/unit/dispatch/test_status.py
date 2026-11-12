"""The status files, the configuration errors, the ready list's source and nothing project-specific in the code (S5, S6)."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from conftest import REPO, GIB

SOURCE = REPO / "src" / "gov" / "dispatch"


def test_the_status_holds_every_part_after_a_pass(project):
    project.ticket("W2-1")
    project.ticket("W2-2")
    project.lead_process(4242, "T-other", rss=1 * GIB)
    project.state.mkdir(parents=True, exist_ok=True)
    (project.state / "land.txt").write_text("W2-7=0123456789ab\nW2-8=ba9876543210\n")
    (project.state / "land-done.txt").write_text("W2-8=ba9876543210\n")
    (project.state / "inbox").mkdir()
    (project.state / "inbox" / "x.txt").write_text("log: l\nW2: W2-9\nstatus: DONE\n")
    project.ready(project.entry("W2-1"), project.entry("W2-2"))
    project.tick()
    data = project.status()
    assert data["ok"] is True and data["time"] and data["outcome"] == "started"
    assert data["running"] == [{"ticket": "T-other", "pid": 4242}]
    assert data["load"]["load_1m"] == 1.0 and data["memory"]["available_bytes"] == 20 * GIB
    assert data["memory"]["floor_bytes"] == 3 * GIB and data["memory"]["working_size_bytes"] == 1 * GIB
    assert data["gate"]["open"] is True and "slots" in data and "peaks" in data and "peaks_ahead" in data
    assert data["queue"] == ["W2-7=0123456789ab"]   # land.txt's pending lines only
    assert [i["W2"] for i in data["inbox"]] == ["W2-9"]
    assert data["started"]["W2"] == "W2-1" and [s["W2"] for s in data["skipped"]] == ["W2-2"]
    text = project.status_text()
    assert text.splitlines()[0].startswith("dispatch pass ")
    for word in ("running", "load", "memory", "gate", "slots", "peaks", "queue", "inbox"):
        assert word in text


def test_a_failing_pass_says_so_at_the_top_and_replaces_the_stale_file(project, monkeypatch):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.status()["ok"] is True
    from gov.resources import gate

    def boom(*args, **kwargs):
        raise RuntimeError("the gate reading broke")
    monkeypatch.setattr(gate, "read", boom)
    code, _ = project.tick()
    assert code == 1
    assert project.status_text().splitlines()[0].startswith("PASS FAILED ")
    assert "the gate reading broke" in project.status_text().splitlines()[0]
    data = project.status()
    assert data["ok"] is False and "the gate reading broke" in data["reason"] and "running" not in data


def test_status_prints_the_status_and_says_when_it_is_old(project):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.tick()
    code, out = project.tick("status")
    assert code == 0 and out.splitlines()[0].startswith("dispatch pass ") and "older" not in out
    code, out = project.tick("status", as_json=True)
    assert json.loads(out)["result"]["ok"] is True
    old = time.time() - 600
    for name in ("status.json", "status.txt"):
        os.utime(project.state / name, (old, old))
    data = project.status()
    data["time"] = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(old))
    (project.state / "status.json").write_text(json.dumps(data))
    code, out = project.tick("status")
    assert code == 0 and "older than three minutes" in out


def test_status_without_a_pass_says_so(project):
    code, out = project.tick("status")
    assert code == 0 and "no pass has run" in out


def test_status_is_written_whole_with_no_temporary_left(project):
    project.tick()
    assert sorted(p.name for p in project.state.iterdir() if p.name.startswith(".")) == []


def test_a_missing_configuration_is_exit_2_named(project):
    (project.root / "governance" / "project" / "dispatch.yaml").unlink()
    code, _ = project.tick()
    assert code == 2 and "dispatch.yaml" in project.status_text().splitlines()[0]


def test_a_missing_or_malformed_value_is_exit_2_named(project):
    for key, value in (("max_leads", None), ("integration_branch", None), ("worktrees_root", None),
                       ("stagger_s", "soon"), ("cpu_band", -1), ("max_leads", True), ("launch_command", "gov launch"),
                       ("notifier_command", []), ("nightly_hold", {"from": "25:00", "until": "06:00"}),
                       ("job_markers", ["x"]), ("command_timeout_s", 0)):
        project.write_config(**{key: value})
        code, _ = project.tick()
        assert code == 2, (key, value)
        assert key in project.status_text().splitlines()[0], (key, value)
        project.settings.pop(key, None)
        project.settings.update({"max_leads": 3, "stagger_s": 0, "cpu_band": 1, "integration_branch": "integ",
                                 "worktrees_root": str(project.worktrees), "command_timeout_s": 20})
        project.settings["launch_command"] = [sys.executable, str(project.base / "launch_stub.py"), "{ticket}"]
        project.settings["notifier_command"] = [sys.executable, str(project.base / "notify_stub.py")]
        project.settings.pop("nightly_hold", None)
        project.settings.pop("job_markers", None)
        project.write_config()
    assert project.tick()[0] == 0


def test_a_malformed_yaml_file_is_exit_2(project):
    (project.root / "governance" / "project" / "dispatch.yaml").write_text("dispatch: [unclosed\n")
    assert project.tick()[0] == 2


def test_the_nightly_hold_is_shown_and_never_holds_a_start(project):
    project.write_config(nightly_hold={"from": "00:00", "until": "23:59"}, landing_command=["land", "{W2}"])
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.started() == ["W2-1-log"]
    assert project.status()["nightly_hold"] == {"from": "00:00", "until": "23:59"}


def test_a_ready_list_as_gov_plan_writes_it_starts_only_what_is_on_it(project):
    from gov.plan.render import RUN
    project.ticket("W2-1")
    project.ticket("W2-2")
    (project.state / "briefs").mkdir(parents=True, exist_ok=True)
    (project.state / "briefs" / f"W2-1-A5-{RUN}.md").write_text("go\n")
    project.ready("# batch 1", f"W2-1 T-W2-1 W2-1-A5-{RUN}.md W2-1-A5-{RUN}.json")
    project.tick()
    assert project.started() == [f"W2-1-A5-{RUN}.json"]
    assert project.tick()[0] == 0 and len(project.started()) == 1  # W2-2 is not on the list


def test_nothing_project_specific_in_the_code():
    forbidden = ("w2/integrate", "w2/W2-", "/home/usain", "gov-os-worktrees", "Dynamic-Agentic-Engineering-OS",
                 ".gov-runtime/scratch/orchestrator")
    patterns = [re.compile(r"DAEO-[0-9a-z]{4}"), re.compile(r"\bW2-\d+")]
    found = []
    for path in sorted(SOURCE.glob("*.py")):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if any(word in line for word in forbidden) or any(p.search(line) for p in patterns):
                found.append(f"{path.name}:{number}: {line.strip()}")
    assert found == []
    assert SOURCE.is_dir() and subprocess.run([sys.executable, "-c", "import gov.dispatch"], env={
        **os.environ, "PYTHONPATH": str(REPO / "src")}).returncode == 0
