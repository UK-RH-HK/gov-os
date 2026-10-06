"""The seam in ``lift()`` is closed: planted ``ancestry`` and ``terminal`` do not bypass the rules.

A reviewer found that ``gov.pause.command.lift`` takes ``ancestry`` and
``terminal`` as public keyword arguments. An agent can write a Python script
that imports the function and calls it with a forged ancestry (no Claude Code
session, a readable chain to the system's first process) and a real
pseudo-terminal pair, passing all four rules and lifting the freeze without
being the owner in person.

This test asserts the seam is closed: calling ``lift(root, ancestry=[...],
terminal=(master_fd, slave_fd))`` in a project that has a freeze set does NOT
lift the freeze. The freeze flag is still present after the call. After the fix,
either:

- ``lift()`` no longer accepts those parameters (TypeError), or
- it ignores them and reads the real ancestry from ``/proc`` (which, inside the
  test runner's subprocess, includes a Claude Code session or an unreadable
  chain), so it refuses.

**Expected red:** ``lift()`` accepts the kwargs and uses them, so the forged
ancestry passes rule 1, the pty passes rule 2, the shown code typed back passes
rule 3, and the freeze is lifted: the flag is gone.
"""

from __future__ import annotations

import os

import w1_50_freeze_support as support
from w1_50_freeze_support import (  # noqa: F401  fixtures
    freeze_frozen, freeze_project, freeze_sandbox,
)

lift = support.lift_support


def test_an_agent_script_that_calls_lift_with_planted_parameters_does_not_lift(freeze_frozen, freeze_sandbox):
    """A forged ancestry and a real pty, with the shown code typed back: every rule would pass.

    The call uses ``drive()``, which spawns a subprocess that imports
    ``gov.pause.command.lift`` and calls it with a planted ancestry (a plain
    terminal's chain, no Claude Code session, readable to the system's first
    process) and a real pseudo-terminal (the driver's default). The shown code
    is typed back correctly. This is exactly what an agent could do by writing
    a Python script and running it via a Bash tool call.

    After the fix the call must fail and the freeze must stay.
    """
    before = support.flag_state(freeze_frozen)

    runs = lift.drive(freeze_frozen, freeze_sandbox, ancestry=lift.PLAIN_TERMINAL)
    run = runs[0]

    assert run.status != lift.LIFTED, (
        f"lift() accepted planted ancestry and terminal and lifted the freeze: the seam is open. "
        f"An agent can import gov.pause.command.lift and call it with a forged ancestry and a real "
        f"pty pair, bypassing all four rules (DEC-409). {run.describe()}"
    )
    support.assert_nothing_changed(freeze_frozen, before, "lift() with planted parameters")
    assert os.path.lexists(support.flag(freeze_frozen)), (
        f"{support.FLAG_REL} was removed by lift() called with planted parameters"
    )
    support.assert_frozen(
        support.guard_write(freeze_frozen, freeze_sandbox),
        "after lift() called with planted ancestry and terminal"
    )
