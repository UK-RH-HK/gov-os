"""KPI success 2 [CAP-01.b, CAP-21.a], batch 4: a commit with two parents that sets ACTIVE again a decision the
owner had demoted. Added after implementation, from a behaviour a review described (DEC-136).

The rule is DEC-360's, as the README reads it: the owner's approval fact is the ``Role: owner`` trailer on the
commit that sets the decision ``ACTIVE``; "later" is by ancestry; setting a decision ``ACTIVE`` again after another
status is a new change and needs its own fact.

In every case here the owner's commit set the decision ``ACTIVE``, and a commit that descends from it set it
``PROPOSED``. The demotion is therefore the later word on the decision. A commit with two parents that holds the
decision ``ACTIVE``, one of whose parents is that demotion or descends from it, is the change that sets ``ACTIVE``
again, however its file came to be: kept from the other parent, or written new. Its own ``Role`` trailer is the
fact.

- The first group: four such commits by an agent, different in kind. Each fails.
- The second group, the controls: the same commit by the owner passes, and so does an agent's merge that brings in
  the owner's own later commit that set the decision ``ACTIVE`` again.

The demotion and the commit that keeps ``ACTIVE`` are never side by side here: a decision that one side sets
``ACTIVE`` and the other demotes, neither descending from the other, is the open package DP-6.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import AGENT, OWNER, adr_path, decision

ADR = "ADR-0010"
PATH = adr_path(ADR)

APPROVED = decision(ADR, "ACTIVE")
DEMOTED = decision(ADR, "PROPOSED")
REWRITTEN = decision(ADR, "ACTIVE", body="Body text, written new by the merge.")
README_ON_THE_BRANCH = {"notes/branch.md": "# Notes of the branch\n\nNo frontmatter here.\n"}


def unapproved(found, record_id=ADR):
    return support.matching(found, support.ACTIVE_UNAPPROVED, [record_id])


def approved_then_branched_then_demoted(project):
    """The owner sets the decision ACTIVE; a branch `work` is cut there and an agent commits another file on it;
    on `main` the owner then sets the decision PROPOSED. Leaves `main` checked out. Returns the two owner commits:
    the one that set ACTIVE and the one that demoted."""
    activation = project.put({**support.CLEAN, PATH: APPROVED}, who=OWNER)
    project.switch("work", new=True)
    project.put(README_ON_THE_BRANCH, who=AGENT)
    project.switch("main")
    demotion = project.put({PATH: DEMOTED}, who=OWNER)
    return activation, demotion


def the_branch_keeps_its_own_tree(project):
    """On the branch the agent merges the main line with the strategy that keeps the branch's tree; the main line
    then moves forward to that merge. The merge's file is its first parent's."""
    approved_then_branched_then_demoted(project)
    project.switch("work")
    merge = project.merge_with("main", who=AGENT, strategy="ours")
    project.switch("main")
    support.git(project.root, "merge", "-q", "--ff-only", "work")
    return merge


def the_main_line_takes_the_branch_file(project):
    """The agent merges the branch into the main line and takes the branch's version of the file. The merge's file
    is its second parent's."""
    approved_then_branched_then_demoted(project)
    return project.merge_with("work", who=AGENT, take={PATH: "work"})


def a_commit_by_hand_names_the_old_commit_as_a_parent(project):
    """A straight history. The agent makes a commit whose first parent is the demotion and whose second parent is
    the owner's old commit, an ancestor of the first, with the old file."""
    activation = project.put({**support.CLEAN, PATH: APPROVED}, who=OWNER)
    demotion = project.put({PATH: DEMOTED}, who=OWNER)
    support.git(project.root, "checkout", activation, "--", PATH)
    return project.commit_by_hand([demotion, activation], "restore ADR-0010", who=AGENT)


def the_merge_writes_the_file_new(project):
    """The agent's merge of the branch writes the file ACTIVE with a body neither parent holds."""
    approved_then_branched_then_demoted(project)
    return project.merge_with("work", who=AGENT, files={PATH: REWRITTEN})


AGENT_MERGES = {
    "the branch keeps its own tree and main moves forward": (the_branch_keeps_its_own_tree, APPROVED),
    "the main line takes the branch's file": (the_main_line_takes_the_branch_file, APPROVED),
    "a commit by hand names the owner's old commit as a parent": (a_commit_by_hand_names_the_old_commit_as_a_parent,
                                                                 APPROVED),
    "the merge writes the file new": (the_merge_writes_the_file_new, REWRITTEN),
}


def assert_head_is(project, commit, text):
    """The fixture is what the case says: `main` is at ``commit``, which has two parents and holds ``text``."""
    assert support.git(project.root, "rev-parse", "main", "HEAD").split() == [commit, commit], "HEAD is elsewhere"
    assert len(support.parents_of(project.root, commit)) == 2, "the fixture's last commit has not two parents"
    assert support.git(project.root, "show", f"HEAD:{PATH}") == text, "the fixture's HEAD holds another file"


# ---- an agent's commit with two parents that sets ACTIVE again fails (DEC-360)

@pytest.mark.parametrize("how", sorted(AGENT_MERGES))
def test_an_agent_merge_that_sets_active_again_a_decision_the_owner_demoted_fails(api, project, how):
    """In a straight line this is `test_an_agent_that_sets_an_approved_decision_active_again_fails`."""
    build, text = AGENT_MERGES[how]
    assert_head_is(project, build(project), text)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


# ---- the controls: the rule does not over-reach

def test_an_owner_merge_that_sets_active_again_a_demoted_decision_passes(api, project):
    """The same merge as "the main line takes the branch's file", made by the owner: the commit that sets ACTIVE
    again carries `Role: owner`."""
    approved_then_branched_then_demoted(project)
    merge = project.merge_with("work", who=OWNER, take={PATH: "work"})
    assert_head_is(project, merge, APPROVED)
    found = api.check(project.root)
    assert not unapproved(found), support.show(found)


def test_an_agent_merge_that_brings_in_the_owner_commit_that_set_active_again_passes(api, project):
    """After the demotion, the owner's commit on a branch sets the decision ACTIVE again. The agent's merge commit
    brings it to the main line, whose own parent still holds PROPOSED, and sets nothing: the branch's commit
    descends from the demotion and is the later word."""
    project.put({**support.CLEAN, PATH: APPROVED}, who=OWNER)
    project.put({PATH: DEMOTED}, who=OWNER)
    project.switch("owner-accepts-again", new=True)
    project.put({PATH: APPROVED}, who=OWNER)
    project.switch("main")
    project.put({"README.md": "# A project\n\nReworded.\n"}, who=AGENT)
    merge = project.merge("owner-accepts-again", who=AGENT)
    assert_head_is(project, merge, APPROVED)
    found = api.check(project.root)
    assert not unapproved(found), support.show(found)
