"""W2-199, success line 7 (RT-7, one state file, one wake rule for the jobs).

Every heavy run appends events to the one runtime log (``~/.gov-os/runtime/log.jsonl``): ``ready``, ``wait`` (``reason``
one of ``load``, ``slots``, ``gpu``, ``priority``, ``room`` true or false, at most one per reason change), ``admitted``,
``started``, ``ended``, each with ``job`` (a unique id), ``kind``, ``pid`` and ``at``. The watch pass writes state.json
``jobs`` (``running``: kind, slot, pid, workers, cpus, started; ``waiting``: kind, pid, reason, waited_s) and
``admission`` (``load_1m``, ``start_below``, ``load_limit``, ``margin``, ``room``, ``binding``); the runtime folder holds
``state.json`` and ``log.jsonl`` only; a run with ``GOV_MSG_ADDRESS`` sends one wake message ``job:<job id>`` when its
command ends, a run without it none. The stall check's own tests (``tests/unit/orchestration/test_dispatcher_stall*``,
``tests/acceptance/W2-121c/test_w2_121c_s11_dispatcher_stall.py``) stay green: they are not run from this folder.

The test designer's readings: an event's ``pid`` is the ``gov resources`` process's own; ``jobs.running`` and
``jobs.waiting`` are lists (or objects keyed by job id); ``binding`` is a text naming what would hold a start now (here
the word ``load``); only the ``load`` and ``gpu`` waits are pinned to ``room`` false.
"""

from __future__ import annotations

import os
import re

import w2_199_support as s

ONE_SLOT = {"GOV_HEAVY_SLOTS": "1"}


def test_s7_a_pass_with_one_run_held_by_the_load_and_one_running_lists_each_and_the_planted_readings(box):
    running = box.start("running")
    running.must_start(5.0)
    box.load(13.0)
    waiting = box.start("waiting", hold=False)
    assert s.poll(lambda: box.events("wait", pid=waiting.pid), 5.0), f"no `wait` event of the held run: {box.log()}"
    box.run_pass()
    state = box.state()
    jobs = state.get("jobs")
    assert isinstance(jobs, dict), f"state.json has no `jobs` object: {sorted(state)}"
    run_list, wait_list = s.as_list(jobs.get("running")), s.as_list(jobs.get("waiting"))
    assert len(run_list) == 1 and len(wait_list) == 1, f"jobs: {jobs}"
    entry = run_list[0]
    for key in ("kind", "slot", "pid", "workers", "cpus", "started"):
        assert entry.get(key) not in (None, ""), f"the running job lacks {key}: {entry}"
    assert entry["kind"] == "test" and entry["pid"] == running.pid, f"the running job: {entry}"
    held = wait_list[0]
    assert held.get("kind") == "test" and held.get("pid") == waiting.pid and held.get("reason") == "load", (
        f"the waiting job: {held}")
    assert isinstance(held.get("waited_s"), (int, float)) and held["waited_s"] >= 0, f"waited_s: {held}"
    admission = state.get("admission")
    assert isinstance(admission, dict), f"state.json has no `admission` object: {sorted(state)}"
    assert abs(admission.get("load_1m", -1) - 13.0) < 1e-6, f"admission: {admission}"
    assert abs(admission.get("start_below", -1) - 12.0) < 1e-6, f"admission: {admission}"
    assert admission.get("load_limit") == 20 and abs(admission.get("margin", -1) - 1.0) < 1e-6, f"admission: {admission}"
    assert admission.get("room") is False, f"admission.room at load 13 over 12: {admission}"
    assert "load" in str(admission.get("binding", "")).lower(), f"admission.binding names no load: {admission}"
    box.load(3.0)
    waiting.must_start(4.0)
    assert waiting.finish()[0] == 0 and running.release_and_finish()[0] == 0


