"""KPI success 1: "with no model", and what a closure does when the code facet cannot answer [CAP-57.a].

Also here: a closure only reads (CAP-27), and it reads the record graph as the store holds it (DEC-344).

Every test here runs without the real code tool. Where a test needs the tool to be absent or to fail, the ``PATH``
holds ``git`` alone or a stand-in program that records each run and fails.
"""

from __future__ import annotations

import pytest

import w1_20_support as support


def _path(box, tmp_path, case):
    """A PATH on which the code tool is absent, or is a program that fails whenever it is run."""
    if case == "absent":
        return str(box.bare), None
    marker = tmp_path / "tool-runs"
    return f"{support.stub(tmp_path / 'failing', support.TOOL, marker)}:{box.bare}", marker


# --------------------------------------------------------------------------
# The code facet cannot answer
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", ["absent", "failing"])
def test_an_unavailable_code_facet_is_stated_and_ends_nothing(graph, box, tmp_path, case):
    """An id that is no record could be a symbol. The tool cannot say: the output says so, and keeps the records.

    Never an exception, never a silent omission: the id is in the gap list, and not as "no such id" (DEC-034:
    NOT_FOUND is not absent).
    """
    path, _ = _path(box, tmp_path, case)
    found = support.ask(graph, [support.SOLO, support.UNKNOWN], box, depth=1, path=path)
    assert support.code_facet(found) == "unavailable"
    assert support.ids(found) == [support.SOLO], "the record side is lost with the code facet"
    assert support.gap_reasons(found, support.UNKNOWN) == [support.GAP_FACET]
    assert found["stopping_reason"] == support.FACET_UNAVAILABLE


def test_a_closure_of_records_alone_does_not_run_the_code_tool(graph, box, tmp_path):
    """Package DP-4: the code facet is asked only about a start id that is no record, and about symbols.

    A complete closure of records is CLOSURE_COMPLETE whatever the state of the code index, and it does not say
    the code facet is unavailable: nothing was asked of it. The same holds for a record's edge to no record.
    """
    path, marker = _path(box, tmp_path, "failing")
    found = support.ask(graph, [support.HUB, support.CYCLE[0]], box, depth=3, path=path)
    assert found["stopping_reason"] == support.COMPLETE and found["gaps"] == []
    dangling = support.ask(graph, [support.DANGLING_START], box, depth=3, path=path)
    assert support.gap_ids(dangling) == [support.MISSING_NEAR, support.MISSING_FAR]
    assert not marker.exists(), f"the code tool was run for a closure of records:\n{marker.read_text()}"
    assert support.code_facet(found) != "unavailable" and support.code_facet(dangling) != "unavailable"


# --------------------------------------------------------------------------
# No model
# --------------------------------------------------------------------------

def test_a_closure_starts_no_ollama_and_asks_no_model(graph, box, tmp_path):
    """An ``ollama`` program on PATH and in GOV_OLLAMA_BIN, and a listening endpoint in OLLAMA_HOST: neither is used.

    The ids cover a complete closure, a depth cut, a dangling edge and an id that is no record, so every path of
    the closure runs.
    """
    marker = tmp_path / "ollama-runs"
    stubs = support.stub(tmp_path / "models", "ollama", marker, exit_code=0)
    with support.Listener() as listener:
        for ids, depth in (([support.HUB], 5), ([support.CHAIN[0]], 1), ([support.DANGLING_START, support.UNKNOWN], 5)):
            run = support.closure(graph, ids, box, depth=depth, path=f"{stubs}:{box.bare}",
                                  GOV_OLLAMA_BIN=stubs / "ollama", OLLAMA_HOST=listener.address)
            support.result(run)
        assert listener.connections() == 0, "gov closure connected to the Ollama endpoint"
    assert not marker.exists(), f"gov closure ran ollama:\n{marker.read_text()}"


# --------------------------------------------------------------------------
# A read command
# --------------------------------------------------------------------------

def test_a_closure_changes_nothing_in_the_repository(repo, box):
    """CAP-27: ``git status --porcelain`` stays empty. The store is read, not written, and HEAD does not move."""
    store, head = support.sha256(repo / support.STORE_REL), support.head(repo)
    for ids, depth in (([support.HUB], 0), ([support.DANGLING_START, support.UNKNOWN], 5)):
        support.ask(repo, ids, box, depth=depth)
    assert support.porcelain(repo) == []
    assert support.sha256(repo / support.STORE_REL) == store, "gov closure wrote the store"
    assert support.head(repo) == head


def test_a_closure_does_not_build_the_store(built, base, box, tmp_path):
    """No store was loaded: the closure does not load one (DEC-322), and it does not call the closure complete.

    Whether that is the error STORE_MISSING or a result that states the record facet unavailable is the
    engineer's: either way it is an envelope, not a traceback.
    """
    root = support.clone(base, tmp_path / "repo")
    run = support.closure(root, [support.HUB], box, depth=1)
    document = support.envelope(run)
    assert not (root / support.STORE_REL).exists(), "gov closure built the store"
    if document["ok"]:
        assert support.result(run)["stopping_reason"] != support.COMPLETE
    else:
        assert run.returncode == 1 and document["error"]["code"] == "STORE_MISSING", run.describe()


# --------------------------------------------------------------------------
# The record graph is the store's: HEAD at the load, not the working tree (DEC-344)
# --------------------------------------------------------------------------

def _cut_the_chain(repo):
    """An uncommitted edit: the third record of the chain no longer names the fourth."""
    rel = support.record_path(support.CHAIN[2])
    support.write(repo, rel, support.record(support.CHAIN[2]))
    return rel


def test_an_uncommitted_edit_of_a_record_is_not_in_the_closure(repo, box):
    """The caller sees the records as the store holds them: the edit in the working tree changes no edge."""
    before = support.ask(repo, [support.CHAIN[0]], box, depth=50)
    _cut_the_chain(repo)
    after = support.ask(repo, [support.CHAIN[0]], box, depth=50)
    assert support.ids(after) == support.CHAIN
    assert (after["closure"], after["gaps"], after["stopping_reason"]) == \
        (before["closure"], before["gaps"], before["stopping_reason"])


def test_the_result_names_the_files_that_differ_from_head(repo, box):
    """Package DP-7: ``uncommitted`` lists the paths whose working tree is not HEAD's; a clean tree has none."""
    assert support.ask(repo, [support.CHAIN[0]], box, depth=1)["uncommitted"] == []
    rel = _cut_the_chain(repo)
    assert support.ask(repo, [support.CHAIN[0]], box, depth=1)["uncommitted"] == [rel]
