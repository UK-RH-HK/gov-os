"""W2-155 profile of the warm real-model query path (read-only probe; writes only under the given work dir).

Usage: python3 profile_warm.py <workdir> [tier ...]
Per tier: clone (W1-19's clone_tier), semantic.refresh, three warm-up questions, then each dev query of the tier
once through fusion.search(root, q, limit=None, refresh=False), as W1-19's timed pass does. Each stage is timed by
wrapping module attributes (looked up at call time), and the timed queries run under cProfile.
"""
import cProfile
import io
import json
import math
import os
import pstats
import sys
import time
from collections import defaultdict
from pathlib import Path

TREE = Path("/home/usain/gov-os-worktrees/W2-155")
sys.path.insert(0, str(TREE / "src"))
sys.path.insert(0, str(TREE / "tests/acceptance/W1-19"))
import w1_19_support as support  # noqa: E402

from gov.retrieval import fusion, lexical, semantic, ollama, rerank as rerank_mod  # noqa: E402

work = Path(sys.argv[1])
tiers = sys.argv[2:] or list(support.TIERS.values())

TIMES = defaultdict(list)   # stage -> [seconds per timed query (summed within the query)]
CUR = defaultdict(float)
COUNT = defaultdict(int)
ACTIVE = [False]


def wrap(module, name, label=None):
    original = getattr(module, name)
    label = label or f"{module.__name__.split('.')[-1]}.{name}"

    def timed(*args, **kwargs):
        start = time.perf_counter()
        try:
            return original(*args, **kwargs)
        finally:
            if ACTIVE[0]:
                CUR[label] += time.perf_counter() - start
                COUNT[label] += 1
    timed.__wrapped__ = original
    setattr(module, name, timed)


wrap(lexical, "search")
wrap(semantic, "search")
wrap(fusion, "_records")
wrap(fusion, "rerank", "rerank.rerank (service round trip)")
wrap(lexical, "_checked")
wrap(lexical, "_git")
wrap(lexical, "_ranked")
wrap(semantic, "_status")
wrap(semantic, "_vectors")
wrap(semantic, "_pin")
wrap(semantic, "_ready")
wrap(semantic, "query_vector")
wrap(semantic, "_embed")
wrap(semantic, "_ask")
wrap(semantic, "_device")
wrap(semantic, "_cached")
wrap(semantic, "_cache")
wrap(semantic, "_built_at")
wrap(semantic, "_open")
REQS = []
_orig_ask = rerank_mod._ask


def _ask_rec(interpreter, query, texts):
    start = time.perf_counter()
    try:
        return _orig_ask(interpreter, query, texts)
    finally:
        if ACTIVE[0]:
            longest = max(len(query) + len(t) for t in texts)
            REQS.append({"n": len(texts), "longest_pair": longest, "padded": len(texts) * longest,
                         "chars": sum(len(query) + len(t) for t in texts), "s": time.perf_counter() - start})


rerank_mod._ask = _ask_rec
if os.environ.get("PROF_REQUEST_CHARS"):  # run 2 A/B, probe only: the request bound
    rerank_mod.MAX_REQUEST_CHARS = int(os.environ["PROF_REQUEST_CHARS"])
if os.environ.get("PROF_RERANK_CHARS"):
    fusion.RERANK_CHARS = int(os.environ["PROF_RERANK_CHARS"])
for name in ("ensure_query_available",):
    if hasattr(ollama, name):
        wrap(ollama, name)

queries = support.dev_queries()
by_tier = {tier: [q for q in queries if q["programme"] == prog] for prog, tier in support.TIERS.items()}
report = {"load_before": os.getloadavg(), "tiers": {}}
profiler = cProfile.Profile()
totals = []
for tier in tiers:
    reuse = os.environ.get("PROF_REUSE")
    root = Path(reuse) / f"{tier}-clone" / tier if reuse else support.clone_tier(tier, work / f"{tier}-clone" / tier)
    t0 = time.perf_counter()
    built = semantic.refresh(root)
    build_s = time.perf_counter() - t0
    for text in support.WARM_UP_QUERIES:
        fusion.search(root, text, limit=None, refresh=False)
    tier_rows = []
    for query in by_tier[tier]:
        CUR.clear()
        ACTIVE[0] = True
        profiler.enable()
        start = time.perf_counter()
        answer = fusion.search(root, query["query"], limit=None, refresh=False)
        total = time.perf_counter() - start
        profiler.disable()
        ACTIVE[0] = False
        totals.append(total)
        row = {"id": query["id"], "total": total, "reranked": answer["reranked"], "n": len(answer["hits"]),
               "facets": {k: {kk: vv for kk, vv in v.items() if kk in ("available", "reason")}
                          for k, v in answer["facets"].items()}}
        row.update({k: v for k, v in CUR.items()})
        for k, v in CUR.items():
            TIMES[k].append(v)
        tier_rows.append(row)
    report["tiers"][tier] = {"build_s": build_s, "refresh_error": built.get("error"), "rows": tier_rows}

report["load_after"] = os.getloadavg()
report["requests"] = REQS
report["rerank_chars"] = fusion.RERANK_CHARS


def p95(xs):
    o = sorted(xs)
    return o[max(0, math.ceil(0.95 * len(o)) - 1)] if o else None


report["summary"] = {"n": len(totals), "p95": p95(totals), "mean": sum(totals) / len(totals),
                     "median": sorted(totals)[len(totals) // 2], "max": max(totals)}
report["stages"] = {k: {"mean": sum(v) / len(totals), "p95": p95(v), "calls_per_query": COUNT[k] / len(totals)}
                    for k, v in TIMES.items()}
stream = io.StringIO()
pstats.Stats(profiler, stream=stream).sort_stats("cumulative").print_stats(45)
stream2 = io.StringIO()
pstats.Stats(profiler, stream=stream2).sort_stats("tottime").print_stats(25)
(work / "profile.json").write_text(json.dumps(report, indent=1))
(work / "cprofile_cum.txt").write_text(stream.getvalue())
(work / "cprofile_tot.txt").write_text(stream2.getvalue())
print(json.dumps({"summary": report["summary"], "stages": report["stages"],
                  "load": [report["load_before"], report["load_after"]]}, indent=1))
