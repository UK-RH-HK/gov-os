"""KPI S4 and F3: an id the archive alone holds resolves as history; an id in neither file is still a finding.

The planted project (``w2_203_support.plant``) cites an archive-only id and an id no file holds, side by side, in
each place: a kept entry's labels, a ticket's sources, a note's ``decisions:`` and ``constrains:`` keys, a test
file's comment, and a commit's message and ``Implements:`` trailer. One commit predates the archive file.
The clone cases run the same checks on two temporary clones of this repository, the base and HEAD.
"""

from __future__ import annotations

import sqlite3

import pytest

import w2_203_support as s

UNKNOWN_ID, NOT_IN_FORCE, UNRECORDED, UNREADABLE = \
    "UNKNOWN_ID", "NOT_IN_FORCE_AS_RULE", "DECISION_UNRECORDED", "REGISTER_UNREADABLE"
UNRESOLVED = "UNRESOLVED"


def _heading(record_id: str) -> str:
    return s.ENTRY[record_id].split("\n", 1)[0]


@pytest.fixture(scope="module")
def links(planted, home):
    """``gov links --all --json`` on the planted project: its findings."""
    done = s.gov(s.src(), home, home / "links", "links", "--all", "--json", "--root", str(planted.root))
    return s.json_of(done)["result"]["findings"]


def _closure(root, ids, depth=1) -> tuple[dict, dict]:
    from gov import closure

    answer = closure.closure(root, list(ids), depth)
    return ({item["id"]: item["kind"] for item in answer["closure"]},
            {gap["id"]: gap["reason"] for gap in answer["gaps"]})


# ---------------------------------------------------------------- S4, the planted project

def test_s4_the_archive_is_read_for_ids_and_headings_only(planted):
    from gov.util import archive

    expected = {record_id: _heading(record_id) for record_id in s.ARCHIVE_ORDER}
    assert archive.read(planted.root) == expected
    assert archive.ids_in(s.archive_text()) == expected
    assert archive.ids_in("no entry here\n") == {}


def test_s4_no_archive_named_or_held_reads_as_none(plant):
    from gov.util import archive

    assert archive.read(plant("unnamed", archive_key=False, index=False, load=False).root) is None
    assert archive.read(plant("absent", archive_file=False, index=False, load=False).root) is None


def test_s4_a_commit_citing_an_archived_id_is_no_finding_of_the_citations_check(planted):
    from gov.check import citations

    findings = citations.check(planted.root)
    about = [f for f in findings if f.get("decision") in s.ARCHIVE_ONLY or f.get("commit") == planted.commits["archived"]]
    assert not about, f"the citations check finds the archived id unrecorded: {about}"
    old = [f for f in findings if f.get("commit") == planted.commits["old"] or f["code"] == UNREADABLE]
    assert not old, f"a commit whose tree predates the archive is a finding by that alone: {old}"


def test_s4_gov_links_counts_archived_ids_among_the_ids_that_exist(planted, links):
    from gov.util import archive

    assert archive.read(planted.root), "premise: the planted project's archive is read"
    about = [(f["code"], f["ids"], f["path"]) for f in links
             if f["code"] in (UNKNOWN_ID, NOT_IN_FORCE) and set(f["ids"]) & set(s.ARCHIVE_ONLY)]
    assert not about, f"gov links: {about}"


def test_s4_no_dangling_reference_of_the_store_names_an_archived_id(planted):
    from gov import records

    assert set(s.ARCHIVE_ONLY) <= set(s.archived_rows(planted.root))
    about = [row for row in records.dangling(planted.root) if row["target"] in s.ARCHIVE_ONLY]
    assert not about, f"dangling: {about}"


