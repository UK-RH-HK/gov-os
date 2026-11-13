"""The first review's findings (DEC-136, DEC-413): five behaviours the suite did not hold, each as ``gov impact``'s
output already names it (``graphs``, ``complete``, ``gaps``, ``change[].deletable``, ``radius``, ``--out``,
``--compare``, ``matches``, ``differences``).

1. A record graph that does not match the working tree is never reported current (reading R4; DEC-391 DP-7:
   ``gov closure`` already names such paths under ``uncommitted``).
2. A CIT-E whose kind is not a list never matches (reading R6).
3. A CIT-P written from an incomplete assessment never reads as complete (reading R3, R4).
4. A name shared by two code definitions is deletable only when every definition of it is (reading R8).
5. A code file the index does not hold makes the code graph not current, whatever its modification time (R4).

The cases that build a code index are ``local_only``: they cannot run in a worker's sandbox (P-W2-38).
"""

from __future__ import annotations

import copy
import os

import pytest

import w2_37_support as support

LATE_TICKET, LATE_TICKET_REL = "PROJ-ac02", ".tickets/PROJ-ac02.md"
MAIN_TICKET, MAIN_TICKET_REL = "PROJ-ac03", ".tickets/PROJ-ac03.md"
CAP_REL = f"docs/contract/{support.CAP}.md"
CITE_REL = f"docs/changes/{support.CITE}.md"
CITP_REL = f"docs/changes/{support.CITP}.md"


def as_project(root):
    made = support.Project.__new__(support.Project)
    made.root, made.minute = root, 100
    return made


def radius_number(found):
    return int(found["radius"].lstrip("R").rstrip("+"))


# --------------------------------------------------------------------------
# 1. A record graph that does not match the working tree is never reported current
# --------------------------------------------------------------------------

def a_ticket_added_and_not_committed(project, box, reindex):
    """A ticket that implements DEC-001 is written after the store was loaded, and not committed."""
    project.write(LATE_TICKET_REL, support.ticket(LATE_TICKET, implements=[support.CHANGED]))
    return (LATE_TICKET,), (), (LATE_TICKET_REL,)


def an_edge_removed_and_not_committed(project, box, reindex):
    """CAP-901's edge to DEC-001 is removed after the store was loaded, and not committed."""
    project.write(CAP_REL, support.capability(support.CAP))
    return (), (support.CAP,), (CAP_REL,)


def a_switch_to_an_older_branch(project, box, reindex):
    """On ``main`` a ticket implementing DEC-001 is added and CAP-901's edge removed; the store (and, when asked,
    the code index) is loaded there; then the repository is switched to ``older``, the fixture's commit, where the
    ticket is absent and the edge present."""
    project.git("branch", "older")
    project.write(MAIN_TICKET_REL, support.ticket(MAIN_TICKET, implements=[support.CHANGED]))
    project.write(CAP_REL, support.capability(support.CAP))
    project.commit("on main: a ticket added, an edge removed")
    support.load_store(project.root, box)
    reindex()
    project.git("checkout", "-q", "older")
    return (support.CAP,), (MAIN_TICKET,), (MAIN_TICKET_REL, CAP_REL)


STATES = {
    "ticket-added-uncommitted": a_ticket_added_and_not_committed,
    "edge-removed-uncommitted": an_edge_removed_and_not_committed,
    "switched-to-older-branch": a_switch_to_an_older_branch,
}


def assert_record_graph_not_reported_current(run, listed, unlisted, paths):
    """Reading R4: either the report reads the tree as it is now (each of ``listed`` is listed, none of
    ``unlisted`` is), or it says the record graph is not current: ``complete: false``, ``graphs.record`` not ``ok``,
    and the word ``stale`` or the paths that differ named (a refusal: the record graph or store named, and the same
    word or paths)."""
    document = support.envelope(run)
    show = run.describe()
    if document["ok"] is True:
        found = support.assessment(run)
        ids = support.ids_of(found)
        if all(i in ids for i in listed) and not any(i in ids for i in unlisted):
            return                                            # read as it stands now: nothing dropped, nothing stale
        support.assert_incomplete(run, "record")
        said = support.text_of(found["graphs"]) + support.text_of(found["gaps"]) \
            + support.text_of(found.get("warnings", []))
    else:
        support.assert_incomplete(run, "record")
        said = support.text_of(document.get("error"))
    assert "stale" in said.lower() or any(path in said for path in paths), \
        f"the report neither reads the tree as it is now (listed {listed}, not listed {unlisted}) nor says the " \
        f"record graph is stale or names the paths that differ {paths}\n{show}"


