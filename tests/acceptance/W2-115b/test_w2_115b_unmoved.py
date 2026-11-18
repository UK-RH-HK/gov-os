"""Failure line 1: the integration branch never advances after a red, a red on the base too, a G-1 refusal, or a
head that moved during the run (README, "The planted runs": red, unexplained, authors_alone, moved)."""

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
def unexplained(landing):
    return landing("unexplained")


def test_a_red_on_the_base_too_is_batch_unexplained_and_moves_nothing(unexplained):
    error = support.refusal(unexplained.run, "BATCH_UNEXPLAINED", support.EXIT_NOT_ALL_LANDED)
    reds = (error.get("details") or {}).get("reds") or []
    assert support.KNOWN_RED_NODE in reds, f"the error's details do not name the red: {error.get('details')}"
    assert_not_moved(unexplained)
    assert support.status_at(unexplained.root, "main", A.id) == "open"


def test_unexplained_closed_exactly_when_merged(unexplained):
    support.envelope(unexplained.run)
    support.assert_closed_iff_merged(unexplained, "main")


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
