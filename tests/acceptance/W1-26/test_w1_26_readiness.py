"""KPI S1 (partial): readiness integration.

``gov check`` runs readiness checking and reports READINESS_INVALID as a
finding. The W1-13 residual notes that bare ``gov readiness`` answers
READINESS_INVALID in any project with a change from today's template;
``gov check`` must know this.
"""

from __future__ import annotations

import w1_26_support as support


# --------------------------------------------------------------------------
# gov check runs readiness checking
# --------------------------------------------------------------------------

def test_gov_check_runs_readiness(project, sandbox, interface):
    """``gov check`` includes readiness results in its output."""
    project.add_readiness_dimensions()
    rows = support.fresh_rows()
    project.add_specification(rows, spec_id="SPEC-rd01", change="rd01-readiness")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    output_text = run.stdout + str(result)
    assert "readiness" in output_text.lower(), \
        f"gov check does not mention readiness in its output\n{run.describe()}"


# --------------------------------------------------------------------------
# READINESS_INVALID is a finding
# --------------------------------------------------------------------------

def test_readiness_invalid_is_a_finding(project, sandbox, interface):
    """A specification that is READINESS_INVALID produces a finding."""
    project.add_readiness_dimensions()
    folder = "openspec/changes/bad-spec"
    project.write(f"{folder}/.openspec.yaml", "schema: feature-readiness\n")
    project.write(f"{folder}/proposal.md",
                  "---\nid: SPEC-bad1\ntype: specification\nstatus: DRAFT\n"
                  "state_class: AUTHORITATIVE\ntitle: Bad spec\n---\n# Bad\n")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    output_text = run.stdout + str(result)
    assert "readiness" in output_text.lower() or "READINESS_INVALID" in output_text, \
        f"READINESS_INVALID is not reported\n{run.describe()}"


# --------------------------------------------------------------------------
# A complete specification does not trigger a readiness finding
# --------------------------------------------------------------------------

def test_complete_specification_no_readiness_finding(project, sandbox, interface):
    """A specification with all required rows PRESENT does not trigger a readiness finding."""
    project.add_readiness_dimensions()
    rows = support.complete_rows()
    project.add_specification(rows, spec_id="SPEC-rd02", change="rd02-good")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    for family_name, entry in families.items():
        if "readiness" in family_name.lower():
            status = entry.get("status") if isinstance(entry, dict) else entry
            if status == support.RED:
                assert "READINESS_INVALID" not in str(entry), \
                    f"complete spec triggers READINESS_INVALID in {family_name}\n{run.describe()}"


# --------------------------------------------------------------------------
# A project with no specifications has no readiness finding
# --------------------------------------------------------------------------

def test_no_specifications_no_readiness_finding(project, sandbox, interface):
    """A project with no specifications has no readiness finding."""
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    for family_name, entry in families.items():
        if "readiness" in family_name.lower():
            status = entry.get("status") if isinstance(entry, dict) else entry
            assert status != support.RED, \
                f"no specs but {family_name} is RED\n{run.describe()}"
