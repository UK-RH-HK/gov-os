"""The seam in ``lift()`` is closed: planted ``ancestry`` and ``terminal`` do not bypass the rules.

A reviewer found that ``gov.pause.command.lift`` takes ``ancestry`` and
``terminal`` as public keyword arguments. An agent can write a Python script
that imports the function and calls it with a forged ancestry (no Claude Code
session, a readable chain to the system's first process) and a real
pseudo-terminal pair, passing all four rules and lifting the freeze without
being the owner in person.

After the fix ``lift(root)`` takes no ``ancestry`` or ``terminal`` parameters.
A private function ``_lift_test(root, ancestry=None, terminal=None)`` keeps the
seam open for the test suite only. This test calls the public ``lift`` function
with planted keyword arguments and asserts the call fails: a TypeError because
the parameters are not accepted (the seam is closed).

**Expected red while ``lift()`` still takes kwargs:** the forged ancestry passes
rule 1, the pty passes rule 2, the shown code typed back passes rule 3, and the
freeze is lifted.

**Expected green after the fix:** ``lift()`` rejects the kwargs with TypeError
(the driver reports ``status == "missing"``), and the freeze flag stays.
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

    The call uses ``drive()`` with ``function=SEAM_FUNCTION`` (``"lift"``),
    which spawns a subprocess that imports the public ``gov.pause.command.lift``
    and calls it with a planted ancestry and a real pseudo-terminal. After the
    fix, ``lift()`` does not accept ``ancestry`` or ``terminal`` kwargs, so the
    call raises TypeError. The driver reports this as ``status == "missing"``
    (the function does not take the contract's parameters).

    Before the fix (expected red): ``lift()`` accepts the kwargs, uses them,
    and lifts the freeze.
    """
    before = support.flag_state(freeze_frozen)

    runs = lift.drive(freeze_frozen, freeze_sandbox, ancestry=lift.PLAIN_TERMINAL,
                      function=lift.SEAM_FUNCTION)
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
