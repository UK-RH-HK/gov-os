"""KPI success 3 and failure 3: the same answers as a private reranker (DEC-979 item 4, DEC-374).

For the same inputs on the same device, the order and the scores match a private reranker's (within float
rounding; ties keep the given order). Failure: answers that differ from a private reranker's on the same inputs
and device.

The reference is ``gov.retrieval.rerank.rerank`` itself, given a private, in-process reranker of the same stand-in
model in the same session (the public ``reranker=`` loader), beside the computed expectation. The measurement on
the 20 visible memory questions and the 48 is the research document's, with the real model; these cases hold the
rule on planted texts.
"""

from __future__ import annotations

import w2_112_support as support
from w2_112_support import candidates, check_scored, query_of, raised


def _same(service, private, who):
    assert isinstance(private, list), f"the private reference could not be computed: {private!r}"
    assert [entry["chunk_id"] for entry in service] == [entry["chunk_id"] for entry in private], \
        (f"{who}: the service's order {[e['chunk_id'] for e in service]} is not a private reranker's "
         f"{[e['chunk_id'] for e in private]} on the same inputs")
    for mine, theirs in zip(service, private):
        assert abs(float(mine["rerank_score"]) - float(theirs["rerank_score"])) <= support.TOLERANCE, \
            f"{who}: {mine['chunk_id']} scored {mine['rerank_score']} by the service, {theirs['rerank_score']} privately"
        assert {key: value for key, value in mine.items() if key != "rerank_score"} == \
            {key: value for key, value in theirs.items() if key != "rerank_score"}, \
            f"{who}: the service's candidate differs from the private one beyond its score: {mine!r}"[:600]


def test_the_services_answers_match_a_private_rerankers_on_the_same_inputs(box):
    service = box.warm()
    query, given = query_of("match"), candidates("match", 30, ties=3)
    report = box.search(query, given, private=True)
    assert raised(report) is None, f"the search raised: {raised(report)}"
    assert box.scorers_of(query) == {service}, \
        f"the search was not answered by the service {service} but by {box.scorers_of(query)}"
    check_scored(report["result"], query, given, "the service's answer")
    _same(report["result"], report["private"], "the service against a private reranker")


def test_candidates_the_service_scores_alike_keep_the_order_given(box):
    service = box.warm()
    query = query_of("alike")
    given = candidates("alike", 6, ties=6)  # one text, six candidates: six equal scores
    report = box.search(query, given, private=True)
    assert raised(report) is None, f"the search raised: {raised(report)}"
    assert box.scorers_of(query) == {service}, "the search was not answered by the service"
    assert [entry.get("chunk_id") for entry in report["result"]] == [entry["chunk_id"] for entry in given], \
        f"candidates scored alike did not keep the order given: {[e.get('chunk_id') for e in report['result']]}"
    _same(report["result"], report["private"], "equal scores through the service")


def test_the_same_inputs_get_the_same_answer_whichever_session_asks_and_whatever_shares_the_model(box):
    # Several sessions at once, three of them with the same inputs and the others with their own: whatever the
    # service scores together, each answer is the private one for its own inputs.
    service = box.warm()
    query, given = query_of("shared"), candidates("shared", 10, ties=2)
    requests = [{"query": query, "candidates": given} for _ in range(3)]
    requests += [{"query": query_of(f"own{n}"), "candidates": candidates(f"own{n}", 10)} for n in range(3)]
    reports = box.together(requests)
    for number, (request, report) in enumerate(zip(requests, reports)):
        assert raised(report) is None, f"session {number} raised: {raised(report)}"
        check_scored(report["result"], request["query"], request["candidates"], f"session {number}")
    assert box.scorers_of(query) == {service}, "the sessions were not all answered by the service"
