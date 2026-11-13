"""W2-15a's mode switch: ``python3 modes.py <mode> <gov arguments>`` runs the clone's own ``gov`` with its retrieval's
routes switched, src/ unchanged. Modes: lexical, semantic (that route alone, no rerank), fused (every route RRF-fused,
no rerank), rerank (fused plus the shared reranker service: the shipped path, with the private-reranker fallback and
the service start disabled). GOV_W215A_LOG names a file that gets one line per rerank: who scored."""
import os
import sys

from gov.retrieval import rerank as rr
from gov.retrieval import retrieve as rt

MODE = sys.argv.pop(1)
KEEP = {"lexical": {"lexical"}, "semantic": {"semantic"}}.get(MODE)  # None: every route
if MODE not in ("lexical", "semantic", "fused", "rerank"):
    sys.exit(f"modes.py: unknown mode {MODE}")
if KEEP is not None:
    _rrf = rt.rrf
    rt.rrf = lambda routes, **kw: _rrf({k: v for k, v in routes.items() if k in KEEP}, **kw)
if MODE == "rerank":
    def _no_start(*_a, **_k):
        raise ConnectionError("W2-15a: the harness never starts the shared service")
    rr._start = _no_start
    rr._started = lambda _interp: (None, None, "W2-15a: the harness allows no private reranker")
    _rerank = rt.rerank

    def _logged(query, candidates, reranker=None):
        out = _rerank(query, candidates, reranker)
        if os.environ.get("GOV_W215A_LOG"):
            with open(os.environ["GOV_W215A_LOG"], "a", encoding="utf-8") as log:
                log.write(f"{rr.last_outcome()['by']}\t{len(candidates)}\n")
        return out
    rt.rerank = _logged
else:
    rt.rerank = lambda query, candidates, reranker=None: [dict(c) for c in candidates]

from gov.cli.main import main  # noqa: E402

sys.exit(main(sys.argv[1:]))
