"""KPI success 3, "give the same result on repeat" [CAP-05.d, "deterministic"].

DEC-357: the same state. A repeat succeeds and leaves the project as the first
run left it; the two ``result`` objects need not be equal field for field.

The repeats of ``--cancel-agents`` and ``--rollback`` are with their own
cases, in ``test_w1_28_cancel.py`` and ``test_w1_28_rollback.py``. Every call
here is the owner's (no ``GOV_ROLE``, DEC-365).
"""

from __future__ import annotations

import w1_28_support as support


def test_pause_on_a_paused_project_succeeds_and_stays_paused(paused, sandbox, pause, interface):
    support.succeeded(pause(), interface)
    assert support.is_paused(paused), "the second gov pause cleared the flag"
    support.assert_denied(support.guard_write(paused, sandbox, support.ENGINEER), "after two pauses, the write")


def test_one_off_lifts_however_many_pauses(paused, sandbox, pause, lift, interface):
    """A pause is a flag, not a count. The lift is the owner's in person (DEC-409)."""
    support.succeeded(pause(), interface)
    lift()
    assert not support.is_paused(paused), "one gov pause --off did not lift two pauses"
    support.assert_allowed(support.guard_write(paused, sandbox, support.ENGINEER), "after --off, the write")


def test_off_on_a_project_that_is_not_paused_succeeds_and_changes_nothing(project, sandbox, lift):
    lift()  # DEC-409: the owner in person
    assert not support.is_paused(project)
    support.assert_allowed(support.guard_write(project, sandbox, support.ENGINEER), "after --off, the write")


def test_off_twice_gives_the_same_result(paused, lift):
    lift()  # DEC-409: the owner in person, twice
    lift()
    assert not support.is_paused(paused), "the second gov pause --off set the flag again"
