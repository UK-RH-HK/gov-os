"""S4: a reranker that dies after loading is reported, not raised [W2-M104; DEC-374].

W2-M104's closing condition: "A dead reranker yields the absent path or an envelope error, with a case." The absent
path is DEC-374's: the order given is kept, no candidate carries a score, and the outcome says the rerank was
unavailable and why (``last_outcome()``; ``rerank`` in a bundle; ``reranked`` false in the fusion's answer).

The dying rerankers load and then die at the first score: a real child process that prints its "loaded" line and
exits (a closed pipe, an empty answer), the same failure raised directly in each form a dead process gives, and the
default reranker started from a fake reranker environment in the scratch ``HOME`` whose worker does the same. No
model is loaded.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w2_32_support as s

DYING = ["dies-process", "dies:BrokenPipeError", "dies:ConnectionResetError", "dies:EOFError",
         "dies:JSONDecodeError", "dies:RuntimeError"]
CANDIDATES = [{"chunk_id": f"c{i}", "path": f"docs/{name}.md", "text": f"[path: docs/{name}.md]\n{name} note"}
              for i, name in enumerate(("harbour", "bakery", "orchard"))]
NOT_A_REASON = {None, "", "no rerank was asked", "nothing to rerank"}

# The fake reranker environment (DEC-397's path under HOME): the service ends at once without listening; the private
# worker prints its "loaded" line and exits, so the search falls back to a reranker that is dead after loading.
FAKE_PYTHON = """#!/bin/sh
for arg in "$@"; do
  case "$arg" in
    *rerank_worker.py) echo '{"device": "cpu"}'; exit 0 ;;
  esac
done
exit 1
"""


def _reported(outcome):
    assert outcome["by"] == "unavailable", f"a dead reranker is reported as unavailable: {outcome}"
    assert outcome.get("reason") not in NOT_A_REASON, f"the outcome says why the rerank was unavailable: {outcome}"


def _fake_reranker_environment(box):
    python = Path(box.home) / ".local/share/gov-os/reranker-venv/bin/python"
    python.parent.mkdir(parents=True, exist_ok=True)
    python.write_text(FAKE_PYTHON, encoding="utf-8")
    python.chmod(0o755)


@pytest.mark.parametrize("dying", DYING)
def test_rerank_with_a_reranker_that_dies_after_loading_keeps_the_order_and_reports_it(box, dying):
    data = box.call("rerank", query="tide tables", candidates=CANDIDATES, reranker=dying, times=2)
    answers = s.result(data)
    for answer in answers:  # the second search meets the same dead reranker
        assert [c["chunk_id"] for c in answer["ranked"]] == [c["chunk_id"] for c in CANDIDATES], \
            "the order given is kept"
        assert not any("rerank_score" in c for c in answer["ranked"]), "no candidate carries a score"
        _reported(answer["outcome"])


def test_the_default_reranker_that_dies_after_loading_is_reported_not_raised(box):
    _fake_reranker_environment(box)
    data = box.call("rerank", query="tide tables", candidates=CANDIDATES, reranker=None, times=2)
    for answer in s.result(data):
        assert [c["chunk_id"] for c in answer["ranked"]] == [c["chunk_id"] for c in CANDIDATES]
        assert not any("rerank_score" in c for c in answer["ranked"])
        _reported(answer["outcome"])


@pytest.mark.parametrize("dying", ["dies-process", "dies:EOFError"])
def test_the_fusion_with_a_dying_reranker_answers_unreranked_and_reports_it(project, box, standin, dying):
    box.built(project)
    data = box.call("fusion_search", root=str(project), query=s.QUESTIONS[0][0], limit=5, reranker=dying)
    answer = s.result(data)
    assert answer["hits"], "the fused hits are still returned"
    assert answer["reranked"] is False, answer["reranked"]
    _reported(answer["outcome"])
    s.no_traceback(data)


@pytest.mark.parametrize("dying", ["dies-process", "dies:EOFError", None])
def test_retrieve_with_a_dying_reranker_cites_its_evidence_and_reports_the_rerank_unavailable(
        project, box, standin, dying):
    if dying is None:
        _fake_reranker_environment(box)
    box.built(project)
    question, gold = s.QUESTIONS[0]
    data = box.call("retrieve", root=str(project), query=question, reranker=dying)
    bundle = s.result(data)
    assert gold in s.first_paths(bundle["evidence"]), "the evidence is still cited"
    assert bundle["merge"]["reranked"] is False
    _reported(bundle["rerank"])
    s.no_traceback(data)
