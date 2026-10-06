"""W1-50, KPI line 1 (DEC-402), the command's half: ``gov pause`` writes the marker line.

"A freeze flag set by gov pause carries a marker line."

DEC-402: "a marker line written by ``gov pause`` (for example ``FROZEN``, with
who and when)". Pinned in ``w1_50_freeze_README.md``:

- the flag's first line is ``FROZEN <who> <when>``;
- *who* is the caller of DEC-365: ``owner`` with ``GOV_ROLE`` unset,
  ``orchestrator`` otherwise (a worker role is refused and writes nothing);
- *when* is a UTC time in the form the project's records use,
  ``YYYY-MM-DDTHH:MM:SSZ``. Its form is tested, never its value.

Every way of setting the flag writes it: a plain pause, ``--cancel-agents``
and ``--rollback`` (DEC-368, DEC-378). A pause on a project where something
unmarked already sits at the path (the sandbox's placeholder) still freezes
it, and a second pause on a frozen project stays a success, as W1-28's suite
holds it. ``gov pause`` is run as W1-28's suite runs it, on a temporary
project only.
"""

from __future__ import annotations

import os

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import (  # noqa: F401  fixtures
    freeze_interface, freeze_pause, freeze_project, freeze_sandbox)

pause_support = support.pause_support
OWNER, ORCHESTRATOR = pause_support.OWNER, pause_support.ORCHESTRATOR
NAME_OF = {OWNER: support.OWNER_NAME, ORCHESTRATOR: ORCHESTRATOR}
CALLERS = pytest.mark.parametrize("caller", (OWNER, ORCHESTRATOR), ids=("owner", "orchestrator"))


@CALLERS
def test_pause_writes_the_marker_line_with_the_caller_and_the_time(freeze_project, freeze_pause, freeze_interface,
                                                                   caller):
    pause_support.succeeded(freeze_pause(role=caller), freeze_interface)
    support.assert_marker(support.flag(freeze_project), NAME_OF[caller], f"after gov pause by {NAME_OF[caller]}")


@CALLERS
def test_cancel_agents_writes_the_marker_line(freeze_project, freeze_pause, freeze_interface, caller):
    """DEC-368: it also sets the flag. No claim is held, so nothing else happens."""
    pause_support.succeeded(freeze_pause("--cancel-agents", role=caller), freeze_interface)
    support.assert_marker(support.flag(freeze_project), NAME_OF[caller], "after gov pause --cancel-agents")


@CALLERS
def test_rollback_writes_the_marker_line_also_when_it_ends_with_an_error(freeze_project, freeze_pause,
                                                                         freeze_interface, caller):
    """DEC-378: the flag is set first and stays. The ticket does not exist, so the rollback itself fails."""
    run = freeze_pause("--rollback", pause_support.UNKNOWN_TICKET, role=caller)
    pause_support.failed(run, freeze_interface)
    support.assert_marker(support.flag(freeze_project), NAME_OF[caller],
                          "after gov pause --rollback of an unknown ticket")


def test_a_refused_caller_writes_no_flag(freeze_project, freeze_pause, freeze_interface):
    """DEC-365: a worker role is refused. Failure side of the line: no marker without a real pause."""
    pause_support.refused(freeze_pause(role=support.ENGINEER), freeze_interface)
    assert not os.path.lexists(support.flag(freeze_project)), "a refused gov pause left something at the flag's path"


def test_the_flag_pause_writes_is_the_freeze_the_guard_reads(freeze_project, freeze_sandbox, freeze_pause,
                                                             freeze_interface):
    """The writer and the reader agree: the guard denies on the flag as written, and allows once it is emptied."""
    pause_support.succeeded(freeze_pause(), freeze_interface)
    support.assert_marker(support.flag(freeze_project), support.OWNER_NAME, "after gov pause")
    support.assert_frozen(support.guard_write(freeze_project, freeze_sandbox), "after gov pause")
    support.put_text(freeze_project, "")
    support.assert_not_frozen(support.guard_write(freeze_project, freeze_sandbox),
                              "after the flag gov pause wrote was emptied")


@pytest.mark.parametrize("already_there", ("an-empty-file-0444", "text-without-the-marker"))
def test_pause_freezes_a_project_that_has_an_unmarked_file_at_the_path(freeze_project, freeze_sandbox, freeze_pause,
                                                                       freeze_interface, already_there):
    """The sandbox's placeholder may sit at the path when the owner pauses: the pause must still be a real one."""
    if already_there == "an-empty-file-0444":
        support.put_placeholder(freeze_project)
    else:
        support.put_text(freeze_project, "off\n")
    pause_support.succeeded(freeze_pause(), freeze_interface)
    support.assert_marker(support.flag(freeze_project), support.OWNER_NAME,
                          f"after gov pause over {already_there}")
    support.assert_frozen(support.guard_write(freeze_project, freeze_sandbox), f"after gov pause over {already_there}")


def test_a_second_pause_on_a_frozen_project_succeeds_and_keeps_a_marker(freeze_project, freeze_sandbox, freeze_pause,
                                                                        freeze_interface):
    """W1-28: a pause is a flag, not a count. Whether the second pause rewrites the line is not pinned."""
    pause_support.succeeded(freeze_pause(), freeze_interface)
    pause_support.succeeded(freeze_pause(role=ORCHESTRATOR), freeze_interface)
    line = support.first_line(support.flag(freeze_project))
    assert support.MARKER_LINE.fullmatch(line or ""), f"after two pauses the flag's first line is {line!r}"
    support.assert_frozen(support.guard_write(freeze_project, freeze_sandbox), "after two pauses")
    support.lift_support.lift_as_the_owner(freeze_project, freeze_sandbox)  # DEC-409: the owner in person
    assert not os.path.lexists(support.flag(freeze_project)), "gov pause --off left the flag"
    support.assert_not_frozen(support.guard_write(freeze_project, freeze_sandbox), "after --off")
