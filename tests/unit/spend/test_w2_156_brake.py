"""W2-156 builder tests: the runaway brake's rule and ``gov spend`` (S1, S2, S4, S5, S6; F1, F2).

Regression evidence only (DEC-136). Every project is planted under ``tmp_path``; the records are the forms of W2-60b's
session record and W2-60a's launch record; ``gov spend`` runs in process through ``gov.cli.main.main``.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from gov.cli.main import main
from gov.spend import brake

T = "DAEO-abcd"


class Project:
    def __init__(self, root: Path):
        self.root = root
        self.n = 0

    def session(self, ticket=T, cost=1.0, started="2026-11-10T10:00:00Z", pid=1, ended="2026-11-10T11:00:00Z"):
        """A session record: ``cost`` a number, or None for not measured."""
        self.n += 1
        sid = f"00000000-0000-4000-8000-{self.n:012d}"
        value = {"value": cost, "source": "result line"} if cost is not None else \
            {"value": None, "not_measured": "no cost line"}
        self.put("sessions", sid, {"record": "gov-session", "format": 1, "session_id": sid, "worktree": str(self.root),
                                   "pid": pid, "started_at": started, "ended_at": ended, "exit_code": 0,
                                   "ticket": {"value": ticket, "source": "launch"},
                                   "role": {"value": "engineer", "source": "launch"}, "cost_usd": value})

    def launch(self, ticket=T, projection=None, started="2026-11-10T09:00:00Z", key=True):
        self.n += 1
        sid = f"11111111-0000-4000-8000-{self.n:012d}"
        data = {"record": "gov-launch", "session_id": sid, "started_at": started, "role": "engineer", "ticket": ticket}
        if key:
            data["projection_usd"] = projection
        self.put("launches", sid, data)

    def put(self, folder, sid, data):
        path = self.root / ".gov-runtime" / folder / f"{sid}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def spend(self, capsys, *argv):
        code = main(["spend", *argv, "--root", str(self.root)])
        out = capsys.readouterr()
        return code, out.out, out.err

    def spend_dir(self) -> Path:
        return self.root / ".gov-runtime" / "spend"

    def marker(self, ticket=T) -> Path:
        return self.spend_dir() / "braked" / f"{ticket}.json"

    def log(self) -> list[dict]:
        path = self.spend_dir() / "brakes.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def inbox(self) -> list[Path]:
        folder = self.root / ".gov-runtime" / "dispatch" / "inbox"
        return sorted(folder.iterdir()) if folder.is_dir() else []


@pytest.fixture
def project(tmp_path):
    return Project(tmp_path / "project")


@pytest.fixture(autouse=True)
def _home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))


def planted(project, factor, projection=2.0):
    project.launch(projection=projection)
    project.session(cost=projection * factor)


# -- S1: the running cost ------------------------------------------------------------------------------------------

def test_s1_sum_totals_the_measured_three_names_one_unknown_never_zero(project, capsys):
    project.launch(projection=3.0)
    for cost in (1.5, 2.0, 2.5, None):
        project.session(cost=cost)
    code, out, _ = project.spend(capsys, "sum")
    assert code == 0
    assert out.splitlines() == [f"{T}: cost 6.00 USD, 1 unknown; projection 3.00 USD; not braked"]


def test_s1_one_line_per_ticket_with_a_counted_record_and_only_those(project, capsys):
    project.session(ticket="DAEO-aaaa", cost=1.0)
    project.session(ticket="DAEO-bbbb", cost=None)
    project.launch(ticket="DAEO-cccc", projection=5.0)  # launched, no session record yet: no line
    _, out, _ = project.spend(capsys, "sum")
    lines = out.splitlines()
    assert [line.split(":")[0] for line in lines] == ["DAEO-aaaa", "DAEO-bbbb"]
    assert "no projection" in lines[0] and "unknown" not in lines[0]
    assert "cost 0.00 USD, 1 unknown" in lines[1]  # unknown counted and named, the sum itself adds nothing


def test_s1_sum_shows_braked_when_the_marker_exists(project, capsys):
    planted(project, 2.5)
    project.spend(capsys, "check")
    _, out, _ = project.spend(capsys, "sum")
    assert out.splitlines() == [f"{T}: cost 5.00 USD; projection 2.00 USD; braked"]


def test_s1_a_record_that_cannot_be_read_is_named_and_skipped_never_counted_as_zero(project, capsys):
    project.session(cost=1.0)
    bad = project.root / ".gov-runtime" / "sessions" / "broken.json"
    bad.write_text("{not json", encoding="utf-8")
    other = project.root / ".gov-runtime" / "sessions" / "other.json"
    other.write_text(json.dumps({"record": "something-else"}), encoding="utf-8")
    code, out, err = project.spend(capsys, "sum")
    assert code == 0 and out.splitlines() == [f"{T}: cost 1.00 USD; no projection; not braked"]
    assert "broken.json" in err and "other.json" in err


def test_s1_a_malformed_cost_counts_as_unknown_not_zero(project, capsys):
    project.session(cost=1.0)
    project.session(cost=-3.0)  # not a cost the record can hold
    project.session(cost=True)
    _, out, _ = project.spend(capsys, "sum")
    assert f"{T}: cost 1.00 USD, 2 unknown" in out


# -- S2: the brake -------------------------------------------------------------------------------------------------

def test_s2_at_1_99_times_the_projection_gives_no_brake(project, capsys):
    planted(project, 1.99)
    code, out, _ = project.spend(capsys, "check")
    assert code == 0 and "BRAKE" not in out
    assert not project.spend_dir().exists() and not project.inbox()


def test_s2_exactly_twice_the_projection_is_not_braked_though_the_float_sum_is_not_exact(project, capsys):
    project.launch(projection=2.2)
    for cost in (1.1, 1.1, 2.2):  # 1.1 + 1.1 + 2.2 is 4.4 only to the cent in floats
        project.session(cost=cost)
    code, out, _ = project.spend(capsys, "check")
    assert code == 0 and "BRAKE" not in out and not project.marker().exists() and not project.inbox()


def test_s2_at_2_01_times_one_record_one_marker_one_inbox_item_and_a_second_check_writes_none(project, capsys):
    planted(project, 2.01, projection=3.0)
    code, out, _ = project.spend(capsys, "check")
    assert code == 0 and f"BRAKE {T}" in out
    log = project.log()
    assert len(log) == 1 and log[0]["kind"] == "brake" and log[0]["ticket"] == T
    assert log[0]["cost_usd"] == 6.03 and log[0]["projection_usd"] == 3.0
    marker = json.loads(project.marker().read_text())
    assert marker["ticket"] == T and marker["cost_usd"] == 6.03 and marker["projection_usd"] == 3.0
    (item,) = project.inbox()
    text = item.read_text()
    assert T in text and "6.03" in text and "3.00" in text
    before = (project.log(), [p.name for p in project.inbox()], project.marker().read_text())
    code, out, _ = project.spend(capsys, "check")
    assert code == 0 and "BRAKE" not in out and "already braked" in out
    assert (project.log(), [p.name for p in project.inbox()], project.marker().read_text()) == before


def test_s2_the_projection_is_the_latest_launch_record_holding_one(project, capsys):
    project.launch(projection=1.0, started="2026-11-10T08:00:00Z")
    project.launch(projection=4.0, started="2026-11-10T09:00:00Z")
    project.launch(projection=None, started="2026-11-10T09:30:00Z")        # null: holds none
    project.launch(started="2026-11-10T09:45:00Z", key=False)              # absent: holds none
    project.session(cost=7.0)  # twice 1.0 would brake; the latest projection is 4.0
    _, out, _ = project.spend(capsys, "sum")
    assert "projection 4.00 USD" in out
    project.spend(capsys, "check")
    assert not project.marker().exists()


def test_s2_check_brakes_only_the_tickets_past_twice(project, capsys):
    for ticket, cost in (("DAEO-aaaa", 9.0), ("DAEO-bbbb", 3.0)):
        project.launch(ticket=ticket, projection=2.0)
        project.session(ticket=ticket, cost=cost)
    project.spend(capsys, "check")
    assert project.marker("DAEO-aaaa").exists() and not project.marker("DAEO-bbbb").exists()
    assert len(project.inbox()) == 1 and len(project.log()) == 1


def test_s2_a_brake_in_a_git_repository_is_written_in_the_main_checkout(tmp_path, capsys):
    project = Project(tmp_path / "repo")
    project.root.mkdir()
    subprocess.run(["git", "init", "-q", str(project.root)], check=True)
    planted(project, 3.0)
    code, _, _ = project.spend(capsys, "check")
    assert code == 0 and project.marker().exists() and len(project.inbox()) == 1


# -- S4: no projection ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("launch", ["none", "without the key", "null"])
def test_s4_a_large_cost_and_no_projection_is_never_braked_and_is_named(project, capsys, launch):
    if launch == "without the key":
        project.launch(key=False)
    elif launch == "null":
        project.launch(projection=None)
    project.session(cost=9999.0)
    code, out, _ = project.spend(capsys, "check")
    assert code == 0 and "no projection" in out and T in out
    assert not project.spend_dir().exists() and not project.inbox()


def test_s4_another_tickets_projection_is_not_this_tickets(project, capsys):
    project.launch(ticket="DAEO-zzzz", projection=1.0)
    project.session(ticket=T, cost=50.0)
    project.spend(capsys, "check")
    assert not project.marker().exists() and not project.inbox()


# -- S5: the clear -------------------------------------------------------------------------------------------------

def test_s5_clear_removes_the_marker_records_the_note_and_restarts_the_count(project, capsys):
    planted(project, 3.0)  # 6.00 against 2.00
    project.spend(capsys, "check")
    assert project.marker().exists()
    code, out, _ = project.spend(capsys, "clear", T, "--projection-usd", "10", "--note", "more work than planned")
    assert code == 0 and not project.marker().exists()
    clear = project.log()[-1]
    assert clear["kind"] == "clear" and clear["ticket"] == T and clear["note"] == "more work than planned"
    assert clear["projection_usd"] == 10.0 and brake._stamp(clear["at"]) is not None
    _, out, _ = project.spend(capsys, "sum")
    assert out.strip() == ""  # the cost before the clear is no longer counted: no line for it
    project.session(cost=1.5, started=brake.now())
    _, out, _ = project.spend(capsys, "sum")
    assert out.splitlines() == [f"{T}: cost 1.50 USD; projection 10.00 USD; not braked"]
    project.spend(capsys, "check")
    assert not project.marker().exists()  # 1.50 of 10.00: the old 6.00 does not count


def test_s5_clear_without_a_projection_records_null_and_keeps_the_launch_projection(project, capsys):
    planted(project, 3.0)
    project.spend(capsys, "check")
    project.spend(capsys, "clear", T, "--note", "checked")
    assert project.log()[-1]["projection_usd"] is None
    project.session(cost=1.0, started=brake.now())
    _, out, _ = project.spend(capsys, "sum")
    assert "projection 2.00 USD" in out


def test_s5_a_new_overspend_after_the_clear_brakes_again_on_the_cost_since_only(project, capsys):
    planted(project, 3.0)
    project.spend(capsys, "check")
    project.spend(capsys, "clear", T, "--note", "once")
    project.session(cost=4.5, started=brake.now())  # 4.5 > 2 x 2.0; the earlier 6.00 would make it 10.50
    project.spend(capsys, "check")
    assert json.loads(project.marker().read_text())["cost_usd"] == 4.5
    assert [e["kind"] for e in project.log()] == ["brake", "clear", "brake"] and len(project.inbox()) == 2


def test_s5_clear_needs_a_note_and_a_positive_projection(project, capsys):
    planted(project, 3.0)
    project.spend(capsys, "check")
    for argv in (("clear", T), ("clear", T, "--note", "  "), ("clear", T, "--note", "x", "--projection-usd", "0"),
                 ("clear", T, "--note", "x", "--projection-usd", "abc")):
        with pytest.raises(SystemExit) as stop:
            main(["spend", *argv, "--root", str(project.root)])
        assert stop.value.code == 2
    assert project.marker().exists() and len(project.log()) == 1


def test_clear_names_a_ticket_a_marker_can_have(project, capsys):
    code = main(["spend", "clear", "../x", "--note", "n", "--root", str(project.root)])
    assert code == 1 and "SPEND_TICKET_INVALID" in capsys.readouterr().err


# -- S6 / F1: record-only ------------------------------------------------------------------------------------------

def tree(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*")}


def test_s6_check_leaves_a_running_session_alive_calls_no_notifier_and_writes_only_spend_and_one_inbox_item(
        project, capsys, tmp_path):
    stub = tmp_path / "notifier.sh"
    calls = tmp_path / "calls.txt"
    stub.write_text(f"#!/bin/sh\necho called >> {calls}\n")
    stub.chmod(0o755)
    config = project.root / "governance" / "project" / "dispatch.yaml"
    config.parent.mkdir(parents=True)
    config.write_text(f"dispatch:\n  notifier_command: ['{stub}']\n", encoding="utf-8")
    running = subprocess.Popen(["sleep", "300"])
    try:
        project.launch(projection=2.0)
        project.session(cost=9.0, pid=running.pid, ended=None)
        before = tree(project.root)
        code, _, _ = project.spend(capsys, "check")
        assert code == 0
        new = tree(project.root) - before
        assert {n for n in new if not n.startswith((".gov-runtime/spend", ".gov-runtime/dispatch"))} == set()
        assert len(project.inbox()) == 1
        assert not calls.exists()
        state = Path(f"/proc/{running.pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
        assert running.poll() is None and state != "T"
    finally:
        running.kill()
        running.wait()


def test_the_module_writes_nothing_while_it_only_reads(project, capsys):
    planted(project, 1.0)
    before = tree(project.root)
    project.spend(capsys, "sum")
    project.spend(capsys, "check")
    assert tree(project.root) == before
