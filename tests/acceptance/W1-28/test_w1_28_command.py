"""``gov pause`` is a built command with the three options the KPI lines name.

KPI success 1 and 2 name the forms: ``gov pause``, ``gov pause --off``,
``gov pause --cancel-agents`` and ``gov pause --rollback <ticket>``. The
command is the module ``src/gov/pause/command.py`` (DEC-317), which declares
its arguments, so a missing ticket is argparse's usage error (exit code 2,
``src/gov/cli/main.py``).

These cases do not need the ``built`` fixture: they are the ones that fail
with the command's own answer while it is not built. None can pause anything:
the first is a worker's call (``GOV_ROLE=engineer``, DEC-365), the others
never reach the handler.
"""

from __future__ import annotations

import pytest

import w1_28_support as support


def test_gov_pause_is_no_longer_answered_as_not_implemented(raw_project, sandbox, interface):
    run = support.pause(raw_project, sandbox, role=support.ENGINEER)
    envelope = support.cli_support.assert_envelope(run, interface, command="pause")
    code = (envelope.get("error") or {}).get("code")
    assert code not in (support.NOT_IMPLEMENTED, support.MODULE_INVALID), \
        f"gov pause is not built: it answers {code}\n{run.describe()}"
    assert not support.is_paused(raw_project), "a worker's gov pause paused the project"


@pytest.mark.parametrize("option", ["--off", "--cancel-agents", "--rollback"])
def test_help_names_each_option(raw_project, sandbox, option):
    run = support.gov(raw_project, sandbox, "pause", "--help")
    assert run.returncode == 0, run.describe()
    assert option in run.stdout, f"gov pause --help does not name {option}\n{run.describe()}"
    assert not support.is_paused(raw_project), "gov pause --help paused the project"


def test_rollback_without_a_ticket_is_a_usage_error(raw_project, sandbox):
    before = support.head(raw_project)
    run = support.pause(raw_project, sandbox, "--rollback")
    assert run.returncode == 2, f"--rollback takes a ticket; without one the exit code is 2\n{run.describe()}"
    assert support.head(raw_project) == before, "HEAD moved"
    assert not support.is_paused(raw_project), "a usage error paused the project"
