"""KPI success 2 [CAP-01.b, CAP-21.a], batch 5: the approval rule judges a merge against the merge base (DEC-398).
Added after implementation, from the owner's decision on package DP-6 and from behaviours a review described
(DEC-136).

The rule, as the README states it. A decision is its ``id``; its state in a commit is whether the commit holds it
and with which ``status``, wherever its file lies. A commit with several parents that holds the decision ``ACTIVE``
sets nothing only when

- a parent holds it ``ACTIVE``, and
- no other parent changed its id, its status or its presence since the merge base, and
- every parent that holds it ``ACTIVE`` was set ``ACTIVE`` by commits that carry the owner's fact.

Otherwise the merge commit is itself the change that sets the decision ``ACTIVE`` and its own ``Role`` trailer is
the fact (DEC-360): an agent's fails, the owner's passes.

- The first group: one side sets ``ACTIVE``, the other demotes or removes, neither descends from the other
  (package DP-6 of batch 4, decided), and the merge that keeps the owner's file over an agent's (the residual of
  batch 3).
- The second group: three histories a review described, in which an agent's merge keeps a decision ``ACTIVE``
  against the owner's later demotion and the checker as built says nothing.
- The third group, the controls: everyday merges pass.

Where the parents have several merge bases or none: ``test_w1_11_approval_fail_closed.py``.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import AGENT, OWNER, adr_path, decision

ADR = "ADR-0010"
PATH = adr_path(ADR)
MOVED = "decisions/ADR-0010.md"

APPROVED = decision(ADR, "ACTIVE")
DEMOTED = decision(ADR, "PROPOSED")
ACCEPTED_AGAIN = decision(ADR, "ACTIVE", body="Body text, accepted again by the owner.")
BY_THE_AGENT = decision(ADR, "ACTIVE", body="Body text, set ACTIVE again by an agent.")
THIRD_VERSION = decision(ADR, "ACTIVE", body="Body text, written new by the first merge.")
NOTES = "# Notes\n\nNo frontmatter here.\n"

# How the owner takes the decision back, and what the file was before the owner's approving commit: the later
# word puts the decision where it stood before it was approved.
LATER_WORDS = ("demoted to PROPOSED", "removed")


def unapproved(found, record_id=ADR):
    return support.matching(found, support.ACTIVE_UNAPPROVED, [record_id])


def take_back(project, how, path=PATH):
    """The owner's later word on the decision: `status: PROPOSED`, or the file removed."""
    if how == "removed":
        return project.remove(path, who=OWNER, message="withdraw ADR-0010")
    return project.put({path: DEMOTED}, who=OWNER, message="ADR-0010 is PROPOSED again")


def assert_head_holds(project, commit, path, text):
    """The fixture is what the case says: `HEAD` is the merge ``commit`` and holds ``text`` at ``path``."""
    assert support.git(project.root, "rev-parse", "HEAD").strip() == commit, "HEAD is elsewhere"
    assert len(support.parents_of(project.root, commit)) == 2, "the fixture's last commit has not two parents"
    assert support.git(project.root, "show", f"HEAD:{path}") == text, "the fixture's HEAD holds another file"


# ---- one side sets ACTIVE, the other demotes or removes, neither later (DEC-398)

def one_side_accepts_the_other_takes_back(project, how, merger):
    """The owner's commit set the decision ACTIVE; two lines part there. On a branch the owner demotes it and sets
    it ACTIVE again with a new text. On the main line the owner takes it back. Neither commit descends from the
    other. The merge keeps the branch's ACTIVE file."""
    project.put({**support.CLEAN, PATH: APPROVED}, who=OWNER)
    project.switch("owner-accepts-again", new=True)
    project.put({PATH: DEMOTED}, who=OWNER)
    project.put({PATH: ACCEPTED_AGAIN}, who=OWNER)
    project.switch("main")
    take_back(project, how)
    merge = project.merge_with("owner-accepts-again", who=merger, take={PATH: "owner-accepts-again"})
    assert_head_holds(project, merge, PATH, ACCEPTED_AGAIN)


