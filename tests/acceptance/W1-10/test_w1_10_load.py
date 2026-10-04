"""KPI success 1 [CAP-13.a]: frontmatter of every record and ``Implements:``/``Task:`` trailers load into
``.gov-runtime/store.db`` deterministically (same digest twice).
"""

from __future__ import annotations

import w1_10_support as support


# ---- the store

def test_load_writes_the_store_as_a_sqlite_database(graph):
    store = graph.root / support.STORE_REL
    assert store.is_file(), f"load did not write {support.STORE_REL}"
    assert store.read_bytes()[:16] == b"SQLite format 3\x00", f"{support.STORE_REL} is not a SQLite database"


def test_load_writes_nothing_in_the_project_outside_gov_runtime(graph):
    changed = [line for line in support.porcelain(graph.root) if not line[3:].startswith(".gov-runtime/")]
    assert not changed, f"load changed the project outside .gov-runtime/: {changed}"
    assert support.head(graph.root) == graph.commits["new_body"], "load moved HEAD"


def test_the_frontmatter_of_every_record_is_loaded(api, graph):
    records = {record["id"]: record for record in api.records(graph.root)}
    assert sorted(records) == support.RECORD_IDS
    adr = records["ADR-0004"]
    assert (adr["type"], adr["status"]) == ("decision", "SUPERSEDED")
    ticket = records[support.TICKET]
    assert (ticket["type"], ticket["status"]) == ("task", "closed")


def test_a_record_carries_its_canonical_path(api, graph):
    """DEC-239: the canonical path is derived by gov, not stored in the frontmatter."""
    paths = {record["id"]: record["path"] for record in api.records(graph.root)}
    assert paths == support.RECORD_PATHS


def test_the_fixture_has_no_invalid_record(graph):
    assert graph.summary["invalid"] == []


# ---- the same digest twice

def test_two_loads_give_the_same_digest(api, repo):
    first = api.load(repo.root)["digest"]
    second = api.load(repo.root)["digest"]
    assert first == second, "the same repository loaded twice gives two digests"


def test_the_digest_query_returns_the_digest_of_the_load(api, graph):
    assert api.digest(graph.root) == graph.summary["digest"]


# ---- trailers (DEC-182)

def test_every_commit_is_loaded(api, graph):
    commits = support.by_commit(api.commits(graph.root))
    assert sorted(commits) == support.all_commits(graph.root)


def test_trailers_of_the_final_block_are_loaded(api, graph):
    commits = support.by_commit(api.commits(graph.root))
    assert commits[graph.commits["final_block"]] == support.EXPECTED_TRAILERS["final_block"]


def test_a_trailer_with_several_ids_gives_each_id(api, graph):
    """The form in use in this repository: ``Implements: DEC-199, DEC-200``."""
    commits = support.by_commit(api.commits(graph.root))
    assert commits[graph.commits["two_ids"]] == support.EXPECTED_TRAILERS["two_ids"]


def test_a_commit_before_2026_10_03_falls_back_to_the_message_body(api, graph):
    commits = support.by_commit(api.commits(graph.root))
    assert commits[graph.commits["old_body"]] == support.EXPECTED_TRAILERS["old_body"]


def test_a_commit_from_2026_10_03_is_read_from_the_final_block_only(api, graph):
    commits = support.by_commit(api.commits(graph.root))
    assert commits[graph.commits["new_body"]] == support.EXPECTED_TRAILERS["new_body"], \
        "Task:/Implements: lines outside the final trailer block were read as trailers on a commit after 2026-10-03"


def test_a_commit_without_trailers_has_none(api, graph):
    commits = support.by_commit(api.commits(graph.root))
    assert commits[graph.commits["base"]] == ([], [])


def test_a_changed_file_returns_its_commits_with_their_trailers(api, graph):
    """CAP-13's acceptance line: the commits of a file, with their ``Implements:`` and ``Task:`` trailers."""
    commits = support.by_commit(api.commits(graph.root, path="src/app.py"))
    assert commits == {graph.commits[name]: support.EXPECTED_TRAILERS[name] for name in ("old_body", "final_block")}


def test_the_trailers_of_a_file_resolve_to_records(api, graph):
    ids = set(api.ids(graph.root))
    for tasks, implements in support.by_commit(api.commits(graph.root, path="src/app.py")).values():
        assert set(tasks) | set(implements) <= ids
    kinds = {record["id"]: record["type"] for record in api.records(graph.root)}
    assert kinds[support.TICKET] == "task" and kinds["ADR-0002"] == "decision"


def test_a_file_no_commit_changed_has_no_commits(api, graph):
    assert api.commits(graph.root, path="src/never.py") == []
