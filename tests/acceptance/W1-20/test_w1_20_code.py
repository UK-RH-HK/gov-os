"""KPI success 1, the code side: ids are resolved through codebase-memory callers and callees [CAP-57.a].

These tests run the real code tool on a temporary repository of four functions in one file: ``w20_top`` calls
``w20_mid``, ``w20_mid`` calls ``w20_leaf``, ``w20_side`` calls ``w20_leaf``. The repository is indexed through
``gov.codeintel.index``; a closure never builds an index. Without the ``codebase-memory-mcp`` and ``gitleaks``
binaries the tests are skipped. This repository is never indexed.
"""

from __future__ import annotations

import pytest

import w1_20_support as support

pytestmark = pytest.mark.local_only

LEAF, MID, TOP, SIDE, DRAFT = support.LEAF, support.MID, support.TOP, support.SIDE, support.DRAFT
ALL = sorted([LEAF, MID, TOP, SIDE])


def _ask(root, ids, box, depth):
    return support.ask(root, ids, box, depth=depth, path=box.full)


def test_the_wrapper_gives_the_callers_the_source_states(indexed_wrapper, box):
    """The premise, which passes before W1-20: the expected answers are the fixture's and the wrapper agrees."""
    for name, expected in support.CALLERS.items():
        answer = support.call("gov.codeintel", "callers", indexed_wrapper, box, name, path=box.full)
        assert sorted(entry["name"] for entry in answer) == expected, f"callers({name}) of the fixture"


def test_a_symbol_is_resolved_and_its_callers_are_followed_to_the_depth(indexed, box):
    """From the leaf: its two callers at one hop, the caller of one of them at two."""
    near = _ask(indexed, [LEAF], box, 1)
    assert support.ids(near, "symbol") == sorted([LEAF, MID, SIDE]) and support.ids(near, "record") == []
    assert near["stopping_reason"] == support.DEPTH_LIMIT
    assert support.gap_ids(near) == [TOP] and support.gap_reasons(near, TOP) == [support.GAP_DEPTH]
    far = _ask(indexed, [LEAF], box, 2)
    assert support.ids(far, "symbol") == ALL
    assert far["stopping_reason"] == support.COMPLETE and far["gaps"] == []
    assert support.code_facet(far) == "available"


def test_the_callees_of_a_symbol_are_followed(indexed, box):
    """Package DP-6: from the top, what it calls and what that calls; then the other caller of the leaf."""
    none = _ask(indexed, [TOP], box, 0)
    assert support.ids(none, "symbol") == [TOP] and support.gap_ids(none) == [MID]
    two = _ask(indexed, [TOP], box, 2)
    assert support.ids(two, "symbol") == sorted([TOP, MID, LEAF])
    assert two["stopping_reason"] == support.DEPTH_LIMIT and support.gap_ids(two) == [SIDE]
    three = _ask(indexed, [TOP], box, 3)
    assert support.ids(three, "symbol") == ALL and three["stopping_reason"] == support.COMPLETE


def test_records_and_symbols_are_resolved_in_one_closure(indexed, box):
    found = _ask(indexed, [support.CYCLE[0], MID], box, 1)
    assert support.ids(found, "record") == support.CYCLE
    assert support.ids(found, "symbol") == sorted([MID, TOP, LEAF])
    assert support.gap_ids(found) == [SIDE] and found["stopping_reason"] == support.DEPTH_LIMIT


def test_an_id_that_is_no_record_and_no_symbol_is_an_unresolved_gap(indexed, box):
    """Failure 2 with both facets answering: the id is listed as unresolved, next to what did resolve."""
    found = _ask(indexed, [LEAF, support.UNKNOWN, support.DANGLING_START], box, 5)
    assert support.code_facet(found) == "available"
    assert support.ids(found, "symbol") == ALL
    assert support.gap_ids(found) == sorted([support.UNKNOWN, support.MISSING_NEAR, support.MISSING_FAR])
    for missing in (support.UNKNOWN, support.MISSING_NEAR, support.MISSING_FAR):
        assert support.gap_reasons(found, missing) == [support.GAP_UNRESOLVED]
    assert found["stopping_reason"] != support.COMPLETE


def test_repeated_runs_and_a_rebuilt_index_print_the_same_bytes(indexed, box, tmp_path):
    """Failure 1 on the code side: other hash seeds, and the index built anew between two runs."""
    ids = [LEAF, support.CHAIN[0], support.UNKNOWN]
    outputs = [support.closure(indexed, ids, box, depth=1, path=box.full, PYTHONHASHSEED=seed).stdout
               for seed in ("0", "7", "random")]
    support.build_index(indexed, box)
    outputs.append(support.closure(indexed, ids, box, depth=1, path=box.full, PYTHONHASHSEED="3").stdout)
    assert len(set(outputs)) == 1 and outputs[0].strip(), "gov closure printed different bytes on one commit"
    assert str(indexed).encode() not in outputs[0], "the output holds an absolute path of the repository"


def test_a_repository_without_a_code_index_states_the_facet_unavailable(built, tools, code_base, box, tmp_path):
    """The tool is there and the repository was never indexed: stated in the output, and no index is built."""
    root = support.clone(code_base, tmp_path / "repo")
    support.load_store(root, box)
    found = _ask(root, [support.CYCLE[0], LEAF], box, 1)
    assert support.code_facet(found) == "unavailable"
    assert support.ids(found) == support.CYCLE
    assert support.gap_reasons(found, LEAF) == [support.GAP_FACET]
    assert found["stopping_reason"] == support.FACET_UNAVAILABLE
    assert not (root / support.INDEX_REL / "files").exists(), "gov closure built a code index"
    assert support.porcelain(root) == []


def test_a_closure_over_code_starts_no_ollama_and_asks_no_model(indexed, box, tmp_path):
    marker = tmp_path / "ollama-runs"
    stubs = support.stub(tmp_path / "models", "ollama", marker, exit_code=0)
    with support.Listener() as listener:
        run = support.closure(indexed, [LEAF, support.HUB], box, depth=3, path=f"{stubs}:{box.full}",
                              GOV_OLLAMA_BIN=stubs / "ollama", OLLAMA_HOST=listener.address)
        assert support.ids(support.result(run), "symbol") == ALL
        assert listener.connections() == 0, "gov closure connected to the Ollama endpoint"
    assert not marker.exists(), f"gov closure ran ollama:\n{marker.read_text()}"


# --------------------------------------------------------------------------
# The code side is the working tree as it was indexed (DEC-344)
# --------------------------------------------------------------------------

def test_an_uncommitted_function_in_the_index_is_in_the_closure(draft, box):
    """The caller sees the code as the index holds it: a caller that exists only in the working tree is there."""
    found = _ask(draft, [LEAF], box, 1)
    assert support.ids(found, "symbol") == sorted([LEAF, MID, SIDE, DRAFT])


def test_the_result_names_the_code_file_that_differs_from_head(draft, indexed, box):
    """Package DP-7: the file the two sides can disagree on is named; a clean tree names none."""
    assert _ask(draft, [LEAF], box, 1)["uncommitted"] == [support.CODE_REL]
    assert _ask(indexed, [LEAF], box, 1)["uncommitted"] == []
