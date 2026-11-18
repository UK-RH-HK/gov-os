"""Success line 5: who wrote the acceptance tests is checked by code, G-1 (README, "The planted runs": authors and
authors_alone)."""

from __future__ import annotations

import pytest

import w2_115b_support as support
from w2_115b_support import C, D, E, G, H, K

REFUSED = "TEST_AUTHOR_REFUSED"


@pytest.fixture(scope="module")
def authors(landing):
    return landing("authors")


@pytest.fixture()
def result(authors):
    """The answer, read in the case itself: on the base every case fails here, with no envelope (README)."""
    return lambda: support.answer(authors.run, support.EXIT_NOT_ALL_LANDED)


def refusal_of(result, ticket):
    found = [r for r in result.get("refused") or [] if r.get("ticket") == ticket.id]
    assert len(found) == 1, f"{ticket.id} is not refused once: {result.get('refused')}"
    return found[0]


def assert_refused_whole(landing, result, ticket):
    """Refused with G-1's code and the offending commit's full id; nothing of it landed; its ticket stays open."""
    entry = refusal_of(result, ticket)
    assert entry.get("code") == REFUSED
    assert landing.extra["offending"][ticket.id] in (entry.get("commits") or []), \
        f"the offending commit is not named: {entry}"
    assert ticket.id not in (result.get("landed") or [])
    assert not support.is_ancestor(landing.root, landing.tips[ticket.id], "main")
    assert support.show(landing.root, "main", ticket.suite_file) == support.show(
        landing.root, landing.old_head, ticket.suite_file), "the refused ticket's test change is at the head"
    assert support.status_at(landing.root, "main", ticket.id) == "open"


def test_an_engineer_commit_to_the_acceptance_tests_is_refused_with_its_id(authors, result):
    result = result()
    assert_refused_whole(authors, result, C)


def test_an_engineer_commit_to_the_ticket_s_acceptance_path_is_refused(authors, result):
    result = result()
    assert_refused_whole(authors, result, K)


def test_the_test_designer_s_and_the_owner_s_commits_land(authors, result):
    result = result()
    for ticket in (D, E):
        assert ticket.id in (result.get("landed") or []), f"{ticket.id} did not land: {result}"
        assert support.is_ancestor(authors.root, authors.tips[ticket.id], "main")
        assert support.status_at(authors.root, "main", ticket.id) == "closed"


def test_a_clean_merge_of_the_test_designer_s_branch_lands(authors, result):
    result = result()
    assert G.id in (result.get("landed") or []), f"{G.id} did not land: {result}"
    assert support.is_ancestor(authors.root, authors.extra["clean_merge"], "main")
    assert support.status_at(authors.root, "main", G.id) == "closed"
    assert not [r for r in result.get("refused") or [] if r.get("ticket") == G.id]


def test_a_merge_that_edits_an_acceptance_test_in_its_resolution_is_refused(authors, result):
    result = result()
    entry = refusal_of(result, H)
    assert entry.get("code") == REFUSED
    assert authors.extra["offending"][H.id] in (entry.get("commits") or []), f"the merge is not named: {entry}"
    assert not support.is_ancestor(authors.root, authors.tips[H.id], "main")
    assert support.status_at(authors.root, "main", H.id) == "open"


def test_the_rest_of_the_batch_lands_through_close_commits_with_exit_3(authors, result):
    result = result()
    assert sorted(result.get("landed") or []) == sorted([D.id, E.id, G.id])
    assert sorted(r.get("ticket") for r in result.get("refused") or []) == sorted([C.id, H.id, K.id])
    support.assert_landed_through_close_commits(authors, result, "main", authors.old_head)


def test_authors_closed_exactly_when_merged(authors, result):
    result()
    support.assert_closed_iff_merged(authors, "main")


# -- one refused ticket alone: refused before any run, nothing moves --------------------------------------------

@pytest.fixture(scope="module")
def alone(landing):
    return landing("authors_alone")


def test_a_ticket_refused_alone_is_named_and_nothing_moves(alone):
    result = support.answer(alone.run, support.EXIT_NOT_ALL_LANDED)
    entry = refusal_of(result, C)
    assert entry.get("code") == REFUSED and alone.extra["offending"][C.id] in (entry.get("commits") or [])
    assert result.get("landed") == [] and result.get("head") is None
    assert support.heads(alone.state()) == support.heads(alone.before), "a branch moved"
    assert support.status_at(alone.root, "main", C.id) == "open"


def test_authors_alone_closed_exactly_when_merged(alone):
    support.envelope(alone.run)
    support.assert_closed_iff_merged(alone, "main")
