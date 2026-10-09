"""W1-02 — a decision reached in time is answered exactly as today (DEC-580, points 2, 3 and 4).

DEC-580: "The guard's hook program keeps its own deadline of 20 seconds and
answers "refuse" when it reaches it." Everything that is decided before then
keeps its answer. **Every case of this module is green before the change and
stays green.**

Held, through the hook run as a process on a hook input, each in a temporary
project of its own (``w1_02_deadline_support``; the module's hook processes run
side by side and the module waits once, about four seconds):

- **a step that is slow and ends before the deadline** (the first program the
  hook starts takes four seconds) changes nothing: an allowed call is allowed
  and its bookkeeping is done, a refused one is refused with the reason it has
  without the slow step;
- **a refusal reached in time** is never the deadline's answer;
- **an internal failure** keeps its own answer: exit code 2 and one finding of
  the guard, of the kind it has today;
- **the bound the program has on reading its input** stays as it is: an input
  that is left open is answered after three seconds with exit code 2 and one
  finding (``test_w1_02_guard_failure.py`` holds the same within five seconds);
- **a tiny limit named** in the hook input, the environment and the files a
  worker may write stops no work: an ordinary call is allowed as today.

That an ordinary decision is not slowed down is held by the suite's latency
case (``test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms``), which
this round leaves as it is.

No id and no failure message carries a path or a command.
"""

from __future__ import annotations

import json

import pytest

import w1_02_deadline_support as deadline

Call = deadline.Call
SHORT = (deadline.SHORT_STEP_S,)
TINY_FIELDS = deadline.limit_fields(deadline.TINY)
TINY_ENV = deadline.limit_environment(deadline.TINY)
TINY_FILES = deadline.files_that_name_a_limit(deadline.TINY)

SLOW_AND_ALLOWED = (
    Call("a-Bash-call-by-an-engineer", "Bash", deadline.bash(), deadline.ENGINEER, sleeps=SHORT),
    Call("a-Read-by-a-session-with-no-role", "Read", deadline.read_of(deadline.OUTSIDE_TICKET_REL),
         deadline.NO_ROLE, sleeps=SHORT),
)
SLOW_AND_REFUSED = Call("a-slow-Write-by-an-engineer-outside-its-ticket", "Write",
                        deadline.write_to(deadline.OUTSIDE_TICKET_REL), deadline.ENGINEER, sleeps=SHORT)
REFUSED_AT_ONCE = (
    Call("a-Write-by-an-engineer-outside-its-ticket", "Write", deadline.write_to(deadline.OUTSIDE_TICKET_REL),
         deadline.ENGINEER),
    Call("a-Write-by-a-session-with-no-role", "Write", deadline.write_to(deadline.IN_TICKET_REL), deadline.NO_ROLE),
)
# label -> the kind of the finding the guard leaves today
FAILURES = {"an-input-that-is-not-JSON": "invalid_json", "an-input-with-no-tool-name": "missing_field"}
FAILING = (
    Call("an-input-that-is-not-JSON", "Bash", deadline.bash(), raw="this is not JSON {"),
    Call("an-input-with-no-tool-name", "Bash", deadline.bash(),
         raw=json.dumps({"session_id": "w1-02-acceptance-session", "hook_event_name": "PreToolUse",
                         "tool_input": deadline.bash()})),
)
# label -> the kind of the finding the guard leaves today
LEFT_OPEN = {"an-input-left-open-with-nothing-sent": "empty_input",
             "an-input-left-open-after-half-of-the-object": "invalid_json"}
INPUT_LEFT_OPEN = (
    Call("an-input-left-open-with-nothing-sent", "Bash", deadline.bash(), send="nothing"),
    Call("an-input-left-open-after-half-of-the-object", "Bash", deadline.bash(), send="half"),
)
TINY_LIMIT = (
    Call("a-Bash-call-by-an-engineer-with-a-tiny-limit-named", "Bash", {**deadline.bash(), **TINY_FIELDS},
         deadline.ENGINEER, top=TINY_FIELDS, env=TINY_ENV, prepare=TINY_FILES),
    Call("a-Write-by-the-orchestrator-with-a-tiny-limit-named", "Write",
         lambda project: {**deadline.write_to(deadline.OUTSIDE_TICKET_REL)(project), **TINY_FIELDS},
         deadline.ORCHESTRATOR, top=TINY_FIELDS, env=TINY_ENV, prepare=TINY_FILES),
    Call("a-Bash-call-by-an-engineer-with-a-tiny-limit-named-and-a-slow-step", "Bash",
         {**deadline.bash(), **TINY_FIELDS}, deadline.ENGINEER, sleeps=SHORT, top=TINY_FIELDS, env=TINY_ENV,
         prepare=TINY_FILES),
)
EVERY_CALL = SLOW_AND_ALLOWED + (SLOW_AND_REFUSED,) + REFUSED_AT_ONCE + FAILING + INPUT_LEFT_OPEN + TINY_LIMIT


def _labels(calls):
    return [call.label for call in calls]


@pytest.fixture(scope="module")
def prompt(hook, tmp_path_factory):
    """Every hook process of the module, started together: ``{label: Outcome}``."""
    return deadline.run_side_by_side(tmp_path_factory.mktemp("deadline-in-time"), EVERY_CALL,
                                     limit_s=deadline.IN_TIME_UPPER_S)


