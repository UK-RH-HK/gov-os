"""S2 and S5: the idle check, each legitimate wait, running work, stale pids and the open items' sources."""

from __future__ import annotations

import json

from .conftest import HOUR, NOW

ALIVE = {"pid": 5001, "cmdline": "bash launched-worker", "start": NOW - 600, "state": "S", "fds": []}
FILE_ITEMS = "session_watch:\n  items: {source: file, path: items.txt}\n"


def items_file(hook, text: str) -> None:
    (hook.root / "items.txt").write_text(text)


def unblocked(hook) -> None:
    hook.plan(hook.ready_of("T-1", "T-2"))


def test_unblocked_items_and_nothing_running_block_naming_each(hook):
    unblocked(hook)
    out = hook.run("idle")
    assert out["decision"] == "block" and "T-1" in out["reason"] and "T-2" in out["reason"]
    assert "later" not in out["reason"] and "IDLE-REASON" in out["reason"]
    assert "idle" in hook.log().splitlines()[0].split("\t")


def test_a_shut_gate_a_shut_disk_and_a_full_machine_let_the_turn_end_naming_the_wait(hook):
    cases = {
        "gate": {"gate": {"open": False, "reasons": ["load too high"], "disk": {"open": True}}},
        "disk": {"gate": {"open": True, "reasons": [], "disk": {"open": False}}},
        "machine": {"outcome": "refused", "gate": {"open": True, "disk": {"open": True}}},
    }
    unblocked(hook)
    for word, status in cases.items():
        hook.new_turn()
        hook.status(status)
        out = hook.run("idle")
        assert "decision" not in out and word in out["systemMessage"], (word, out)
    assert hook.log().count("\n") == 3


def test_a_status_older_than_five_minutes_is_not_used(hook):
    unblocked(hook)
    hook.status({"gate": {"open": False, "disk": {"open": True}}}, age_s=301)
    assert hook.run("idle")["decision"] == "block"


def test_every_item_waiting_on_the_owner_lets_the_turn_end_with_counts(hook):
    hook.config(FILE_ITEMS)
    items_file(hook, "# a note\nA-1 WAIT owner decision\nA-2 WAIT owner\nA-3 WAIT a running job\nA-4 DONE\n")
    out = hook.run("idle")
    assert "decision" not in out and "owner" in out["systemMessage"] and "2" in out["systemMessage"]


def test_a_running_job_lets_the_turn_end_naming_it(hook):
    unblocked(hook)
    hook.status({"running_jobs": [{"kind": "verify", "pid": 7}], "gate": {"open": True, "disk": {"open": True}}})
    out = hook.run("idle")
    assert "decision" not in out and "running" in out["systemMessage"]
    hook.new_turn()
    hook.status({"pending_starts": [{"log": "l", "ticket": "T-1"}]})
    assert "decision" not in hook.run("idle")
    hook.new_turn()
    hook.status({"running": [{"ticket": "T-1", "pid": 9}]})
    assert "decision" not in hook.run("idle")


def test_a_background_agent_and_a_background_task_count_as_running(hook, tmp_path):
    unblocked(hook)
    agents, tasks = tmp_path / "agents", tmp_path / "tasks"
    hook.touch(agents / "agent-a.meta.json", 60, json.dumps({"description": "builder"}))
    hook.touch(agents / "agent-a.jsonl", 60)
    hook.monkeypatch.setenv("GOV_SESSION_WATCH_SUBAGENTS", str(agents))
    out = hook.run("idle")
    assert "decision" not in out and "builder" in out["systemMessage"]
    (agents / "agent-a.meta.json").write_text(json.dumps({"finished": True}))
    hook.new_turn()
    assert hook.run("idle")["decision"] == "block"
    hook.touch(agents / "agent-b.meta.json", 4000, json.dumps({"description": "silent"}))  # unfinished, long silent
    hook.touch(agents / "agent-b.jsonl", 4000)
    hook.new_turn()
    assert hook.run("idle")["decision"] == "block"
    task = hook.touch(tasks / "t1.output", 5)
    hook.monkeypatch.setenv("GOV_SESSION_WATCH_TASKS", str(tasks))
    hook.procs({"pid": 77, "cmdline": "bash -c 'make big'", "start": NOW - 100, "state": "S", "fds": [str(task)]})
    hook.new_turn()
    assert "make big" in hook.run("idle")["systemMessage"]
    hook.procs({"pid": 77, "cmdline": "sleep 30", "start": NOW - 100, "state": "S", "fds": [str(task)]})
    hook.new_turn()  # a bare sleep timer is not work
    assert hook.run("idle")["decision"] == "block"


