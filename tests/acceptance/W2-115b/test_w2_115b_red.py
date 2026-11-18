"""Success line 3: on red the failing tests are named and nothing moves (README, "The planted runs": red)."""

from __future__ import annotations

import pytest

import w2_115b_support as support
from w2_115b_support import A


@pytest.fixture(scope="module")
def red(landing):
    return landing("red")


@pytest.fixture()
def result(red):
    """The answer, read in the case itself: on the base every case fails here, with no envelope (README)."""
    return lambda: support.answer(red.run, support.EXIT_NOT_ALL_LANDED)


def test_a_red_ticket_is_not_landed_and_is_named_the_culprit_with_exit_3(red, result):
    result = result()
    assert result.get("landed") == []
    assert result.get("culprits") == [A.id]
    assert result.get("head") is None and result.get("closes") == []


def test_the_answer_names_the_failing_test_s_node_id(red, result):
    result = result()
    reds = result.get("reds") or []
    assert support.USES_WIDGET_NODE in reds, f"the failing node id is not named: {reds}"


def test_the_integration_branch_the_work_branch_and_the_ticket_file_are_as_they_were(red, result):
    result()
    before, after = support.heads(red.before), support.heads(red.state())
    for ref in ("refs/heads/main", "refs/heads/topic/aa"):
        assert after.get(ref) == before.get(ref), f"{ref} moved: {before.get(ref)} -> {after.get(ref)}"
    assert support.show(red.root, "main", A.ticket_rel) == support.show(red.root, red.old_head, A.ticket_rel)
    assert red.state()["files"][A.ticket_rel] == red.before["files"][A.ticket_rel]
    assert support.status_at(red.root, "main", A.id) == "open"


def test_red_closed_exactly_when_merged(red, result):
    result()
    support.assert_closed_iff_merged(red, "main")
