"""W1-03 — a call of another actor that never ended stops blocking the restore once it is known to be over.

KPI success 2: "Changes under tests/acceptance/** by a non-test-designer role
are restored from HEAD and the breach is recorded". KPI failure 2.

DEC-142 (owner answer to KD-5): "A snapshot of another actor's call that never
ended (for example, a declined prompt) no longer blocks restoration once that
call is known to be over: its session has issued a later tool call, or the hook
timeout has passed. Restoration still requires certain attribution; otherwise
flag." The owner's answer on the timeout: ten minutes, as a named setting,
default 600 s.

A call never ends when the PreToolUse hook ran and no PostToolUse run followed:
the owner declined the permission prompt, or the session or subagent was
interrupted. Until that call is known to be over it counts as an overlapping
call, and DEC-130 holds: flag and never revert.

Each test leaves such a call behind, lets time or a later tool call pass, and
then has an engineer change acceptance tests in one whole Bash call.

- **A later tool call** is a PreToolUse run for the actor that left the call
  behind: the same ``session_id`` and the same ``agent_id``, or none.
- **Time.** The call that never ended is made to lie in the past
  (``support.run_guard_earlier``): its PreToolUse run gets a clock that is some
  minutes behind, and the files that run wrote get that age. Nothing waits. The
  engineer's call happens at the machine's time.
"""

from __future__ import annotations

import dataclasses
import os

import pytest

import w1_03_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
DESIGNER = support.TEST_DESIGNER
TICKET = support.TICKET_ID
WBS = support.TICKET_WBS_ID
ACCEPTANCE = support.ACCEPTANCE_REL
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
ACCEPTANCE_README = f"{ACCEPTANCE}/{WBS}/README.md"
SOURCE = support.SOURCE_FILE

DESIGNER_AGENT = "agent-w1-03-designer"
ENGINEER_AGENT = "agent-w1-03-engineer"
OTHER_ENGINEER_AGENT = "agent-w1-03-engineer-two"

TEN_MINUTES_S = 600   # the owner's answer: the default of the named setting
MARGIN_S = 60

# The breach: a changed acceptance test, a new one, and a change inside the engineer's own paths.
ADDED = f"{ACCEPTANCE}/{WBS}/test_added.py"
BREACH = f"echo changed >> {ACCEPTANCE_FILE} && echo new > {ADDED} && echo changed >> {SOURCE}"
BREACH_PATHS = (ACCEPTANCE_FILE, ADDED, SOURCE)


@dataclasses.dataclass(frozen=True)
class Actor:
    """Who makes a tool call: a session with its declared role, and inside it the main thread or a subagent."""
    role: str | None            # GOV_ROLE of the session
    subagent: str | None = None   # agent_type; None on the main thread
    agent_id: str | None = None
    session_id: str = support.SESSION_ID

    def hook(self):
        return {"role": self.role, "ticket": TICKET, "subagent": self.subagent, "agent_id": self.agent_id,
                "session_id": self.session_id}


ORCHESTRATOR_MAIN = Actor(ORCHESTRATOR)
ENGINEER_MAIN = Actor(ENGINEER)
ENGINEER_SUBAGENT = Actor(ORCHESTRATOR, ENGINEER, ENGINEER_AGENT)


# --------------------------------------------------------------------------
# Tool calls, step by step
# --------------------------------------------------------------------------

def _begin(project, sandbox, actor, command, seconds_ago=0, literal=False, decision="allow"):
    """The PreToolUse hook runs for a Bash call of ``actor``, now or ``seconds_ago``. Nothing else has happened yet."""
    call = support.literal_call(command) if literal else support.script_call(sandbox, command)
    if seconds_ago:
        guard = support.run_guard_earlier(project, call, sandbox, seconds_ago, **actor.hook())
    else:
        guard = support.run_guard(project, call, sandbox, **actor.hook())
    assert guard.decision == decision, (
        f"the PreToolUse hook answered the fixture call `{command}` with {guard.decision!r}, "
        f"not {decision!r}: {guard.describe()}"
    )
    return call


