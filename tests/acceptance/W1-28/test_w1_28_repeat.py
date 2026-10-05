"""KPI success 4, second clause [CAP-05.d, "deterministic"]: "give the same result on repeat".

Read as a statement about state (decision package DP-7): a repeat succeeds as
the first run did, and leaves the project as the first run left it. Whether
the two ``result`` objects are equal field by field is not asserted.

The repeats of ``--cancel-agents`` and ``--rollback`` are with their own
cases, in ``test_w1_28_cancel.py`` and ``test_w1_28_rollback.py``.
"""

from __future__ import annotations

import w1_28_support as support


def test_pause_on_a_paused_project_succeeds_and_stays_paused(paused, sandbox, pause, interface):
    support.succeeded(pause(), interface)
    assert support.is_paused(paused), "the second gov pause cleared the flag"
    support.assert_denied(support.guard_write(paused, sandbox, support.ENGINEER), "after two pauses, the write")


def test_one_off_lifts_however_many_pauses(paused, sandbox, pause, interface):
    """A pause is a flag, not a count."""
    support.succeeded(pause(), interface)
    support.succeeded(pause("--off"), interface)
    assert not support.is_paused(paused), "one gov pause --off did not lift two pauses"
    support.assert_allowed(support.guard_write(paused, sandbox, support.ENGINEER), "after --off, the write")


def test_off_on_a_project_that_is_not_paused_succeeds_and_changes_nothing(project, sandbox, pause, interface):
    support.succeeded(pause("--off"), interface)
    assert not support.is_paused(project)
    support.assert_allowed(support.guard_write(project, sandbox, support.ENGINEER), "after --off, the write")


def test_off_twice_gives_the_same_result(paused, pause, interface):
    support.succeeded(pause("--off"), interface)
    support.succeeded(pause("--off"), interface)
    assert not support.is_paused(paused), "the second gov pause --off set the flag again"
