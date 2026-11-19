"""KPI S3 and F4: the archive is out of memory; its ids and headings are in a table of their own (EMERGENCY-2 11.3).

One planted project (``w2_203_support.plant``), its keyword index and record store built in place by
``lexical.refresh`` and ``store.load``: no model, no network, no vector, never a real worktree's store. Each case
first reads the store's archived-ids table, so a pass always means "the load read the archive and kept it apart",
never "the archive was not looked at".
"""

from __future__ import annotations

import shutil
import sqlite3

import pytest

import w2_203_support as s

ARCHIVE_DIR = "docs/archive/"
ONLY_IN_THE_ARCHIVE = (s.ARCHIVE_WORD, s.ARCHIVE_WORDS, s.A_HISTORY, s.A_OWNER, "skerrywell exception")


def _heading(record_id: str) -> str:
    return s.ENTRY[record_id].split("\n", 1)[0]


def _search(root, question: str) -> dict:
    from gov.retrieval import lexical

    answer = lexical.search(root, question, refresh=False)
    assert answer.get("available") is True, f"premise: the keyword index is not available: {answer!r}"
    return answer


def _paths(answer: dict) -> set[str]:
    return {hit["path"] for hit in answer.get("hits") or []} | {chunk["path"] for chunk in answer.get("ranked") or []}


# ---------------------------------------------------------------- S3

def test_s3_the_archives_ids_and_headings_are_in_a_table_of_their_own(planted):
    from gov.store import layout, loader

    assert (loader.ARCHIVE_KEY, loader.ARCHIVE_TABLE) == (s.ARCHIVE_KEY, s.ARCHIVE_TABLE)
    held = s.archived_rows(planted.root)
    assert held == {record_id: _heading(record_id) for record_id in s.ARCHIVE_ORDER}, \
        "the table holds one row per entry of the archive at HEAD, its id and its heading"
    assert tuple(layout.STORES["record"]["tables"][s.ARCHIVE_TABLE]) == ("id", "heading")


def test_s3_the_table_is_outside_the_digest(planted, tmp_path):
    from gov import store

    assert s.archived_rows(planted.root)
    before = store.digest(planted.root)
    copy = tmp_path / "copy"
    (copy / ".gov-runtime").mkdir(parents=True)
    shutil.copy2(planted.root / s.STORE_REL, copy / s.STORE_REL)
    with sqlite3.connect(copy / s.STORE_REL) as connection:
        connection.execute(f"DELETE FROM {s.ARCHIVE_TABLE}")
    assert store.digest(copy) == before, "the digest changes with the archived-ids table: the table is inside it"


@pytest.mark.parametrize("question", [s.KEPT_WORDS, s.K_FIRST])
def test_s3_a_decision_of_the_kept_register_still_resolves_by_id_and_by_its_words(planted, question):
    from gov.retrieval.retrieve import retrieve

    assert s.archived_rows(planted.root)
    assert s.REGISTER_REL in _paths(_search(planted.root, question)), \
        f"the keyword index does not find the kept entry for {question!r}"
    evidence = retrieve(planted.root, question)["evidence"]
    assert any(item.get("id") == s.K_FIRST and item["path"] == s.REGISTER_REL for item in evidence), \
        f"gov retrieve does not return {s.K_FIRST} for {question!r}: {[(i.get('id'), i['path']) for i in evidence]}"


def test_s3_a_path_map_that_names_no_archive_gives_an_empty_table(plant):
    root = plant("unnamed", archive_key=False, index=False).root
    assert s.archived_rows(root) == {}, "no archive is named: the table is empty"
    assert {row[0] for row in s.rows(root, "SELECT id FROM records WHERE type = 'decision'")} == set(s.KEPT_IDS)


def test_s3_a_named_archive_that_head_does_not_hold_refuses_nothing(plant):
    root = plant("absent", archive_file=False, index=False).root  # the load ran: a refusal would have raised there
    assert s.archived_rows(root) == {}
    assert {row[0] for row in s.rows(root, "SELECT id FROM records WHERE type = 'decision'")} == set(s.KEPT_IDS)


# ---------------------------------------------------------------- F4

def test_f4_no_archive_only_decision_is_a_store_record(planted):
    assert set(s.ARCHIVE_ONLY) <= set(s.archived_rows(planted.root))
    held = s.rows(planted.root, "SELECT id, path FROM records")
    assert not [row for row in held if row[0] in s.ARCHIVE_ONLY or row[1].startswith(ARCHIVE_DIR)], \
        f"the store holds a record of the archive: {held}"
    assert {row[0] for row in held if row[1] == s.REGISTER_REL} == set(s.KEPT_IDS)
    sources = s.rows(planted.root, "SELECT source FROM edges UNION SELECT source FROM stated_links")
    assert not {row[0] for row in sources} & set(s.ARCHIVE_ONLY), "the archive is read for edges or statements"


def test_f4_no_archive_only_decision_is_a_register_entries_row(planted):
    assert set(s.ARCHIVE_ONLY) <= set(s.archived_rows(planted.root))
    held = {row[0] for row in s.rows(planted.root, "SELECT id FROM register_entries")}
    assert held == set(s.KEPT_IDS), f"register_entries holds {sorted(held)}"


def test_f4_no_chunk_of_the_keyword_index_is_of_the_archive(planted):
    from gov.retrieval import lexical

    assert s.archived_rows(planted.root)
    chunks = {row[0] for row in s.rows(planted.root, "SELECT path FROM lexical_chunk")}
    assert s.REGISTER_REL in chunks, "premise: the kept register is indexed"
    assert not {path for path in chunks if path.startswith(ARCHIVE_DIR)}, f"indexed: {sorted(chunks)}"
    files = dict(s.rows(planted.root, "SELECT path, indexed FROM lexical_file"))
    assert files.get(s.ARCHIVE_REL) == lexical.KEPT_OUT, \
        f"the file table records the archive as {files.get(s.ARCHIVE_REL)!r}, not kept out by the path map's policy"
    assert files.get(s.REGISTER_REL) == 1, f"the file table records the kept register as {files.get(s.REGISTER_REL)!r}"
    assert _search(planted.root, s.ARCHIVE_WORD) and not _paths(_search(planted.root, s.ARCHIVE_WORD)), \
        f"a word only the archive holds is found: {_paths(_search(planted.root, s.ARCHIVE_WORD))}"


@pytest.mark.parametrize("question", ONLY_IN_THE_ARCHIVE)
def test_f4_a_search_for_a_decision_only_the_archive_holds_returns_no_chunk_of_it(planted, question):
    from gov.retrieval.retrieve import retrieve

    assert s.archived_rows(planted.root)
    found = _paths(_search(planted.root, question))
    assert not {path for path in found if path.startswith(ARCHIVE_DIR)}, f"{question!r}: {sorted(found)}"
    for bundle in (retrieve(planted.root, question), retrieve(planted.root, question, ids=(s.A_HISTORY,), radius=1)):
        evidence = [(item.get("id"), item["path"]) for item in bundle["evidence"]]
        assert not [item for item in evidence if item[1].startswith(ARCHIVE_DIR) or item[0] in s.ARCHIVE_ONLY], \
            f"gov retrieve answers {question!r} with the archive: {evidence}"
