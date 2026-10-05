"""W1-13 -- ``gov readiness`` is a built command of the registry.

Settled by the sources: the registry reserved ``readiness`` at W1-07 (CAP-28.b) and this ticket builds it, from
``src/gov/readiness/command.py`` alone (DEC-317). It is a read command (CAP-27 names it). The names of its two
selectors are package DP-4.
"""

from __future__ import annotations

import w1_13_support as support

cli_support = support.cli_support


def test_readiness_no_longer_returns_not_implemented(raw_gov, interface):
    """Without arguments the command still answers with the envelope (W1-07), and is no usage error."""
    run = raw_gov(support.COMMAND, "--json")
    envelope = cli_support.assert_envelope(run, interface, command=support.COMMAND)
    code = (envelope.get("error") or {}).get("code")
    assert code != support.NOT_IMPLEMENTED, f"gov readiness is reserved and not built yet\n{run.describe()}"
    assert run.returncode != 2, f"gov readiness without arguments is a usage error\n{run.describe()}"


def test_help_names_the_two_selectors(raw_gov):
    """The registry's help line: "readiness of a ticket or a gate"; a ticket names its specification (DEC-307)."""
    run = raw_gov(support.COMMAND, "--help")
    assert run.returncode == 0, run.describe()
    for argument in (support.ARG_SPECIFICATION, support.ARG_TICKET):
        assert argument in run.stdout, f"gov readiness --help does not name {argument}\n{run.describe()}"


def test_an_unknown_argument_is_a_usage_error(raw_gov):
    """A built command checks its arguments (exit code 2, API-0002)."""
    run = raw_gov(support.COMMAND, "--no-such-option", "--json")
    assert run.returncode == 2, f"an unknown option of a built command must end with exit code 2\n{run.describe()}"


def test_a_specification_that_does_not_exist_does_not_pass(project, gov, interface):
    """A gate asked about a specification nobody wrote must not answer "closed"."""
    project.specification(support.complete_rows())
    run = gov(*support.select("SPEC-none"))
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode != 0, \
        f"an unknown specification passes\n{run.describe()}"


def test_without_arguments_nothing_is_written(project, gov):
    """CAP-27: with specifications in the project, open and complete, the bare command changes nothing."""
    project.specification(support.fresh_rows())
    project.specification(support.complete_rows(), spec_id=support.OTHER_SPEC, change=support.OTHER_CHANGE)
    project.settle()
    before = project.state()
    run = gov(support.COMMAND, "--json")
    assert project.state() == before, f"gov readiness changed the project\n{run.describe()}"
