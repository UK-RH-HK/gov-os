"""W2-121c, RT-7 one state file and one watcher pass (success line 4).

``gov dispatch watch`` is one machine-wide pass (no ``dispatch.yaml``: every pass here runs in a plain folder) that
writes ``~/.gov-os/runtime/state.json`` whole and appends its events to ``log.jsonl``; the folder holds no other file
once the pass ends; a second pass while the folder's lock is held exits 4 and writes nothing; the pass leaves no
process of its own running after it exits.
"""

from __future__ import annotations

import w2_121c_support as s

LEAD = "lead:DAEO-p7"


def _plant_activity(box):
    """Watches, sessions and messages: a live session, an ended one, a pid watch, an exit-file watch, a stalled
    transcript, and messages in two inboxes."""
    live = box.sleeper()
    box.register(live.pid, s.start_ticks(live.pid), notify=LEAD, address="engineer:DAEO-p7")
    pid, ticks = box.dead_pid()
    box.register(pid, ticks, ticket="DAEO-p7b", notify=LEAD)
    box.watch(LEAD, "a sleeper", "--pid", str(box.sleeper().pid))
    box.watch(LEAD, "a job", "--exit-file", str(box.base / "job.exit"))
    transcript = s.write(box.base / "transcript.jsonl", "{}\n")
    box.watch(LEAD, "the cto", "--transcript", str(transcript), "--stall-after", "600")
    box.send(LEAD, "notice", "a notice")
    box.send("cto", "wake", "a wake message")
    return live


def test_rt7b_after_five_passes_the_runtime_folder_holds_state_json_and_log_jsonl_only(box):
    live = _plant_activity(box)
    for number in range(5):
        if number == 2:
            box.end(live)
            s.write(box.base / "job.exit", "0\n")
        box.run_pass()
    listing = sorted(path.name for path in box.runtime.iterdir())
    assert listing == ["log.jsonl", "state.json"], f"the runtime folder holds {listing}"
    state = box.state()
    assert state.get("format") == 1, f"state.json's format is not 1: {state.get('format')!r}"
    missing = [key for key in ("pass", "machine", "limits", "sessions", "watches", "incidents", "problems")
               if key not in state]
    assert not missing, f"state.json lacks {missing}"
    events = box.log()
    assert events and all("at" in line and "event" in line for line in events), f"log.jsonl lines: {events[:5]}"
    assert sum(1 for line in events if line["event"] == "pass") >= 5, "log.jsonl does not record the five passes"


def test_rt7b_a_pass_while_the_lock_is_held_exits_4_and_writes_nothing(box):
    box.run_pass()
    exit_file = s.write(box.base / "held.exit", "0\n")
    box.watch(LEAD, "a finished job", "--exit-file", str(exit_file))
    state, log = box.state_path.read_bytes(), box.log_path.read_bytes()
    runtime_mark = box.mark_bytes("runtime")
    box.hold_runtime_lock()
    done = box.run_pass(check=False)
    assert done.returncode == 4, f"a pass while the lock is held exited {done.returncode}, not 4\n{s.said(done)}"
    assert box.state_path.read_bytes() == state, "state.json changed under a held lock"
    assert box.log_path.read_bytes() == log, "log.jsonl changed under a held lock"
    assert box.mark_bytes("runtime") == runtime_mark, "the runtime inbox's mark moved under a held lock"
    assert box.messages(LEAD) == [], "a pass under a held lock sent a message"
    assert sorted(path.name for path in box.runtime.iterdir()) == ["log.jsonl", "state.json"]
    box.release_locks()
    box.run_pass()
    assert len(box.wakes(LEAD)) == 1, "once the lock is free the pass does send the finished job's message"


def test_rt7b_no_process_of_the_pass_is_alive_after_it_returns(box):
    _plant_activity(box)
    for _ in range(2):
        found = box.pass_under_subreaper()
        assert found["rc"] == 0, f"the pass exited {found['rc']}\n{found['stdout'][-2000:]}\n{found['stderr'][-2000:]}"
        assert found["children"] == [], f"processes of the pass still alive after it returned: {found['children']}"
