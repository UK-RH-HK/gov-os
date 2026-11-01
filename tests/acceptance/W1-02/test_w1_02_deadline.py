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
  end (a Bash call by an engineer; a
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

**Since W2-L160** (``Rewrite-Reason: DEC-951 (P-B1-1); DEC-783 item 2; W2-L160``):
the first program a decision starts is the freeze look-up, which runs git by
absolute path with a limit of its own of 15 s (DEC-783 item 2), so a stand-in
first on the search path no longer reaches it. The three calls whose first
program does not end now make the look-up's real git wait for ever, on the
repository's configuration as a named pipe; each is held to a refusal in a
rule's form at the look-up's limit (``LOOK_UP_LOWER_S`` to ``LOOK_UP_UPPER_S``).
Every other call keeps the deadline of DEC-580, its reason and its window, by a
slow step the look-up does not cover: a named pipe of the bookkeeping (point 4,
and the late input, whose pipe the case lets go 19.5 s after the input). The
labels are kept, so that a case is the same case before and after.

**Since the ticket's batch 2** (``Rewrite-Reason: DEC-802 (P-B1-2); W2-L160``):
the Bash bookkeeping starts git by the look-up's absolute path too. The
orchestrator's Bash call whose every program takes a few seconds now holds each
git the hook starts 5.5 s, once, on the repository's configuration as a pipe
paced by program: the look-up ends after one such step, inside its 15 s, and the
bookkeeping's steps pass the deadline, which refuses with DEC-580's reason in
its window. No call has a stand-in first on the search path any more.

No id and no failure message carries a path or a command.
"""

from __future__ import annotations

import pytest

import w1_02_deadline_support as deadline

Call = deadline.Call
A_FEW_SECONDS = 5.5                      # four such steps pass the deadline; no single one comes near it
LATE_INPUT_S = 2.0                       # inside the program's bound on reading its input
ALMOST_THE_DEADLINE_S = 19.5             # alone under the deadline; with the late input over it

POINT_1 = (
    # Rewrite-Reason: DEC-951 (P-B1-1); DEC-783 item 2; W2-L160. The first program is the freeze look-up's real git,
    # which waits for ever on the repository's configuration: the look-up's limit refuses (was: a stand-in first on
    # the search path, with a child of its own for the first call).
    Call("a-Bash-call-by-an-engineer-whose-first-program-does-not-end", "Bash", deadline.bash(),
         deadline.ENGINEER, config_after=deadline.NEVER),
    Call("a-Write-by-the-orchestrator-whose-first-program-does-not-end", "Write",
         deadline.write_to(deadline.OUTSIDE_TICKET_REL), deadline.ORCHESTRATOR, config_after=deadline.NEVER),
    Call("a-Read-by-a-session-with-no-role-whose-first-program-does-not-end", "Read",
         deadline.read_of(deadline.OUTSIDE_TICKET_REL), deadline.NO_ROLE, config_after=deadline.NEVER),
    Call("a-Bash-call-by-an-engineer-with-a-pipe-in-the-bookkeeping-before-the-decision", "Bash", deadline.bash(),
         deadline.ENGINEER, prepare=deadline.a_pipe_among_the_pending_calls),
    Call("a-Write-by-an-engineer-with-a-pipe-in-the-bookkeeping-after-the-rules-allowed-it", "Write",
         deadline.write_to(deadline.IN_TICKET_REL), deadline.ENGINEER, prepare=deadline.a_pipe_at_the_counter),
    # Rewrite-Reason: DEC-802 (P-B1-2); W2-L160. The Bash bookkeeping starts git by absolute path since the ticket's
    # batch 2: every git the hook starts, the look-up's and the bookkeeping's, is held a few seconds by the repository's
    # configuration, paced by program (was: a stand-in first on the search path, sleeping on every start). The look-up
    # ends after one such step, well inside its 15 s; the bookkeeping's steps pass the deadline.
    Call("a-Bash-call-by-the-orchestrator-whose-every-program-takes-a-few-seconds", "Bash", deadline.bash(),
         deadline.ORCHESTRATOR, config_every=A_FEW_SECONDS),
    # Rewrite-Reason: DEC-951 (P-B1-1); DEC-783 item 2; W2-L160. The slow step is the bookkeeping before the
    # decision, a named pipe the case lets go 19.5 s after the input (was: the first program, now the look-up).
    Call("a-Bash-call-by-an-engineer-whose-input-comes-late-and-whose-first-program-is-slow", "Bash",
         deadline.bash(), deadline.ENGINEER, prepare=deadline.a_pipe_among_the_pending_calls,
         release_after=ALMOST_THE_DEADLINE_S, send_after=LATE_INPUT_S),
)

# Each: a Bash call by an engineer that the rules allow, whose bookkeeping before the decision waits on a named pipe.
# Rewrite-Reason: DEC-951 (P-B1-1); DEC-783 item 2; W2-L160 (was: whose first program does not end, now the look-up,
# whose own limit would answer before the deadline).
PIPE = deadline.a_pipe_among_the_pending_calls
POINT_4 = (
    Call("fields-named-like-a-time-limit-at-the-top-of-the-hook-input", "Bash", deadline.bash(),
         prepare=PIPE, top=deadline.limit_fields(deadline.LARGE)),
    Call("fields-named-like-a-time-limit-inside-the-tool-input", "Bash",
         {**deadline.bash(), **deadline.limit_fields(deadline.LARGE)}, prepare=PIPE),
    Call("variables-named-like-a-time-limit-with-a-large-value-and-the-switches-set", "Bash", deadline.bash(),
         prepare=PIPE, env=deadline.limit_environment(deadline.LARGE)),
    Call("variables-named-like-a-time-limit-set-to-zero-and-the-switches-set", "Bash", deadline.bash(),
         prepare=PIPE, env=deadline.limit_environment(0, "true")),
    Call("files-a-worker-may-write-that-name-a-larger-limit", "Bash", deadline.bash(),
         prepare=deadline.each_of(deadline.files_that_name_a_limit(deadline.LARGE), PIPE)),
)

LABELS_1 = [call.label for call in POINT_1]
LABELS_4 = [call.label for call in POINT_4]
# The calls whose slow step is a program: the real git, seen in the project (Rewrite-Reason: DEC-951 (P-B1-1);
# DEC-783 item 2; DEC-802 (P-B1-2); W2-L160). No call has a stand-in any more, and so no stand-in's child.
WITH_A_REAL_GIT = [call.label for call in POINT_1 + POINT_4 if call.config]
WITH_A_PROGRAM = WITH_A_REAL_GIT
# The calls whose every git is held a few seconds: the paced configuration held one at least.
PACED = [call.label for call in POINT_1 + POINT_4 if call.config_every is not None]
# The calls whose slow step is the freeze look-up: its own limit answers (DEC-783 item 2).
AT_THE_LOOK_UP = [call.label for call in POINT_1 + POINT_4 if call.config_after == deadline.NEVER]


@pytest.fixture(scope="module")
def late(hook, tmp_path_factory):
    """Every hook process of the module, started together: ``{label: Outcome}``. One wait for all cases."""
    return deadline.run_side_by_side(tmp_path_factory.mktemp("deadline"), POINT_1 + POINT_4)


@pytest.mark.parametrize("label", LABELS_1)
def test_a_decision_still_running_at_the_deadline_is_refused(late, label):
    """Point 1: a call the rules would allow is refused, in a refusal's form, shortly after 20 seconds.

    Rewrite-Reason: DEC-951 (P-B1-1); DEC-783 item 2; W2-L160. A call whose first program does not end is refused at
    the freeze look-up's own limit of 15 s, in a refusal's form; every other call at the deadline, as before.
    """
    outcome = late[label]
    if label in AT_THE_LOOK_UP:
        deadline.assert_refused_by_the_look_up_s_limit(outcome, f"'{label}'")
        return
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
    """Point 1: the slow step's process is gone shortly after the answer.

    Rewrite-Reason: DEC-951 (P-B1-1); DEC-783 item 2; DEC-802 (P-B1-2); W2-L160. The slow step's process is the real
    git, seen in the project; for the paced call, the configuration held it (was: the stand-in's own record, and the
    check of the stand-in's child, empty since the look-up's rewrite: P-W1-02-CHILD, with the orchestrator).
    """
    unanswered = [label for label in WITH_A_PROGRAM if not late[label].answered]
    assert not unanswered, f"no answer, the hook was ended by the case: {unanswered}"
    for label in WITH_A_PROGRAM:
        outcome = late[label]
        assert outcome.seen >= 1, f"'{label}': no process the hook started was seen in the project"
        if label in PACED:
            assert outcome.held >= 1, f"'{label}': the hook started no git that the configuration held"
        assert outcome.left_running == 0, (
            f"'{label}': {outcome.left_running} process(es) the hook started were still running "
            f"{deadline.GONE_WITHIN_S:.0f} s after its answer ({outcome.describe()})"
        )
