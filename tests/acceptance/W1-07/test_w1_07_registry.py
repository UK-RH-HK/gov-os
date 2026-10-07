"""KPI success 5 [CAP-28.b]: the registry reserves the twelve Wave 1 operations as ``gov`` commands.

A reserved command that is not built yet returns a ``NOT_IMPLEMENTED`` envelope.
W1-07 builds a minimal ``status`` and ``check --list``; the ticket that builds
another command revises that command's case here.

Planned revision (DEC-190, reason "planned: command implemented"): ``checkpoint``
is built by W1-25 and is no longer expected to return ``NOT_IMPLEMENTED``; the
list is ``NOT_BUILT`` in ``w1_07_support.py``.

Planned revision (DEC-190, reason "planned: command implemented"): ``closure``
is built by W1-20 and leaves the same list. It requires a depth and an id
(DEC-391): the cases that run every command give it both
(``support.invocation``), and a call without them is a usage error.

Planned revision (DEC-190, reason "planned: command implemented"): ``readiness``
is built by W1-13 and leaves the same list.

Planned revision (DEC-190, reason "planned: command implemented"): ``pause``
is built by W1-28 and leaves the same list.
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
def test_each_wave_1_operation_is_a_gov_command(request, interface, name):
    """The name is known: no usage error, and the envelope names the command."""
    # Revised after implementation: W1-27's rebuild recreates the lexical index through its owner
    # and its secrets filter (DEC-440); the size of the copied tree, not the behaviour, made the
    # case time out.
    gov = request.getfixturevalue("small_gov" if name in support.TREE_SENSITIVE_COMMANDS else "gov")
    run = gov(*support.invocation(name), "--json")
    assert run.returncode != 2, f"gov {name} is a usage error: the command is not reserved\n{run.describe()}"
    support.assert_envelope(run, interface, command=name)


def test_closure_without_its_arguments_is_a_usage_error(gov, interface):
    """A built command that requires arguments answers a call without them as a usage error (exit code 2), and no
    longer as ``NOT_IMPLEMENTED``. Standard output is empty or an envelope with ``ok: false`` (README, reading 8)."""
    run = gov("closure", "--json")
    assert run.returncode == 2, f"gov closure without a depth and an id must end with exit code 2\n{run.describe()}"
    assert support.NOT_IMPLEMENTED not in run.stdout, run.describe()
    if run.stdout.strip():
        envelope = support.assert_envelope(run, interface, command="closure")
        assert envelope["ok"] is False


@pytest.mark.parametrize("name", support.NOT_BUILT)
def test_a_reserved_command_not_yet_built_returns_not_implemented(gov, interface, name):
    run = gov(name, "--json")
    support.assert_error(run, interface, support.NOT_IMPLEMENTED, exit_code=1, command=name)


def test_a_name_outside_the_registry_is_not_answered_as_not_implemented(gov):
    """``NOT_IMPLEMENTED`` is for reserved commands; any other name is a usage error."""
    run = gov("no-such-command", "--json")
    assert run.returncode == 2, run.describe()
    assert support.NOT_IMPLEMENTED not in run.stdout, run.describe()
