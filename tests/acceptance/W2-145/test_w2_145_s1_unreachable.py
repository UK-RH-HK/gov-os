"""S1 (and failure lines 1 and 2): the shared service unreachable, in any way, leaves the search unranked and named,
and no reranker other than the shared service is ever started (DEC-1048 (5), DEC-1046 (1), DEC-374, DEC-1033,
DEC-1065 (1)).

One planted case per failure kind S1 names (``w2_145_support.KINDS``): no listener and its start refused (no GPU
slot, below its GPU share, no GPU, the GPU hidden); the socket refused, EPERM; no connection within ``CONNECT_S``;
no answer within the request's time limit; an error answer; the connection closed without an answer; an answer of
the wrong length (too few scores, too many), and, as an edge, a line that is not an answer.

For each: the search keeps the order given and no candidate carries a ``rerank_score``; ``last_outcome()`` is by
``unavailable`` with a reason that names the shared service and its failure; the planted interpreter recorded no
start of ``rerank_worker.py`` and no program other than the shared service (``rerank_service.py``); the stand-in
model was loaded by no process (on the GPU or the CPU); and the calling process holds none of the model's libraries.
The bundle's ``merge.reranked`` is false and its ``rerank`` entry says ``unavailable`` with that reason.

Every kind but the EPERM one needs Unix sockets (a stand-in server, or the session reaching the point where it starts
the service): in the launch sandbox the session's own ``socket(AF_UNIX)`` is refused first, and those cases fail on
their premise with the sandbox named. Run them outside it.
"""

from __future__ import annotations

import pytest

import w2_145_support as support
from w2_145_support import KIND_IDS, KINDS, Planted, box_for, candidates, check_unranked, query_of, raised


@pytest.mark.parametrize("kind", KINDS, ids=KIND_IDS)
def test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker(boxes, kind):
    box = box_for(boxes, kind)
    planted = Planted(box, kind)
    try:
        query, given = query_of(f"s1-{kind.name}"), candidates(f"s1-{kind.name}", 6)
        report = box.search(query, given, env=planted.env)
        who = f"the search whose service is unreachable ({kind.name})"
        assert raised(report) is None, f"{who} raised: {raised(report)}"
        planted.premise()
        check_unranked(report["result"], given, who)
        outcome = report.get("outcome") or {}
        assert outcome.get("by") == "unavailable", \
            f"{who}: last_outcome() is by {outcome.get('by')!r}, not 'unavailable': {outcome}"
        support.check_reason(outcome.get("reason"), kind, f"{who}, last_outcome()")
        support.check_no_private(box, report, who)
    finally:
        planted.close()


@pytest.mark.parametrize("kind", KINDS, ids=KIND_IDS)
def test_s1_the_bundle_of_an_unreachable_service_is_unranked_and_names_it_unavailable_with_the_reason(
        boxes, project, kind):
    tools, root = project
    box = box_for(boxes, kind)
    env = box.env(PATH=f"{box.state / 'bin'}:{tools}")
    planted = Planted(box, kind, env=env)
    try:
        report = box.start({"mode": "retrieve", "root": str(root), "query": support.QUERY}, env=planted.env).wait()
        who = f"the retrieval whose service is unreachable ({kind.name})"
        assert raised(report) is None, f"{who} raised: {raised(report)}"
        planted.premise()
        bundle = report["result"]
        assert isinstance(bundle, dict) and isinstance(bundle.get("merge"), dict), f"no bundle: {bundle!r}"[:800]
        assert bundle.get("evidence"), f"{who}: the project's question found no evidence: {bundle!r}"[:800]
        assert bundle["merge"].get("reranked") is False, f"{who}: the bundle says reranked: {bundle['merge']}"
        entry = bundle.get("rerank")
        assert isinstance(entry, dict) and entry.get("by") == "unavailable", \
            f"{who}: the bundle's rerank entry does not say unavailable: {entry!r}"
        support.check_reason(entry.get("reason"), kind, f"{who}, the bundle's rerank entry")
        support.check_no_private(box, report, who)
    finally:
        planted.close()