def test_a_pid_file_counts_only_alive_young_and_without_an_exit_file(hook):
    unblocked(hook)
    hook.pidfile("job-a", 5001)
    hook.procs(ALIVE)
    assert "decision" not in hook.run("idle")
    hook.new_turn()
    hook.pidfile("job-a", 5001, exit_file=True)
    assert hook.run("idle")["decision"] == "block"
    (hook.root / ".gov-runtime/jobs/job-a.exit").unlink()
    hook.procs({**ALIVE, "state": "Z"})
    hook.new_turn()
    assert hook.run("idle")["decision"] == "block"


def test_a_pid_past_three_hours_is_named_as_stale_and_not_counted(hook):
    unblocked(hook)
    hook.pidfile("old-job", 5001)
    hook.procs({**ALIVE, "start": NOW - 3 * HOUR - 60})
    out = hook.run("idle")
    assert out["decision"] == "block" and "stale" in out["reason"] and "old-job" in out["reason"]
    assert "stale" in hook.log()


def test_pid_globs_are_the_projects(hook):
    unblocked(hook)
    hook.touch(hook.root / "elsewhere" / "w.pid", 60, "5001\n")
    hook.procs(ALIVE)
    assert hook.run("idle")["decision"] == "block"  # the default glob does not reach it
    hook.config("session_watch:\n  pid_globs: ['elsewhere/*.pid']\n")
    hook.new_turn()
    assert "decision" not in hook.run("idle")


# -- S5: the open items' sources ---------------------------------------------------------------------------------

def test_the_lines_reader_names_the_unblocked_items(hook):
    hook.config(FILE_ITEMS)
    items_file(hook, "A-1 NOT STARTED\nA-2 WAIT owner\nA-3 closed? no\nA-4 CLOSED\n")
    out = hook.run("idle")
    assert out["decision"] == "block" and "A-1" in out["reason"] and "A-3" in out["reason"]
    assert "A-2" not in out["reason"] and "A-4" not in out["reason"]


def test_a_module_reader_returns_items_with_states(hook, tmp_path, monkeypatch):
    (tmp_path / "myreader.py").write_text(
        "def read(path):\n"
        "    return [{'id': 'R-1', 'title': 't', 'state': 'open'}, {'id': 'R-2', 'title': 't', 'state': 'owner'},\n"
        "            {'id': 'R-3', 'title': 't', 'state': 'job'}, {'id': 'R-4', 'title': 't', 'state': 'closed'}]\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    hook.config("session_watch:\n  items: {source: file, path: items.txt, reader: 'myreader:read'}\n")
    items_file(hook, "anything")
    out = hook.run("idle")
    assert out["decision"] == "block" and "R-1" in out["reason"] and "R-2" not in out["reason"]


def test_both_sources_give_the_same_block_text(hook):
    hook.plan(hook.ready_of("T-1", "T-2"))
    from_dispatcher = hook.run("idle")["reason"]
    hook.new_turn()
    hook.config(FILE_ITEMS)
    items_file(hook, "T-1 NOT STARTED\nT-2 NOT STARTED\n")
    assert hook.run("idle")["reason"] == from_dispatcher


def test_the_dispatcher_source_leaves_out_tickets_the_status_shows_running(hook):
    from gov.session_watch import items

    hook.plan(hook.ready_of("T-1", "T-2"))
    found = items.dispatcher_items(hook.root, {"T-1"})
    assert [i.id for i in found] == ["T-2"] and found[0].state == "open"


def test_a_failing_plan_is_an_error_named_to_the_owner_and_logged(hook):
    hook.plan("", code=2)
    out = hook.run("idle")
    assert "decision" not in out and "plan" in out["systemMessage"]
    assert "error" in hook.log() and "plan" in hook.log()


def test_a_plan_with_findings_is_still_a_plan(hook):
    hook.plan(hook.ready_of("T-1"), code=1)
    assert hook.run("idle")["decision"] == "block"


def test_a_plan_that_times_out_is_an_error(hook, monkeypatch):
    from gov.session_watch import items

    monkeypatch.setattr(items, "PLAN_TIMEOUT_S", 0.3)
    hook.plan(hook.ready_of("T-1"), sleep=5)
    out = hook.run("idle")
    assert "decision" not in out and "plan" in out["systemMessage"] and "timed out" in out["systemMessage"]