@pytest.mark.parametrize("how", LATER_WORDS)
def test_an_agent_merge_that_keeps_active_over_a_concurrent_owner_demotion_fails(api, project, how):
    """The main line changed the decision's status (or its presence) since the merge base, so the merge is not a
    commit that sets nothing: choosing ACTIVE over the other side's word is the change, and an agent made it."""
    one_side_accepts_the_other_takes_back(project, how, AGENT)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def test_an_owner_merge_that_keeps_active_over_a_concurrent_demotion_passes(api, project):
    """The control: the same merge by the owner carries the fact."""
    one_side_accepts_the_other_takes_back(project, "demoted to PROPOSED", OWNER)
    found = api.check(project.root)
    assert not unapproved(found), support.show(found)


def test_an_agent_merge_that_keeps_the_owner_file_over_an_agent_file_at_the_same_path_fails(api, project):
    """Two branches add the same path, the owner's and an agent's, both ACTIVE; the agent's merge keeps the owner's
    file. Both sides changed the decision's presence since the merge base, and one of the two ACTIVE parents was
    set by an agent: the merge decides which decision stands, and an agent made it. The mirror of batch 3's
    `test_an_agent_decision_kept_by_a_merge_over_the_owner_file_at_the_same_path_fails`."""
    project.put(support.CLEAN)
    project.switch("owner-adds", new=True)
    owners = decision(ADR, "ACTIVE", title="The owner's decision")
    project.put({PATH: owners}, who=OWNER)
    project.switch("main")
    project.put({PATH: decision(ADR, "ACTIVE", title="The agent's decision", body="Another decision.")}, who=AGENT)
    merge = project.merge_with("owner-adds", who=AGENT, take={PATH: "owner-adds"})
    assert_head_holds(project, merge, PATH, owners)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


# ---- three histories a review described: the owner's later word is undone by an agent's merge (DEC-360, DEC-398)

def the_demoted_line_has_merged_an_old_branch(project, how, merger, with_the_old_branch=True):
    """Before the owner's approval the decision stood as ``how`` says (PROPOSED, or no file), and a branch `old` was
    cut there; it never touches the decision. The owner sets the decision ACTIVE; a branch `work` is cut there and
    keeps it. On the main line the owner takes the decision back, and an agent merges `old`. Then the merge of
    `work` keeps the decision ACTIVE."""
    project.put({**support.CLEAN, **({} if how == "removed" else {PATH: DEMOTED})}, who=OWNER)
    project.switch("old", new=True)
    project.put({"notes/old.md": NOTES}, who=AGENT)
    project.switch("main")
    project.put({PATH: APPROVED}, who=OWNER, message="accept ADR-0010")
    project.switch("work", new=True)
    project.put({"notes/work.md": NOTES}, who=AGENT)
    project.switch("main")
    take_back(project, how)
    if with_the_old_branch:
        project.merge("old", who=AGENT)
    merge = project.merge_with("work", who=merger, take={PATH: "work"})
    assert_head_holds(project, merge, PATH, APPROVED)


@pytest.mark.parametrize("how", LATER_WORDS)
def test_an_agent_merge_that_keeps_active_fails_although_the_demoted_line_merged_an_old_branch(api, project, how):
    """The merge base of the two parents is the owner's approving commit, where the decision is ACTIVE; the main
    line holds another state, so it changed the decision since. That an old branch, merged in between, holds the
    state from before the approval makes the demotion no earlier word."""
    the_demoted_line_has_merged_an_old_branch(project, how, AGENT)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


