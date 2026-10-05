"""KPI success 2 and failure 1: changed blobs re-index before the next retrieval; an empty or stale index is
reported, never returned as absent; a retrieval never returns pre-edit text as current [CAP-17.a].

Two ways to retrieve (README, interface): ``search(root, query)`` brings the index up to date first;
``search(root, query, refresh=False)`` never writes, and when the index is missing, empty or stale it reports the
facet ``FACET_UNAVAILABLE`` with the reason and no hit. Zero hits from an up-to-date index is an available answer.
"""

from __future__ import annotations

import pytest

import w1_17_support as support

OLD = "Retry after the pool drains."
NEW = "Retry once the saffron ibis lands."
EDITED_TEXT = support.RUNBOOK_TEXT.replace(OLD, NEW)
LINE = support.line_of(support.RUNBOOK_TEXT, OLD)


def _edit(repo, committed=True):
    support.write(repo, support.RUNBOOK, EDITED_TEXT)
    if committed:
        support.commit(repo, "the runbook changes")


def test_an_edited_file_is_re_indexed_before_the_next_retrieval(api, repo):
    api.refresh(repo)
    assert support.places(api.search(repo, OLD)) == [(support.RUNBOOK, LINE)]
    _edit(repo)
    assert support.places(api.search(repo, NEW)) == [(support.RUNBOOK, LINE)], "the edited text is not returned"


def test_the_text_from_before_an_edit_is_not_returned_as_current(api, repo):
    """Failure 1. The retrieval after the edit asks for the old sentence first: no hit, from an available index."""
    api.refresh(repo)
    _edit(repo)
    answer = api.search(repo, OLD)
    assert answer["available"] and answer["hits"] == [], f"the pre-edit text is returned as current: {answer!r}"
    assert support.places(api.search(repo, NEW, refresh=False)) == [(support.RUNBOOK, LINE)], \
        "the retrieval left the index stale"


def test_an_uncommitted_edit_to_a_tracked_file_is_re_indexed_too(api, repo):
    """Package DP-7, the recommended option: the corpus is the tracked files as they stand in the working tree,
    the content the secret filter judges. An edit that is not committed yet is still an edit (CAP-17 acceptance)."""
    api.refresh(repo)
    _edit(repo, committed=False)
    old = api.search(repo, OLD)
    assert old["hits"] == [], f"the pre-edit text is returned as current: {old!r}"
    assert support.places(api.search(repo, NEW)) == [(support.RUNBOOK, LINE)]


def test_a_removed_file_is_no_longer_returned(api, repo):
    api.refresh(repo)
    support.git(repo, "rm", "-q", support.CLIENT)
    support.commit(repo, "the client goes")
    expected = [place for place in support.occurrences(support.ERROR) if place[0] != support.CLIENT]
    assert support.places(api.search(repo, support.ERROR)) == expected


def test_a_renamed_file_is_returned_under_its_new_path_only(api, repo):
    """The blob is unchanged; its path is not."""
    api.refresh(repo)
    support.git(repo, "mv", support.LONG, "notes/deep/renamed.md")
    support.commit(repo, "a rename")
    expected = [("notes/deep/renamed.md", number) for number in support.MARKED_LINES]
    assert support.places(api.search(repo, support.MARKER)) == expected


def test_zero_hits_from_an_up_to_date_index_is_an_available_answer(api, indexed):
    """The other side of "reported, never returned as absent": this answer means the string occurs nowhere."""
    answer = api.search(indexed.root, support.ABSENT, refresh=False)
    assert answer["available"] is True and answer["hits"] == [], answer
    assert not answer.get("reason"), f"an available answer gives a reason for being unavailable: {answer!r}"
    assert api.freshness(indexed.root)["status"] == "fresh"


def test_a_stale_index_is_reported_by_a_retrieval_that_may_not_write(api, repo):
    """The old sentence is still in the index. The answer is ``FACET_UNAVAILABLE``, not the old text, and not an
    available answer with zero hits either: both queries are refused. The call leaves the index as it was."""
    before = api.refresh(repo)["digest"]
    _edit(repo)
    for query in (OLD, NEW, support.ABSENT):
        support.unavailable(api.search(repo, query, refresh=False), "stale")
    assert api.digest(repo) == before, "a retrieval with refresh=False changed the index"
    assert api.freshness(repo)["status"] == "stale"
    assert support.places(api.search(repo, NEW)) == [(support.RUNBOOK, LINE)]
    assert api.freshness(repo)["status"] == "fresh"


def test_a_missing_index_is_reported_by_a_retrieval_that_may_not_write(api, repo):
    """No index was ever built. The answer is not "no occurrence", and nothing is written."""
    support.unavailable(api.search(repo, support.ERROR, refresh=False), "missing", "empty")
    assert not (repo / support.RUNTIME_REL).exists(), "a retrieval with refresh=False wrote .gov-runtime/"
    assert api.freshness(repo)["status"] in ("missing", "empty")
    assert not (repo / support.RUNTIME_REL).exists(), "freshness wrote .gov-runtime/"


def test_the_first_retrieval_builds_a_missing_index(api, repo):
    """With no index at all every blob is a changed blob: the retrieval indexes them and answers."""
    assert support.places(api.search(repo, support.ERROR)) == support.occurrences(support.ERROR)
    assert api.freshness(repo)["status"] == "fresh"


def test_an_empty_index_is_reported_not_answered_as_zero_hits(api, tmp_path):
    """A repository whose path map classes every file as product data: the index is built and holds nothing."""
    root = tmp_path / "empty"
    root.mkdir()
    support.git(root, "init", "-q", "-b", "main")
    support.adopt(root, {"everything": (["**"], "product")})
    support.write(root, "notes/page.md", f"# Page\n\n{support.ERROR}\n")
    support.commit(root, "product data only", support.BASE_DATE)
    assert api.refresh(root)["indexed"] == []
    assert api.chunks(root) == []
    for refresh in (True, False):
        support.unavailable(api.search(root, support.ERROR, refresh=refresh), "empty")
    assert api.freshness(root)["status"] == "empty"


def test_freshness_names_the_paths_that_are_stale(api, repo):
    """An edited file, a new one and a removed one; nothing is written by asking."""
    api.refresh(repo)
    state = api.freshness(repo)
    assert (state["status"], state["stale"]) == ("fresh", []), state
    _edit(repo, committed=False)
    new = support.write(repo, "notes/added.md", "# Added\n")
    support.git(repo, "rm", "-q", support.CLIENT)
    support.commit(repo, "three changes")
    state = api.freshness(repo)
    assert state["status"] == "stale"
    assert sorted(state["stale"]) == sorted([support.RUNBOOK, new, support.CLIENT]), state
    assert api.freshness(repo)["status"] == "stale", "asking for the freshness state refreshed the index"
    api.refresh(repo)
    assert api.freshness(repo)["stale"] == []


@pytest.mark.parametrize("kind", ["product-data", "secret"])
def test_a_file_the_corpus_excludes_does_not_make_the_index_stale(api, repo, kind):
    """A tracked file that is never indexed is not a changed blob waiting to be indexed: the index stays fresh."""
    api.refresh(repo)
    if kind == "product-data":
        support.write(repo, "tenant-exports/2026/orders.csv", "id,total\n1,10\n")
    else:
        support.write(repo, "notes/planted.md", f"# Notes\n\n{support.CANARY}\n")
    support.commit(repo, "a file outside the corpus")
    api.refresh(repo)
    state = api.freshness(repo)
    assert (state["status"], state["stale"]) == ("fresh", []), state
    assert api.search(repo, support.ABSENT, refresh=False)["available"] is True
