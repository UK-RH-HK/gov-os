"""KPI S1 (partial): decision checker integration.

``gov check`` runs ``gov.decisions.checker.check(root)`` and includes its
findings. The findings from the decision checker become RED findings in the
authority/role limits family.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import w1_26_support as support


# --------------------------------------------------------------------------
# gov check runs the decision checker
# --------------------------------------------------------------------------

def _decision_checker_findings(project, sandbox):
    """``gov.decisions.checker.check(root)`` on the project, called in a new process with this worktree's code."""
    code = ("import json, sys\nfrom gov.decisions.checker import check\n"
            "print(json.dumps(check(sys.argv[1]), default=str))\n")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(sandbox.home), "LC_ALL": "C.UTF-8",
           "TMPDIR": str(sandbox.tmpdir), "PYTHONPATH": str(support.SRC),
           "PYTHONPYCACHEPREFIX": str(sandbox.pycache)}
    done = subprocess.run([sys.executable, "-c", code, str(project.root)], cwd=str(project.root), env=env,
                          capture_output=True, text=True, timeout=support.CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"the decision checker did not run:\n{done.stderr}"
    return json.loads(done.stdout)


def test_gov_check_runs_decision_checker(green_project, sandbox, interface):
    """``gov check`` includes the decision checker's findings: each finding ``gov.decisions.checker.check`` gives
    on the project is a finding of ``core-authority``, by its code and message.

    Revised (W2-67, I2 §2.7): it asserted "ACTIVE", "supersed" or "authority" anywhere in the output, which every
    output holds (the check ids and family names). The decisions are committed with the owner's trailer, so the
    checker's findings are those of the planted defect: a decision set ACTIVE without it is a gap of
    ``core-authority`` that DEC-627 put on the Wave 2 list."""
    project = green_project
    project.add_decision("ADR-0001", "ACTIVE", superseded_by="ADR-0002")
    project.add_decision("ADR-0002", "ACTIVE", supersedes=["ADR-0001"])
    project.commit("two decisions, set ACTIVE by the owner\n\nRole: owner")
    expected = _decision_checker_findings(project, sandbox)
    assert expected, "the decision checker finds nothing on a decision ACTIVE while superseded: no premise"
    run = support.run_check(project, sandbox)
    result, _ = support.result_and_envelope(run, interface)
    entry = support.check_entry(result, "core-authority")
    held = {(finding.get("code"), finding.get("message")) for finding in entry.get("findings") or []
            if isinstance(finding, dict)}
    missing = [finding for finding in expected if (finding.get("code"), finding.get("message")) not in held]
    assert not missing, (
        f"the decision checker's findings {missing} are not findings of core-authority: {entry}\n{run.describe()}"
    )
    assert entry.get("status") == support.RED, f"core-authority is not RED on its findings: {entry}"


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

def test_duplicate_id_flagged(green_project, sandbox, interface):
    """A duplicate decision id is flagged as RED by the decision checker, called as-is: ``core-authority`` (the
    authority/role limits family) is RED with a finding that names the id and both files.

    Revised (W2-67, I2 §2.5 and §2.7): it judged only that ``gov check`` failed, as
    ``test_w1_26_planted_defects.py::test_planted_graph_defect_duplicate_id`` did on the same pair, on a base that
    was red before the defect; the two now hold two behaviours: that one the graph check's finding, this one the
    decision checker's."""
    project = green_project
    project.add_decision("DEC-DUP-001", "ACTIVE")
    project.write("docs/adr/DEC-DUP-001-copy.md",
                  support.decision("DEC-DUP-001", "PROPOSED"))
    project.commit()
    run = support.run_check(project, sandbox)
    result, _, _ = support.assert_check_red_naming(run, interface, "core-authority", "DEC-DUP-001",
                                                   "docs/adr/DEC-DUP-001.md", "docs/adr/DEC-DUP-001-copy.md")
    support.assert_family_red(result, "authority/role limits")


def test_supersession_cycle_flagged(green_project, sandbox, interface):
    """A supersession cycle is flagged: ``core-authority`` is RED with a finding that names both decisions of the
    cycle."""
    project = green_project
    project.add_decision("DEC-CYC-001", "SUPERSEDED", superseded_by="DEC-CYC-002")
    project.add_decision("DEC-CYC-002", "SUPERSEDED", superseded_by="DEC-CYC-001",
                          supersedes=["DEC-CYC-001"])
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-authority", "DEC-CYC-001", "DEC-CYC-002")
