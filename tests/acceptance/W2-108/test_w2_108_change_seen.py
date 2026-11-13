"""KPI 3 (DEC-969): a change is still seen. A store rebuilt, a file changed (a tracked file edited in the working
tree, committed or not: DEC-344) or a head moved between two calls is seen as such (a new key, a fresh check); a
process that cannot read the fingerprint or the head checks every time and never reuses an old answer.

Failure line: a stale answer reused after the store, a file or the head changed.

Every case first makes several calls in one process (so whatever can be remembered is remembered), then changes
the store, a file or the head, and calls again in the same process. Both facets: the lexical one reports the index
stale after such a change, as it does today (DEC-342); the semantic one too.
"""

from __future__ import annotations

import pytest

import w2_108_support as S
from w2_108_support import build

HERON_QUESTION = "cobalt heron pier signal raised at noon"
WARM = [S.lexical_freshness(), S.lexical_search(S.PHRASE), S.semantic_search(S.QUESTIONS[1]),
        S.retrieve(S.QUESTIONS[1])]
AFTER = [S.lexical_freshness(), S.lexical_search(S.PHRASE), S.semantic_search(S.QUESTIONS[1]),
         S.retrieve(S.QUESTIONS[1])]


def warm_then(driver, root, change, after, host, rounds=2):
    """``WARM`` ``rounds`` times, the steps of ``change``, then ``after``, in one process: (warm answers, after)."""
    values = driver.run(root, [*WARM * rounds, *change, *after], host=host).values()
    return values[:len(WARM) * rounds], values[len(WARM) * rounds:]


def assert_fresh_before(before):
    for number in range(0, len(before), len(WARM)):
        freshness, lexical, semantic, bundle = before[number:number + len(WARM)]
        assert freshness == {"status": S.FRESH, "stale": []}, freshness
        assert S.facet(lexical)[0] and lexical["hits"], lexical
        assert S.facet(semantic)[0] and semantic["hits"], semantic
        assert bundle["facets"]["lexical"]["available"] and bundle["facets"]["semantic"]["available"], bundle


def assert_stale_after(after, path):
    freshness, lexical, semantic, bundle = after
    assert freshness == {"status": S.STALE, "stale": [path]}, \
        f"the lexical index was not reported stale after {path} changed: an old answer was reused\n{freshness}"
    assert S.facet(lexical) == (False, S.UNAVAILABLE, S.STALE), f"lexical facet after {path} changed: {lexical}"
    assert S.facet(semantic) == (False, S.UNAVAILABLE, S.STALE), f"semantic facet after {path} changed: {semantic}"
    assert bundle["facets"] == {"lexical": {"available": False, "reason": S.STALE},
                                "semantic": {"available": False, "reason": S.STALE}}, bundle["facets"]
    assert bundle["stopping_reason"] == S.UNAVAILABLE and bundle["evidence"] == [], bundle


@pytest.mark.parametrize("how", ["edited", "deleted"])
def test_a_file_changed_in_the_working_tree_is_seen(planted, driver, embedder, how):
    change = [S.edit(S.BAKERY, "# Bakery\n\nThe bakery now sells only rye.\n")] if how == "edited" \
        else [S.remove(S.BAKERY)]
    before, after = warm_then(driver, planted, change, AFTER, embedder.host)
    assert_fresh_before(before)
    assert_stale_after(after, S.BAKERY)


def test_a_committed_change_is_seen(planted, driver, embedder):
    change = [S.edit(S.TIDES, "# Tides\n\nThe tide tables are kept by the lock keeper.\n"),
              S.git_step("add", "-A"), S.git_step("commit", "-q", "-m", "a committed change")]
    before, after = warm_then(driver, planted, change, AFTER, embedder.host)
    assert_fresh_before(before)
    assert_stale_after(after, S.TIDES)


