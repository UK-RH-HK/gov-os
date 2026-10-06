"""KPI S8 (CAP-01.c): authority class change check.

Fails a record that changes authority class without a decision: a research or
lesson record cited as a decision or policy, or a superseded record used to
satisfy a current requirement.
"""

from __future__ import annotations

import w1_26_support as support


# --------------------------------------------------------------------------
# A research record cited as a decision -> RED
# --------------------------------------------------------------------------

def test_research_cited_as_decision_is_red(project, sandbox, interface):
    """A research record that is cited as a decision fails."""
    project.add_record("docs/research/RES-001.md", "RES-001", "research", "ACTIVE",
                        title="A research finding")
    project.add_decision("DEC-AUTH-001", "ACTIVE", depends_on=["RES-001"],
                          title="Depends on research as if it were policy")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


def test_research_cited_as_policy_is_red(project, sandbox, interface):
    """A research record used where a policy record is expected fails."""
    project.add_record("docs/research/RES-002.md", "RES-002", "research", "ACTIVE",
                        title="Research as policy")
    project.write(".tickets/POL-aaaa.md",
                  "---\nid: POL-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Ticket citing research\nrole: engineer\nallowed_paths:\n- src/**\n"
                  "sources:\n- RES-002\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# POL-aaaa\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# A lesson record cited as policy -> RED
# --------------------------------------------------------------------------

def test_lesson_cited_as_policy_is_red(project, sandbox, interface):
    """A lesson record cited as a policy fails."""
    project.add_record("docs/lessons/LES-001.md", "LES-001", "lesson", "ACTIVE",
                        title="A lesson learned")
    project.add_decision("DEC-AUTH-002", "ACTIVE", depends_on=["LES-001"],
                          title="Depends on lesson as policy")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# A superseded record used to satisfy a current requirement -> RED
# --------------------------------------------------------------------------

def test_superseded_record_satisfying_current_requirement_is_red(project, sandbox, interface):
    """A superseded record used to satisfy a current requirement fails."""
    project.add_decision("DEC-OLD-001", "SUPERSEDED", superseded_by="DEC-NEW-001",
                          title="Old decision")
    project.add_decision("DEC-NEW-001", "ACTIVE", supersedes=["DEC-OLD-001"],
                          title="New decision")
    project.write(".tickets/REQ-aaaa.md",
                  "---\nid: REQ-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Ticket citing superseded\nrole: engineer\nallowed_paths:\n- src/**\n"
                  "sources:\n- DEC-OLD-001\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# REQ-aaaa\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# A valid authority chain -> no finding
# --------------------------------------------------------------------------

def test_valid_authority_chain_no_finding(project, sandbox, interface):
    """An ACTIVE decision cited by a ticket is fine."""
    project.add_decision("DEC-VALID-001", "ACTIVE", title="A valid decision")
    project.write(".tickets/VAL-aaaa.md",
                  "---\nid: VAL-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Ticket citing valid decision\nrole: engineer\nallowed_paths:\n- src/**\n"
                  "sources:\n- DEC-VALID-001\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# VAL-aaaa\n")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    auth_family = "authority/role limits"
    if auth_family in families:
        status = support.family_status(result, auth_family)
        assert status != support.RED, \
            f"a valid authority chain is flagged RED\n{run.describe()}"
