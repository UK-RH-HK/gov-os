"""Write scope to the ticket's allowed paths is the path-map guard's (DEC-820 (4), DEC-1112 (1)).

S2: ... Write scope to the ticket's allowed paths (DEC-820 (4)) is the path-map guard's: a file-tool write, or a Bash
write the guard can name, outside them is refused for each worker role; a script's write the guard cannot name, inside
the worktree (python3 -c with open(..., 'w')), is the known gap the CIT-E names [changed, DEC-1112 (1)].
S3: an allowed path that is a name pattern (such as test_batch*) is held by the path-map guard's match, for the file
tools and the Bash writes it names [changed, DEC-1112 (1)].
F1: a file-tool write, or a Bash write the guard can name, outside the ticket's paths still succeeds.

The kernel's PreToolUse hook is copied into the fixture project and run as the harness runs it (event JSON on stdin,
``GOV_ROLE`` and ``GOV_TICKET`` set). Each worker role is asked on the ticket it is launched on (``TICKET_OF``). The
premise case asks a write inside each role's scope, so a guard that refuses everything fails it.
"""

from __future__ import annotations

import pytest

import w2_56_support as s
import w2_56_sandbox_support as sb

OUTSIDE = "src/b/w56-outside.txt"      # outside every worker role's scope on its ticket
INSIDE = {
    s.ENGINEER: "src/app/w56-inside.txt",
    s.TEST_DESIGNER: "tests/acceptance/W2-77/test_w56_inside.py",
    s.AUDITOR: ".gov-runtime/scratch/w56-review.md",          # the auditor writes its record in scratch only
    s.PRODUCT_SPEC: "docs/spec/w56-inside.md",
    s.RESEARCH: "experiments/spikes/exp-56/w56-inside.md",
}


@pytest.fixture
def box(tmp_path):
    box = s.make_box(tmp_path)
    sb.project(box, guard=True, extra={".gov-runtime/scratch/keep.md": "scratch\n"})
    return box


def _ask(box, role, tool, tool_input, ticket=None):
    return sb.ask_guard(box, tool, tool_input, role, (ticket or s.TICKET_OF[role]).tk)


def _path(box, rel):
    return str(box.project / rel)


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s2_premise_a_write_inside_the_roles_scope_is_allowed(box, role):
    rel = INSIDE[role]
    for tool, tool_input in (("Write", {"file_path": _path(box, rel), "content": "x\n"}),
                             ("Bash", {"command": f"echo x > {rel}"})):
        decision = _ask(box, role, tool, tool_input)
        assert decision.decision == "allow", f"{role}: {tool} to {rel} inside its scope: {decision.describe()}"


@pytest.mark.parametrize("tool", ("Write", "Edit"))
@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s2_the_guard_refuses_a_file_tool_write_outside_the_tickets_paths(box, role, tool):
    if tool == "Write":
        tool_input = {"file_path": _path(box, OUTSIDE), "content": "x\n"}
    else:
        tool_input = {"file_path": _path(box, "src/b/main.py"), "old_string": "VALUE = 2", "new_string": "VALUE = 9"}
    decision = _ask(box, role, tool, tool_input)
    assert decision.decision == "deny", f"{role}: {tool} outside the ticket's paths: {decision.describe()}"


BASH_OUTSIDE = (
    (s.ENGINEER, "redirect", f"echo x > {OUTSIDE}"),
    (s.ENGINEER, "tee", f"printf x | tee {OUTSIDE}"),
    (s.ENGINEER, "cp", f"cp README.md {OUTSIDE}"),
    (s.ENGINEER, "touch", f"touch {OUTSIDE}"),
    (s.ENGINEER, "mv", f"mv docs/notes.md {OUTSIDE}"),
    (s.ENGINEER, "sed-in-place", "sed -i s/2/3/ src/b/main.py"),
    (s.ENGINEER, "another-worktree", "echo x > {home}/gov-os-worktrees/W2-78/w56.txt"),
    (s.TEST_DESIGNER, "redirect", f"echo x > {OUTSIDE}"),
    (s.AUDITOR, "redirect", f"echo x > {OUTSIDE}"),
    (s.PRODUCT_SPEC, "redirect", f"echo x > {OUTSIDE}"),
    (s.RESEARCH, "redirect", f"echo x > {OUTSIDE}"),
)


@pytest.mark.parametrize("case", BASH_OUTSIDE, ids=[f"{c[0]}-{c[1]}" for c in BASH_OUTSIDE])
def test_s2_the_guard_refuses_a_bash_write_it_names_outside_the_tickets_paths(box, case):
    role, _, command = case
    command = command.replace("{home}", str(box.home))
    decision = _ask(box, role, "Bash", {"command": command})
    assert decision.decision == "deny", f"{role}: `{command}` writes outside the ticket's paths: {decision.describe()}"


PATTERN_CASES = (
    ("Write", "tests/unit/test_batch_one.py", "allow"),
    ("Bash", "echo x > tests/unit/test_batch_two.py", "allow"),
    ("Bash", "cp README.md tests/unit/test_batch_three.py", "allow"),
    ("Write", "tests/unit/test_other.py", "deny"),
    ("Bash", "touch tests/unit/test_other.py", "deny"),
    ("Write", "tests/unit/sub/test_batch_four.py", "deny"),      # one * holds within one folder
    ("Write", "tests/test_batch_five.py", "deny"),
)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=[f"{c[0]}-{c[2]}-{i}" for i, c in enumerate(PATTERN_CASES)])
def test_s3_a_name_pattern_is_held_by_the_guards_match(box, case):
    tool, target, expected = case
    tool_input = {"file_path": _path(box, target), "content": "x\n"} if tool == "Write" else {"command": target}
    decision = _ask(box, s.ENGINEER, tool, tool_input, ticket=sb.PATTERN)
    assert decision.decision == expected, (
        f"allowed path tests/unit/test_batch*: {tool} {target!r} should be {expected}: {decision.describe()}")
