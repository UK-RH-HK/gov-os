"""KPI success 2 [CAP-01.b, CAP-21.a]: a change that sets a decision ACTIVE without an owner approval fact from
git fails.

"The change" is the commit that last set the decision's ``status`` to ``ACTIVE``: the commit that added the file
with that status, or the one that changed the status to it.

The owner's approval fact is the ``Role: owner`` trailer on that commit, and a later owner commit approves nothing
earlier (DEC-360). The trailer is read from the final trailer block; for a commit made before 2026-10-03 the
message body counts too (DEC-182).

- The first group: a change that carries no such trailer fails.
- The second group: the owner's commit approves the change it carries, and no other.
- The third group: commits made before 2026-10-03.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import AGENT, AGENT_AS_OWNER, ANONYMOUS, OWNER, adr_path, decision

ADR = "ADR-0010"
PATH = adr_path(ADR)


def unapproved(found, record_id=ADR):
    return support.matching(found, support.ACTIVE_UNAPPROVED, [record_id])


# ---- a change without the owner's trailer fails

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


def test_the_owner_name_and_email_on_an_agent_commit_are_no_approval(api, project):
    """DEC-360: the fact is the trailer. Here agents commit under the owner's name and email."""
    project.put(support.CLEAN)
    project.put({PATH: decision(ADR, "ACTIVE")}, who=AGENT_AS_OWNER)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


# ---- the owner's commit approves the change it carries, and no other (DEC-360)

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


LATER_OWNER_COMMITS = {
    "edits the decision": {PATH: decision(ADR, "ACTIVE", body="Body text, reworded by the owner.")},
    "changes another file": {"README.md": "# A project\n\nReworded by the owner.\n"},
}


@pytest.mark.parametrize("later", sorted(LATER_OWNER_COMMITS))
def test_a_later_owner_commit_that_does_not_set_active_approves_nothing_earlier(api, project, later):
    """DEC-360: "A later owner commit approves nothing earlier". The agent's commit set the decision ACTIVE."""
    project.put({**support.CLEAN, PATH: decision(ADR, "PROPOSED")})
    project.put({PATH: decision(ADR, "ACTIVE")}, who=AGENT)
    project.put(LATER_OWNER_COMMITS[later], who=OWNER)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


# ---- commits made before 2026-10-03 (DEC-182)

def test_the_owner_role_in_the_message_body_of_a_commit_made_before_the_trailer_rule_approves(api, project):
    """DEC-182: a check that reads trailers falls back to the message body for a commit made before 2026-10-03.
    The same message, dated after it, is `test_the_owner_named_in_the_message_body_of_an_agent_commit_is_no_approval`."""
    project.write(PATH, decision(ADR, "ACTIVE"))
    project.commit("accept ADR-0010\n\nRole: owner\n\nA closing paragraph, which is not a trailer block.",
                   who=OWNER, trailers=(), date=support.BEFORE_THE_TRAILER_RULE)
    project.put(support.CLEAN)
    found = api.check(project.root)
    assert not unapproved(found), support.show(found)


def test_an_agent_commit_made_before_the_trailer_rule_is_no_approval(api, project):
    """An old commit is read from its whole message; it is not approved for being old."""
    project.write(PATH, decision(ADR, "ACTIVE"))
    project.commit("accept ADR-0010\n\nRole: engineer\n\nA closing paragraph, which is not a trailer block.",
                   who=AGENT, trailers=(), date=support.BEFORE_THE_TRAILER_RULE)
    project.put(support.CLEAN)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])
