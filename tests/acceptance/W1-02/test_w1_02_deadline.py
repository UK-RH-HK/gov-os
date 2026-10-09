"""W1-02 — a decision still running at the guard's own deadline is refused (DEC-580, points 1 and 4).

DEC-580: "The guard's hook program keeps its own deadline of 20 seconds and
answers "refuse" when it reaches it."

Why: the harness ends a hook at its time limit and lets the call through
(``docs/research/EXP-hook-time-limit.md``), so a decision that is still running
then is lost and the call runs. The hook entries carry a limit of 60 seconds.

Every case asks the hook, run as a process on a hook input, in a temporary
project of its own (``w1_02_deadline_support``). **The module waits once**: all
its hook processes are started side by side, each with a slow step of its own,
and each case asserts on one of them afterwards.

**Where the slow step sits** (how each is made: the support module's head):

- *before any rule on the call*: the first program a decision starts does not
  end (a Bash call by an engineer, where the stand-in has a child of its own; a
  Write by the orchestrator; a Read by a session with no role); the bookkeeping
  the hook does before it decides waits on a named pipe (a Bash call);
- *after the rules have allowed the call*: the bookkeeping for a Write that is
  let through waits on a named pipe; every program the hook starts for a Bash
  call that is let through takes a few seconds, none of them long, and together
  they pass 20 seconds;
- *spread over reading the input and a step*: the input arrives after two
  seconds and the first program takes nineteen and a half.

Each of these calls is one the rules allow. **Held for each**: the hook ends by
itself with a refusal in the form a rule's refusal has (exit code 0, a deny
decision), whose reason says the guard could not decide in time and names
DEC-580; not before ``LOWER_S`` and by ``UPPER_S``; the answer carries nothing
of the call; nothing the hook started is still running shortly afterwards.

**Point 4**: a field, a variable or a file that names a larger limit, or
switches the limit off, changes nothing of this.

**Red today**: the program as built keeps no deadline. It waits for the slow
step to its end (the case ends the process at ``PROCESS_LIMIT_S``: no answer),
or it allows the call when the steps have ended (after about 22 s and 28 s).

No id and no failure message carries a path or a command.
"""

from __future__ import annotations

import pytest

import w1_02_deadline_support as deadline

Call = deadline.Call
NEVER = (deadline.STAND_IN_ENDS_S,)      # the first program the hook starts does not end before the case does
A_FEW_SECONDS = 5.5                      # four such steps pass the deadline; no single one comes near it
LATE_INPUT_S = 2.0                       # inside the program's bound on reading its input
ALMOST_THE_DEADLINE_S = 19.5             # alone under the deadline; with the late input over it

POINT_1 = (
    Call("a-Bash-call-by-an-engineer-whose-first-program-does-not-end", "Bash", deadline.bash(),
         deadline.ENGINEER, sleeps=NEVER, child=True),
    Call("a-Write-by-the-orchestrator-whose-first-program-does-not-end", "Write",
         deadline.write_to(deadline.OUTSIDE_TICKET_REL), deadline.ORCHESTRATOR, sleeps=NEVER),
    Call("a-Read-by-a-session-with-no-role-whose-first-program-does-not-end", "Read",
         deadline.read_of(deadline.OUTSIDE_TICKET_REL), deadline.NO_ROLE, sleeps=NEVER),
    Call("a-Bash-call-by-an-engineer-with-a-pipe-in-the-bookkeeping-before-the-decision", "Bash", deadline.bash(),
         deadline.ENGINEER, prepare=deadline.a_pipe_among_the_pending_calls),
    Call("a-Write-by-an-engineer-with-a-pipe-in-the-bookkeeping-after-the-rules-allowed-it", "Write",
         deadline.write_to(deadline.IN_TICKET_REL), deadline.ENGINEER, prepare=deadline.a_pipe_at_the_counter),
    Call("a-Bash-call-by-the-orchestrator-whose-every-program-takes-a-few-seconds", "Bash", deadline.bash(),
         deadline.ORCHESTRATOR, every=A_FEW_SECONDS),
    Call("a-Bash-call-by-an-engineer-whose-input-comes-late-and-whose-first-program-is-slow", "Bash",
         deadline.bash(), deadline.ENGINEER, sleeps=(ALMOST_THE_DEADLINE_S,), send_after=LATE_INPUT_S),
)