@pytest.mark.parametrize("how", LATER_WORDS)
def test_the_same_merge_fails_without_the_old_branch(api, project, how):
    """The same history without the merge of `old`: flagged by the checker as built. The pair shows that the merge
    of an old branch is what hid the case above."""
    the_demoted_line_has_merged_an_old_branch(project, how, AGENT, with_the_old_branch=False)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def the_decision_is_moved_on_a_branch(project, how, merger):
    """The owner sets the decision ACTIVE at `docs/adr/`. A branch only moves the file to `decisions/`. On the main
    line the owner takes the decision back at the old path, or (``how`` is None) leaves it alone. The merge holds
    the moved ACTIVE file and no file at the old path."""
    project.put({**support.CLEAN, PATH: APPROVED}, who=OWNER)
    project.switch("move", new=True)
    project.move(PATH, MOVED, who=AGENT, message="move ADR-0010")
    project.switch("main")
    if how:
        take_back(project, how)
    else:
        project.put({"README.md": "# A project\n\nReworded.\n"}, who=AGENT)
    merge = project.merge_with("move", who=merger, take={MOVED: "move"}, drop=[PATH])
    assert_head_holds(project, merge, MOVED, APPROVED)
    assert not (project.root / PATH).exists(), "the fixture's merge still holds the old path"


@pytest.mark.parametrize("how", LATER_WORDS)
def test_an_agent_merge_that_keeps_a_moved_active_file_over_a_demotion_at_the_old_path_fails(api, project, how):
    """The decision is its id. The branch that moved the file changed neither its id, its status nor its presence;
    the main line changed its status (or removed it). The merge that holds it ACTIVE is the change. With the file
    removed on the main line git makes this merge by itself, with no conflict."""
    the_decision_is_moved_on_a_branch(project, how, AGENT)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [MOVED])


def test_a_second_merge_that_keeps_the_owner_file_does_not_hide_an_agent_reactivation(api, project):
    """The owner sets the decision ACTIVE and a side branch keeps that file. On the main line the owner demotes it
    and an agent sets it ACTIVE again. The agent merges the side branch and writes a third version of the file; a
    second merge of the side branch then holds the owner's original file again. The main line's ACTIVE decision was
    set by an agent's commits, after the owner's demotion: the last merge sets ACTIVE what the owner demoted."""
    project.put({**support.CLEAN, PATH: APPROVED}, who=OWNER)
    project.switch("side", new=True)
    project.put({"notes/side.md": NOTES}, who=AGENT)
    project.switch("main")
    take_back(project, "demoted to PROPOSED")
    project.put({PATH: BY_THE_AGENT}, who=AGENT, message="accept ADR-0010 again")
    project.merge_with("side", who=AGENT, files={PATH: THIRD_VERSION})
    project.switch("side")
    project.put({"notes/side-2.md": NOTES}, who=AGENT)
    project.switch("main")
    merge = project.merge_with("side", who=AGENT, take={PATH: "side"})
    assert_head_holds(project, merge, PATH, APPROVED)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


# ---- the controls: the owner's such merge, and everyday merges (DEC-398, DEC-360)

def test_an_owner_merge_that_keeps_active_over_the_demoted_line_passes(api, project):
    """The merge of `work` in the first history, made by the owner."""
    the_demoted_line_has_merged_an_old_branch(project, "demoted to PROPOSED", OWNER)
    found = api.check(project.root)
    assert not unapproved(found), support.show(found)


def test_an_owner_merge_that_keeps_the_moved_file_over_the_demotion_passes(api, project):
    """The merge of `move` in the second history, made by the owner."""
    the_decision_is_moved_on_a_branch(project, "demoted to PROPOSED", OWNER)
    found = api.check(project.root)
    assert not unapproved(found), support.show(found)


def test_an_agent_merge_of_a_branch_that_only_moved_an_approved_decision_passes(api, project):
    """A move sets nothing and no side changed the decision: the owner's approving commit is still the fact."""
    the_decision_is_moved_on_a_branch(project, None, AGENT)
    found = api.check(project.root)
    assert found == [], f"a register the owner approved does not pass after a move:\n{support.show(found)}"


