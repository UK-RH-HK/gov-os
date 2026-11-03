"""S5: the fusion limit is honoured [W2-M103].

W2-M103: "fusion.search caps at 30 hits regardless of limit"; its closing condition: "fusion.search honours limit, or
rejects a limit above its cap." A planted project holds 50 notes that all match the question, so both routes give
more than 30 chunks. A limit is honoured when exactly that many distinct chunks come back (as many as match, if
fewer); it is rejected when the call refuses it with an error that names the limit or the cap. Silently returning
fewer than asked, while more match, is neither.
"""

from __future__ import annotations

import pytest

import w2_32_support as s

MATCHING = 50
QUESTION = "Which notes mention the quorum of the harbour council?"
WORDS = ("amber", "basalt", "cobalt", "dune", "ember", "fjord", "garnet", "heron", "indigo", "juniper")


def _notes():
    notes = {}
    for i in range(MATCHING):
        a, b = WORDS[i % 10], WORDS[i // 10]
        notes[f"docs/council-{i:02d}.md"] = (f"# Council note {i}\n\nThe harbour council reached its quorum on the "
                                             f"{a} {b} question, item {i}.\n")
    return notes


@pytest.fixture
def many(tmp_path, needs_vectors, box):
    project = s.plant(tmp_path / "many", {**_notes(), "README.md": "# Council notes\n"})
    box.built(project)
    return project


def _honoured_or_refused(data, limit):
    raised = data.get("raised")
    if raised is not None:
        assert any(kind in raised["types"] for kind in ("ValueError", "GovError")), \
            f"a limit above the cap may be refused, as a ValueError or a GovError, not {raised['type']}"
        assert str(limit) in raised["message"] or "30" in raised["message"] or "limit" in raised["message"], \
            f"the refusal names the limit or the cap: {raised['message']}"
        return None
    hits = data["result"]["hits"]
    ids = [hit["chunk_id"] for hit in hits]
    assert len(ids) == len(set(ids)), "each chunk once"
    assert len(hits) == limit, f"asked for {limit} of {MATCHING} matching notes, got {len(hits)}: the limit is not " \
                               f"honoured (W2-M103)"
    return hits


@pytest.mark.parametrize("limit", [31, 40, 50])
def test_a_limit_above_thirty_is_honoured_or_refused(many, box, standin, limit):
    data = box.call("fusion_search", root=str(many), query=QUESTION, limit=limit)
    _honoured_or_refused(data, limit)
    s.no_traceback(data)


@pytest.mark.parametrize("limit", [1, 5, 30])
def test_a_limit_up_to_thirty_returns_exactly_that_many(many, box, standin, limit):
    hits = s.result(box.call("fusion_search", root=str(many), query=QUESTION, limit=limit))["hits"]
    assert len(hits) == limit and len({hit["chunk_id"] for hit in hits}) == limit, len(hits)


def test_a_honoured_limit_keeps_the_order_of_a_smaller_one(many, box, standin):
    """When a larger limit is honoured, the first hits are those a smaller limit gives, in the same order."""
    data = box.call("fusion_search", root=str(many), query=QUESTION, limit=40, reranker="constant")
    if data.get("raised") is not None:
        pytest.skip("this build refuses a limit above its cap; the order of a honoured limit does not arise")
    large = _honoured_or_refused(data, 40)
    small = s.result(box.call("fusion_search", root=str(many), query=QUESTION, limit=5, reranker="constant"))["hits"]
    assert [hit["chunk_id"] for hit in large[:5]] == [hit["chunk_id"] for hit in small]
