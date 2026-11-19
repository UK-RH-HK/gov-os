"""W2-205, success line 4 (RT-5) and the hook part of success line 5 (RT-6): after a compaction the session resumes
at the recorded next step.

``precompact.py`` writes the automatic checkpoint record (as it does now); ``sessionstart.py``, for source ``compact``,
``clear`` or ``resume`` and any role with a ticket, injects as its first part ``Resume at the recorded next step
(<ticket>): <next_action> (checkpoint <path>)`` and the line ``Read your inbox: gov msg read``; with no checkpoint it
injects no such part and exits 0. The inbox line is SessionStart's alone: ``precompact.py`` is not changed.

The hooks are the kernel's files under ``template/governance/kernel/hooks/``, run with the hook JSON on stdin, a fixture
git project as ``CLAUDE_PROJECT_DIR``, ``GOV_TICKET`` and ``GOV_ROLE``. The next step and the path expected after the
two hooks are those ``gov checkpoint --resume --ticket <ticket>`` gives then (the latest record's).
"""

from __future__ import annotations

import re

import pytest

import w2_205_support as s

TICKET = "DAEO-hk05"
STEP = "wire the zq205 valve to the north pump"


def _start(box, root, source, role="engineer", ticket=TICKET) -> str:
    payload = {"session_id": "0f1e2d3c-hook", "hook_event_name": "SessionStart", "source": source, "cwd": str(root),
               "transcript_path": str(root / "transcript.jsonl")}
    return s.injected(s.run_hook(box, "sessionstart.py", payload, root, ticket=ticket, role=role))


def _compact(box, root, role="engineer"):
    transcript = s.write(root / "transcript.jsonl", '{"type": "user", "message": {"role": "user", "content": "go"}}\n')
    payload = {"session_id": "0f1e2d3c-hook", "hook_event_name": "PreCompact", "trigger": "auto", "cwd": str(root),
               "transcript_path": str(transcript), "custom_instructions": ""}
    return s.run_hook(box, "precompact.py", payload, root, ticket=TICKET, role=role)


def _begins_with(text, ticket, next_action, path):
    head = f"{s.RESUME_PART} ({ticket}): {next_action} (checkpoint "
    assert text.startswith(head), (
        f"the injected text does not begin with the recorded next step and the ticket ({head!r}...):\n{text[:600]}")
    named = re.match(r"([^)\n]*)\)", text[len(head):])
    assert named and named.group(1).endswith(path), f"the first part does not name the checkpoint {path}:\n{text[:600]}"
    assert s.INBOX_LINE in text.splitlines(), f"no line `{s.INBOX_LINE}` in the injected text:\n{text[:600]}"


@pytest.mark.parametrize("source, role", [("compact", "engineer"), ("clear", "engineer"), ("resume", "engineer"),
                                          ("compact", "independent-test-designer"), ("compact", "orchestrator")])
def test_s4_precompact_then_sessionstart_inject_the_recorded_next_step_first(box, source, role):
    root = s.project(box.base / "project", TICKET)
    s.checkpoint(box, root, TICKET, STEP)
    _compact(box, root, role)
    latest = s.brief(box, root, TICKET)  # the record the PreCompact hook left as the latest
    _begins_with(_start(box, root, source, role), TICKET, latest["next_action"], latest["path"])


def test_s4_with_no_checkpoint_nothing_of_the_kind_is_injected_and_with_one_it_begins_with_its_next_step(box):
    root = s.project(box.base / "project", TICKET)
    assert s.RESUME_PART not in _start(box, root, "compact"), "a resume part was injected with no checkpoint"
    path = s.checkpoint(box, root, TICKET, STEP)
    _begins_with(_start(box, root, "resume"), TICKET, STEP, path)
    assert s.RESUME_PART not in _start(box, root, "startup"), "a resume part was injected at a plain startup"
    assert s.RESUME_PART not in _start(box, root, "compact", ticket=None), "a resume part with no ticket"


@pytest.mark.parametrize("source", ["compact", "clear", "resume"])
def test_s5_the_sessionstart_output_names_gov_msg_read(box, source):
    root = s.project(box.base / "project", TICKET)
    s.checkpoint(box, root, TICKET, STEP)
    text = _start(box, root, source)
    assert "gov msg read" in text, f"the SessionStart injection (source {source}) does not name `gov msg read`:\n{text[:600]}"
    assert s.INBOX_LINE in text.splitlines(), f"no line `{s.INBOX_LINE}` in the injection:\n{text[:600]}"