def test_an_agent_integration_merge_of_a_branch_where_the_owner_added_a_decision_passes(api, project):
    """An ordinary integration merge: the branch's owner commit adds the decision ACTIVE, the main line moved on
    without it, git makes the merge by itself."""
    project.put(support.CLEAN, who=OWNER)
    project.switch("ticket", new=True)
    project.put({PATH: APPROVED}, who=OWNER, message="accept ADR-0010")
    project.put({"notes/ticket.md": NOTES}, who=AGENT)
    project.switch("main")
    project.put({"README.md": "# A project\n\nReworded.\n"}, who=AGENT)
    merge = project.merge("ticket", who=AGENT)
    assert_head_holds(project, merge, PATH, APPROVED)
    found = api.check(project.root)
    assert found == [], f"an ordinary integration merge does not pass:\n{support.show(found)}"


def test_an_agent_merge_that_brings_nothing_about_decisions_passes(api, project):
    project.put({**support.CLEAN, PATH: APPROVED}, who=OWNER)
    project.switch("ticket", new=True)
    project.put({"notes/ticket.md": NOTES, "src/module.py": "VALUE = 1\n"}, who=AGENT)
    project.switch("main")
    project.put({"README.md": "# A project\n\nReworded.\n"}, who=AGENT)
    project.merge("ticket", who=AGENT)
    found = api.check(project.root)
    assert found == [], f"a merge that touches no decision does not pass:\n{support.show(found)}"


@pytest.mark.parametrize("before", ["PROPOSED before the approval", "no file before the approval"])
def test_an_old_branch_merged_late_into_a_line_where_the_owner_approved_passes(api, project, before):
    """A branch cut before the owner's approval, which never touched the decision, is merged by an agent into the
    main line, where the decision is ACTIVE by the owner and untouched since. The old branch did not change the
    decision since the merge base; the merge sets nothing."""
    project.put({**support.CLEAN, **({PATH: DEMOTED} if before.startswith("PROPOSED") else {})}, who=OWNER)
    project.switch("old", new=True)
    project.put({"notes/old.md": NOTES}, who=AGENT)
    project.switch("main")
    project.put({PATH: APPROVED}, who=OWNER, message="accept ADR-0010")
    project.put({"README.md": "# A project\n\nReworded.\n"}, who=AGENT)
    merge = project.merge("old", who=AGENT)
    assert_head_holds(project, merge, PATH, APPROVED)
    found = api.check(project.root)
    assert found == [], f"an old branch merged late does not pass:\n{support.show(found)}"


def test_the_main_line_merged_back_into_a_ticket_branch_and_the_branch_merged_passes(api, project):
    """A ticket branch is cut before the owner's approval. An agent merges the main line back into it (the branch
    is the first parent, the approval comes with the second), works on, and merges the branch into the main line,
    which has moved on. Neither merge sets anything."""
    project.put({**support.CLEAN, PATH: DEMOTED}, who=OWNER)
    project.switch("ticket", new=True)
    project.put({"notes/ticket.md": NOTES}, who=AGENT)
    project.switch("main")
    project.put({PATH: APPROVED}, who=OWNER, message="accept ADR-0010")
    project.switch("ticket")
    back = project.merge("main", who=AGENT)
    assert_head_holds(project, back, PATH, APPROVED)
    assert api.check(project.root) == [], "the ticket branch does not pass after the merge back"
    project.put({"notes/ticket-2.md": NOTES}, who=AGENT)
    project.switch("main")
    project.put({"README.md": "# A project\n\nReworded.\n"}, who=AGENT)
    merge = project.merge("ticket", who=AGENT)
    assert_head_holds(project, merge, PATH, APPROVED)
    found = api.check(project.root)
    assert found == [], f"the main line does not pass after the ticket branch is merged:\n{support.show(found)}"
