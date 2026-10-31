"""KPI 1 (DEC-969, DEC-966 item 4): within one process, the lexical index's freshness and the semantic store's status
are worked out once per store and tree and reused by every later retrieval call.

Failure line: a freshness or status check repeated on every call within one process.

The work is counted through its public effects (README, "What is counted"): the git commands that list every
tracked file (``git ls-files``) or hash the tracked files' content (``git hash-object``), and the reads of the
path map (from which the files that should be embedded are worked out). N read-only calls on an unchanged store
and tree, in one process, do that work in the first call at most, and never again.
"""

from __future__ import annotations

import pytest

import w2_108_support as S

N = 5


def later_work(calls, first=1):
    """``(call number, listing/hashing commands, path-map reads)`` of every call after the first ``first``."""
    return [(number, *S.work_of(result)) for number, result in enumerate(calls, 1) if number > first]


def assert_no_later_listing(calls, first=1, what="call"):
    repeated = [(number, listing) for number, listing, _ in later_work(calls, first) if listing]
    assert not repeated, (
        f"the freshness check was worked out again in later {what}s of the same process, on an unchanged store and "
        f"tree (call number, listing/hashing git commands): {repeated}\n{S.describe_effects(calls)}")


def test_lexical_freshness_is_worked_out_once(planted, driver, embedder):
    calls = driver.run(planted, [S.lexical_freshness() for _ in range(N)], host=embedder.host)
    assert all(value == {"status": S.FRESH, "stale": []} for value in calls.values()), calls.values()
    assert S.work_of(calls[0])[0] >= 1, "the first call did no listing at all: the count sees nothing\n" \
        + S.describe_effects(calls)
    assert_no_later_listing(calls)


def test_lexical_search_checks_freshness_once(planted, driver, embedder):
    steps = [S.lexical_search(S.QUESTIONS[number % len(S.QUESTIONS)]) for number in range(N)]
    calls = driver.run(planted, steps, host=embedder.host)
    assert all(value["state"] == S.AVAILABLE for value in calls.values()), calls.values()
    assert_no_later_listing(calls)


def test_semantic_status_is_worked_out_once(planted, driver, embedder):
    steps = [S.semantic_search(S.QUESTIONS[number % len(S.QUESTIONS)]) for number in range(N)]
    calls = driver.run(planted, steps, host=embedder.host)
    assert all(value["state"] == S.AVAILABLE for value in calls.values()), calls.values()
    assert S.work_of(calls[0])[1] >= 1, "the first call read no path map: the count sees nothing\n" \
        + S.describe_effects(calls)
    assert_no_later_listing(calls)
    reread = [(number, reads) for number, _, reads in later_work(calls) if reads]
    assert not reread, (
        f"which files should be embedded was worked out again in later calls of the same process (call number, "
        f"path-map reads): {reread}\n{S.describe_effects(calls)}")


def test_retrieve_checks_both_stores_once(planted, driver, embedder):
    steps = [S.retrieve(S.QUESTIONS[number % len(S.QUESTIONS)]) for number in range(N)]
    calls = driver.run(planted, steps, host=embedder.host)
    for value in calls.values():
        assert value["facets"]["lexical"]["available"] and value["facets"]["semantic"]["available"], value["facets"]
    assert_no_later_listing(calls)


def test_every_kind_of_call_shares_one_check(planted, driver, embedder):
    """The answers are shared between the entry points: the freshness worked out for one is reused by the others."""
    steps = [S.lexical_freshness(), S.lexical_search(S.PHRASE), S.semantic_search(S.QUESTIONS[1]),
             S.retrieve(S.QUESTIONS[2]), S.retrieve(S.PHRASE), S.semantic_search(S.QUESTIONS[2]),
             S.lexical_search(S.QUESTIONS[3]), S.lexical_freshness()]
    calls = driver.run(planted, steps, host=embedder.host)
    calls.values()
    hashing = sum(1 for result in calls for argv in S.listing_work(result["effects"])
                  if S.subcommand(argv)[0] in S.HASHING)
    listing = sum(S.work_of(result)[0] for result in calls) - hashing
    assert hashing <= 2 and listing <= 2, (
        f"{len(steps)} calls on one unchanged store and tree listed the tracked files {listing} times and hashed them "
        f"{hashing} times; once per store (the lexical index, the vectors) is at most twice\n"
        f"{S.describe_effects(calls)}")
    assert_no_later_listing(calls, first=3)


def test_an_unchanged_tree_with_an_uncommitted_edit_is_checked_once(planted, driver, embedder):
    """An edit made before the process starts is part of the tree it sees: unchanged between its calls, it is
    checked once, and every call reports the index stale as it is."""
    S.write(planted, S.BAKERY, "# Bakery\n\nThe bakery is closed for the winter.\n")
    calls = driver.run(planted, [S.lexical_freshness() for _ in range(N)] + [S.lexical_search(S.PHRASE)],
                       host=embedder.host)
    assert all(value == {"status": S.STALE, "stale": [S.BAKERY]} for value in calls.values()[:N]), calls.values()
    assert S.facet(calls.values()[N]) == (False, S.UNAVAILABLE, S.STALE)
    assert_no_later_listing(calls)


def test_this_repositorys_store_is_checked_once(repo_store, driver):
    """On the store of the worktree the tests run in: four retrieval calls, one check."""
    steps = [S.retrieve(question) for question in S.REPO_QUESTIONS]
    calls = driver.run(repo_store, steps, env=S.repo_env(driver))
    calls.values()
    assert S.work_of(calls[0])[0] >= 1, S.describe_effects(calls)
    assert_no_later_listing(calls)