@pytest.mark.parametrize("state", list(STATES), ids=list(STATES))
def test_a_record_graph_that_does_not_match_the_tree_is_never_reported_current(project, box, state):
    """Without the code tool: the record side alone (``graphs.record`` is not ``ok``, or the tree is read now)."""
    listed, unlisted, paths = STATES[state](project, box, reindex=lambda: None)
    run = support.impact(project.root, support.CHANGED, box)
    assert_record_graph_not_reported_current(run, listed, unlisted, paths)


@pytest.mark.local_only
@pytest.mark.parametrize("state", ["ticket-added-uncommitted", "switched-to-older-branch"])
def test_with_both_graphs_a_record_graph_that_does_not_match_the_tree_is_never_complete(indexed_own, box, state):
    """With a current code graph, ``complete`` turns on the record graph alone."""
    project = as_project(indexed_own)
    listed, unlisted, paths = STATES[state](project, box, reindex=lambda: support.build_index(indexed_own, box))
    run = support.impact(indexed_own, support.CHANGED, box, path=box.full)
    assert_record_graph_not_reported_current(run, listed, unlisted, paths)


def test_a_store_loaded_from_the_tree_as_it_is_reads_the_record_graph_current(project, box):
    """The success: a ticket committed and the store loaded again; the record graph is ``ok`` and lists it."""
    project.write(LATE_TICKET_REL, support.ticket(LATE_TICKET, implements=[support.CHANGED]))
    project.commit("a ticket, then the store loaded again")
    support.load_store(project.root, box)
    run = support.impact(project.root, support.CHANGED, box)
    found = support.assessment(run)
    assert found["graphs"]["record"] == support.GRAPH_OK, \
        f"a store loaded from a clean tree is not reported current\n{run.describe()}"
    assert support.where(found, LATE_TICKET) == [("tickets", "record")], \
        f"{LATE_TICKET}: {support.where(found, LATE_TICKET)}"


# --------------------------------------------------------------------------
# 2. A CIT-E whose kind is not a list never matches
# --------------------------------------------------------------------------

def compare_records(project, box, kind, proposed_value, executed_value):
    """A CIT-P whose ``kind`` list is ``proposed_value`` and a CIT-E whose ``kind`` is ``executed_value`` (the other
    four kinds agree); committed, the store loaded again, and compared."""
    proposed = copy.deepcopy(support.PROPOSED)
    proposed[kind] = proposed_value
    executed = copy.deepcopy(proposed)
    executed[kind] = executed_value
    project.write(CITP_REL, support.proposal_file(affected=proposed))
    project.write(CITE_REL, support.execution_file(affected=executed))
    project.commit("the change's records")
    support.load_store(project.root, box)
    return support.compare(project.root, CITE_REL, box)


MALFORMED = [("code", "some_symbol", "some_symbol"), ("decisions", {"DEC-099": "done"}, "DEC-099")]


@pytest.mark.parametrize("kind,value,item", MALFORMED, ids=["single-item", "map"])
def test_an_execution_record_whose_kind_is_not_a_list_never_matches(project, box, kind, value, item):
    """The proposal's list for ``kind`` is empty; the CIT-E gives that kind as one item or as a map."""
    run = compare_records(project, box, kind, [], value)
    document = support.envelope(run)
    show = run.describe()
    if document["ok"] is not True:
        support.assert_refused(run, kind)                     # a refusal that names the malformed kind
        return
    found = document["result"]
    assert found.get("matches") is not True, f"a CIT-E whose `{kind}` is {value!r}, not a list, matches\n{show}"
    listed = [entry.get("id") for entry in found.get("differences") or [] if isinstance(entry, dict)]
    assert item in listed, f"{item}, in the CIT-E's `{kind}`, is not listed as a difference: {listed}\n{show}"


def test_an_empty_list_on_both_sides_matches(project, box):
    """The success: both records give ``code`` as an empty list."""
    run = compare_records(project, box, "code", [], [])
    found = support.result(run)
    assert found.get("matches") is True and found.get("differences") == [], \
        f"two records whose `code` lists are both empty do not match\n{run.describe()}"


