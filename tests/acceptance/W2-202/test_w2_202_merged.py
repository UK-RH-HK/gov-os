"""A4 (L2 §3 A4): a branch already merged.

Success line 7 (A4 S1) and failure line 4 (A4 F1). README, "The planted runs": merged, merged_refused.
"""

from __future__ import annotations

import pytest

import w2_202_support as support
from w2_202_support import A, C, kit, module_rel


@pytest.fixture(scope="module")
def merged(landing):
    return landing("merged")


@pytest.fixture()
def landed(merged):
    """The answer of the queue for the hand-merged ticket (on the base: ``CANDIDATE_NOT_ISOLATED``)."""
    return lambda: kit.answer(merged.run, kit.EXIT_LANDED)


# -- success line 7 (A4 S1) ---------------------------------------------------------------------------------------

def test_a_ticket_merged_by_hand_is_closed_by_the_queue_with_exit_0(merged, landed):
    result = landed()
    assert merged.old_head == merged.extra["hand_merge"]
    assert result.get("landed") == [A.id] and result.get("culprits") == [] and result.get("refused") == []
    head = kit.rev(merged.root, "main")
    assert head == result.get("head") != merged.old_head, "the queue did not move main"
    assert kit.status_at(merged.root, head, A.id) == "closed"
    assert kit.status_at(merged.root, merged.old_head, A.id) == "open"
    kit.assert_closed_iff_merged(merged, "main", every=[A.id])


def test_the_queue_makes_no_merge_commit_only_the_close_commit_on_the_head(merged, landed):
    result = landed()
    root = merged.root
    made = kit.git(root, "rev-list", f"{merged.old_head}..{result['head']}").split()
    assert len(made) == 1, f"the queue made {len(made)} commit(s) on the hand-merged head, not the close commit alone"
    close = made[0]
    assert kit.parents(root, close) == [merged.old_head], f"the close commit's parents: {kit.parents(root, close)}"
    assert result.get("tested") == merged.old_head, f"the tested commit {result.get('tested')!r} is not the head"
    paths = kit.changed_paths(root, close)
    ticket_file, record_dir, checkpoint_dir = kit.own_places(A.id)
    stray = [p for p in paths if p != ticket_file and not p.startswith((record_dir, checkpoint_dir))]
    assert not stray and ticket_file in paths, f"the close commit changes {paths}"
    assert [c.get("ticket") for c in result.get("closes") or []] == [A.id]
    assert result["closes"][0].get("commit") == close


def test_the_close_record_is_written_for_the_hand_merged_ticket(merged, landed):
    result = landed()
    front = kit.close_record(merged, result["head"], A.id)
    assert front.get("commit") == merged.old_head, f"the record's commit {front.get('commit')!r} is not the head"
    assert front.get("queue") == result.get("record")
    assert (front.get("branch") or {}).get("tip") == merged.tips[A.id], f"branch: {front.get('branch')!r}"
    assert front.get("reds") == [] and front.get("culprits") == []


def test_the_run_ran_on_the_head_and_the_root_follows(merged, landed):
    result = landed()
    assert result.get("runs"), "no run in the answer"
    for test in ("test_aa", "test_uses_widget"):
        told = merged.told_runs(test)
        assert told and all(r["ok"] for r in told), f"{test} did not run green on the head: {told}"
        assert all((r["seen"][module_rel("widget")] or "").startswith("# CHANGED") for r in told)
    root = merged.root
    assert kit.git(root, "symbolic-ref", "--short", "HEAD").strip() == "main"
    assert kit.rev(root, "HEAD") == result["head"] and kit.git(root, "status", "--porcelain") == ""


def test_the_checks_still_run_for_a_branch_already_merged(landing):
    """Steps 2 to 5 run on the head: an engineer's commit to the acceptance suite is refused by G-1 as for any
    candidate; the ticket is not closed and the branch does not move."""
    refused = landing("merged_refused")
    result = kit.answer(refused.run, kit.EXIT_NOT_ALL_LANDED)
    held = result.get("refused") or []
    assert [(r.get("ticket"), r.get("code")) for r in held] == [(C.id, "TEST_AUTHOR_REFUSED")], f"refused: {held!r}"
    assert refused.extra["offending"] in (held[0].get("commits") or [])
    assert result.get("landed") == []
    support.not_moved(refused)
    assert kit.status_at(refused.root, "main", C.id) == "open"


# -- failure line 4 (A4 F1) ---------------------------------------------------------------------------------------

def test_a_closed_ticket_is_still_ticket_closed_after_its_hand_merged_landing(merged, landed):
    """The ticket the queue has just closed, queued again with its branch still merged: ``TICKET_CLOSED`` as before
    (exit 1, nothing written), never a second close."""
    landed()
    again = merged.extra["again"]
    error = kit.refusal(again["run"], "TICKET_CLOSED", kit.EXIT_REFUSED_TO_RUN)
    assert (error.get("details") or {}).get("ticket") == A.id
    support.unchanged(again["before"], again["after"])
    closes = kit.git(merged.root, "log", "--format=%H", "main", "--", f"docs/close/{A.id}/CL-{A.id}.md").split()
    assert len(closes) == 1, f"{len(closes)} commits wrote the close record"
