"""W2-205, failure line 2: the stall check and its push are untouched (a regression guard: green on the base).

The pass's stall incident for a silent transcript still messages once and pushes once, with the relaunch key on and a
dead session in the same pass. The other half of the line (``tests/acceptance/W2-121c`` green, the branch's diff
touching none of the live paths) is the lead's check, not a test here.
"""

from __future__ import annotations

import os

import w2_205_support as s

DAY_ISO = "2026-11-16T12:00:00+00:00"
DAY = int(s.epoch(DAY_ISO))
AT_DAY = {"GOV_RUNTIME_NOW": DAY_ISO}


def test_f2_guard_a_silent_transcript_still_messages_once_and_pushes_once(box):
    stub, log = s.base.push_stub(box.base)
    transcript = s.write(box.base / "session" / "cto.jsonl", '{"type": "assistant"}\n')
    os.utime(transcript, (DAY - 2 * 3600, DAY - 2 * 3600))
    request = box.watch("cto", "the cto session", "--transcript", str(transcript), "--stall-after", "600",
                        "--push", str(stub))
    box.config({"relaunch": True})
    box.died("DAEO-f205", box.work, "lead:DAEO-f205")  # no session id: nothing to launch
    box.passes(3, extra_env=AT_DAY)
    stalls = [m for m in box.wakes("cto") if str(m.get("id", "")).startswith("stall:")]
    assert [m.get("id") for m in stalls] == [f"stall:{request}:{DAY - 2 * 3600}"], f"the stall messages: {stalls}"
    assert "the cto session" in s.message_words(stalls[0]) and "120" in s.message_words(stalls[0]), stalls[0]
    runs = s.base.wait_for_runs(log, 1, 5.0)
    assert len(s.base.push_runs(log, settle=1.0)) == 1, f"the push ran {len(runs)} times for one incident: {runs}"
    assert runs[0][-1] == stalls[0].get("text"), f"the push's last argument is not the message text: {runs[0]}"
    assert box.claude_calls() == [], f"a session was started: {box.claude_calls()}"