# --------------------------------------------------------------------------
# 3. A CIT-P written from an incomplete assessment never reads as complete
# --------------------------------------------------------------------------

def gap_ids_in(value):
    gaps = value if isinstance(value, list) else []
    return sorted(str(gap.get("id")) if isinstance(gap, dict) else str(gap) for gap in gaps)


def test_a_cit_p_written_from_an_incomplete_assessment_says_so_or_is_refused(repo, box):
    """With ``git`` alone on PATH no code graph can be read, so the assessment is incomplete. The file ``--out``
    writes carries ``complete``, ``graphs`` and ``gaps`` as the printed result gives them, or the write is refused
    and nothing is written."""
    out = repo / "docs" / "changes" / "CITP-901.md"
    run = support.impact(repo, support.CHANGED, box, out=out)
    document = support.envelope(run)
    show = run.describe()
    if document["ok"] is not True:
        support.assert_refused(run)
        said = support.text_of(document.get("error")).lower()
        assert any(word in said for word in ("complete", "code")), \
            f"the refusal does not say why (the assessment is incomplete, the code graph): {said}\n{show}"
        assert not out.exists(), f"a refused --out still wrote {out}\n{show}"
        return
    found = support.assessment(run)
    assert found["complete"] is False, f"the fixture is wrong: no code graph, and the result is complete\n{show}"
    front, _ = support.read_frontmatter(out)
    assert front.get("complete") is False, \
        f"the CIT-P written from an incomplete assessment does not say `complete: false`: {front!r}\n{show}"
    assert front.get("graphs") == found["graphs"], \
        f"the CIT-P's `graphs` {front.get('graphs')!r} are not the result's {found['graphs']!r}\n{show}"
    assert gap_ids_in(front.get("gaps")) == support.gap_ids(found), \
        f"the CIT-P's gaps {gap_ids_in(front.get('gaps'))} are not the result's {support.gap_ids(found)}\n{show}"


@pytest.mark.local_only
def test_a_cit_p_written_from_a_complete_assessment_is_written(indexed_own, box):
    """The success: with both graphs read, ``--out`` writes the CIT-P; whatever it says of completeness is the
    result's."""
    out = indexed_own / "docs" / "changes" / "CITP-902.md"
    run = support.impact(indexed_own, support.CHANGED, box, path=box.full, out=out)
    found = support.assessment(run)
    front, _ = support.read_frontmatter(out)
    support.check_frontmatter(front, support.CITP_TYPE)
    if "complete" in front:
        assert front["complete"] is found["complete"], f"the CIT-P's `complete` is not the result's\n{run.describe()}"
    if "graphs" in front:
        assert front["graphs"] == found["graphs"], f"the CIT-P's `graphs` are not the result's\n{run.describe()}"


# --------------------------------------------------------------------------
# 4. A name shared by two code definitions is deletable only when every definition of it is
# --------------------------------------------------------------------------

SHARED, CALLER, SPARE, CONSTRAINING = "w37_shared", "w37_caller", "w37_spare", "DEC-201"


def shared_name_repo(destination, box, dead_name):
    """``app/alpha.py`` defines w37_shared and w37_caller, which calls it; DEC-201 constrains w37_caller.
    ``app/beta.py`` defines ``dead_name``, which nothing calls: w37_shared again, or w37_spare."""
    project = support.Project(destination)
    project.write(".gitignore", ".gov-runtime/\n")
    project.write(support.PATH_MAP_REL, support.path_map())
    project.write(".gitleaks.toml", support.GITLEAKS_TEMPLATE.read_text(encoding="utf-8"))
    project.write(f"docs/adr/{CONSTRAINING}.md", support.decision(CONSTRAINING, constrains=[CALLER]))
    project.write(".tickets/PROJ-sh01.md", support.ticket("PROJ-sh01", implements=[CONSTRAINING]))
    project.write("app/__init__.py", "")
    project.write("app/alpha.py", f"def {SHARED}(value):\n    return value + 1\n\n\n"
                                  f"def {CALLER}(value):\n    return {SHARED}(value) * 2\n")
    project.write("app/beta.py", f"def {dead_name}(value):\n    return value - 1\n")
    project.commit("two modules")
    support.load_store(project.root, box)
    INDEXED.add(str(project.root))
    support.build_index(project.root, box)
    found = support.call("gov.codeintel", "callers", project.root, box, SHARED, path=box.full)
    names = [str(entry.get("name", entry)) if isinstance(entry, dict) else str(entry) for entry in (found or [])]
    assert any(support.names_symbol(n, CALLER) for n in names), \
        f"the fixture is wrong: the code index does not see {CALLER} call {SHARED} ({names})"
    return project.root


