"""W2-121c, failure line 1: no end is reported twice or missed.

An end the launcher messaged and the pass also sees, an end present through several passes, and a pass killed after
sending but before writing its state each leave exactly one message (the ids make a send idempotent).

The third case is planted as what such a kill leaves: the messages sent and the state.json of the pass before.
"""

from __future__ import annotations

import os
import time

import w2_121c_support as s

LEAD = "lead:DAEO-f1"


def test_f1_an_end_the_launcher_messaged_and_the_pass_also_sees_is_one_message(tmp_path):
    kit = s.LaunchKit(tmp_path, rubric=True)
    box = s.Box(tmp_path / "machine", home=kit.home)
    try:
        s.write(kit.hold, "hold\n")
        proc = kit.popen_launch({"GOV_MSG_ADDRESS": LEAD})
        box.processes.append(proc)  # ended with the case, whatever happens
        if not s.poll(kit.registry_entries, 20.0):
            proc.kill()
            raise AssertionError(f"harness: the held session was never started\n{proc.communicate()}")
        entry = kit.registry_entries()[0]["entry"]
        assert entry, "harness: the held session's registry entry was not seen"
        box.run_pass()  # the pass sees the session alive
        assert box.wakes(LEAD) == [], "a live session gave a message"
        s.write(kit.release, "go\n")
        try:
            proc.communicate(timeout=30)
        except Exception:
            proc.kill()
            raise
        box.passes(2)  # the launcher's message is sent; the pass also sees the end
        time.sleep(0.5)
        box.run_pass()
        ends = [m for m in box.wakes(LEAD) if str(m.get("id", "")).startswith("end:")]
        assert len(ends) == 1, f"{len(ends)} end messages for one launched session, not one: {box.wakes(LEAD)}"
        assert ends[0]["id"] == s.end_id(entry), ends[0]
    finally:
        s.write(kit.release, "go\n")
        box.cleanup()


def test_f1_an_end_present_through_several_passes_is_one_message(box):
    pid, ticks = box.dead_pid()
    entry = box.register(pid, ticks, notify=LEAD)
    box.passes(4)
    wakes = box.wakes(LEAD)
    assert [m.get("id") for m in wakes] == [s.end_id(entry)], f"an end present through 4 passes gave {wakes}"


def test_f1_a_pass_killed_after_sending_but_before_writing_its_state_leaves_one_message(box):
    session = box.sleeper()
    entry = box.register(session.pid, s.start_ticks(session.pid), notify=LEAD)
    job = box.sleeper()
    request = box.watch(LEAD, "a job", "--pid", str(job.pid))
    transcript = s.write(box.base / "t.jsonl", "{}\n")
    box.watch(LEAD, "a session's transcript", "--transcript", str(transcript), "--stall-after", "600")
    box.run_pass()
    before = box.state_path.read_bytes()  # the state a pass killed before its write leaves behind

    box.end(session)
    box.end(job)
    when = int(time.time()) - 7200
    os.utime(transcript, (when, when))
    box.run_pass()  # sends the three messages, writes its state ...
    sent = sorted(m.get("id") for m in box.wakes(LEAD))
    assert len(sent) == 3, f"the pass did not send the three messages: {sent}"
    box.state_path.write_bytes(before)  # ... as if it had been killed before the write
    box.run_pass()
    box.run_pass()
    again = sorted(m.get("id") for m in box.wakes(LEAD))
    assert again == sent, f"after a pass lost its state the messages are {again}, not once each {sent}"
    assert s.end_id(entry) in again and f"watch:{request}" in again, again
