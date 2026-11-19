"""Failure line 1: the integration branch never advances after a red, a G-1 refusal, or a head that moved during the
run, and advances only to the tested merge with its close commits (README, "The planted runs": red, base_red,
authors_alone, moved).

A red that is red on the base too no longer refuses the batch (``BATCH_UNEXPLAINED``): by DEC-1214 L2, Q-CLOSE
(W2-202 A1) it is a known base red, recorded in the landed ticket's close record, and the ticket lands."""

from __future__ import annotations

import pytest

import w2_115b_support as support
from w2_115b_support import A, M


def assert_not_moved(landing, onto="main"):
    after = support.heads(landing.state())
    before = support.heads(landing.before)
    assert after.get(f"refs/heads/{onto}") == before.get(f"refs/heads/{onto}"), \
        f"{onto} moved: {before.get(f'refs/heads/{onto}')} -> {after.get(f'refs/heads/{onto}')}"


def test_a_red_run_does_not_move_the_integration_branch(landing):
    red = landing("red")
    support.answer(red.run, support.EXIT_NOT_ALL_LANDED)
    assert_not_moved(red)


@pytest.fixture(scope="module")
def base_red(landing):
    return landing("base_red")


def test_a_red_on_the_base_too_is_a_known_base_red_and_the_branch_moves_only_to_the_tested_merge(base_red):
    """Rewritten for DEC-1214 L2, Q-CLOSE (W2-202 A1): it asserted ``BATCH_UNEXPLAINED`` and an unmoved branch."""
    result = support.answer(base_red.run, support.EXIT_LANDED)
    assert result.get("landed") == [A.id] and result.get("culprits") == [], f"landed: {result.get('landed')}"
    closes = support.assert_landed_through_close_commits(base_red, result, "main", base_red.old_head)
    assert list(closes) == [A.id]
    assert support.status_at(base_red.root, "main", A.id) == "closed"
    front = support.close_record(base_red, result["head"], A.id)
    verdicts = [r.get("verdict") for r in front.get("reds") or [] if r.get("test") == support.KNOWN_RED_NODE]
    assert verdicts == ["base"], f"the close record does not hold the base red: {front.get('reds')}"
    assert front.get("base_reds") == [support.KNOWN_RED_NODE], f"base_reds: {front.get('base_reds')!r}"


def test_base_red_closed_exactly_when_merged(base_red):
    support.envelope(base_red.run)
    support.assert_closed_iff_merged(base_red, "main")


def test_a_g1_refusal_moves_nothing(landing):
    alone = landing("authors_alone")
    result = support.answer(alone.run, support.EXIT_NOT_ALL_LANDED)
    assert [r.get("code") for r in result.get("refused") or []] == ["TEST_AUTHOR_REFUSED"]
    assert_not_moved(alone)


@pytest.fixture(scope="module")
def moved(landing):
    return landing("moved")


def test_a_head_moved_during_the_run_is_head_moved_and_stays_as_moved(moved):
    support.refusal(moved.run, "HEAD_MOVED", support.EXIT_NOT_ALL_LANDED)
    moved_to = moved.extra.get("moved_to")
    assert moved_to, "the planted test did not move the integration branch during the run"
    assert support.parents(moved.root, moved_to) == [moved.old_head]
    assert support.rev(moved.root, "main") == moved_to, "the queue moved main past the head it found moved"
    assert not support.is_ancestor(moved.root, moved.tips[M.id], "main")
    assert support.status_at(moved.root, "main", M.id) == "open"


def test_moved_closed_exactly_when_merged(moved):
    support.envelope(moved.run)
    support.assert_closed_iff_merged(moved, "main")