INDEXED = set()


@pytest.fixture(scope="module")
def shared_repos(built, tools, box, tmp_path_factory):
    """The repository where both modules define w37_shared, and the same with beta's renamed to w37_spare."""
    base = tmp_path_factory.mktemp("w2-37-shared")
    yield {"shared": shared_name_repo(base / "shared", box, SHARED),
           "renamed": shared_name_repo(base / "renamed", box, SPARE)}
    support.remove_daemon_dirs(box, INDEXED)


def change_entries(found, name):
    entries = [entry for entry in found["change"] if support.names_symbol(entry["id"], name)]
    assert entries, f"`change` does not name {name}: {found['change']}"
    for entry in entries:
        assert isinstance(entry.get("deletable"), bool), f"{name} does not say whether it is deletable: {entry}"
    return entries


@pytest.mark.local_only
def test_a_name_two_definitions_share_is_not_deletable_when_one_is_called(shared_repos, box):
    """beta's w37_shared is dead code; alpha's is called by w37_caller, which DEC-201 constrains."""
    shared = support.ask(shared_repos["shared"], SHARED, box, path=box.full)
    renamed = support.ask(shared_repos["renamed"], SHARED, box, path=box.full)
    entries = change_entries(shared, SHARED)
    assert all(entry["deletable"] is False for entry in entries), \
        f"{SHARED} is reported deletable although {CALLER} calls one of its definitions: {entries}"
    assert radius_number(shared) >= radius_number(renamed), \
        f"{SHARED}, defined twice, has radius {shared['radius']}; with the dead one renamed away it has " \
        f"{renamed['radius']}"


@pytest.mark.local_only
def test_with_the_dead_definition_renamed_each_name_is_judged_alone(shared_repos, box):
    """The success: w37_shared (called) is not deletable; w37_spare (called by nothing, named by no record) is."""
    called = support.ask(shared_repos["renamed"], SHARED, box, path=box.full)
    spare = support.ask(shared_repos["renamed"], SPARE, box, path=box.full)
    assert all(entry["deletable"] is False for entry in change_entries(called, SHARED)), \
        f"{SHARED}, which {CALLER} calls, is reported deletable"
    assert all(entry["deletable"] is True for entry in change_entries(spare, SPARE)), \
        f"{SPARE}, which nothing calls and no record names, is not reported deletable"


# --------------------------------------------------------------------------
# 5. A code file the index does not hold makes the code graph not current, whatever its modification time
# --------------------------------------------------------------------------

MOVED_REL, MOVED = "app/moved.py", "w37_moved"
LONG_AGO = 946684800                       # 2000-01-01T00:00:00Z: older than any index this suite builds


@pytest.mark.local_only
@pytest.mark.parametrize("committed", [False, True], ids=["untracked", "committed"])
def test_a_code_file_older_than_the_index_but_not_in_it_is_never_missed(indexed_own, box, committed):
    """After the index was built, app/moved.py, which calls w37_apply, arrives with its modification time (and its
    folder's) from before the index, as ``mv``, ``cp -p`` or unpacking an archive leave it. The change is w37_apply,
    so the new caller is one hop away."""
    project = as_project(indexed_own)
    folder = indexed_own / "app"
    before = os.stat(folder)
    path = project.write(MOVED_REL, f"from app.flow import {support.SYMBOL}\n\n\n"
                                    f"def {MOVED}(value):\n    return {support.SYMBOL}(value) + 13\n")
    os.utime(path, (LONG_AGO, LONG_AGO))
    os.utime(folder, ns=(before.st_atime_ns, before.st_mtime_ns))
    if committed:
        project.commit("a moved caller")
    run = support.impact(indexed_own, support.SYMBOL, box, path=box.full)
    document = support.envelope(run)
    if document["ok"] is True and support.where(support.assessment(run), MOVED, symbol=True):
        return                                                # read as it stands now: nothing dropped
    support.assert_incomplete(run, "code")
