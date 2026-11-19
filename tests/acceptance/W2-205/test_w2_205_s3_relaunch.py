"""W2-205, success line 3 (RT-5) and failure line 1: a session that died resumes at its recorded next step, once.

With ``{"relaunch": true}`` in ``~/.gov-os/runtime/config.json`` the watch pass, on a registry entry whose process is
gone without a return (no message with the entry's end id from the entry's address in its launcher's inbox, no exit
file of the entry holding 0), claims ``~/.gov-os/runtime/relaunch/relaunch:<ticket>:<boot>:<pid>:<start_ticks>`` and
starts, detached, ``gov launch <role> <ticket> -- --resume <session id> "<text naming next_action>"`` in the entry's
repository, then logs ``relaunched``. A second death of the ticket in the boot is one wake message
``died-twice:<ticket>:<boot>``; an entry with no session id is one wake message that it cannot resume; the key absent,
false or unreadable: no relaunch.

The launch is real (``gov launch`` in W2-184's fixture project) and ends at the recording stand-in CLI
(``~/.local/bin/claude``), which records its arguments; the session to resume was started by a real launch first, so
its launch record exists. A dead session is a registry entry planted for a process that ran and is gone.
"""

from __future__ import annotations

import json
import os

import w2_205_support as s

LEAD = "lead:DAEO-rl05"
STEP = "wire the zq205 valve to the north pump"
ON = {"relaunch": True}


def _resume_of(call) -> str:
    args = call["args"]
    return args[args.index("--resume") + 1]


def _died_twice(rig) -> list[dict]:
    return [m for m in rig.home.wakes(LEAD) if str(m.get("id", "")).startswith("died-twice:")]


def _launchers_end(line) -> bool:
    event = json.loads(line)
    return event.get("event") == "end" and not event.get("estimated")


def _dead(rig, ticket, step=STEP):
    """A ticket with a resumable session, a checkpoint holding ``step`` and a dead registry entry of that session."""
    session_id = rig.session(ticket)
    rig.checkpoint(ticket, step)
    return rig.died(ticket, session_id), session_id


def test_s3_the_launcher_records_the_session_id_in_the_registry_entry(make_rig):
    rig = make_rig(LEAD)
    session_id = rig.session("DAEO-rl00")
    seen = rig.kit.registry_entries()
    assert len(seen) == 1 and seen[0]["entry"], f"harness: the session's registry entry was not seen: {seen}"
    assert seen[0]["entry"].get("session_id") == session_id, (
        f"the registry entry's session_id is {seen[0]['entry'].get('session_id')!r}, not the session's {session_id}")


def test_s3_a_death_is_relaunched_once_with_resume_and_the_next_step_and_a_second_pass_adds_none(make_rig):
    rig = make_rig(LEAD)
    entry, session_id = _dead(rig, "DAEO-rl01")
    rig.home.config(ON)
    rig.home.run_pass()
    resumed = rig.resumed(wait_for=1)
    assert len(resumed) == 1, f"the pass started {len(resumed)} launches that resume a session, not one"
    args = resumed[0]["args"]
    assert _resume_of(resumed[0]) == session_id, f"the launch does not resume the dead session {session_id}: {args}"
    after = args[args.index("--resume") + 2:]
    assert any(STEP in arg for arg in after), f"no argument after --resume names the checkpoint's next step: {args}"
    assert os.path.realpath(resumed[0]["cwd"]) == os.path.realpath(rig.project), resumed[0]["cwd"]
    assert len(rig.home.events("relaunched")) == 1, f"the log's `relaunched` events: {rig.home.events('relaunched')}"

    rig.home.put_entry(entry)  # still in the registry at the next pass
    rig.home.passes(2)
    assert len(rig.resumed(settle=2.0)) == 1, "a second pass over the same death started another launch"
    assert len(rig.home.events("relaunched")) == 1, "a second pass logged another `relaunched` event"
    assert _died_twice(rig) == [], f"one death was messaged as died twice: {_died_twice(rig)}"


def test_s3_a_second_death_of_the_ticket_in_the_boot_is_one_died_twice_message_and_no_launch(make_rig):
    rig = make_rig(LEAD)
    _entry, session_id = _dead(rig, "DAEO-rl02")
    rig.home.config(ON)
    rig.home.run_pass()
    assert len(rig.resumed(wait_for=1)) == 1, "the first death was not relaunched once"
    rig.died("DAEO-rl02", session_id)
    rig.home.passes(2)
    assert len(rig.resumed(settle=2.0)) == 1, "a second death of the ticket in the boot was relaunched"
    twice = _died_twice(rig)
    assert [m.get("id") for m in twice] == [f"died-twice:DAEO-rl02:{s.boot_id()}"], (
        f"the second death is not one wake message died-twice:<ticket>:<boot>: {rig.home.wakes(LEAD)}")
    assert "died twice" in s.message_words(twice[0]).lower() and "DAEO-rl02" in s.message_words(twice[0]), twice[0]


def test_s3_an_entry_with_no_session_id_is_one_cannot_resume_message_and_no_launch(box):
    root = s.project(box.base / "project", "DAEO-rl03")
    s.checkpoint(box, root, "DAEO-rl03", STEP)
    box.config(ON)
    box.died("DAEO-rl03", root, LEAD)
    box.passes(2)
    named = box.named(LEAD, "cannot resume")
    assert len(named) == 1, f"{len(named)} wake messages naming that it cannot resume, not one: {box.wakes(LEAD)}"
    assert "DAEO-rl03" in s.message_words(named[0]), f"the message does not name the ticket: {named[0]}"
    assert box.events("relaunched") == [] and box.claude_calls() == [], "an entry with no session id was relaunched"


