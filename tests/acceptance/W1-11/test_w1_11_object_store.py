"""Batch 4: a repository whose object store does not hold every earlier version of a decision file. Added after
implementation, from behaviours a review described (DEC-136).

Two rules meet here.

- **KPI success 3 and failure line 2: files stay byte-identical; the check only reads.** `.git/` is under the
  root. A check writes no file there either, and fetches nothing from a remote: a clone made with a blob filter
  holds only the files of its checkout, and reading an earlier version through git would fetch it and write new
  pack files. The first group.
- **KPI success 2 and DEC-360: a history the check cannot read approves nothing.** The approval fact is on the
  commit that set the decision ``ACTIVE``. When the version of the file in an earlier commit cannot be read, the
  check does not know that commit left the status alone, so a later owner commit is not shown to be the one that
  set it. The check gives ``ACTIVE_UNAPPROVED`` for the decision or raises ``GovError``; it never passes. The
  second group.

The history in every case: the owner adds the decision ``PROPOSED``, an agent sets it ``ACTIVE``, the owner then
edits its body and leaves it ``ACTIVE``. With every object present this is flagged
(`test_a_later_owner_commit_that_does_not_set_active_approves_nothing_earlier`).

These cases run the check without loading the store: the checker needs none (README), and what `gov.store.load`
does in such a repository is not this ticket's.
"""

from __future__ import annotations

import shutil

import w1_11_support as support
from w1_11_support import AGENT, OWNER, adr_path, decision

ADR = "ADR-0010"
PATH = adr_path(ADR)


def agent_sets_active_then_the_owner_edits(project):
    """Returns the agent's commit, the one that set the decision ACTIVE."""
    project.put({**support.CLEAN, PATH: decision(ADR, "PROPOSED")}, who=OWNER)
    agents = project.put({PATH: decision(ADR, "ACTIVE")}, who=AGENT)
    project.put({PATH: decision(ADR, "ACTIVE", body="Body text, reworded by the owner.")}, who=OWNER)
    return agents


def assert_no_pass(kind, result):
    """``ACTIVE_UNAPPROVED`` for the decision, or a ``GovError``; never a pass."""
    if kind == "findings":
        support.assert_flagged(result, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def partial(project, tmp_path):
    """A clone of ``project`` with a blob filter, and the id of the agent's version of the file, which it lacks."""
    agents = agent_sets_active_then_the_owner_edits(project)
    clone = support.partial_clone(project.root, tmp_path / "partial")
    blob = support.git(project.root, "rev-parse", f"{agents}:{PATH}").strip()
    assert blob in support.absent_objects(clone.root), "the fixture is no partial clone: it holds every version"
    return clone


# ---- the check writes nothing under the root, `.git/` included, and fetches nothing

def test_a_check_leaves_every_file_under_git_as_it_was(api, project):
    """The control: in a repository that holds every object, no file under the root differs after a check that
    finds something, `.git/` included."""
    agent_sets_active_then_the_owner_edits(project)
    before = support.everything_under(project.root)
    kind, result = support.outcome(api, project.root)
    assert_no_pass(kind, result)
    assert support.differences(before, support.everything_under(project.root)) == []


def test_a_check_of_a_partial_clone_fetches_nothing_and_writes_nothing(api, project, tmp_path):
    """The remote is there to be asked. The check does not ask it: no pack file and no other file appears under
    `.git/`, and the earlier versions are as absent after the check as before."""
    clone = partial(project, tmp_path)
    before, absent = support.everything_under(clone.root), support.absent_objects(clone.root)
    kind, result = support.outcome(api, clone.root)
    assert support.differences(before, support.everything_under(clone.root)) == []
    assert support.absent_objects(clone.root) == absent, "the check fetched objects from the remote"
    assert_no_pass(kind, result)


def test_a_check_of_a_partial_clone_whose_remote_is_out_of_reach_does_not_pass(api, project, tmp_path):
    """The remote's folder is gone. The check gives a finding or a `GovError`, and writes nothing."""
    clone = partial(project, tmp_path)
    shutil.move(str(project.root), str(tmp_path / "moved-away"))
    before = support.everything_under(clone.root)
    kind, result = support.outcome(api, clone.root)
    assert support.differences(before, support.everything_under(clone.root)) == []
    assert_no_pass(kind, result)


# ---- a version of the file that cannot be read approves nothing (DEC-360)

def test_a_missing_object_does_not_make_a_later_owner_commit_the_approval(api, project):
    """The object that holds the agent's version of the file is absent from the object store. It is not "the file
    did not exist then": the owner's edit is not the commit that set the decision ACTIVE."""
    agents = agent_sets_active_then_the_owner_edits(project)
    support.remove_object(project.root, f"{agents}:{PATH}")
    kind, result = support.outcome(api, project.root)
    assert_no_pass(kind, result)
