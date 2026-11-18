"""Success line 4: a red batch's culprit is sent back and the rest land (README, "The planted runs": batch)."""

from __future__ import annotations

import pytest

import w2_115b_support as support
from w2_115b_support import A, B


@pytest.fixture(scope="module")
def batch(landing):
    return landing("batch")


@pytest.fixture()
def result(batch):
    """The answer, read in the case itself: on the base every case fails here, with no envelope (README)."""
    return lambda: support.answer(batch.run, support.EXIT_NOT_ALL_LANDED)


def test_the_culprit_is_sent_back_named_with_its_failing_test(batch, result):
    result = result()
    assert result.get("culprits") == [B.id]
    assert B.node in (result.get("reds") or []), f"the culprit's failing test is not named: {result.get('reds')}"


def test_the_culprit_s_branch_is_not_merged_and_its_ticket_stays_open(batch, result):
    result()
    assert not support.is_ancestor(batch.root, batch.tips[B.id], "main")
    assert support.status_at(batch.root, "main", B.id) == "open"
    assert support.heads(batch.state()).get("refs/heads/topic/bb") == batch.tips[B.id]


def test_the_other_lands_and_closes(batch, result):
    result = result()
    assert result.get("landed") == [A.id]
    assert support.is_ancestor(batch.root, batch.tips[A.id], "main")
    assert support.status_at(batch.root, "main", A.id) == "closed"
    support.assert_landed_through_close_commits(batch, result, "main", batch.old_head)


def test_the_other_s_close_record_names_the_culprit_and_the_merge_without_it(batch, result):
    result()
    front = support.close_record(batch, "main", A.id)
    assert front.get("culprits") == [B.id]
    commit = front.get("commit")
    assert commit and support.parents(batch.root, commit) == [batch.old_head, batch.tips[A.id]], \
        f"the record's commit {commit} is not the merge of A alone onto the old head"
    assert not support.is_ancestor(batch.root, batch.tips[B.id], commit)


def test_the_rest_was_run_again_without_the_culprit(batch, result):
    result = result()
    runs = batch.told_runs("test_aa")
    gadget = support.module_rel("gadget")
    with_b = [r for r in runs if "BROKEN" in (r["seen"].get(gadget) or "")]
    without_b = [r for r in runs if "BROKEN" not in (r["seen"].get(gadget) or "")]
    assert with_b, "A's suite did not run on the merged result of both tickets"
    assert without_b and all(r["ok"] for r in without_b), "A's suite was not run again on the merge without B"
    assert all(r["seen"][support.module_rel("widget")].startswith("# CHANGED") for r in runs)


def test_batch_closed_exactly_when_merged(batch, result):
    result()
    support.assert_closed_iff_merged(batch, "main")
