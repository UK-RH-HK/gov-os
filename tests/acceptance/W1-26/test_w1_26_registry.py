"""KPI S7 (CAP-38.b): the check registry names all 17 governance test families.

Every declared check runs; absent families are reported by name, never silently
missing. This ticket registers 7 core checks; 3 are already declared by other
tickets; 7 families have no check yet.
"""

from __future__ import annotations

import pytest

import w1_26_support as support


# --------------------------------------------------------------------------
# All 17 families named
# --------------------------------------------------------------------------

def test_all_17_families_named_in_result(project, sandbox, interface):
    """The check result names all 17 governance test families."""
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    support.assert_all_families_named(result)


def test_exactly_17_families(project, sandbox, interface):
    """The result names exactly 17 families, no more, no fewer."""
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    assert len(families) == 17, f"expected 17 families, got {len(families)}: {sorted(families)}"


# --------------------------------------------------------------------------
# Absent families reported by name
# --------------------------------------------------------------------------

@pytest.mark.parametrize("family", support.NOT_YET_REGISTERED,
                         ids=[f.replace("/", "-").replace(" ", "-") for f in support.NOT_YET_REGISTERED])
def test_absent_family_reported_by_name(project, sandbox, interface, family):
    """A family with no registered check is reported by name, not silently absent."""
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    support.assert_family_present(result, family)


# --------------------------------------------------------------------------
# Core checks registered by this ticket
# --------------------------------------------------------------------------

@pytest.mark.parametrize("check_id", sorted(support.CORE_CHECKS),
                         ids=sorted(support.CORE_CHECKS))
def test_core_check_declared(project, sandbox, interface, check_id):
    """Each of the 7 core-* check declarations exists and is listed."""
    project.add_core_declarations()
    project.commit()
    run = project.gov(sandbox, "check", "--list", "--json")
    envelope = support.cli_support.assert_envelope(run, interface, command="check")
    assert envelope["ok"] is True, run.describe()
    records = support.cli_support.find_records(envelope["result"])
    ids = [r["id"] for r in records]
    assert check_id in ids, f"core check {check_id} is not listed: {ids}"


# --------------------------------------------------------------------------
# Already-declared checks are listed
# --------------------------------------------------------------------------

@pytest.mark.parametrize("check_id", support.ALREADY_DECLARED)
def test_already_declared_check_is_listed(project, sandbox, interface, check_id):
    """Checks declared by other tickets are listed by ``gov check --list``."""
    run = project.gov(sandbox, "check", "--list", "--json")
    envelope = support.cli_support.assert_envelope(run, interface, command="check")
    assert envelope["ok"] is True, run.describe()
    records = support.cli_support.find_records(envelope["result"])
    ids = [r["id"] for r in records]
    assert check_id in ids, f"already-declared check {check_id} is not listed: {ids}"


# --------------------------------------------------------------------------
# Declared checks run
# --------------------------------------------------------------------------

def test_declared_checks_are_run(project, sandbox, interface):
    """Every declared check is run (its command is executed), not just listed."""
    marker_file = sandbox.elsewhere / "w1-26-check-ran"
    project.add_check_declaration("w1-26-marker", "schema/invariants",
                                  command=f"touch {marker_file}")
    project.commit()
    run = support.run_check(project, sandbox)
    support.envelope_of(run, interface)
    assert marker_file.exists(), f"the declared check's command was not run\n{run.describe()}"


def test_a_new_check_added_to_the_folder_is_picked_up(project, sandbox, interface):
    """Adding a new check declaration file is enough; no code change is needed."""
    project.commit()
    run1 = project.gov(sandbox, "check", "--list", "--json")
    envelope1 = support.cli_support.assert_envelope(run1, interface, command="check")
    before = {r["id"] for r in support.cli_support.find_records(envelope1["result"])}

    project.add_check_declaration("w1-26-new-family", "audit reproducibility",
                                  command="true")
    project.commit()
    run2 = project.gov(sandbox, "check", "--list", "--json")
    envelope2 = support.cli_support.assert_envelope(run2, interface, command="check")
    after = {r["id"] for r in support.cli_support.find_records(envelope2["result"])}
    assert "w1-26-new-family" in after - before, \
        f"a new declaration was not picked up: before={before}, after={after}"


# --------------------------------------------------------------------------
# Misspelled family name in a declaration is not silently dropped
# --------------------------------------------------------------------------

def test_misspelled_family_name_not_silently_dropped(project, sandbox, interface):
    """A declaration whose family is a typo (not in the 17 FAMILIES) must not be silently ignored.

    The runner pre-populates family statuses from the FAMILIES tuple, then
    merges check results by ``if fam in families``. A misspelled family name
    (e.g. ``schema/invariant`` instead of ``schema/invariants``) causes the
    check's findings to be silently dropped — the family stays GREEN even though
    the check produced RED findings.
    """
    project.add_check_declaration(
        "w1-26-typo-family", "schema/invariant",
        severity="hard-block",
        command="python3 -m gov.check.schema",
    )
    project.write("docs/adr/BAD-TYPO-001.md",
                  "---\nid: BAD-TYPO-001\ntype: decision\nstate_class: AUTHORITATIVE\n"
                  "title: Bad decision for typo test\n---\n# BAD-TYPO-001\n")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)

    ok = envelope.get("ok", True)
    rc = run.returncode

    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    typo_status = support.family_status(result, "schema/invariant")
    correct_status = support.family_status(result, "schema/invariants")

    detected = (
        ok is False
        or rc != support.EXIT_OK
        or typo_status in (support.RED, support.YELLOW)
        or correct_status in (support.RED, support.YELLOW)
    )
    assert detected, (
        f"a declaration with misspelled family 'schema/invariant' was silently dropped; "
        f"the check's RED findings vanished. ok={ok}, rc={rc}, "
        f"typo_family={typo_status!r}, correct_family={correct_status!r}\n{run.describe()}"
    )