# Each: a Bash call by an engineer that the rules allow, whose first program does not end.
POINT_4 = (
    Call("fields-named-like-a-time-limit-at-the-top-of-the-hook-input", "Bash", deadline.bash(),
         sleeps=NEVER, top=deadline.limit_fields(deadline.LARGE)),
    Call("fields-named-like-a-time-limit-inside-the-tool-input", "Bash",
         {**deadline.bash(), **deadline.limit_fields(deadline.LARGE)}, sleeps=NEVER),
    Call("variables-named-like-a-time-limit-with-a-large-value-and-the-switches-set", "Bash", deadline.bash(),
         sleeps=NEVER, env=deadline.limit_environment(deadline.LARGE)),
    Call("variables-named-like-a-time-limit-set-to-zero-and-the-switches-set", "Bash", deadline.bash(),
         sleeps=NEVER, env=deadline.limit_environment(0, "true")),
    Call("files-a-worker-may-write-that-name-a-larger-limit", "Bash", deadline.bash(),
         sleeps=NEVER, prepare=deadline.files_that_name_a_limit(deadline.LARGE)),
)

LABELS_1 = [call.label for call in POINT_1]
LABELS_4 = [call.label for call in POINT_4]
# The calls whose slow step is a program: the stand-in's process id is known to the case.
WITH_A_PROGRAM = [call.label for call in POINT_1 + POINT_4 if call.sleeps or call.every]
WITH_A_CHILD = [call.label for call in POINT_1 + POINT_4 if call.child]


@pytest.fixture(scope="module")
def late(hook, tmp_path_factory):
    """Every hook process of the module, started together: ``{label: Outcome}``. One wait for all cases."""
    return deadline.run_side_by_side(tmp_path_factory.mktemp("deadline"), POINT_1 + POINT_4)


@pytest.mark.parametrize("label", LABELS_1)
def test_a_decision_still_running_at_the_deadline_is_refused(late, label):
    """Point 1: a call the rules would allow is refused, in a refusal's form, shortly after 20 seconds."""
    outcome = late[label]
    deadline.assert_refused_at_the_deadline(outcome, f"'{label}'")
    deadline.assert_within_the_deadline_s_window(outcome, f"'{label}'")


@pytest.mark.parametrize("label", LABELS_4)
def test_nothing_a_session_can_set_raises_the_deadline_or_switches_it_off(late, label):
    """Point 4: the deadline's value is the guard's own: the answer is the same refusal, at the same time."""
    outcome = late[label]
    deadline.assert_refused_at_the_deadline(outcome, f"the call with {label}")
    deadline.assert_within_the_deadline_s_window(outcome, f"the call with {label}")


def test_the_deadline_s_refusal_carries_nothing_of_the_call(late):
    """Point 1: the reason names the rule and the decision: no command, no content, no path, neither protected file."""
    unanswered = [label for label in LABELS_1 + LABELS_4 if deadline.refusal_of(late[label]) is None]
    assert not unanswered, f"not refused in a refusal's form: {unanswered}"
    for label in LABELS_1 + LABELS_4:
        outcome = late[label]
        text = deadline.said(outcome)
        # Positions only: a failure must not print what an answer must not print.
        shown = [index for index, value in enumerate(deadline.secrets_of(outcome)) if value in text]
        assert not shown, f"the answer to '{label}' carries {len(shown)} value(s) of the call (positions {shown})"


def test_nothing_the_hook_started_is_left_running_after_its_answer(late):
    """Point 1: the slow step's process, and a child of that process, are gone shortly after the answer."""
    unanswered = [label for label in WITH_A_PROGRAM if not late[label].answered]
    assert not unanswered, f"no answer, the hook was ended by the case: {unanswered}"
    for label in WITH_A_PROGRAM:
        outcome = late[label]
        assert outcome.stand_in_starts >= 1, f"'{label}': the hook did not start the stand-in program"
        assert outcome.left_running == 0, (
            f"'{label}': {outcome.left_running} process(es) the hook started were still running "
            f"{deadline.GONE_WITHIN_S:.0f} s after its answer ({outcome.describe()})"
        )
    for label in WITH_A_CHILD:
        assert late[label].children >= 1, f"'{label}': the stand-in program did not start its own child"
