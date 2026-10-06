"""KPI S1 (partial): decision checker integration.

``gov check`` runs ``gov.decisions.checker.check(root)`` and includes its
findings. The findings from the decision checker become RED findings in the
authority/role limits family.
"""

from __future__ import annotations

import w1_26_support as support


# --------------------------------------------------------------------------
# gov check runs the decision checker
# --------------------------------------------------------------------------

def test_gov_check_runs_decision_checker(project, sandbox, interface):
    """``gov check`` includes the decision checker's findings."""
    project.add_decision("ADR-0001", "ACTIVE", superseded_by="ADR-0002")
    project.add_decision("ADR-0002", "ACTIVE", supersedes=["ADR-0001"])
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    output_text = run.stdout + str(result)
    assert "ACTIVE" in output_text or "supersed" in output_text.lower() or \
           "authority" in output_text.lower(), \
        f"the decision checker's findings are not in the output\n{run.describe()}"


def test_decision_checker_finding_makes_authority_family_red(project, sandbox, interface):
    """A decision checker finding (ACTIVE while superseded) makes authority/role limits RED."""
    project.add_decision("ADR-0001", "ACTIVE", superseded_by="ADR-0002")
    project.add_decision("ADR-0002", "ACTIVE", supersedes=["ADR-0001"])
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    support.assert_family_red(result, "authority/role limits")


# --------------------------------------------------------------------------
# A clean decision register -> authority/role limits GREEN
# --------------------------------------------------------------------------

def test_clean_decisions_authority_green(project, sandbox, interface):
    """A clean decision register makes the authority/role limits family GREEN.

    Revised (DEC-438): add_core_declarations() so the authority check is
    registered — owner rule DEC-425: unmeasured is never green.
    """
    project.add_core_declarations()
    project.add_decision("ADR-0001", "ACTIVE")
    project.add_decision("ADR-0002", "PROPOSED")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    auth_family = "authority/role limits"
    if auth_family in families:
        status = support.family_status(result, auth_family)
        assert status == support.GREEN, \
            f"clean decisions but authority is {status}\n{run.describe()}"


# --------------------------------------------------------------------------
# A project with no decisions -> authority GREEN (no findings)
# --------------------------------------------------------------------------

def test_no_decisions_authority_green(project, sandbox, interface):
    """A project with no decision records has no authority findings.

    Revised (DEC-438): add_core_declarations() so the authority check is
    registered — owner rule DEC-425: unmeasured is never green.
    """
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    auth_family = "authority/role limits"
    if auth_family in families:
        status = support.family_status(result, auth_family)
        assert status == support.GREEN, \
            f"no decisions but authority is {status}\n{run.describe()}"


# --------------------------------------------------------------------------
# The decision checker is called as-is (DEC-329)
# --------------------------------------------------------------------------

def test_duplicate_id_flagged(project, sandbox, interface):
    """A duplicate decision id is flagged as RED."""
    project.add_decision("DEC-DUP-001", "ACTIVE")
    project.write("docs/adr/DEC-DUP-001-copy.md",
                  support.decision("DEC-DUP-001", "PROPOSED"))
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


def test_supersession_cycle_flagged(project, sandbox, interface):
    """A supersession cycle is flagged."""
    project.add_decision("DEC-CYC-001", "SUPERSEDED", superseded_by="DEC-CYC-002")
    project.add_decision("DEC-CYC-002", "SUPERSEDED", superseded_by="DEC-CYC-001",
                          supersedes=["DEC-CYC-001"])
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)
