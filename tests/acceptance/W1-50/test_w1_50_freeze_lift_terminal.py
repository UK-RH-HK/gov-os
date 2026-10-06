"""KPI success 5 (DEC-409, rule 2): the lift needs a terminal on both sides and a one-time code typed back.

"gov pause --off requires an interactive terminal (stdin and stdout are TTYs)
and a one-time random code LIFT-<4 digits> typed back; a wrong code, piped
input or no TTY refuses and nothing changes."

Every case calls the internal function ``gov.pause.command.lift`` in a new
process (``w1_50_freeze_lift``), with the ancestry of a plain terminal planted,
so that the terminal and the code are the only things that can refuse. The
terminal is a pseudo-terminal the driver opens; the driver reads the shown
code from it and types the reply on it, as a person would. A planted pipe is
no terminal: the product asks ``os.isatty`` itself, so the seam is no way
round rule 2 (``w1_50_freeze_README.md``).

Every project is this test's own temporary repository.
"""

from __future__ import annotations

import os
import re

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import freeze_frozen, freeze_project, freeze_sandbox  # noqa: F401  fixtures

lift = support.lift_support

NAMES_THE_TERMINAL = re.compile(r"terminal|tty", re.IGNORECASE)
NAMES_THE_CODE = re.compile(r"code", re.IGNORECASE)
RUNS = 12


def _the_one_code(run, what):
    codes = set(run.codes)
    assert len(codes) == 1, f"{what}: the terminal did not show exactly one code LIFT-<4 digits>: {run.shown!r}"
    return codes.pop()


def _assert_secret(project, run, code, what):
    """The code is shown on the terminal and nowhere else: no file of the project, no result, no error."""
    assert support.files_holding(project, code) == [], \
        f"{what}: the code {code} is written under the project: {support.files_holding(project, code)}"
    assert code not in run.says(), f"{what}: the code {code} is in what the function gave back: {run.says()}"


def test_the_shown_code_typed_back_on_a_terminal_lifts(freeze_frozen, freeze_sandbox):
    run = lift.lift(freeze_frozen, freeze_sandbox)

    assert run.status == lift.LIFTED, f"the shown code was typed back on a terminal: {run.describe()}"
    code = _the_one_code(run, "the lift")
    assert run.typed == code + "\n"
    assert isinstance(run.result, dict) and run.result.get("paused") is False, \
        f"the result does not say that the pause is lifted: {run.result!r}"
    assert not os.path.lexists(support.flag(freeze_frozen)), f"the lift left {support.FLAG_REL}"
    support.assert_not_frozen(support.guard_write(freeze_frozen, freeze_sandbox), "after the lift")
    _assert_secret(freeze_frozen, run, code, "after the lift")


@pytest.mark.parametrize("terminal", [lift.PIPE_IN, lift.PIPE_OUT, lift.PIPES, lift.NO_TERMINAL])
def test_without_a_terminal_on_both_sides_the_lift_refuses(freeze_frozen, freeze_sandbox, terminal):
    """Piped input; an output that is no terminal; neither. Whatever is shown is typed back right, and it still
    refuses: the product itself asks whether what it reads and writes are terminals."""
    before = support.flag_state(freeze_frozen)

    run = lift.lift(freeze_frozen, freeze_sandbox, terminal=terminal)

    assert run.status == lift.REFUSED, f"{terminal}: the lift was not refused: {run.describe()}"
    assert NAMES_THE_TERMINAL.search(run.message), \
        f"{terminal}: the refusal does not name the missing terminal as its reason: {run.message!r}"
    support.assert_nothing_changed(freeze_frozen, before, terminal)
    for code in set(lift.CODE.findall(run.shown)):
        _assert_secret(freeze_frozen, run, code, terminal)


@pytest.mark.parametrize("reply", [lift.WRONG, lift.EMPTY_LINE, lift.END_OF_INPUT])
def test_anything_but_the_shown_code_refuses_at_once(freeze_frozen, freeze_sandbox, reply):
    """One attempt for each run: a wrong code, an empty line or the end of the input ends the run. A function that
    asks again, or goes on waiting, does not come back and the case fails."""
    before = support.flag_state(freeze_frozen)

    run = lift.lift(freeze_frozen, freeze_sandbox, reply=reply)

    assert run.status == lift.REFUSED, f"{reply}: the lift was not refused: {run.describe()}"
    code = _the_one_code(run, reply)
    after_the_reply = run.shown[len(run.shown_before_reply):]
    typed = (run.typed or "").strip()
    assert not [c for c in lift.CODE.findall(after_the_reply) if c != typed], \
        f"{reply}: a code was shown again after the reply: {after_the_reply!r}"
    assert NAMES_THE_CODE.search(run.message), f"{reply}: the refusal does not name the code: {run.message!r}"
    support.assert_nothing_changed(freeze_frozen, before, reply)
    support.assert_frozen(support.guard_write(freeze_frozen, freeze_sandbox), f"after the refused lift ({reply})")
    _assert_secret(freeze_frozen, run, code, reply)


def test_the_code_is_new_on_every_run_and_no_seed_fixes_it(freeze_frozen, freeze_sandbox):
    """The code comes from the system's random source. Twelve runs in one process, Python's ``random`` seeded
    with the same number before each: a code drawn from that generator would be the same twelve times. Twelve equal
    codes from the system's source have a chance of one in 10^44."""
    runs = lift.drive(freeze_frozen, freeze_sandbox, reply=lift.WRONG, runs=RUNS, seed=0)
    lift.built(runs[0])

    assert len(runs) == RUNS and all(run.status == lift.REFUSED for run in runs), \
        f"not every run with a wrong code was refused: {[run.describe() for run in runs]}"
    codes = [_the_one_code(run, f"run {number}") for number, run in enumerate(runs, 1)]
    assert all(re.fullmatch(r"LIFT-\d{4}", code) for code in codes), codes
    assert len(set(codes)) > 1, f"the code is the same on every run: {codes}"


# --------------------------------------------------------------------------
# When nothing is frozen
# --------------------------------------------------------------------------

@pytest.mark.parametrize("planted", [{"ancestry": lift.SESSION_ANCESTRIES["operator-console"]},
                                     {"terminal": lift.PIPES}], ids=["under-a-session", "without-a-terminal"])
def test_with_nothing_frozen_the_checks_still_come_first(freeze_project, freeze_sandbox, planted):
    """DEC-409's rules 1 and 2 are about the command ``gov pause --off``, not about a flag that is there: an agent
    session learns nothing from it and changes nothing with it."""
    before = support.flag_state(freeze_project)

    run = lift.lift(freeze_project, freeze_sandbox, **planted)

    assert run.status == lift.REFUSED, f"with no freeze, the lift form was not refused: {run.describe()}"
    support.assert_nothing_changed(freeze_project, before, "with no freeze")


def test_with_nothing_frozen_the_owner_in_person_is_told_not_paused(freeze_project, freeze_sandbox):
    """W1-28: ``--off`` on a project that is not paused succeeds and changes nothing. Whether the code is asked for
    then is not pinned: the driver types it back when it is shown."""
    result = lift.lift_as_the_owner(freeze_project, freeze_sandbox)

    assert isinstance(result, dict) and result.get("paused") is False, f"the result does not say not paused: {result!r}"
    assert not os.path.lexists(support.flag(freeze_project))
