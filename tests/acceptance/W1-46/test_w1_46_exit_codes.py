"""W1-46 -- a command's own exit code ends the process (batch 4, after implementation).

DEC-317 (owner, on W1-25's DP-1): "one generic change is made in
``src/gov/cli/main.py``: each command's handler, arguments, act paths and exit
codes come from its own module, including command-defined exit codes beyond 0
and 1. W1-07's suite is re-run."

**What can be seen from outside.** ``docs/interfaces/API-0002.yaml`` gives 0, 1
and 2 to success, a governance error and a usage error, and 3 and 4 to
verification and control state, which no command built today returns. The one
command of today's ``gov`` with an exit code of its own is ``gov launch``: it
ends with the exit code of the worker session it started (as built in
``c70bbb69``). That is the case tested here, with a stand-in session that ends
with a code beyond 0 and 1. A refusal stays a governance error: exit code 1.

Not tested, because it cannot be seen without the names a command module
exposes, which no decision fixes: that a new command's module alone, with no
change to ``main.py``, adds a command, its arguments and its act paths.

W1-07's cases (the twelve reserved commands, the envelope, exit codes 0, 1 and
2, ``NOT_IMPLEMENTED``) are not copied: ``tests/acceptance/W1-07/`` is re-run
as it stands.

No session is started.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

ENGINEER = support.ENGINEER


@pytest.mark.parametrize("code", (3, 4, 42))
def test_gov_launch_ends_with_the_exit_code_of_the_session_it_started(launch, cli, code):
    """A command-defined exit code beyond 0 and 1 is the process's exit code, not folded into 0 or 1."""
    support.set_session_exit_code(cli, code)
    result = launch(ENGINEER)
    result.session()
    assert result.run.returncode == code, (
        f"the worker session ended with exit code {code}, and gov launch with {result.run.returncode}\n"
        f"{result.describe()}"
    )


def test_a_session_that_ends_well_is_exit_code_0(launch, cli):
    support.set_session_exit_code(cli, 0)
    result = launch(ENGINEER)
    result.session()
    assert result.run.returncode == 0, result.describe()


def test_a_refused_launch_is_a_governance_error_with_exit_code_1(launch):
    """API-0002: "1: governance error". A refusal is the launcher's own answer, whatever a session would return."""
    result = launch(ENGINEER, "DAEO-zz00")
    support.assert_refused(result, "ticket")
    assert result.run.returncode == 1, f"a refused launch ended with exit code {result.run.returncode}, not 1"


def test_a_launch_without_its_arguments_is_a_usage_error_with_exit_code_2(project, sandbox, cli, launcher):
    """API-0002: "2: usage error". ``gov launch`` with no role and no ticket starts nothing."""
    run = support.run_gov(project, sandbox, "launch", cli=cli)
    assert run.returncode == 2, f"gov launch with no arguments ended with exit code {run.returncode}, not 2"
    assert support.calls(cli) == [], "gov launch with no arguments started the CLI"
