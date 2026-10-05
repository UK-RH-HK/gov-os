"""KPI success 3, second half [CAP-05.c], with the record of KPI success 4 [CAP-05.d].

"gov pause --rollback <ticket> reverts the ticket's commits with git revert and
records it" (ROLLBACK_TRANSACTION).

- **The ticket's commits** are those whose ``Task:`` trailer names the ticket,
  in the final trailer block; a commit made before 2026-10-03 is read from the
  whole message (DEC-182, as ``gov.store`` reads them).
- **With git revert:** history only grows. The HEAD before the rollback is an
  ancestor of the HEAD after it, and HEAD's reflog shows no reset, rebase or
  amend. What HEAD holds afterwards is the project without the ticket's
  changes and with every other ticket's.
- **Order.** The fixture's second commit changes the line its first commit
  wrote, so the reverts apply cleanly only newest first.
- **On repeat** the committed files are the same as after the first run.

Left to decision package DP-5, and asserted nowhere: one revert commit or
several, their message and trailers, merge commits, a conflict, whether an
unknown ticket or a ticket with no commit is an error, whether a dirty tree is
refused. For those the cases below hold only what every option keeps: nothing
is reverted that is not the ticket's, and uncommitted work is not lost.
The record's place and shape are DP-6; the case here follows its recommended
option in the weakest form (the ticket's file names each reverted commit).
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w1_28_support as support

SHORT = 7  # a commit is named by at least the first seven characters of its hash


def _rollback(pause, interface, ticket=support.TICKET):
    return support.succeeded(pause("--rollback", ticket), interface)


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


def test_rollback_leaves_no_uncommitted_change_outside_the_tickets(project, pause, interface, history):
    """The reverts are commits. Only the record may be left uncommitted, in ``.tickets/`` (DP-6)."""
    _rollback(pause, interface)
    left = [line for line in support.porcelain(project).splitlines()
            if not line[3:].startswith(support.TICKETS_REL + "/")]
    assert not left, f"the rollback left uncommitted changes: {left}"
    assert not (Path(project) / ".git" / "REVERT_HEAD").exists(), "a revert is still in progress"


def test_the_result_names_each_reverted_commit(pause, interface, history):
    first, other, second = history
    said = support.text_of(_rollback(pause, interface))
    for commit in (first, second):
        assert commit[:SHORT] in said, f"the result does not name the reverted commit {commit[:SHORT]}: {said}"
    assert other[:SHORT] not in said, f"the result names the other ticket's commit {other[:SHORT]}: {said}"


def test_the_rollback_is_recorded_in_the_ticket(project, pause, interface, history):
    """DP-6, recommended option: the record is in the ticket's file and names what was reverted."""
    first, other, second = history
    before = support.ticket_file(project)
    untouched = support.ticket_file(project, support.OTHER_TICKET)
    _rollback(pause, interface)
    text = support.ticket_file(project)
    assert text != before, f".tickets/{support.TICKET}.md is unchanged: the rollback was not recorded in the ticket"
    for commit in (first, second):
        assert commit[:SHORT] in text, f".tickets/{support.TICKET}.md does not name the reverted commit {commit}"
    assert support.ticket_file(project, support.OTHER_TICKET) == untouched, "the other ticket's file changed"


def test_rollback_gives_the_same_result_on_repeat(project, pause, interface, history):
    """KPI success 4. A repeat does not revert the reverts: HEAD holds the same files as after the first run."""
    _rollback(pause, interface)
    tree = support.tree_outside_tickets(project)
    _rollback(pause, interface)
    support.assert_rolled_back(project, "after the repeat")
    assert support.tree_outside_tickets(project) == tree, "the committed files changed on repeat"


def test_rollback_finds_a_commit_made_before_the_trailer_rule_by_its_message_body(project, pause, interface):
    """DEC-182: a commit made before 2026-10-03 may name its ticket in the body, not in the final block."""
    support.ticket_history(project, date=support.OLD_DATE, in_body=True)
    _rollback(pause, interface)
    support.assert_rolled_back(project)


@pytest.mark.parametrize("ticket", [support.OTHER_TICKET, support.UNKNOWN_TICKET],
                         ids=["a-ticket-with-no-commit", "an-unknown-ticket"])
def test_rollback_with_nothing_to_revert_changes_nothing(project, pause, interface, ticket):
    """Whether this is an error is DP-5; either way no commit is made and no file changes."""
    support.commit(project, {support.FEATURE_REL: "STEP = 1\n"}, "feature, step 1", support.TICKET)
    tree = support.tree_outside_tickets(project)
    run = pause("--rollback", ticket)
    envelope = support.cli_support.assert_envelope(run, interface, command="pause")
    code = (envelope.get("error") or {}).get("code")
    assert code not in (support.NOT_IMPLEMENTED, support.MODULE_INVALID), run.describe()
    assert support.tree_outside_tickets(project) == tree, f"committed files changed\n{run.describe()}"
    assert (Path(project) / support.FEATURE_REL).read_text(encoding="utf-8") == "STEP = 1\n", \
        f"the working tree lost another ticket's file\n{run.describe()}"


def test_rollback_does_not_lose_uncommitted_work(project, pause, history):
    """Whether a dirty tree is refused is DP-5; either way git revert, unlike a reset, keeps what is not committed."""
    path = Path(project) / support.FEATURE_REL
    path.write_text("STEP = 2\nUNCOMMITTED = True\n", encoding="utf-8")
    run = pause("--rollback", support.TICKET)
    assert support.NOT_IMPLEMENTED not in run.stdout, run.describe()
    assert path.is_file() and "UNCOMMITTED = True" in path.read_text(encoding="utf-8"), \
        f"the uncommitted change to {support.FEATURE_REL} is gone\n{run.describe()}"