def test_s4_the_closure_of_an_archived_id_lists_it_as_history(planted):
    kinds, gaps = _closure(planted.root, [s.A_HISTORY])
    assert kinds.get(s.A_HISTORY) == "history" and s.A_HISTORY not in gaps, f"closure {kinds}, gaps {gaps}"
    assert kinds.get(s.K_FIRST) == "record" and kinds.get(s.NOTE) == "record", \
        f"its neighbours are the records whose edges name it: {kinds}"
    assert set(kinds) == {s.A_HISTORY, s.K_FIRST, s.NOTE}, f"the archive gives it no edge of its own: {kinds}"
    alone, gaps = _closure(planted.root, [s.A_OWNER], depth=3)  # no record names it: it is still history
    assert alone == {s.A_OWNER: "history"} and not gaps


def test_s4_the_closure_from_a_kept_entry_reaches_the_archived_id_as_history(planted):
    kinds, gaps = _closure(planted.root, [s.K_FIRST])
    assert kinds.get(s.K_FIRST) == "record", f"premise: {kinds}"
    assert kinds.get(s.A_HISTORY) == "history" and s.A_HISTORY not in gaps, f"closure {kinds}, gaps {gaps}"


def test_s4_a_store_built_before_the_table_is_still_read(planted, tmp_path):
    from gov import closure, records

    assert s.ARCHIVE_TABLE in s.tables(planted.root), f"the load wrote no table {s.ARCHIVE_TABLE}"
    old = tmp_path / "old"
    s.git(planted.root, "clone", "-q", str(planted.root), str(old))
    (old / ".gov-runtime").mkdir()
    with sqlite3.connect(planted.root / s.STORE_REL) as source, sqlite3.connect(old / s.STORE_REL) as copy:
        source.backup(copy)
        copy.execute(f"DROP TABLE {s.ARCHIVE_TABLE}")
    assert isinstance(records.dangling(old), list)
    answer = closure.closure(old, [s.K_FIRST, s.A_HISTORY], 1)
    assert {item["id"] for item in answer["closure"]} >= {s.K_FIRST}


# ---------------------------------------------------------------- F3, the planted project

def test_f3_a_commit_citing_an_id_in_neither_file_is_still_unrecorded(planted):
    from gov.check import citations
    from gov.util import archive

    assert s.NEITHER not in archive.read(planted.root)
    found = {(f["code"], f.get("commit"), f.get("decision")) for f in citations.check(planted.root)}
    assert found == {(UNRECORDED, planted.commits["neither"], s.NEITHER)}, f"the citations check: {found}"


def test_f3_gov_links_still_finds_an_id_in_neither_file_unknown_in_each_place(planted, links):
    from gov.util import archive

    assert s.NEITHER not in archive.read(planted.root)
    places = {f["path"] for f in links if f["code"] == UNKNOWN_ID and f["ids"][0] == s.NEITHER}
    wanted = {s.REGISTER_REL, s.TICKET_REL, s.NOTE_REL, s.TEST_REL, planted.commits["neither"]}
    assert places == wanted, f"UNKNOWN_ID for {s.NEITHER} in {sorted(places)}, expected in {sorted(wanted)}"


def test_f3_an_id_in_neither_file_is_still_a_dangling_reference(planted):
    from gov import records

    assert s.NEITHER not in s.archived_rows(planted.root)
    about = {(row["type"], row["source"]) for row in records.dangling(planted.root) if row["target"] == s.NEITHER}
    assert about == {("SUPERSEDES", s.K_SECOND), ("CONSTRAINS", s.NOTE), ("IMPLEMENTS", planted.commits["neither"])}


def test_f3_an_id_in_neither_file_is_still_an_unresolved_gap_of_the_closure(planted):
    assert s.NEITHER not in s.archived_rows(planted.root)
    kinds, gaps = _closure(planted.root, [s.NEITHER])
    assert gaps == {s.NEITHER: UNRESOLVED} and not kinds, "a start id that is no record, archived id or symbol"
    kinds, gaps = _closure(planted.root, [s.K_SECOND])
    assert gaps.get(s.NEITHER) == UNRESOLVED and s.NEITHER not in kinds, f"a reached target: {kinds}, {gaps}"


# ---------------------------------------------------------------- S4, this repository against its base