def test_s7_the_runtime_folder_holds_state_json_and_log_jsonl_only(box):
    job = box.start("a", hold=True)
    job.must_start(5.0)
    assert box.events("started", pid=job.pid), "the running job's `started` event is not in the runtime log"
    box.run_pass()
    assert sorted(os.listdir(box.runtime)) == ["log.jsonl", "state.json"], os.listdir(box.runtime)
    assert job.release_and_finish()[0] == 0
    box.run_pass()
    assert sorted(os.listdir(box.runtime)) == ["log.jsonl", "state.json"], os.listdir(box.runtime)


def test_s7_a_finished_run_reads_ready_admitted_started_ended_with_one_job_id_and_the_common_fields(box):
    first = box.start("a", hold=False)
    assert first.finish()[0] == 0
    second = box.start("b", hold=False)
    assert second.finish()[0] == 0
    ids = []
    for proc in (first.proc, second.proc):
        job = box.job_id(proc.pid)
        ids.append(job)
        mine = [e for e in box.log() if e.get("job") == job]
        assert [e["event"] for e in mine] == ["ready", "admitted", "started", "ended"], f"events of {job}: {mine}"
        for event in mine:
            assert event.get("kind") == "test" and event.get("pid") == proc.pid and event.get("at"), (
                f"an event lacks kind, pid or at: {event}")
    assert len(set(ids)) == 2, f"the two runs share a job id: {ids}"


def test_s7_a_run_held_by_the_load_logs_one_load_wait_with_room_false_between_ready_and_admitted(box):
    box.load(13.0)
    job = box.start("a", hold=False)
    assert job.held_for(2.5)
    box.load(3.0)
    job.must_start(4.0)
    assert job.finish()[0] == 0
    mine = [e for e in box.log() if e.get("job") == box.job_id(job.pid)]
    assert [e["event"] for e in mine] == ["ready", "wait", "admitted", "started", "ended"], f"events: {mine}"
    wait = mine[1]
    assert wait.get("reason") == "load" and wait.get("room") is False, f"the wait event: {wait}"


def test_s7_a_run_held_for_a_slot_logs_a_slots_wait(box):
    holder = box.start("holder", extra_env=ONE_SLOT)
    holder.must_start(5.0)
    second = box.start("second", extra_env=ONE_SLOT, hold=False)
    assert second.held_for(1.5)
    waits = box.events("wait", pid=second.pid)
    assert waits and waits[0].get("reason") == "slots", f"the wait events of a run held for a slot: {waits}"
    assert len(waits) == 1, f"one `wait` per reason change: {waits}"
    holder.release_and_finish()
    second.must_start(4.0)
    assert second.finish()[0] == 0


def test_s7_a_run_with_gov_msg_address_sends_one_wake_message_naming_kind_and_exit_code(box):
    address = "lead:DAEO-x"
    job = box.start("a", hold=False, code=4, pre="sleep 0.5", extra_env={"GOV_MSG_ADDRESS": address})
    assert job.finish()[0] == 4
    wakes = s.poll(lambda: box.wakes(address), 4.0)
    assert wakes, f"no wake message in {address}'s inbox after the command ended"
    assert len(wakes) == 1, f"{len(wakes)} wake messages, not one: {wakes}"
    wake = wakes[0]
    assert wake.get("id") == f"job:{box.job_id(job.pid)}", f"the message id is {wake.get('id')!r}, not job:<job id>"
    words = s.base.message_words(wake)
    assert re.search(r"(?<!\d)4(?!\d)", words), f"the message does not name the exit code 4: {wake}"
    assert re.search(r"\btest\b", words), f"the message does not name the kind: {wake}"
    assert re.search(r"\bran\b|second|\d\s*s\b", words, re.I), f"the message does not name the seconds it ran: {wake}"


def test_s7_a_run_without_gov_msg_address_sends_no_message(box):
    job = box.start("a", hold=False, code=4)
    assert job.finish()[0] == 4
    assert box.events("ended"), "the run left no `ended` event: the test would be vacuous"
    found = [path for path in box.inbox_root.rglob("messages.jsonl") if path.read_text().strip()] \
        if box.inbox_root.exists() else []
    assert not found, f"a run without GOV_MSG_ADDRESS sent a message: {found}"