def test_a_second_edit_of_an_edited_file_is_seen(planted, driver, embedder):
    """A file already edited (uncommitted) when the store was rebuilt, edited again: the list of changed files is
    the same before and after the second edit, its content is not."""
    S.write(planted, S.BAKERY, f"# Bakery\n\nThe {S.NEW_PHRASE} is baked into the rye.\n")
    build(driver, planted, embedder.host)
    steps = [S.lexical_freshness(), S.lexical_search(S.NEW_PHRASE), S.semantic_search(HERON_QUESTION)] * 2
    after = [S.lexical_freshness(), S.lexical_search(S.NEW_PHRASE), S.semantic_search(HERON_QUESTION),
             S.retrieve(HERON_QUESTION)]
    values = driver.run(planted, [*steps, S.edit(S.BAKERY, "# Bakery\n\nThe rye is sold out.\n"), *after],
                        host=embedder.host).values()
    before, later = values[:len(steps)], values[len(steps):]
    assert before[0] == {"status": S.FRESH, "stale": []}, before[0]
    assert [hit["path"] for hit in before[1]["hits"]] == [S.BAKERY], before[1]
    assert S.facet(before[2])[0], before[2]
    assert_stale_after(later, S.BAKERY)


@pytest.mark.parametrize("records", [True, False], ids=["full-rebuild", "index-and-vectors-only"])
def test_a_store_rebuilt_by_another_process_is_seen(planted, driver, embedder, records):
    """The store rebuilt between two calls, by another process, with the tree and the head unchanged: a fully
    rebuilt store, or one whose lexical index and vectors alone were refreshed (their own refresh functions)."""
    S.write(planted, S.NEW_FILE, S.NEW_TEXT)
    S.git(planted, "add", S.NEW_FILE)          # tracked, uncommitted: the head does not move (DEC-344)
    stale = [S.lexical_freshness(), S.lexical_search(S.NEW_PHRASE), S.semantic_search(HERON_QUESTION)]
    after = [S.lexical_freshness(), S.lexical_search(S.NEW_PHRASE), S.semantic_search(HERON_QUESTION),
             S.retrieve(S.NEW_PHRASE)]
    values = driver.run(planted, [*stale * 3, S.rebuild(records=records), *after], host=embedder.host).values()
    before, later = values[:len(stale) * 3], values[len(stale) * 3:]
    for number in range(0, len(before), len(stale)):
        assert before[number] == {"status": S.STALE, "stale": [S.NEW_FILE]}, before[number]
        assert S.facet(before[number + 1]) == (False, S.UNAVAILABLE, S.STALE), before[number + 1]
        assert S.facet(before[number + 2]) == (False, S.UNAVAILABLE, S.STALE), before[number + 2]
    freshness, lexical, semantic, bundle = later
    assert freshness == {"status": S.FRESH, "stale": []}, \
        f"the store was rebuilt by another process, but the old answer was reused: {freshness}"
    assert S.facet(lexical) == (True, S.AVAILABLE, None), lexical
    assert [hit["path"] for hit in lexical["hits"]] == [S.NEW_FILE], lexical
    assert S.facet(semantic) == (True, S.AVAILABLE, None), semantic
    assert semantic["hits"][0]["path"] == S.NEW_FILE, semantic["hits"][:3]
    assert bundle["facets"]["lexical"]["available"] and bundle["facets"]["semantic"]["available"], bundle["facets"]
    assert S.NEW_FILE in [item["path"] for item in bundle["evidence"]], bundle["evidence"]


def test_a_store_rebuilt_in_the_same_process_is_seen(planted, driver, embedder):
    """The same process refreshes the index and the vectors itself (``refresh``), between two read-only calls."""
    S.write(planted, S.NEW_FILE, S.NEW_TEXT)
    S.git(planted, "add", S.NEW_FILE)
    stale = [S.lexical_freshness(), S.lexical_search(S.NEW_PHRASE), S.semantic_search(HERON_QUESTION)]
    refresh = [S.call(S.LEXICAL, "refresh", "{root}"), S.call(S.SEMANTIC, "refresh", "{root}")]
    values = driver.run(planted, [*stale * 2, *refresh, *stale], host=embedder.host).values()
    assert values[0] == {"status": S.STALE, "stale": [S.NEW_FILE]}, values[0]
    freshness, lexical, semantic = values[len(stale) * 2 + len(refresh):]
    assert freshness == {"status": S.FRESH, "stale": []}, freshness
    assert [hit["path"] for hit in lexical["hits"]] == [S.NEW_FILE], lexical
    assert S.facet(semantic)[0] and semantic["hits"][0]["path"] == S.NEW_FILE, semantic