def _key(finding: dict) -> tuple:
    return finding["code"], tuple(finding["ids"]), finding["path"]


def test_s4_real_gov_links_reports_no_finding_about_an_archived_id_that_the_base_lacked(base_clone, head_clone, home,
                                                                                         moved):
    base, head = s.both(base_clone, head_clone, home, "-m", "gov.cli.main", "links", "--all", "--json", "--root",
                        "{root}")
    base, head = ({_key(f) for f in answer["result"]["findings"]} for answer in (base, head))
    about = {key for key in head if set(key[1]) & moved["only"]}
    unknown = sorted(key for key in about if key[0] == UNKNOWN_ID)
    assert not unknown, f"{len(unknown)} UNKNOWN_ID findings name an archived id: {unknown[:5]}"
    new = sorted(about - base)
    assert not new, f"{len(new)} findings about archived ids that the base did not have: {new[:5]}"


def test_s4_real_the_citations_check_reports_no_finding_about_the_archive_that_the_base_lacked(base_clone, head_clone,
                                                                                               home, moved):
    code = ("import json, pathlib; from gov.check import citations; "
            "print(json.dumps(citations.check(pathlib.Path('{root}'))))")
    base, head = s.both(base_clone, head_clone, home, "-c", code)
    archived = {record_id for record_id, _ in moved["archive"]}
    was = {(f["commit"], f["decision"]) for f in base if f["code"] == UNRECORDED}
    new = sorted((f["commit"][:12], f["decision"]) for f in head if f["code"] == UNRECORDED
                 and f["decision"] in archived and (f["commit"], f["decision"]) not in was)
    assert not new, f"{len(new)} commits cite an archived id that the check finds unrecorded: {new[:5]}"
    files = (s.ARCHIVE_REL, s.REGISTER_REL)
    was = {(f["commit"], f["path"]) for f in base if f["code"] == UNREADABLE}
    new = sorted((f["commit"][:12], f["path"]) for f in head if f["code"] == UNREADABLE and f["path"] in files
                 and (f["commit"], f["path"]) not in was)
    assert not new, f"the register or the archive is unreadable in {len(new)} trees where the base read it: {new[:5]}"


def test_s4_real_every_archived_id_a_kept_entry_cites_resolves(head_clone, moved):
    """HEAD's own store, built in the temporary clone: the archived ids the kept entries cite are history in the
    closure, with no gap, and no dangling reference names an archived id."""
    from gov import closure, records, store
    from gov.util import archive

    from gov.store.loader import register_entries

    live = {entry["id"] for entry in register_entries((head_clone / s.ARCHIVE_REL).read_text(encoding="utf-8"))[0]}
    held = {record_id for record_id, _ in moved["register"]}
    # the archive's live entries, as the store counts them: a heading with no status line was no record on the base
    cited = sorted(({record_id for _, text in moved["register"] for record_id in s.cited(text)} - held) & live)
    assert len(cited) > 300, f"premise: the kept entries cite {len(cited)} ids the register does not hold"
    read = archive.read(head_clone)
    assert read and not [record_id for record_id in cited if record_id not in read], \
        f"cited by a kept entry and in neither file: {[i for i in cited if i not in (read or {})][:10]}"
    heading_of = {record_id: text.split("\n", 1)[0].rstrip() for record_id, text in moved["archive"]}
    assert all(read[record_id] == heading_of[record_id] for record_id in cited), "an id's heading is the archive's"
    store.load(head_clone)
    answer = closure.closure(head_clone, cited, 0)
    kinds = {item["id"]: item["kind"] for item in answer["closure"]}
    wrong = [record_id for record_id in cited if kinds.get(record_id) != "history"]
    assert not wrong and not answer["gaps"], f"not history: {wrong[:10]}; gaps: {answer['gaps'][:5]}"
    about = [row for row in records.dangling(head_clone) if row["target"] in moved["only"]]
    assert not about, f"{len(about)} dangling references name an archived id: {about[:5]}"
