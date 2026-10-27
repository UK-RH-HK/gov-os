"""W2-65 KPI success 1 to 3 and the failure line: a guard program that cannot run blocks the call (DEC-880 item 3).

Claude Code blocks a PreToolUse call only on exit 2 (its standard error goes to the model) or a deny decision on
standard output; any other non-zero exit is a non-blocking error and the call goes through. So each line that runs the
guard (preToolUse) or the containment program (postToolUse, postToolUseFailure), in this repository's hook source and
in the template's, must end with exit 2 and a message naming its program whenever the program ends with anything other
than 0 or 2, and must pass 0 (with whatever the program wrote, a deny decision included) and 2 through unchanged.

The lines are read from this worktree's sources and run through ``sh -c`` in a temporary project and home; the program
each line starts is a stand-in placed where the line looks for it (``w2_65_support``).
"""

from __future__ import annotations

import json

import pytest

import w2_65_support as support

LINES = support.guarded_lines()
IDS = [line.id for line in LINES]
MISSING_INTERPRETER = "/nonexistent/w265/python3"

# The ways a program cannot run: (label, program text, interpreter or None for the real one). Each ends with an exit
# other than 0 or 2, or never starts.
CANNOT_RUN = [
    ("a syntax error from a half-finished edit", "def half_finished(:\n    pass\n", None),
    ("an exit 1 with nothing written", "import os, sys\nopen(os.environ['W265_MARK'], 'w').close()\nsys.exit(1)\n",
     None),
    ("a crash (killed by a signal)",
     "import os, signal\nopen(os.environ['W265_MARK'], 'w').close()\nos.kill(os.getpid(), signal.SIGKILL)\n", None),
    ("an interpreter that cannot start", "import sys\nsys.exit(0)\n", MISSING_INTERPRETER),
]

DENY = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                               "permissionDecisionReason": "w265 stand-in deny"}}


def _marking(text: str, mark) -> str:
    """The program text with its marker path written in (the line's environment is the session's, not the case's)."""
    return text.replace("os.environ['W265_MARK']", repr(str(mark)))


def test_both_sources_hold_the_guard_and_the_containment_lines_and_the_guard_stays_recognisable():
    """Each source has a preToolUse line that runs the guard, and lines that run the containment program on
    postToolUse and postToolUseFailure. The guard's line keeps the text the launcher recognises it by
    (``hooks/pretooluse.py``, I1 §2.3), so the launcher still sees the guard in the generated settings."""
    for source in support.SOURCES:
        found = {(line.event, line.program_name) for line in LINES if line.source == source}
        assert ("preToolUse", "pretooluse.py") in found, (
            f"{support.SOURCES[source]} has no preToolUse line containing {support.GUARD_PROGRAM!r}: {found}")
        for event in ("postToolUse", "postToolUseFailure"):
            assert (event, "posttooluse.py") in found, (
                f"{support.SOURCES[source]} has no {event} line running the containment program: {found}")


@pytest.mark.parametrize("line", LINES, ids=IDS)
def test_a_program_that_cannot_run_blocks_the_call(line, tmp_path):
    """For each way the program cannot run, the line ends with exit 2 (the only exit Claude Code blocks on) and
    standard error names the program."""
    failures = []
    for number, (label, text, interpreter) in enumerate(CANNOT_RUN):
        box = support.make_box(tmp_path / f"case-{number}", interpreter=interpreter or support.REAL_PYTHON)
        mark = box.markers / "program-ran"
        support.place_program(box, line, _marking(text, mark))
        done = support.run_line(line, box)
        if done.returncode != 2:
            failures.append(f"- {label}: the line ended with exit {done.returncode}, so the call is not blocked "
                            f"(only exit 2 blocks)\n{done.describe()}")
        elif line.program_name not in done.stderr:
            failures.append(f"- {label}: exit 2, but standard error does not name {line.program_name}\n"
                            f"{done.describe()}")
        if "W265_MARK" in text and not mark.exists():
            failures.append(f"- {label}: the stand-in at {line.program_rel} never ran, so the case measured "
                            f"nothing\n{done.describe()}")
    assert not failures, (f"{line.id} lets a call through when its program cannot run:\n" + "\n".join(failures))


@pytest.mark.parametrize("line", LINES, ids=IDS)
def test_exit_0_and_exit_2_pass_through_unchanged(line, tmp_path):
    """The line never turns its program's exit 0 into a refusal: exit 0 stays 0 with the program's standard output
    unchanged (a deny decision included, which is how the guard refuses with exit 0); exit 2 stays 2 with the
    program's standard error delivered. The program reads the event's input from standard input."""
    reads_input = "import json, sys\ncall = json.load(sys.stdin)\n"
    deny = json.dumps({**DENY, "w265_tool_use_id": "toolu_w265_0001"})
    cases = [
        ("exit 0, nothing written", reads_input + "sys.exit(0)\n", 0, "", None),
        ("exit 0 with a deny decision",
         reads_input + "deny = " + repr(json.dumps(DENY)) + "\n"
         "out = json.loads(deny); out['w265_tool_use_id'] = call['tool_use_id']\n"
         "sys.stdout.write(json.dumps(out)); sys.exit(0)\n", 0, deny, None),
        ("exit 2 with a refusal on standard error",
         reads_input + "sys.stderr.write('w265 refused ' + call['tool_use_id']); sys.exit(2)\n",
         2, None, "w265 refused toolu_w265_0001"),
    ]
    failures = []
    for number, (label, text, exit_code, stdout, stderr_part) in enumerate(cases):
        box = support.make_box(tmp_path / f"case-{number}")
        support.place_program(box, line, text)
        done = support.run_line(line, box)
        if done.returncode != exit_code:
            failures.append(f"- {label}: the line ended with exit {done.returncode}, not {exit_code}\n"
                            f"{done.describe()}")
            continue
        if stdout is not None and done.stdout != stdout:
            failures.append(f"- {label}: standard output changed: {done.stdout!r} instead of {stdout!r}\n"
                            f"{done.describe()}")
        if stderr_part is not None and stderr_part not in done.stderr:
            failures.append(f"- {label}: the program's standard error {stderr_part!r} is not delivered\n"
                            f"{done.describe()}")
    assert not failures, (f"{line.id} does not pass its program's answer through:\n" + "\n".join(failures))
