"""W1-02 — a guard that fails or runs out of time on a tool of the round does not let the call through (DEC-685).

KPI failure 2: "Guard crash or timeout lets the call through without a recorded
finding". The round changes neither the guard's answer on its own failure
(exit code 2 and one finding, DEC-110) nor its own deadline of 20 seconds
(DEC-580). Held here for the tool names of the round: a made-up name, a name
that begins ``mcp__``, a tool refused by name, and ``MultiEdit``.

In the form of ``test_w1_02_guard_failure.py``:

- **an input the guard cannot use** (no tool input, a tool input that is no
  object, an object cut short) is not let through; where the guard answers it
  as its own failure, one finding is recorded;
- **a ticket file the guard cannot use** lets neither a ``MultiEdit`` inside
  the former ticket paths nor a tool the guard does not know through.

In the form of ``test_w1_02_deadline.py``:

- **a decision that cannot end** (the first program the hook starts does not
  end) is answered with a refusal by ``w1_02_deadline_support.UPPER_S``: at
  once where the guard refuses the tool before it starts a program, at the
  deadline otherwise. The hook processes are started side by side, so the
  module waits once.

**Green today, and green after the round**: the inputs the guard cannot use
(its report of its own failure) and the decisions that cannot end (its
deadline). **Red today**: the three cases of a ticket file the guard cannot
use, in which the guard answers allow for the three tools it does not know and
for ``MultiEdit``.
"""

from __future__ import annotations

import json

import pytest

import w1_02_deadline_support as deadline
import w1_02_support as support
import w1_02_tools_support as tools

ENGINEER = support.ENGINEER
TICKET = support.TICKET_ID
SOURCE = tools.SOURCE_REL

# label -> (tool, builder(project) -> the input a well-formed call would carry)
TOOLS = {
    "a-made-up-tool": (tools.MADE_UP, lambda project: {"file_path": str(project / SOURCE)}),
    "a-tool-of-an-mcp-server": ("mcp__notes__add", lambda project: {"note": {"title": "a note", "body": "text"}}),
    "Monitor": ("Monitor", lambda project: {"command": "echo ready", "description": "wait for a line"}),
    "MultiEdit": ("MultiEdit", lambda project: tools.multiedit_input(project / SOURCE)),
}
BAD_STDIN = ("no-tool-input", "tool-input-not-an-object", "truncated-json")


def _bad_stdin(kind, label, project, sandbox):
    tool_name, build = TOOLS[label]
    data = support.payload(project, tool_name, build(project), sandbox)
    if kind == "no-tool-input":
        del data["tool_input"]
    elif kind == "tool-input-not-an-object":
        data["tool_input"] = SOURCE
    elif kind == "truncated-json":
        return json.dumps(data)[:-25]
    else:
        raise ValueError(kind)
    return json.dumps(data)


@pytest.mark.parametrize("label", sorted(TOOLS))
@pytest.mark.parametrize("kind", BAD_STDIN)
def test_an_input_the_guard_cannot_use_is_not_let_through(project, sandbox, kind, label):
    """Refused; and where the answer is the guard's report of its own failure, exactly one finding of the guard."""
    before = support.findings(project)
    result = support.run_hook_raw(project, _bad_stdin(kind, label, project, sandbox), sandbox, ENGINEER, TICKET)
    what = f"stdin {kind} for {label}"
    assert result.decision == "deny", (
        f"{what} was not refused: decision={result.decision} exit={result.returncode}"
    )
    new = support.findings(project)[len(before):]
    if result.returncode == 2:
        assert len(new) == 1, f"{what}: exit code 2 with {len(new)} new line(s) in {support.FINDINGS_REL}"
        finding = json.loads(new[0])
        assert finding.get("source") == "guard", f"{what}: the finding does not name its source as guard"
        for key in ("kind", "reason"):
            assert isinstance(finding.get(key), str) and finding[key].strip(), f"{what}: the finding has no {key}"
        if kind != "truncated-json":
            assert finding.get("tool_name") == TOOLS[label][0], f"{what}: the finding names another tool"
    assert support.porcelain(project) == "", f"{what}: git status --porcelain changed"


