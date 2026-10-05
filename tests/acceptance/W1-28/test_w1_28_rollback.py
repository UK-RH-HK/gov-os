"""KPI success 2, second half [CAP-05.c], with the record and the repeat of KPI success 3 [CAP-05.d].

"gov pause --rollback <ticket> reverts the ticket's commits with git revert and
records it" (ROLLBACK_TRANSACTION).

- **The ticket's commits** are those whose ``Task:`` trailer names the ticket,
  in the final trailer block; a commit made before 2026-10-03 is read from the
  whole message (DEC-182, as ``gov.store`` reads them).
- **With git revert:** history only grows. The HEAD before the rollback is an
  ancestor of the HEAD after it, and HEAD's reflog shows no reset, rebase or
  amend. What HEAD holds afterwards is the project without the ticket's
  changes and with every other ticket's.

DEC-366, point by point:

- one ``git revert --no-edit`` per commit of the ticket, newest first: one
  revert commit for each, with git's own message (``This reverts commit
  <hash>.``); the fixture's second commit changes the line its first commit
  wrote, so the reverts apply cleanly only newest first;
- a merge commit is skipped and named in the result, which says that a merge's
  own conflict resolutions stay;
- a revert commit carries ``Role:`` and ``Reverts-Task: <ticket>``, not
  ``Task:``;
- a conflicting revert aborts everything with an error;
- an unknown ticket is an error; a ticket with no commit succeeds with an
  empty list;
- a dirty tree is refused;
- a repeat reverts nothing and succeeds.

DEC-367: the record is one commit to the ticket file, made after the reverts,
with the trailers ``Task: <ticket>`` and ``Reverts-Task: <ticket>``.
DEC-368: the rollback also sets the freeze flag.

**The result** lists the reverted commits as ``reverted``, newest first, and
the skipped merge commits as ``skipped_merges``; an entry names its commit by
at least seven characters of the hash.

Not asserted (decision packages DP-10 and DP-11): whether the flag is set by a
rollback that ends with an error, and whether a rollback that reverts nothing
on its first run writes a record.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import w1_28_support as support

SHORT = support.SHORT


def _rollback(pause, interface, ticket=support.TICKET, role=support.OWNER):
    return support.succeeded(pause("--rollback", ticket, role=role), interface)


def _reverts(project, since):
    """The commits made after ``since`` without the last, which is the record; oldest first."""
    made = support.new_commits(project, since)
    assert made, "the rollback made no commit"
    return made[:-1]


# --------------------------------------------------------------------------
# The plain case
# --------------------------------------------------------------------------

def test_rollback_reverts_the_commits_of_the_ticket_and_no_other(project, pause, interface, history):
    _rollback(pause, interface)
    support.assert_rolled_back(project)


def test_rollback_only_adds_commits(project, pause, interface, history):
    before, entries = support.head(project), len(support.reflog(project))
    branch = support.git(project, "symbolic-ref", "HEAD")
    _rollback(pause, interface)

    after = support.head(project)
    assert after != before, "the rollback made no commit"
    support.git(project, "merge-base", "--is-ancestor", before, after)  # fails when history was rewritten
    for commit in history:
        support.git(project, "merge-base", "--is-ancestor", commit, after)
    assert support.git(project, "symbolic-ref", "HEAD") == branch, "the rollback changed the branch"
    new = support.reflog(project)[:len(support.reflog(project)) - entries]
    moved = [entry for entry in new if entry.startswith(("reset", "rebase")) or "amend" in entry.split(":")[0]]
    assert not moved, f"HEAD was moved by something other than new commits: {moved}"


def test_rollback_leaves_no_uncommitted_change(project, pause, interface, history):
    """The reverts are commits, and so is the record (DEC-367)."""
    _rollback(pause, interface)
    assert support.porcelain(project) == "", f"the rollback left uncommitted changes:\n{support.porcelain(project)}"
    assert not support.revert_in_progress(project), "a revert is still in progress"


def test_rollback_makes_one_revert_commit_per_commit_newest_first(project, pause, interface, history):
    first, other, second = history
    before = support.head(project)
    _rollback(pause, interface)
    reverts = _reverts(project, before)
    assert len(reverts) == 2, f"2 commits of the ticket, and {len(reverts)} revert commits before the record"
    for revert, original in zip(reverts, (second, first)):  # oldest revert first: it reverts the newest commit
        text = support.message(project, revert)
        assert f"This reverts commit {original}" in text, \
            f"the revert commit {revert[:SHORT]} is not git's revert of {original[:SHORT]}:\n{text}"
        assert other not in text


def test_a_revert_commit_carries_role_and_reverts_task_and_not_task(project, pause, interface, history):
    """The ``Role:`` is the caller's: the owner's, who calls with no ``GOV_ROLE`` (DEC-365, DEC-360)."""
    before = support.head(project)
    _rollback(pause, interface)
    for revert in _reverts(project, before):
        text = support.message(project, revert)
        assert support.trailers(project, revert, "Reverts-Task") == [support.TICKET], \
            f"the revert commit {revert[:SHORT]} has not the one trailer `Reverts-Task: {support.TICKET}`:\n{text}"
        assert support.trailers(project, revert, "Task") == [], \
            f"the revert commit {revert[:SHORT]} carries a `Task:` trailer:\n{text}"
        assert support.trailers(project, revert, "Role") == [support.OWNER_NAME], \
            f"the revert commit {revert[:SHORT]} has not the one trailer `Role: {support.OWNER_NAME}`:\n{text}"


def test_the_orchestrators_revert_commits_carry_its_role(project, pause, interface, history):
    before = support.head(project)
    _rollback(pause, interface, role=support.ORCHESTRATOR)
    for revert in _reverts(project, before):
        assert support.trailers(project, revert, "Role") == [support.ORCHESTRATOR], \
            support.message(project, revert)


def test_the_result_names_each_reverted_commit_newest_first(pause, interface, history):
    first, other, second = history
    result = _rollback(pause, interface)
    reverted = support.listed(result, "reverted")
    assert len(reverted) == 2 and support.names(reverted[0], second) and support.names(reverted[1], first), \
        f"`reverted` is not the ticket's 2 commits, newest first ({second[:SHORT]}, {first[:SHORT]}): {reverted}"
    assert other[:SHORT] not in support.text_of(result), \
        f"the result names the other ticket's commit {other[:SHORT]}: {result}"
    assert support.listed(result, "skipped_merges") == []


def test_rollback_sets_the_freeze_flag(project, sandbox, pause, interface, history):
    """DEC-368."""
    assert not support.is_paused(project)
    _rollback(pause, interface)
    assert support.flag(project).is_file(), f"gov pause --rollback did not set {support.FREEZE_FLAG_REL}"
    support.assert_denied(support.guard_write(project, sandbox, support.ENGINEER), "after --rollback, the write")


def test_rollback_runs_on_a_paused_project(paused, pause, interface, history):
    """The owner pauses first, then rolls back: the command commits as its own process, which the guard does not judge."""
    _rollback(pause, interface)
    support.assert_rolled_back(paused)
    assert support.is_paused(paused), "the rollback cleared the flag"


# --------------------------------------------------------------------------
# The record (DEC-367)
# --------------------------------------------------------------------------

def test_the_rollback_is_recorded_by_a_commit_to_the_ticket_file_after_the_reverts(project, pause, interface,
                                                                                    history):
    before = support.head(project)
    _rollback(pause, interface)
    record, reverts = support.head(project), _reverts(project, before)
    text = support.message(project, record)
    assert support.changed_paths(project, record) == [support.ticket_rel()], \
        f"the last commit of the rollback changes {support.changed_paths(project, record)}, " \
        f"not {support.ticket_rel()} alone"
    assert support.trailers(project, record, "Task") == [support.TICKET], \
        f"the record commit has not the one trailer `Task: {support.TICKET}`:\n{text}"
    assert support.trailers(project, record, "Reverts-Task") == [support.TICKET], \
        f"the record commit has not the one trailer `Reverts-Task: {support.TICKET}`:\n{text}"
    for revert in reverts:
        assert support.is_ancestor(project, revert, record), "the record commit was not made after the reverts"
        assert support.ticket_rel() not in support.changed_paths(project, revert), \
            f"the revert commit {revert[:SHORT]} changes the ticket file"
    assert support.is_paused(project), "the record was committed and the freeze (DEC-368) is not set"


def test_the_ticket_file_names_each_reverted_commit(project, pause, interface, history):
    """CAP-05.d, "recovery auditable (recorded in the ticket)": the ticket's file says what was reverted."""
    first, other, second = history
    before = support.ticket_file(project)
    untouched = support.ticket_file(project, support.OTHER_TICKET)
    _rollback(pause, interface)
    text = support.committed(project, support.ticket_rel())
    assert text != before, f"{support.ticket_rel()} is unchanged in HEAD: the rollback was not recorded in the ticket"
    for commit in (first, second):
        assert commit[:SHORT] in text, f"{support.ticket_rel()} does not name the reverted commit {commit[:SHORT]}"
    assert other[:SHORT] not in text, f"{support.ticket_rel()} names the other ticket's commit"
    assert support.status_line(text) == support.status_line(before), "the rollback changed the ticket's status"
    assert support.ticket_file(project, support.OTHER_TICKET) == untouched, "the other ticket's file changed"


