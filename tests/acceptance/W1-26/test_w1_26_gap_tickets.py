"""KPI S3 (CAP-30.b, DEC-089): gap ticket check.

Fails a specification with a required open readiness row that has no linked gap
ticket. The gap_ticket field is reported as written by the readiness checker
(W1-13); this ticket's check validates the link.
"""

from __future__ import annotations

import w1_26_support as support


# --------------------------------------------------------------------------
# A required MISSING row with no gap_ticket -> RED
# --------------------------------------------------------------------------

def test_required_missing_row_no_gap_ticket_is_red(project, sandbox, interface):
    """A specification with a required MISSING row and no gap_ticket fails."""
    rows = support.fresh_rows()
    project.add_specification(rows, spec_id="SPEC-gp01", change="gp01-gap")
    project.add_readiness_dimensions()
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


def test_required_missing_row_with_unlinked_gap_ticket_is_red(project, sandbox, interface):
    """A specification with a required MISSING row whose gap_ticket is UNLINKED fails."""
    rows = support.fresh_rows()
    for row in rows:
        row["gap_ticket"] = "UNLINKED"
    project.add_specification(rows, spec_id="SPEC-gp02", change="gp02-gap")
    project.add_readiness_dimensions()
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# A required MISSING row with a valid gap_ticket -> passes
# --------------------------------------------------------------------------

def test_required_missing_row_with_valid_gap_ticket_passes(project, sandbox, interface):
    """A specification with a required MISSING row and a valid gap_ticket passes the gap check."""
    rows = support.fresh_rows()
    for row in rows:
        if row["state"] == "MISSING":
            row["gap_ticket"] = "GAP-aaaa"
    project.add_specification(rows, spec_id="SPEC-gp03", change="gp03-gap")
    project.add_readiness_dimensions()
    project.add_ticket("GAP-aaaa", "W1-99")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    gap_family = "concurrency/claims"
    if gap_family in families:
        status = support.family_status(result, gap_family)
        assert status != support.RED or "gap" not in str(families[gap_family]).lower(), \
            f"the gap ticket check failed even though valid tickets are linked\n{run.describe()}"


# --------------------------------------------------------------------------
# A gap_ticket naming a closed ticket -> RED
# --------------------------------------------------------------------------

def test_gap_ticket_naming_closed_ticket_is_red(project, sandbox, interface):
    """A gap_ticket that names a closed ticket fails."""
    rows = support.fresh_rows()
    for row in rows:
        if row["state"] == "MISSING":
            row["gap_ticket"] = "CLOSED-aaaa"
    project.add_specification(rows, spec_id="SPEC-gp04", change="gp04-gap")
    project.add_readiness_dimensions()
    project.write(".tickets/CLOSED-aaaa.md",
                  "---\nid: CLOSED-aaaa\ntype: task\nstatus: closed\nstate_class: AUTHORITATIVE\n"
                  "title: Closed gap\nrole: engineer\nallowed_paths:\n- src/**\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# CLOSED-aaaa\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# A gap_ticket naming a nonexistent ticket -> RED
# --------------------------------------------------------------------------

def test_gap_ticket_naming_nonexistent_ticket_is_red(project, sandbox, interface):
    """A gap_ticket that names a ticket that does not exist fails."""
    rows = support.fresh_rows()
    for row in rows:
        if row["state"] == "MISSING":
            row["gap_ticket"] = "NOPE-zzzz"
    project.add_specification(rows, spec_id="SPEC-gp05", change="gp05-gap")
    project.add_readiness_dimensions()
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# A complete specification with all rows satisfied -> no gap finding
# --------------------------------------------------------------------------

def test_complete_specification_no_gap_finding(project, sandbox, interface):
    """A specification with every required row PRESENT has no gap issue."""
    rows = support.complete_rows()
    project.add_specification(rows, spec_id="SPEC-gp06", change="gp06-gap")
    project.add_readiness_dimensions()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    for family_name, entry in families.items():
        if "gap" in str(entry).lower():
            status = entry.get("status") if isinstance(entry, dict) else entry
            assert status != support.RED, \
                f"complete spec triggers a gap finding in {family_name}\n{run.describe()}"
