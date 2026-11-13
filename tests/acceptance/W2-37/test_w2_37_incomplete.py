"""An impact report never reads as complete when a graph was missing, stale or unreadable: it says which graph
and that the result is incomplete (the brief's failure lines; DEC-037: a facet that cannot answer is never "no
evidence exists").

A report "says it" in one of two ways (reading R4): it succeeds with ``complete: false`` and a ``graphs.<graph>``
that is not ``ok``, or it refuses with an error that names the graph.
"""

from __future__ import annotations

import pytest

import w2_37_support as support


def test_without_a_record_store_the_report_is_not_complete(built, base, box, tmp_path):
    root = support.clone(base, tmp_path / "repo")          # no store loaded
    support.assert_incomplete(support.impact(root, support.CHANGED, box), "record")


def test_an_unreadable_record_store_is_said(repo, box):
    stores = sorted(path for path in (repo / ".gov-runtime").rglob("*.db") if path.is_file())
    assert stores, f"the fixture is wrong: the loaded store left no database under {repo / '.gov-runtime'}"
    for path in stores:
        path.write_bytes(b"this is not a database\n" * 64)
    support.assert_incomplete(support.impact(repo, support.CHANGED, box), "record")


def test_a_stale_record_store_is_said_and_never_complete(project, box):
    """A ticket that implements DEC-001 is committed after the store was loaded."""
    project.write(".tickets/PROJ-ac01.md", support.ticket("PROJ-ac01", implements=[support.CHANGED]))
    project.commit("a late ticket")
    run = support.impact(project.root, support.CHANGED, box)
    document = support.envelope(run)
    if document["ok"] is True and "PROJ-ac01" in support.ids_of(support.assessment(run), "tickets"):
        return                                                # read as it stands now: nothing dropped
    support.assert_incomplete(run, "record", word="stale")


def test_an_unreadable_code_graph_is_said_and_the_record_side_still_given(graph, box):
    """With ``git`` alone on PATH the code tool cannot run. DEC-001 names the symbol w37_apply."""
    run = support.impact(graph, support.CHANGED, box)
    found = support.assert_incomplete(run, "code")
    if found is not None:
        for record_id in (support.SPEC, support.OTHER_DECISION, support.TICKET, support.TEST_RECORD):
            assert support.where(found, record_id), f"{record_id} is dropped when the code graph is unreadable"
        assert support.where(found, support.SYMBOL, symbol=True) or support.in_gaps(found, support.SYMBOL, True), \
            f"{support.SYMBOL}, which DEC-001 names, is neither listed nor named as a gap\n{run.describe()}"


@pytest.mark.local_only
def test_a_code_graph_never_built_is_said(built, tools, code_base, box, tmp_path):
    root = support.clone(code_base, tmp_path / "repo")
    support.load_store(root, box)                         # the code index is not built
    support.assert_incomplete(support.impact(root, support.CHANGED, box, path=box.full), "code")


@pytest.mark.local_only
def test_a_stale_code_graph_is_said_and_never_complete(indexed_own, box):
    """A caller of w37_apply is committed after the code index was built; the change is w37_apply itself, so the
    late caller is one hop away."""
    project = support.Project.__new__(support.Project)
    project.root, project.minute = indexed_own, 100
    rel = indexed_own / support.CODE_REL
    project.write(support.CODE_REL, rel.read_text(encoding="utf-8")
                  + f"\n\ndef w37_late(value):\n    return {support.SYMBOL}(value) + 11\n")
    project.commit("a late caller")
    run = support.impact(indexed_own, support.SYMBOL, box, path=box.full)
    document = support.envelope(run)
    if document["ok"] is True and support.where(support.assessment(run), "w37_late", symbol=True):
        return                                            # read as it stands now: nothing dropped
    support.assert_incomplete(run, "code", word="stale")