# --------------------------------------------------------------------------
# The edge cases of DEC-366
# --------------------------------------------------------------------------

def test_rollback_gives_the_same_result_on_repeat(project, pause, interface, history):
    """A repeat reverts nothing and succeeds: neither the reverts nor the record are reverted, and no commit is made."""
    _rollback(pause, interface)
    after, tree = support.head(project), support.tree_outside_tickets(project)
    result = _rollback(pause, interface)
    assert support.listed(result, "reverted") == [], f"the repeat reverted something: {result}"
    support.assert_rolled_back(project, "after the repeat")
    assert support.tree_outside_tickets(project) == tree, "the committed files changed on repeat"
    assert support.head(project) == after, "the repeat made a commit (DEC-357: the state of the first run)"
    assert support.porcelain(project) == "", f"the repeat left changes:\n{support.porcelain(project)}"
    assert support.is_paused(project), "the repeat cleared the flag"


def test_rollback_skips_a_merge_commit_and_names_it(project, pause, interface):
    side, other, merge, after = support.merged_history(project)
    before = support.head(project)
    result = _rollback(pause, interface)

    skipped, reverted = support.listed(result, "skipped_merges"), support.listed(result, "reverted")
    assert len(skipped) == 1 and support.names(skipped[0], merge), \
        f"`skipped_merges` does not name the merge commit {merge[:SHORT]} alone: {skipped}"
    assert len(reverted) == 2 and support.names(reverted[0], after) and support.names(reverted[1], side), \
        f"`reverted` is not the 2 other commits of the ticket, newest first: {reverted}"
    assert re.search(r"conflict resolution", support.text_of(result), re.IGNORECASE), \
        f"the result does not say that a merge's own conflict resolutions stay: {result}"

    reverts = _reverts(project, before)
    assert len(reverts) == 2, f"{len(reverts)} revert commits; the merge is not reverted"
    assert not any(merge in support.message(project, revert) for revert in reverts), "a commit reverts the merge"
    assert support.committed(project, support.FEATURE_REL) is None, "the commit on the merged side is not reverted"
    assert support.committed(project, support.EXTRA_REL) is None, "the commit after the merge is not reverted"
    assert support.committed(project, support.OTHER_REL) == support.OTHER_TEXT, "the other ticket's commit is gone"
    support.git(project, "merge-base", "--is-ancestor", merge, "HEAD")


