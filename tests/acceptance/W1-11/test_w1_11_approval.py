"""KPI success 2 [CAP-01.b, CAP-21.a]: a change that sets a decision ACTIVE without an owner approval fact from
git fails.

"The change" is the commit that last set the decision's ``status`` to ``ACTIVE``: the commit that added the file
with that status, or the one that changed the status to it.

- The first group holds whatever an owner approval fact turns out to be (package DP-2). The agent's commits differ
  from the owner's in every respect a rule could read: author, committer, ``Role`` trailer, no signature, no tag.
- The second group follows DP-2's recommended option: the owner's commit carries ``Role: owner`` in its final
  trailer block. Those tests wait on DP-2.
"""

from __future__ import annotations

import w1_11_support as support
from w1_11_support import AGENT, ANONYMOUS, OWNER, adr_path, decision

ADR = "ADR-0010"
PATH = adr_path(ADR)


def unapproved(found, record_id=ADR):
    return support.matching(found, support.ACTIVE_UNAPPROVED, [record_id])


# ---- whatever an owner approval fact is: an agent's change carries none

def test_an_agent_commit_that_adds_an_active_decision_fails(api, project):
    project.put(support.CLEAN)
    project.put({PATH: decision(ADR, "ACTIVE")}, who=AGENT)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def test_an_agent_commit_that_changes_a_status_to_active_fails(api, project):
    project.put({**support.CLEAN, PATH: decision(ADR, "PROPOSED")})
    project.put({PATH: decision(ADR, "ACTIVE")}, who=AGENT)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def test_a_commit_without_any_trailer_that_sets_a_decision_active_fails(api, project):
    project.put(support.CLEAN)
    project.put({PATH: decision(ADR, "ACTIVE")}, who=ANONYMOUS)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def test_a_project_file_cannot_manufacture_the_approval(api, project):
    """CAP-01.b: what the record says about its own approval is not a fact."""
    project.put(support.CLEAN)
    claimed = decision(ADR, "ACTIVE", body="ACCEPTED (owner, 2026-10-04). Approved by the owner.",
                       approved_by="owner", approved=True, role="owner", author="The Owner")
    project.put({PATH: claimed,
                 "governance/project/approvals.yaml": f"approved:\n  - id: {ADR}\n    by: owner\n"}, who=AGENT)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def test_the_owner_named_in_the_message_body_of_an_agent_commit_is_no_approval(api, project):
    """DEC-182: from 2026-10-03 a trailer counts only in the final trailer block."""
    project.put(support.CLEAN)
    project.write(PATH, decision(ADR, "ACTIVE"))
    project.commit("accept ADR-0010\n\nRole: owner\nApproved-by: The Owner <owner@example.invalid>\n\n"
                   "A closing paragraph, which is not a trailer block.", who=AGENT)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def test_an_agent_commit_that_adds_a_proposed_decision_passes(api, project):
    project.put(support.CLEAN)
    project.put({PATH: decision(ADR, "PROPOSED")}, who=AGENT)
    assert not unapproved(api.check(project.root))


def test_every_unapproved_active_decision_is_flagged(api, project):
    project.put(support.CLEAN)
    project.put({adr_path("ADR-0010"): decision("ADR-0010", "ACTIVE"),
                 adr_path("ADR-0011"): decision("ADR-0011", "ACTIVE")}, who=AGENT)
    found = api.check(project.root)
    for record_id in ("ADR-0010", "ADR-0011"):
        support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [record_id], [adr_path(record_id)])


# ---- with DP-2's recommended option: `Role: owner` in the final trailer block

def test_an_owner_commit_that_sets_a_decision_active_passes(api, project):
    project.put({**support.CLEAN, PATH: decision(ADR, "PROPOSED")}, who=AGENT)
    project.put({PATH: decision(ADR, "ACTIVE")}, who=OWNER)
    found = api.check(project.root)
    assert not unapproved(found), support.show(found)


def test_a_register_the_owner_approved_passes_the_whole_check(api, project):
    project.put(support.CLEAN, who=OWNER)
    found = api.check(project.root)
    assert found == [], f"a clean register, committed by the owner, does not pass:\n{support.show(found)}"


def test_an_agent_edit_that_leaves_an_approved_decision_active_passes(api, project):
    """The agent's change does not set the decision ACTIVE: the owner's commit did."""
    project.put({**support.CLEAN, PATH: decision(ADR, "ACTIVE")}, who=OWNER)
    project.put({PATH: decision(ADR, "ACTIVE", body="Body text, with a typo fixed.")}, who=AGENT)
    found = api.check(project.root)
    assert not unapproved(found), support.show(found)


def test_an_agent_that_sets_an_approved_decision_active_again_fails(api, project):
    """An approval covers the change that carries it, not a later one."""
    project.put({**support.CLEAN, PATH: decision(ADR, "ACTIVE")}, who=OWNER)
    project.put({PATH: decision(ADR, "PROPOSED")}, who=AGENT)
    project.put({PATH: decision(ADR, "ACTIVE")}, who=AGENT)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])
