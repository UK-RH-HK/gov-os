"""KPI success 1 and failure 2: every command returns the API-0002 envelope, with exit codes 0-4.

The envelope fields and the exit codes are read from ``docs/interfaces/API-0002.yaml``
(see ``load_interface``), so a field the interface does not define, a missing
field or a field of another type is drift.
"""

from __future__ import annotations

import pytest

import w1_07_support as support

SESSION = "w1-07-acceptance-session"


@pytest.mark.parametrize("args", support.EVERY_INVOCATION, ids=support.label)
def test_every_command_returns_the_envelope(request, interface, args):
    # Revised after implementation: W1-27's rebuild recreates the lexical index through its owner
    # and its secrets filter (DEC-440); the size of the copied tree, not the behaviour, made the
    # case time out.
    gov = request.getfixturevalue("small_gov" if args[0] in support.TREE_SENSITIVE_COMMANDS else "gov")
    run = gov(*args, "--json")
    support.assert_envelope(run, interface, command=args[0])


@pytest.mark.parametrize("args", support.EVERY_INVOCATION, ids=support.label)
def test_the_envelope_has_no_field_outside_the_interface(request, interface, args):
    """Failure 2: exactly ``ok``, ``command``, ``result``, ``session`` and, on an error, ``error`` with its three keys."""
    # Revised after implementation: W1-27's rebuild recreates the lexical index through its owner
    # and its secrets filter (DEC-440); the size of the copied tree, not the behaviour, made the
    # case time out.
    gov = request.getfixturevalue("small_gov" if args[0] in support.TREE_SENSITIVE_COMMANDS else "gov")
    envelope = gov(*args, "--json").envelope()
    assert set(interface.required) <= set(envelope) <= set(interface.required) | set(interface.optional), \
        f"gov {support.label(args)}: the envelope fields are {sorted(envelope)}"
    if not envelope["ok"]:
        assert sorted(envelope["error"]) == sorted(interface.optional["error"])


def test_status_succeeds_with_exit_code_0(gov, interface):
    run = gov("status", "--json")
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True, f"the minimal status does not succeed\n{run.describe()}"
    assert run.returncode == 0
    assert "error" not in envelope or envelope["error"] is None


def test_a_governance_error_has_exit_code_1_and_its_code_in_the_json(gov, interface):
    """Exit code 1 is "governance error (GovError code in JSON)"; a NOT_IMPLEMENTED command is one (DEC-186, DEC-190)."""
    run = gov("close", "--json")
    error = support.assert_error(run, interface, support.NOT_IMPLEMENTED, exit_code=1, command="close")
    assert "details" in error


def test_an_unknown_command_is_a_usage_error(gov, interface):
    run = gov("no-such-command", "--json")
    assert run.returncode == 2, f"an unknown command must end with exit code 2\n{run.describe()}"
    if run.stdout.strip():
        envelope = support.assert_envelope(run, interface)
        assert envelope["ok"] is False


def test_an_unknown_option_is_a_usage_error(gov, interface):
    run = gov("status", "--no-such-option", "--json")
    assert run.returncode == 2, f"an unknown option must end with exit code 2\n{run.describe()}"
    if run.stdout.strip():
        envelope = support.assert_envelope(run, interface)
        assert envelope["ok"] is False


@pytest.mark.parametrize("args, expected", [(("status",), 0), (("check",), 3), (("no-such-command",), 2)],
                         ids=["status", "check", "unknown"])
def test_the_exit_code_is_the_same_without_json(gov, args, expected):
    run = gov(*args)
    assert run.returncode == expected, f"without --json the exit code must still be {expected}\n{run.describe()}"


def test_the_envelope_carries_the_session_given(gov, interface):
    run = gov("status", "--json", "--session", SESSION)
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["session"] == SESSION, f"--session is not the envelope's session\n{run.describe()}"


def test_an_error_envelope_carries_the_session_given(gov, interface):
    run = gov("check", "--json", "--session", SESSION)
    envelope = support.assert_envelope(run, interface, command="check")
    assert envelope["session"] == SESSION, f"--session is not the envelope's session\n{run.describe()}"


def test_root_names_the_project_from_another_directory(gov, interface, sandbox, project):
    run = gov("status", "--json", "--root", str(project), cwd=sandbox.elsewhere)
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True, f"status with --root from another directory does not succeed\n{run.describe()}"
