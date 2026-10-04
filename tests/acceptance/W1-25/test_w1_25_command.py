"""W1-25 -- ``gov checkpoint`` is a built command of the registry, with ``--watch`` as its own argument.

Settled by the sources (no package affects this file): the registry reserved
``checkpoint`` at W1-07 (CAP-28.b) and this ticket builds it; the KPI names
``gov checkpoint --watch``. How the command is wired into ``src/gov/cli/`` is
package DP-1; these tests go through the command either way.
"""

from __future__ import annotations

import w1_25_support as support

cli_support = support.cli_support


def test_checkpoint_no_longer_returns_not_implemented(raw_gov, interface):
    """KPI success 1: the command exists. Without arguments it still answers with the envelope (W1-07)."""
    run = raw_gov("checkpoint", "--json")
    envelope = cli_support.assert_envelope(run, interface, command="checkpoint")
    code = (envelope.get("error") or {}).get("code")
    assert code != support.NOT_IMPLEMENTED, f"gov checkpoint is reserved and not built yet\n{run.describe()}"
    assert run.returncode != 2, f"gov checkpoint without arguments is a usage error\n{run.describe()}"


def test_checkpoint_without_arguments_writes_nothing(project, gov):
    before = support.state(project)
    run = gov("checkpoint", "--json")
    assert support.state(project) == before, f"gov checkpoint without arguments changed the project\n{run.describe()}"


def test_help_names_watch(raw_gov):
    """KPI success 3 [CAP-37.c]: ``--watch`` is an argument of the command."""
    run = raw_gov("checkpoint", "--help")
    assert run.returncode == 0, run.describe()
    assert "--watch" in run.stdout, f"gov checkpoint --help does not name --watch\n{run.describe()}"


def test_watch_is_accepted_as_an_argument(raw_gov, interface):
    run = raw_gov("checkpoint", "--watch", "--json")
    assert run.returncode != 2, f"gov checkpoint --watch is a usage error\n{run.describe()}"
    envelope = cli_support.assert_envelope(run, interface, command="checkpoint")
    code = (envelope.get("error") or {}).get("code")
    assert code != support.NOT_IMPLEMENTED, f"gov checkpoint --watch is not built yet\n{run.describe()}"


def test_an_unknown_argument_is_a_usage_error(raw_gov):
    """A built command checks its arguments (exit code 2, API-0002)."""
    run = raw_gov("checkpoint", "--no-such-option", "--json")
    assert run.returncode == 2, f"an unknown option of a built command must end with exit code 2\n{run.describe()}"