def test_s3_only_a_death_without_a_return_is_relaunched(make_rig):
    rig = make_rig(LEAD)
    _died, died_session = _dead(rig, "DAEO-rl04")
    messaged = rig.died("DAEO-rl4m", rig.session("DAEO-rl4m"))
    rig.checkpoint("DAEO-rl4m", STEP)
    rig.home.send(LEAD, "wake", "session engineer DAEO-rl4m ended with exit code 0", "--id", s.end_id(messaged),
                  "--from", messaged["address"], "--data", '{"ticket": "DAEO-rl4m", "exit_code": 0}')
    exit_file = s.write(rig.home.base / "DAEO-rl4x.exit", "0\n")
    rig.died("DAEO-rl4x", rig.session("DAEO-rl4x"), exit_file=str(exit_file))
    rig.checkpoint("DAEO-rl4x", STEP)
    rig.home.config(ON)
    rig.home.run_pass()
    resumed = rig.resumed(wait_for=1, settle=2.0)
    assert [_resume_of(call) for call in resumed] == [died_session], (
        f"the launches are not the one death without a return (a launcher message saying exit code 0 and an exit "
        f"file holding 0 are returns): {[call['args'][-4:] for call in resumed]}")
    assert len(rig.home.events("relaunched")) == 1 and len(rig.home.claims()) == 1, (
        f"`relaunched` events {rig.home.events('relaunched')}, claims {rig.home.claims()}")


def test_s3_the_key_absent_false_or_unreadable_gives_the_slice_1_message_only_and_true_relaunches(make_rig):
    rig = make_rig(LEAD)
    for number, config in enumerate((None, {"relaunch": False}, "{not json", {})):
        if config is not None:
            rig.home.config(config)
        entry, _session = _dead(rig, f"DAEO-rl5{number}")
        rig.home.run_pass()
        assert rig.resumed(settle=1.0) == [] and rig.home.claims() == [] and rig.home.events("relaunched") == [], (
            f"config.json {config!r}: a relaunch (launches {len(rig.resumed())}, claims {rig.home.claims()})")
        ends = [m for m in rig.home.wakes(LEAD) if m.get("id") == s.end_id(entry)]
        assert len(ends) == 1, f"config.json {config!r}: {len(ends)} slice 1 end messages for the death, not one"
        rig.home.drop_entry(entry)
    assert _died_twice(rig) == [] and rig.home.named(LEAD, "cannot resume") == [], rig.home.wakes(LEAD)
    rig.home.config(ON)
    _entry, session_id = _dead(rig, "DAEO-rl59")
    rig.home.run_pass()
    assert [_resume_of(call) for call in rig.resumed(wait_for=1, settle=1.0)] == [session_id], (
        "with the key true the death was not relaunched once")


def test_f1_a_pass_killed_after_the_launch_and_before_its_log_line_does_not_relaunch_again(make_rig):
    rig = make_rig(LEAD)
    entry, _session = _dead(rig, "DAEO-rlf1")
    rig.home.config(ON)
    rig.home.drop_entry(entry)
    rig.home.run_pass()  # the state and the log a pass killed before its writes leaves behind
    state, log = rig.home.state_path.read_bytes(), rig.home.log_path.read_text(encoding="utf-8").splitlines()
    rig.home.put_entry(entry)
    rig.home.run_pass()
    assert len(rig.resumed(wait_for=1)) == 1, "the pass did not relaunch the death once"
    claim = f"relaunch:DAEO-rlf1:{entry['boot']}:{entry['pid']}:{entry['start_ticks']}"
    assert rig.home.claims() == [claim], f"the claim files are {rig.home.claims()}, not [{claim}]"

    rig.home.state_path.write_bytes(state)  # ... as if the pass had been killed after the launch
    kept = [line for line in rig.home.log_path.read_text(encoding="utf-8").splitlines()
            if line in log or _launchers_end(line)]  # what the launched session's own launcher wrote stays
    rig.home.log_path.write_text("".join(line + "\n" for line in kept), encoding="utf-8")
    assert rig.home.events("relaunched") == [], "harness: the killed pass's log line is still there"
    rig.home.put_entry(entry)
    rig.home.passes(2)
    assert len(rig.resumed(settle=2.0)) == 1, "the pass after a killed pass relaunched the same death again"
    assert rig.home.claims() == [claim], f"the claim files after the second pass: {rig.home.claims()}"
    assert _died_twice(rig) == [], f"one death was messaged as died twice: {_died_twice(rig)}"


def test_f1_a_session_that_dies_every_time_is_relaunched_once_and_its_checkpoint_is_not_rewritten(make_rig):
    rig = make_rig(LEAD)
    _entry, session_id = _dead(rig, "DAEO-rlf2")
    before = s.checkpoint_files(rig.project, "DAEO-rlf2")
    rig.home.config(ON)
    rig.home.run_pass()
    assert len(rig.resumed(wait_for=1)) == 1, "the first death was not relaunched once"
    for _ in range(3):  # it dies again, and again, and again
        rig.died("DAEO-rlf2", session_id)
        rig.home.run_pass()
    assert len(rig.resumed(settle=2.0)) == 1, f"a session that dies every time was launched {len(rig.resumed())} times"
    assert len(rig.home.events("relaunched")) == 1, rig.home.events("relaunched")
    assert len(_died_twice(rig)) == 1, f"the later deaths are not one died-twice message: {_died_twice(rig)}"
    assert s.checkpoint_files(rig.project, "DAEO-rlf2") == before, "the relaunch rewrote or added a checkpoint record"
