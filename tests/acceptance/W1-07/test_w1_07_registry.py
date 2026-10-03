"""KPI success 5 [CAP-28.b]: the registry reserves the twelve Wave 1 operations as ``gov`` commands.

A reserved command that is not built yet returns a ``NOT_IMPLEMENTED`` envelope.
W1-07 builds a minimal ``status`` and ``check --list``; the ticket that builds
another command revises that command's case here.
"""

from __future__ import annotations

import re

import pytest

import w1_07_support as support


def test_help_names_every_reserved_command(gov):
    run = gov("--help")
    assert run.returncode == 0, f"gov --help does not end with exit code 0\n{run.describe()}"
    words = set(re.findall(r"[a-z][a-z-]*", run.stdout))
    missing = [name for name in support.RESERVED_COMMANDS if name not in words]
    assert not missing, f"gov --help does not name the reserved commands {missing}\n{run.describe()}"


@pytest.mark.parametrize("name", support.RESERVED_COMMANDS)
def test_each_wave_1_operation_is_a_gov_command(gov, interface, name):
    """The name is known: no usage error, and the envelope names the command."""
    run = gov(name, "--json")
    assert run.returncode != 2, f"gov {name} is a usage error: the command is not reserved\n{run.describe()}"
    support.assert_envelope(run, interface, command=name)


@pytest.mark.parametrize("name", support.NOT_BUILT)
def test_a_reserved_command_not_yet_built_returns_not_implemented(gov, interface, name):
    run = gov(name, "--json")
    support.assert_error(run, interface, support.NOT_IMPLEMENTED, exit_code=1, command=name)


def test_a_name_outside_the_registry_is_not_answered_as_not_implemented(gov):
    """``NOT_IMPLEMENTED`` is for reserved commands; any other name is a usage error."""
    run = gov("no-such-command", "--json")
    assert run.returncode == 2, run.describe()
    assert support.NOT_IMPLEMENTED not in run.stdout, run.describe()
