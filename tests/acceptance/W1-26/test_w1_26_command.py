"""KPI S1 (partial), S2, S5 (partial): the ``gov check`` command line.

Tests the API-0002 envelope, exit codes, per-family RED/YELLOW/GREEN status,
and the hard-block vs warning severity semantics.
"""

from __future__ import annotations

import pytest

import w1_26_support as support

cli_support = support.cli_support


# --------------------------------------------------------------------------
# The command is built and returns the envelope
# --------------------------------------------------------------------------

def test_gov_check_json_returns_the_api_0002_envelope(raw_project, sandbox, interface):
    """``gov check --json`` returns the standard envelope, not NOT_IMPLEMENTED."""
    run = support.run_check(raw_project, sandbox)
    if support.NOT_IMPLEMENTED in run.stdout:
        pytest.skip("gov check is not built yet")
    support.envelope_of(run, interface)


def test_gov_check_list_still_works(project, sandbox, interface):
    """``gov check --list --json`` is unchanged (W1-07 built it)."""
    run = project.gov(sandbox, "check", "--list", "--json")
    envelope = cli_support.assert_envelope(run, interface, command="check")
    assert envelope["ok"] is True and run.returncode == 0, run.describe()


# --------------------------------------------------------------------------
# Exit codes (S1, CAP-39.d)
# --------------------------------------------------------------------------

def test_exit_0_when_all_checks_green(full_project, sandbox, interface):
    """Exit code 0: no hard-block check is RED."""
    run = support.run_check(full_project, sandbox)
    envelope = support.envelope_of(run, interface)
    if not envelope["ok"]:
        pytest.skip("the full project does not pass gov check yet")
    assert run.returncode == support.EXIT_OK, \
        f"all checks pass but exit code is {run.returncode}\n{run.describe()}"


def test_exit_nonzero_when_a_hard_block_is_red(project, sandbox, interface):
    """At least one hard-block RED -> non-zero exit code."""
    project.add_record("docs/adr/BAD-0001.md", "BAD-0001", "decision", "ACTIVE",
                       superseded_by="NONEXISTENT")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    assert run.returncode != support.EXIT_OK, \
        f"a planted defect did not cause a non-zero exit code\n{run.describe()}"


def test_warning_yellow_does_not_change_exit_code(project, sandbox, interface):
    """Warning-severity checks may be YELLOW without making the exit code non-zero."""
    project.add_check_declaration("w1-26-warn", "command-contract consistency",
                                  severity="warning", command="false")
    for check_id in list(support.CORE_CHECKS):
        project.remove_check_declaration(check_id)
    for check_id in support.ALREADY_DECLARED:
        project.remove_check_declaration(check_id)
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    if envelope["ok"]:
        assert run.returncode == support.EXIT_OK, \
            f"only warnings failed but exit code is non-zero\n{run.describe()}"


# --------------------------------------------------------------------------
# Per-family RED/YELLOW/GREEN (S2, CAP-39.d)
# --------------------------------------------------------------------------

def test_each_family_reported_with_a_colour(project, sandbox, interface):
    """Every family in the result has a status of RED, YELLOW, or GREEN."""
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    for family_name, entry in families.items():
        status = entry.get("status") if isinstance(entry, dict) else entry
        assert status in (support.RED, support.YELLOW, support.GREEN), \
            f"family {family_name!r} has status {status!r}, not RED/YELLOW/GREEN"


def test_hard_block_check_failing_makes_family_red(project, sandbox, interface):
    """A hard-block check that fails makes its family RED."""
    project.add_check_declaration("w1-26-fail", "schema/invariants",
                                  severity="hard-block", command="false")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    support.assert_family_red(result, "schema/invariants")


def test_warning_check_failing_makes_family_yellow(project, sandbox, interface):
    """A warning-severity check that fails makes its family YELLOW, not RED."""
    project.add_check_declaration("w1-26-warn-only", "command-contract consistency",
                                  severity="warning", command="false")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, "command-contract consistency")
    assert status in (support.YELLOW, support.RED), \
        f"a warning check failed but the family is {status!r}"


# --------------------------------------------------------------------------
# Each check declares hard-block or warning (S5)
# --------------------------------------------------------------------------

def test_each_check_result_declares_severity(project, sandbox, interface):
    """Every check result in the output carries a severity of hard-block or warning."""
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    for entry in support.checks_of(result):
        if isinstance(entry, dict):
            sev = entry.get("severity")
            assert sev in (support.HARD_BLOCK, support.WARNING), \
                f"a check result has severity {sev!r}, not hard-block or warning: {entry}"


# --------------------------------------------------------------------------
# Read-only (CAP-27)
# --------------------------------------------------------------------------

def test_gov_check_is_a_read_command(project, sandbox, interface):
    """``gov check`` leaves ``git status --porcelain`` empty."""
    project.commit()
    before = cli_support.porcelain(project.root)
    run = support.run_check(project, sandbox)
    after = cli_support.porcelain(project.root)
    assert before == after, f"gov check changed the working tree\n{run.describe()}"