def _whole(project, sandbox, actor, command, changed=(), snapshot=True):
    """One whole Bash call of ``actor``, now: PreToolUse hook, the command, PostToolUse hook."""
    seen = len(support.finding_lines(project))
    call = _begin(project, sandbox, actor, command) if snapshot else support.script_call(sandbox, command)
    bash = support.run_bash(project, call.command, sandbox)
    support.assert_changed(project, *changed, command=command)
    return support.run_check(project, call, sandbox, bash=bash, seen=seen, **actor.hook())


def _file_tool(project, sandbox, actor, relpath, decision):
    """``actor`` issues a ``Write``: the PreToolUse hook runs. No PostToolUse run follows a file tool."""
    tool_input = {"file_path": str(project / relpath), "content": "written\n"}
    guard = support.run_guard_for_file_tool(project, sandbox, "Write", tool_input, **actor.hook())
    assert guard.decision == decision, (
        f"the PreToolUse hook answered the fixture Write of {relpath} with {guard.decision!r}, "
        f"not {decision!r}: {guard.describe()}"
    )
    if decision == "allow":
        path = project / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("written\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Assertions
# --------------------------------------------------------------------------

def _assert_restored(project, result, what):
    """KPI success 2: the acceptance tests are HEAD again, the breach is recorded, the engineer's own work stays."""
    status = support.porcelain(project, ACCEPTANCE)
    assert status == "", f"{what}: tests/acceptance was not restored from HEAD; git status shows:\n{status}"
    for path in (ACCEPTANCE_FILE, ACCEPTANCE_README):
        assert support.read(project, path) == support.head_text(project, path), (
            f"{what}: {path} does not hold its HEAD content"
        )
    assert not os.path.lexists(project / ADDED), f"{what}: the new test {ADDED} is still there"
    support.assert_caught(result, ACCEPTANCE_FILE, ADDED, what=what, action=support.REVERTED)
    assert support.read(project, SOURCE).endswith("changed\n"), f"{what}: the in-scope change was reverted"
    support.assert_not_recorded(result, SOURCE, what=what)


def _assert_flagged_and_not_restored(project, result, what):
    """DEC-130: attribution is not certain, so the breach is reported, recorded as ``flagged``, and stays."""
    support.assert_caught(result, ACCEPTANCE_FILE, ADDED, what=what, action=support.FLAGGED)
    assert support.read(project, ACCEPTANCE_FILE).endswith("changed\n"), (
        f"{what}: the finding says flagged, and the change to {ACCEPTANCE_FILE} is gone"
    )
    assert support.read(project, ADDED) == "new\n", f"{what}: the finding says flagged, and {ADDED} is gone"
    assert support.read(project, SOURCE).endswith("changed\n"), f"{what}: the in-scope change was reverted"


# --------------------------------------------------------------------------
# Ten minutes have passed
# --------------------------------------------------------------------------

# name: (the actor whose call never ended, its call, the PreToolUse answer, the call is given word for word,
#        the engineer who then changes the acceptance tests)
# The first five are the rows of the table in KD-5.
LEFT_BEHIND = {
    "orchestrator-main-thread-then-an-engineer-subagent": (
        ORCHESTRATOR_MAIN, "ls -la", "allow", False, ENGINEER_SUBAGENT),
    "install-ask-the-owner-declined-then-an-engineer-subagent": (
        ORCHESTRATOR_MAIN, "pip install requests", "ask", True, ENGINEER_SUBAGENT),
    "designer-subagent-that-has-ended-then-the-engineer-s-main-thread": (
        Actor(ENGINEER, DESIGNER, DESIGNER_AGENT), "ls -la", "allow", False, ENGINEER_MAIN),
    "engineer-subagent-then-the-engineer-s-main-thread": (
        Actor(ENGINEER, ENGINEER, ENGINEER_AGENT), "ls -la", "allow", False, ENGINEER_MAIN),
    "subagent-of-an-earlier-session-then-the-engineer-in-a-new-session": (
        Actor(ORCHESTRATOR, DESIGNER, DESIGNER_AGENT), "ls -la", "allow", False,
        Actor(ENGINEER, session_id=support.OTHER_SESSION_ID)),
    "another-engineer-subagent-then-an-engineer-subagent": (
        Actor(ORCHESTRATOR, ENGINEER, OTHER_ENGINEER_AGENT), "ls -la", "allow", False, ENGINEER_SUBAGENT),
}


def _leave_a_call_behind(project, sandbox, case, seconds_ago):
    actor, command, decision, literal, engineer = LEFT_BEHIND[case]
    _begin(project, sandbox, actor, command, seconds_ago=seconds_ago, literal=literal, decision=decision)
    return engineer


@pytest.mark.parametrize("case", sorted(LEFT_BEHIND), ids=sorted(LEFT_BEHIND))
def test_after_ten_minutes_a_call_that_never_ended_no_longer_blocks_the_restore(project, sandbox, case):
    """DEC-142: "or the hook timeout has passed". The owner's answer: ten minutes, default 600 s.

    The actor that left the call behind makes no later call. Eleven minutes
    after that call began, an engineer changes acceptance tests: restored from
    HEAD and recorded as ``reverted``.
    """
    engineer = _leave_a_call_behind(project, sandbox, case, TEN_MINUTES_S + MARGIN_S)
    result = _whole(project, sandbox, engineer, BREACH, changed=BREACH_PATHS)
    _assert_restored(project, result,
                     f"`{BREACH}` by the engineer, {TEN_MINUTES_S + MARGIN_S} s after a call that never ended ({case})")


@pytest.mark.parametrize("case", sorted(LEFT_BEHIND), ids=sorted(LEFT_BEHIND))
def test_before_ten_minutes_have_passed_a_call_that_never_ended_still_blocks_the_restore(project, sandbox, case):
    """DEC-130, KPI failure 2. For all the check knows, the call is still running, and may be writing tests.

    Nine minutes after it began, with no later call of its actor, the
    engineer's change is flagged and not reverted. The limit is ten minutes,
    not less: a Bash call may run that long.
    """
    engineer = _leave_a_call_behind(project, sandbox, case, TEN_MINUTES_S - MARGIN_S)
    result = _whole(project, sandbox, engineer, BREACH, changed=BREACH_PATHS)
    _assert_flagged_and_not_restored(
        project, result,
        f"`{BREACH}` by the engineer, {TEN_MINUTES_S - MARGIN_S} s after a call that never ended ({case})")


# --------------------------------------------------------------------------
# The actor has issued a later tool call
# --------------------------------------------------------------------------

# name: (the actor whose call never ended, the engineer who then changes the acceptance tests)
ACTORS = {
    "orchestrator-main-thread-then-an-engineer-subagent": (ORCHESTRATOR_MAIN, ENGINEER_SUBAGENT),
    "designer-subagent-then-the-engineer-s-main-thread": (Actor(ENGINEER, DESIGNER, DESIGNER_AGENT), ENGINEER_MAIN),
}

SCRATCH_NOTE = f"{support.SCRATCH_REL}/note.md"        # every role may write the scratch set (DEC-108)


def _denied_path(actor):
    """A path the guard denies for this actor.

    DEC-156 (W1-45): the orchestrator may write anywhere except
    tests/acceptance/**. For the orchestrator the denied path is under
    tests/acceptance/; for every other actor of ACTORS it is a source file
    outside the active ticket's allowed_paths.
    Rewrite: owner correction, DEC-156.
    """
    if actor.role == ORCHESTRATOR and actor.subagent is None:
        return ACCEPTANCE_FILE
    return "src/app/main.py"


def _a_bash_call_that_ended(project, sandbox, actor):
    result = _whole(project, sandbox, actor, "ls -la")
    support.assert_silent(result, "`ls -la` on a clean tree")


def _a_bash_call_the_guard_denied(project, sandbox, actor):
    path = _denied_path(actor)
    _begin(project, sandbox, actor, f"echo changed > {path}", literal=True, decision="deny")


def _a_file_tool_call_the_guard_let_through(project, sandbox, actor):
    _file_tool(project, sandbox, actor, SCRATCH_NOTE, "allow")


def _a_file_tool_call_the_guard_denied(project, sandbox, actor):
    _file_tool(project, sandbox, actor, _denied_path(actor), "deny")


LATER_CALLS = {
    "bash-call-that-ended": _a_bash_call_that_ended,
    "bash-call-the-guard-denied": _a_bash_call_the_guard_denied,
    "file-tool-call-the-guard-let-through": _a_file_tool_call_the_guard_let_through,
    "file-tool-call-the-guard-denied": _a_file_tool_call_the_guard_denied,
}


@pytest.mark.parametrize("later_call", sorted(LATER_CALLS), ids=sorted(LATER_CALLS))
@pytest.mark.parametrize("actors", sorted(ACTORS), ids=sorted(ACTORS))
def test_a_later_tool_call_of_its_actor_shows_the_call_is_over(project, sandbox, actors, later_call):
    """DEC-142: "its session has issued a later tool call".

    An actor makes one Bash call at a time. Once the PreToolUse hook has seen a
    later tool call of the same actor, of any tool and whatever the guard
    answered, the earlier call is over. No time has passed. The engineer's
    change to the acceptance tests is restored and recorded as ``reverted``.
    """
    actor, engineer = ACTORS[actors]
    _begin(project, sandbox, actor, "ls -la")                 # the call that never ends
    LATER_CALLS[later_call](project, sandbox, actor)
    status = support.porcelain_all(project)
    assert status == "", f"the fixture's later tool call ({later_call}) left changes in the tree:\n{status}"
    result = _whole(project, sandbox, engineer, BREACH, changed=BREACH_PATHS)
    _assert_restored(project, result,
                     f"`{BREACH}` by the engineer, after a call that never ended and a later "
                     f"{later_call.replace('-', ' ')} of the same actor ({actors})")


@pytest.mark.parametrize("actors", sorted(ACTORS), ids=sorted(ACTORS))
def test_a_later_bash_call_that_has_not_ended_is_an_overlapping_call_itself(project, sandbox, actors):
    """DEC-130. The later call shows the earlier one is over; the later one is open, and not ten minutes old."""
    actor, engineer = ACTORS[actors]
    _begin(project, sandbox, actor, "ls -la")
    _begin(project, sandbox, actor, "ls -la")
    result = _whole(project, sandbox, engineer, BREACH, changed=BREACH_PATHS)
    _assert_flagged_and_not_restored(
        project, result, f"`{BREACH}` by the engineer while a later call of another actor is open ({actors})")


def test_the_designer_s_tests_written_after_its_call_never_ended_stay(project, sandbox):
    """KPI failure 2. The designer subagent's prompt is declined; it goes on and writes a test with ``Write``.

    That later call shows the earlier one is over. The engineer's breach is
    restored; the designer's new test was in the tree before the engineer's
    call and is never touched (DEC-124).
    """
    designer = Actor(ENGINEER, DESIGNER, DESIGNER_AGENT)
    written = f"{ACCEPTANCE}/{WBS}/test_written.py"
    _begin(project, sandbox, designer, "ls -la")
    _file_tool(project, sandbox, designer, written, "allow")
    result = _whole(project, sandbox, ENGINEER_MAIN, BREACH, changed=BREACH_PATHS)
    what = f"`{BREACH}` by the engineer, after the designer subagent's unfinished call and its later Write"
    assert support.read(project, written) == "written\n", f"{what}: the designer's new test {written} is gone"
    assert support.porcelain_all(project, ACCEPTANCE) == f"?? {written}\n", (
        f"{what}: tests/acceptance is not the designer's new test alone:\n{support.porcelain_all(project, ACCEPTANCE)}"
    )
    assert support.read(project, ACCEPTANCE_FILE) == support.head_text(project, ACCEPTANCE_FILE), (
        f"{what}: {ACCEPTANCE_FILE} does not hold its HEAD content"
    )
    support.assert_caught(result, ACCEPTANCE_FILE, ADDED, what=what, action=support.REVERTED)
    support.assert_not_recorded(result, written, SOURCE, what=what)
    assert support.read(project, SOURCE).endswith("changed\n"), f"{what}: the in-scope change was reverted"


# --------------------------------------------------------------------------
# Restoration still requires certain attribution
# --------------------------------------------------------------------------

def test_a_call_known_to_be_over_does_not_hide_another_one_that_is_still_open(project, sandbox):
    """DEC-142: "Restoration still requires certain attribution; otherwise flag."

    The orchestrator's call is over by time. A designer subagent's call began a
    moment ago and has not ended: an overlapping call (DEC-130).
    """
    _begin(project, sandbox, ORCHESTRATOR_MAIN, "ls -la", seconds_ago=TEN_MINUTES_S + MARGIN_S)
    _begin(project, sandbox, Actor(ORCHESTRATOR, DESIGNER, DESIGNER_AGENT), "ls -la")
    result = _whole(project, sandbox, ENGINEER_SUBAGENT, BREACH, changed=BREACH_PATHS)
    _assert_flagged_and_not_restored(
        project, result, f"`{BREACH}` by the engineer subagent while the designer subagent's call is open")


def test_a_call_known_to_be_over_does_not_stand_in_for_a_missing_before_snapshot(project, sandbox):
    """DEC-130, reading 2 of DEC-124: a snapshot belongs to one call. With none of its own, the call is flagged."""
    _begin(project, sandbox, ORCHESTRATOR_MAIN, "ls -la", seconds_ago=TEN_MINUTES_S + MARGIN_S)
    result = _whole(project, sandbox, ENGINEER_SUBAGENT, BREACH, changed=BREACH_PATHS, snapshot=False)
    _assert_flagged_and_not_restored(
        project, result, f"`{BREACH}` by the engineer subagent with no before-snapshot, after a call known to be over")


def test_after_ten_minutes_a_test_changed_before_the_call_is_still_never_put_back(project, sandbox, earlier_work):
    """DEC-124: a path changed before the call is never touched, however old the other actor's call is."""
    draft = f"{ACCEPTANCE}/{WBS}/test_draft.py"
    earlier_work(project, f"echo '# designer' >> {ACCEPTANCE_FILE} && echo draft > {draft}",
                 changed=[ACCEPTANCE_FILE, draft])
    _begin(project, sandbox, Actor(ORCHESTRATOR, DESIGNER, DESIGNER_AGENT), "ls -la",
           seconds_ago=TEN_MINUTES_S + MARGIN_S)
    command = f"echo '# engineer' >> {ACCEPTANCE_FILE}"
    result = _whole(project, sandbox, ENGINEER_SUBAGENT, command)
    what = f"`{command}` by the engineer subagent on the designer's uncommitted test, after a call known to be over"
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.FLAGGED)
    text = support.read(project, ACCEPTANCE_FILE)
    assert "# designer" in text and "# engineer" in text, (
        f"{what}: {ACCEPTANCE_FILE} was put back, or lost the designer's uncommitted work: {text!r}"
    )
    assert support.read(project, draft) == "draft\n", f"{what}: the designer's uncommitted {draft} is gone"
