"""Success line 6: paths outside the ticket's allowed paths are a notice, never a refusal (README, "The planted
runs": notices)."""

from __future__ import annotations

import pytest

import w2_115b_support as support
from w2_115b_support import A


@pytest.fixture(scope="module")
def notices(landing):
    return landing("notices")


@pytest.fixture()
def result(notices):
    """The answer, read in the case itself: on the base every case fails here, with no envelope (README)."""
    return lambda: support.answer(notices.run, support.EXIT_LANDED)


def expected(notices):
    return {"ticket": A.id, "commit": notices.extra["outside"], "path": support.NOTES_REL}


def test_a_commit_outside_the_allowed_paths_is_a_notice_and_the_ticket_lands_and_closes(notices, result):
    result = result()
    assert expected(notices) in (result.get("path_notices") or []), f"not listed: {result.get('path_notices')}"
    assert result.get("landed") == [A.id] and result.get("refused") == []
    assert support.is_ancestor(notices.root, notices.tips[A.id], "main")
    assert support.status_at(notices.root, "main", A.id) == "closed"
    support.assert_landed_through_close_commits(notices, result, "main", notices.old_head)


def test_the_close_record_lists_the_notice(notices, result):
    result()
    front = support.close_record(notices, "main", A.id)
    listed = front.get("path_notices")
    assert isinstance(listed, list) and expected(notices) in listed, f"the close record lists: {listed!r}"


def test_a_path_inside_the_allowed_paths_is_not_listed(notices, result):
    result = result()
    listed = result.get("path_notices") or []
    assert [n.get("path") for n in listed] == [support.NOTES_REL], f"listed: {listed}"
    assert not [n for n in listed if n.get("commit") == notices.extra["inside"]]
    front = support.close_record(notices, "main", A.id)
    assert [n.get("path") for n in front.get("path_notices") or []] == [support.NOTES_REL]


def test_notices_closed_exactly_when_merged(notices, result):
    result()
    support.assert_closed_iff_merged(notices, "main")
