"""KPI success 1: the blob-hash incremental index in the shared store [CAP-18.b].

Incrementality is read from what ``refresh`` reports as indexed in that call: the paths whose content it chunked.
A path is indexed again only when its blob changes. The index lives in the store W1-10 built,
``.gov-runtime/store.db``, next to the record graph.
"""

from __future__ import annotations

import os

import w1_17_support as support

EDITED = support.RUNBOOK


def test_a_second_refresh_indexes_nothing(api, repo):
    first = api.refresh(repo)
    assert set(support.CORPUS) <= set(first["indexed"])
    second = api.refresh(repo)
    assert second["indexed"] == [], f"nothing changed and files were indexed again: {second['indexed']}"
    assert second["digest"] == first["digest"]


def test_only_the_file_whose_blob_changed_is_indexed_again(api, repo):
    api.refresh(repo)
    support.write(repo, EDITED, support.RUNBOOK_TEXT + "\nOne more line.\n")
    support.commit(repo, "one file changes")
    assert api.refresh(repo)["indexed"] == [EDITED]


def test_a_file_rewritten_with_the_same_content_is_not_indexed_again(api, repo):
    """Blob hash, not modification time: every file is written again, a day later, with the content it had."""
    api.refresh(repo)
    for rel, text in support.CORPUS.items():
        support.write(repo, rel, text)
        stamp = os.stat(repo / rel).st_mtime + 86400
        os.utime(repo / rel, (stamp, stamp))
    support.commit(repo, "nothing changes")
    assert api.refresh(repo)["indexed"] == []


def test_a_new_tracked_file_is_the_only_one_indexed(api, repo):
    api.refresh(repo)
    new = support.write(repo, "app/added.py", "VALUE = 1\n")
    support.commit(repo, "one file more")
    assert api.refresh(repo)["indexed"] == [new]


def test_an_index_brought_up_to_date_equals_one_built_from_nothing(api, repo, tmp_path):
    """Edits, a new file, a removed file and a renamed one, refreshed step by step; then a new clone indexed once."""
    api.refresh(repo)
    support.write(repo, EDITED, support.RUNBOOK_TEXT.replace("drains", "empties"))
    support.commit(repo, "an edit")
    api.refresh(repo)
    support.write(repo, "notes/added.md", "# Added\n\nA new note.\n")
    support.git(repo, "rm", "-q", support.CLIENT)
    support.git(repo, "mv", support.TWINS[0], "notes/moved.txt")
    support.commit(repo, "a new file, a removed one and a renamed one", date="2026-09-03T12:00:00+00:00")
    stepwise = api.refresh(repo)["digest"]
    fresh = support.clone(repo, tmp_path / "fresh")
    assert api.refresh(fresh)["digest"] == stepwise
    assert api.chunks(fresh) == api.chunks(repo)


def test_the_index_is_in_the_shared_store_beside_the_record_graph(api, repo):
    """One store file; the record graph's load and the index's refresh leave each other's content alone."""
    graph = api.store("load", repo)["digest"]
    built = api.refresh(repo)["digest"]
    files = support.runtime_files(repo)
    assert files and all(name.startswith("store.db") for name in files), \
        f"the index is not in {support.STORE_REL} alone: .gov-runtime/ holds {files}"
    assert api.store("digest", repo) == graph, "building the index changed the record graph's digest"
    assert api.store("load", repo)["digest"] == graph
    assert api.digest(repo) == built, "loading the record graph changed the index"
    answer = api.search(repo, support.ERROR, refresh=False)
    assert support.places(answer) == support.occurrences(support.ERROR), "the index is gone after a load"


def test_building_the_index_changes_no_tracked_file(api, repo):
    """Derived state only (CAP-07): the working tree is as git left it."""
    api.refresh(repo)
    api.search(repo, support.ERROR)
    assert support.porcelain(repo) == []
