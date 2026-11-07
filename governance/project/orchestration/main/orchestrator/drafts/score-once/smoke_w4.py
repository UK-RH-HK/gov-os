"""E0b smoke check: window 4's real ``retrieve`` (the pin's gov) driven through rx.py on a window-4 clone, read only,
with no GPU and no embedder: the meaning route, the code route's cosine and the scorer are stubs; the keyword route,
the record graph, the closure and the code index are the clone's own (refresh=False: nothing written). Prints counts
only; the question is the check's own, not one of any set.

    env -u GOV_ROLE -u GOV_TICKET HOME=<tmp> GOV_RX_NO_MAIN=1 GOV_RX_CACHE=<tmp>/c GOV_RX='<variant>' \
        [GOV_RX_POOL_OFF=1] <pin python> smoke_w4.py <clone root>
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("rx", Path(__file__).with_name("rx.py"))
rx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rx)
from gov.retrieval import retrieve as rt  # noqa: E402
from gov.retrieval import semantic  # noqa: E402

depths, passes = [], []
_lex_real = rx._lex_search


def lex_seen(r, q, refresh=True, **kw):
    depths.append(kw.get("top_k"))
    return _lex_real(r, q, refresh, **kw)


def sem_stub(r, q, refresh=True, **kw):
    depths.append(("sem", kw.get("top_k")))
    return {"available": True, "facet": "semantic", "state": "AVAILABLE", "reason": None, "hits": []}


def fake_scores(query, texts):
    passes.append(len(texts))
    return [int(hashlib.sha256((query + "\x00" + t).encode()).hexdigest()[:8], 16) / 4e9 for t in texts]


rx._lex_search, rx._sem_search, rx.scores = lex_seen, sem_stub, fake_scores
semantic.distances = lambda r, q, ids: None
QUESTION = "How does the guard refuse a write outside a ticket's allowed paths?"
first = rt.retrieve(root, QUESTION)
later = rt.retrieve(root, QUESTION, continuation=first["continuation"]) if first.get("continuation") else None
print(json.dumps({
    "evidence": len(first["evidence"]), "rerank_by": (first.get("rerank") or {}).get("by"),
    "pool": {k: v for k, v in (first.get("pool") or {}).items() if k != "nested"},
    "keyword_depths": sorted({str(d) for d in depths}), "scored_passes": passes,
    "continuation_evidence": None if later is None else len(later["evidence"]),
    "stores": [list(v) for v in rx.STORES.values() if v]}))
