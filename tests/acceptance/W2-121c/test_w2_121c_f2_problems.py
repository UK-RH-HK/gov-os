"""W2-121c, failure line 2: a pass that cannot read part of the machine says so and loses nothing.

An unreadable registry entry, a missing transcript or an ``nvidia-smi`` that fails is named in state.json's ``problems``
and in the log, the rest of the pass still runs (the message for a planted ended watch is sent), and the previous
state.json is replaced only whole. Each fault is planted in turn, after a clean first pass.
"""

from __future__ import annotations

import pytest

import w2_121c_support as s

LEAD = "lead:DAEO-f2"


def _unreadable_entry(box):
    s.write(box.sessions / "31337.json", '{"pid": 31337, "repository": "/x", "ticket": "DAEO-')
    return ("31337.json",)


def _missing_transcript(box):
    transcript = s.write(box.base / "gone" / "vanished-transcript.jsonl", "{}\n")
    box.watch("lead:DAEO-t", "a vanished transcript", "--transcript", str(transcript), "--stall-after", "600")
    transcript.unlink()
    return ("vanished-transcript.jsonl",)


def _failing_nvidia_smi(box):
    box.gpu_fails()
    return ("nvidia-smi", "gpu")


FAULTS = {"unreadable-registry-entry": _unreadable_entry, "missing-transcript": _missing_transcript,
          "failing-nvidia-smi": _failing_nvidia_smi}


@pytest.mark.parametrize("fault", list(FAULTS))
def test_f2_a_fault_is_named_in_problems_and_the_log_and_the_pass_still_sends(box, fault):
    box.run_pass()
    assert isinstance(box.state().get("problems"), list), "state.json's problems is not a list"
    tokens = FAULTS[fault](box)
    exit_file = s.write(box.base / "ended.exit", "0\n")
    request = box.watch(LEAD, "an ended job", "--exit-file", str(exit_file))

    done = box.run_pass(check=False)
    assert done.returncode == 0, f"a pass with a {fault} exited {done.returncode}, not 0\n{s.said(done)}"
    state = box.state()  # parses: replaced whole
    problems = state.get("problems")
    assert isinstance(problems, list) and any(any(s.mentions(p, t) for t in tokens) for p in problems), (
        f"state.json's problems do not name the {fault} ({tokens}): {problems}")
    logged = [line for line in box.log() if line.get("event") == "problem"]
    assert any(any(s.mentions(line, t) for t in tokens) for line in logged), (
        f"log.jsonl has no problem event naming the {fault} ({tokens}): {logged}")
    wakes = box.wakes(LEAD)
    assert [m.get("id") for m in wakes] == [f"watch:{request}"], (
        f"the ended watch's message was not sent by the pass with a {fault}: {wakes}")