def test_a_moved_head_is_checked_afresh(planted, driver, embedder):
    """The head moves (an empty commit) and nothing else changes: the next calls check again (a new key) and
    answer as before."""
    steps = [*WARM * 2, S.git_step("commit", "-q", "--allow-empty", "-m", "the head moves"),
             S.lexical_freshness(), S.semantic_search(S.QUESTIONS[1])]
    calls = driver.run(planted, steps, host=embedder.host)
    values = calls.values()
    assert_fresh_before(values[:len(WARM) * 2])
    freshness, semantic = calls[-2], calls[-1]
    assert freshness["value"] == {"status": S.FRESH, "stale": []}, freshness["value"]
    # Rewrite-Reason: DEC-1061 (R-1): compared without W2-126's vector-cache counters (S.answer_of).
    assert S.answer_of(semantic["value"]) == S.answer_of(values[2]), \
        "the semantic answer changed although only the head moved"
    assert S.work_of(freshness)[0] >= 1, (
        "after the head moved, the lexical index's freshness was not checked again (no listing or hashing of the "
        f"tracked files)\n{S.describe_effects(calls)}")
    assert sum(S.work_of(semantic)) >= 1, (
        "after the head moved, the semantic store's status was not worked out again (no listing, hashing or "
        f"path-map read)\n{S.describe_effects(calls)}")


def test_a_removed_store_is_seen(planted, driver, embedder):
    """The store removed between two calls: no answer of the old store is reused (DEC-342: missing)."""
    values = driver.run(planted, [*WARM * 2, S.remove(S.STORE_REL), S.lexical_freshness(),
                                  S.lexical_search(S.PHRASE), S.semantic_search(S.QUESTIONS[1])],
                        host=embedder.host).values()
    assert_fresh_before(values[:len(WARM) * 2])
    freshness, lexical, semantic = values[len(WARM) * 2:]
    assert freshness == {"status": "missing", "stale": []}, freshness
    assert S.facet(lexical) == (False, S.UNAVAILABLE, "missing"), lexical
    assert not semantic["available"] and semantic["state"] == S.UNAVAILABLE and semantic["hits"] == [], semantic


def test_without_a_head_every_call_checks(no_commit, driver, embedder):
    """A repository with no commit yet: the head cannot be read, so every call checks, and a change between two
    calls is seen."""
    steps = [S.lexical_freshness(), S.semantic_search(S.QUESTIONS[1])] * 3
    after = [S.lexical_freshness(), S.lexical_search(S.PHRASE), S.semantic_search(S.QUESTIONS[1])]
    calls = driver.run(no_commit, [*steps, S.edit(S.MARKER, "# Marker\n\nThe marker was taken down.\n"), *after],
                       host=embedder.host)
    values = calls.values()
    for number, value in enumerate(values[:len(steps)]):
        assert value == {"status": S.FRESH, "stale": []} if number % 2 == 0 else S.facet(value)[0], value
    unchecked = [number for number, result in enumerate(calls[:len(steps)], 1) if not sum(S.work_of(result))]
    assert not unchecked, (
        f"with no head to key on, calls {unchecked} reused an earlier answer instead of checking\n"
        f"{S.describe_effects(calls)}")
    freshness, lexical, semantic = values[len(steps):]
    assert freshness == {"status": S.STALE, "stale": [S.MARKER]}, freshness
    assert S.facet(lexical) == (False, S.UNAVAILABLE, S.STALE), lexical
    assert S.facet(semantic) == (False, S.UNAVAILABLE, S.STALE), semantic