def test_a_conflicting_revert_aborts_everything_with_an_error(project, pause, interface):
    """The newest commit reverts cleanly, the older one conflicts: nothing of the rollback is left, not the first revert."""
    support.conflicting_history(project)
    before, tickets = support.head(project), support.ticket_files(project)
    run = pause("--rollback", support.TICKET)
    support.failed(run, interface)
    assert support.head(project) == before, f"a conflicting rollback left commits\n{run.describe()}"
    assert support.porcelain(project) == "", \
        f"a conflicting rollback left changes:\n{support.porcelain(project)}\n{run.describe()}"
    assert not support.revert_in_progress(project), "a revert is still in progress"
    assert (Path(project) / support.EXTRA_REL).read_text(encoding="utf-8") == "EXTRA = 1\n"
    assert (Path(project) / support.CHANGED_REL).read_text(encoding="utf-8") == "VALUE = 3\n", \
        "the conflict was left in the working tree"
    assert support.ticket_files(project) == tickets, "an aborted rollback was recorded in a ticket"


def test_rollback_of_an_unknown_ticket_is_an_error(project, pause, interface, history):
    before = support.head(project)
    run = pause("--rollback", support.UNKNOWN_TICKET)
    support.failed(run, interface)
    assert support.head(project) == before, f"HEAD moved\n{run.describe()}"
    assert support.porcelain(project) == "", f"it left changes:\n{support.porcelain(project)}"
    assert not support.ticket_path(project, support.UNKNOWN_TICKET).exists(), "a ticket file was created"


def test_rollback_of_a_ticket_with_no_commit_succeeds_with_an_empty_list(project, pause, interface):
    """The other ticket has a file and no commit. Whether this writes a record is DP-11; nothing else changes."""
    support.commit(project, {support.FEATURE_REL: "STEP = 1\n"}, "feature, step 1", support.TICKET)
    tree = support.tree_outside_tickets(project)
    result = _rollback(pause, interface, ticket=support.OTHER_TICKET)
    assert support.listed(result, "reverted") == [], f"`reverted` is not empty: {result}"
    assert support.tree_outside_tickets(project) == tree, "committed files changed"
    assert (Path(project) / support.FEATURE_REL).read_text(encoding="utf-8") == "STEP = 1\n", \
        "the working tree lost another ticket's file"
    assert support.ticket_file(project) == support.committed(project, support.ticket_rel()), \
        "the file of a ticket that was not named changed"


def test_rollback_on_a_dirty_tree_is_refused(project, pause, interface, history):
    """A tracked file with an uncommitted change: an error, no revert, and the change is still there."""
    before = support.head(project)
    path = Path(project) / support.FEATURE_REL
    path.write_text("STEP = 2\nUNCOMMITTED = True\n", encoding="utf-8")
    run = pause("--rollback", support.TICKET)
    support.failed(run, interface)
    assert support.head(project) == before, f"a rollback on a dirty tree made a commit\n{run.describe()}"
    assert path.read_text(encoding="utf-8") == "STEP = 2\nUNCOMMITTED = True\n", \
        f"the uncommitted change to {support.FEATURE_REL} is gone\n{run.describe()}"
    assert not support.revert_in_progress(project), "a revert is still in progress"


def test_rollback_finds_a_commit_made_before_the_trailer_rule_by_its_message_body(project, pause, interface):
    """DEC-182: a commit made before 2026-10-03 may name its ticket in the body, not in the final block."""
    support.ticket_history(project, date=support.OLD_DATE, in_body=True)
    _rollback(pause, interface)
    support.assert_rolled_back(project)
