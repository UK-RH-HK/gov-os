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

import hashlib
import os
import subprocess
from pathlib import Path

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


def _mirror_for(project, home):
    """The mirror file ``gov pause`` writes for *project* under *home* (DEC-429)."""
    proc = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "--git-common-dir"],
        capture_output=True, text=True, check=True,
    )
    raw = proc.stdout.strip()
    if not os.path.isabs(raw):
        raw = os.path.join(str(project), raw)
    key = hashlib.sha256(os.path.realpath(raw).encode()).hexdigest()
    return Path(home) / ".local/state/gov-os" / key / "freeze"