def _break_ticket(project, how):
    path = project / ".tickets" / f"{TICKET}.md"
    if how == "frontmatter-is-not-yaml":
        path.write_text("---\nallowed_paths: [src/gov/guard/**\n  role: {engineer\n\t- : :\n---\n# broken\n", "utf-8")
    elif how == "empty-file":
        path.write_text("", "utf-8")
    elif how == "is-a-directory":
        path.unlink()
        path.mkdir()
    else:
        raise ValueError(how)


@pytest.mark.parametrize("how", ("frontmatter-is-not-yaml", "empty-file", "is-a-directory"))
def test_a_ticket_file_the_guard_cannot_use_lets_no_tool_of_the_round_through(project, call, how):
    """A guard may read such a file as "no ticket paths" without failing: the case asks for the refusal only."""
    _break_ticket(project, how)
    for label in sorted(TOOLS):
        tool_name, build = TOOLS[label]
        result = call(project, tool_name, build(project), role=ENGINEER, ticket=TICKET)
        support.assert_denied(result, f"with a ticket file that is {how}, {label} by the engineer")


# --------------------------------------------------------------------------
# A decision that cannot end
# --------------------------------------------------------------------------

NEVER = (deadline.STAND_IN_ENDS_S,)      # the first program the hook starts does not end before the case does

LATE = (
    deadline.Call("a-made-up-tool-by-the-orchestrator", tools.MADE_UP, lambda project: {"note": deadline.MARKER},
                  deadline.ORCHESTRATOR, sleeps=NEVER),
    deadline.Call("a-tool-of-an-mcp-server-by-an-engineer", "mcp__notes__add",
                  lambda project: {"note": {"title": "a note", "body": deadline.MARKER}}, deadline.ENGINEER,
                  sleeps=NEVER),
    deadline.Call("Monitor-by-the-orchestrator", "Monitor",
                  lambda project: {"command": "echo " + deadline.MARKER, "description": "wait for a line"},
                  deadline.ORCHESTRATOR, sleeps=NEVER),
    deadline.Call("a-MultiEdit-inside-the-ticket-s-paths-by-an-engineer", "MultiEdit",
                  lambda project: tools.multiedit_input(project / deadline.IN_TICKET_REL, [
                      {"old_string": "VALUE = 1", "new_string": deadline.MARKER}]),
                  deadline.ENGINEER, sleeps=NEVER),
    deadline.Call("a-MultiEdit-outside-them-by-a-session-with-no-role", "MultiEdit",
                  lambda project: tools.multiedit_input(project / deadline.OUTSIDE_TICKET_REL, [
                      {"old_string": "VALUE = 1", "new_string": deadline.MARKER}]),
                  deadline.NO_ROLE, sleeps=NEVER),
)
LABELS = [call.label for call in LATE]


@pytest.fixture(scope="module")
def late(hook, tmp_path_factory):
    """Every hook process of the module, started together: ``{label: Outcome}``. One wait for all cases."""
    return deadline.run_side_by_side(tmp_path_factory.mktemp("unknown-tools-deadline"), LATE)


@pytest.mark.parametrize("label", LABELS)
def test_a_decision_that_cannot_end_is_a_refusal_for_a_tool_of_the_round(late, label):
    """DEC-580 unchanged: refused by the guard's own hand, at once or at its deadline; never let through."""
    outcome = late[label]
    assert outcome.answered, f"'{label}': {outcome.describe()}"
    assert outcome.result.decision == "deny", f"'{label}' was not refused: {outcome.describe()}"
    assert outcome.result.seconds <= deadline.UPPER_S, (
        f"'{label}' was answered after {outcome.result.seconds:.1f} s: the answer is due by {deadline.UPPER_S:.0f} s"
    )


def test_the_refusal_of_a_decision_that_cannot_end_carries_nothing_of_the_call(late):
    """As for every answer at the deadline: no word of the call's input, neither protected file's path."""
    for label in LABELS:
        outcome = late[label]
        text = deadline.said(outcome)
        secrets = (deadline.MARKER, str(outcome.project)) + deadline.secrets_of(outcome)[4:7]
        # Positions only: a failure must not print what an answer must not print.
        shown = [index for index, value in enumerate(secrets) if value in text]
        assert not shown, f"the answer to '{label}' carries {len(shown)} value(s) of the call (positions {shown})"