def _assert_answered_in_time(outcome, what, slow):
    assert outcome.answered, f"{what}: {outcome.describe()}"
    if slow:
        assert outcome.stand_in_starts >= 1, f"{what}: the hook did not start the stand-in program"
        assert outcome.result.seconds >= deadline.SHORT_STEP_S, (
            f"{what} was answered before its slow step could have ended: {outcome.describe()}"
        )
    deadline.assert_not_the_deadline_s_answer(outcome, what)


def _assert_allowed_with_its_bookkeeping(outcome, what, bash):
    assert outcome.result.decision == "allow", f"{what} was not allowed: {outcome.describe()}"
    assert not deadline.new_findings(outcome), f"{what} left a finding: {len(deadline.new_findings(outcome))}"
    if bash:
        assert deadline.pending_entries(outcome.project), (
            f"{what} was allowed, but the hook noted nothing for the check after the call"
        )


def _one_guard_finding(outcome, what):
    new = deadline.new_findings(outcome)
    assert len(new) == 1, f"{what}: expected one new finding, found {len(new)}"
    finding = json.loads(new[0])
    assert finding.get("source") == "guard", f"{what}: the finding does not name its source as guard"
    return finding


@pytest.mark.parametrize("label", _labels(SLOW_AND_ALLOWED))
def test_a_step_that_ends_before_the_deadline_leaves_an_allowed_call_allowed(prompt, label):
    """Point 3: allowed after its four seconds, and the bookkeeping for a Bash call that is let through is done."""
    outcome = prompt[label]
    _assert_answered_in_time(outcome, f"{label} with a slow step", slow=True)
    _assert_allowed_with_its_bookkeeping(outcome, f"{label} with a slow step", bash="Bash" in label)


def test_a_step_that_ends_before_the_deadline_leaves_a_refused_call_refused_with_its_own_reason(prompt):
    """Point 3: the reason is the one the same call gets without the slow step."""
    slow, at_once = prompt[SLOW_AND_REFUSED.label], prompt[REFUSED_AT_ONCE[0].label]
    _assert_answered_in_time(slow, "the slow refused call", slow=True)
    reason, twin = deadline.refusal_of(slow), deadline.refusal_of(at_once)
    assert reason is not None, f"the slow refused call was not refused by a rule: {slow.describe()}"
    assert twin is not None, f"the same call without the slow step was not refused by a rule: {at_once.describe()}"
    assert reason.replace(str(slow.project), "<project>") == twin.replace(str(at_once.project), "<project>"), (
        "a slow step that ended in time changed the reason of the refusal"
    )


@pytest.mark.parametrize("label", _labels(REFUSED_AT_ONCE))
def test_a_refusal_reached_in_time_is_never_the_deadline_s_answer(prompt, label):
    """Point 3: refused by its own rule, with its own reason."""
    outcome = prompt[label]
    _assert_answered_in_time(outcome, label, slow=False)
    assert deadline.refusal_of(outcome) is not None, f"{label} was not refused by a rule: {outcome.describe()}"
    assert not deadline.new_findings(outcome), f"the refusal of {label} left a finding"


@pytest.mark.parametrize("label", sorted(FAILURES))
def test_an_internal_failure_keeps_its_own_answer(prompt, label):
    """Point 3: exit code 2 and one finding of the guard, as today (DEC-110)."""
    outcome = prompt[label]
    _assert_answered_in_time(outcome, label, slow=False)
    assert outcome.result.returncode == 2, f"{label}: the guard did not exit with code 2: {outcome.describe()}"
    finding = _one_guard_finding(outcome, label)
    assert finding.get("kind") == FAILURES[label], f"{label}: the finding's kind changed"


@pytest.mark.parametrize("label", _labels(INPUT_LEFT_OPEN))
def test_the_bound_on_reading_the_input_stays_as_it_is(prompt, label):
    """Point 2: three seconds, then exit code 2 and one finding: not the deadline's answer, and not at 20 seconds."""
    outcome = prompt[label]
    _assert_answered_in_time(outcome, label, slow=False)
    seconds = outcome.result.seconds
    assert deadline.INPUT_LOWER_S <= seconds <= deadline.INPUT_UPPER_S, (
        f"{label} was answered after {seconds:.1f} s; the program's bound on reading its input is "
        f"{deadline.INPUT_BOUND_S:.0f} s (held: {deadline.INPUT_LOWER_S} s to {deadline.INPUT_UPPER_S:.0f} s)"
    )
    assert outcome.result.returncode == 2, f"{label}: the guard did not exit with code 2: {outcome.describe()}"
    finding = _one_guard_finding(outcome, label)
    assert finding.get("kind") == LEFT_OPEN[label], f"{label}: the finding's kind changed"


@pytest.mark.parametrize("label", _labels(TINY_LIMIT))
def test_a_tiny_limit_named_stops_no_work(prompt, label):
    """Point 4: the deadline cannot be shortened into a way to stop all work: an ordinary call is allowed as today."""
    outcome = prompt[label]
    _assert_answered_in_time(outcome, label, slow="slow-step" in label)
    _assert_allowed_with_its_bookkeeping(outcome, label, bash="Bash" in label)
