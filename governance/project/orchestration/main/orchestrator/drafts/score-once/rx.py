"""The retrieval survey's variant switch (DAEO-rd0g, DEC-1066 (5)): ``python3 rx.py <gov arguments>`` runs the m1
clone's own ``gov`` with its fusion, its cuts and its rerank swapped in-process by ``GOV_RX`` (a JSON variant); src/
is unchanged. Built on W2-15a's ``modes.py``: the shared reranker service only (never started here, no private
reranker), the shared query embedder only (through the clone's own code).

Two caches make a variant's run cheap and keep it exact (``GOV_RX_CACHE``, a folder):
- the routes' answers (lexical, semantic, the record route's start ids, the closure, the code route, the chunk list),
  keyed by a digest of their arguments: the store is fixed (``28bdbab1``), so each answer is a pure function of them;
- the reranker's scores, keyed by a digest of (question, text): the cross-encoder is pointwise, one score per pair.
Only digests, chunk records and numbers are stored; no question's text is written anywhere by this file.

The variant's keys (all optional; ``{}`` is the shipped path, measured to reproduce m1 exactly):
- ``exclude``: path globs whose chunks no route returns (G4 simulated: lens B's report, the evaluation fixtures);
- ``k``: RRF's k (60); ``w``: {route: weight} (1 each; 0 drops a route);
- ``closure``/``code``: ``set`` (shipped: the unranked set, in path order), ``sem`` (that route's chunks ranked by
  the stored vectors' cosine to the question's vector), ``off``; ``closure_top``/``code_top``: keep its first n;
- ``fuse``: ``rrf`` (shipped) or ``minmax`` (each route's own score min-max normalised, weighted sum; a route with no
  score of its own gets 1 - (rank - 1) / n);
- ``quota``: n: each route's first n hits go first, interleaved by rank (lexical, semantic, closure, code), then the
  fused order; ``quota_routes`` names the routes (default all);
- ``sem_k``/``lex_k``: the semantic and lexical routes' TOP_K (30);
- ``sem_uncut``: true keeps the meaning route's phrasings fused but not cut back to its TOP_K (DEC-1070 (7), L1);
- ``rerank``: false keeps the fused order; ``chars``: the characters of a chunk the reranker reads (500);
- ``depth``: the first n of the fused list are reranked once, globally, and the pages are cut from that order (the
  shipped path reranks each page's 20 apart);
- ``blend``: {"w": a, "k": c}: the final order is by a / (c + rerank rank) + (1 - a) / (c + fused rank);
- ``lift_r``: the authority lift on the rerank score per tier step (1.0); ``lift_f``: on the fused score (0.004);
- ``named``: n: a route ``named`` of the closure's chunks that belong to the records the question names (its
  ticket, its ids, the record route's start ids), ranked by cosine, its first n kept; not fused (weight 0), used
  by ``front`` (routing: a question that names a record is answered first by that record);
- ``front``: {route: n}: after the rerank, that route's first n hits (in its own order) that are in the page go
  first (routing by question type: the code route answers only a question that names a symbol);
- ``pin``: routes whose rank-1 hit is placed at final rank ``pin_at`` (default 3) when it is below it;
- ``dedup``: true drops an item whose lines lie inside an earlier item's of the same file, in each call;
- ``dedup_text``: true drops an item whose text (over 80 characters, whitespace folded) equals an earlier item's in
  any file, in each call (D4B-STRUCTURE E1: generated and copied texts take one place).
``GOV_RX_LOG`` names a file that gets one line per rerank: who scored and how many texts were sent to the service.
LIVE (D4B-SCORE-ONCE §4): ``GOV_RX_RERANK_DIR2``, ``GOV_RX_RERANK_MODEL2`` and ``GOV_RX_LIVE_RULE`` score each pass
with two trial services at once, merged by a ``combine`` rule; see the block after ``combine``.
"""
import fnmatch
import hashlib
import json
import math
import os
from array import array
import pickle
import re
import sqlite3
import sys
from pathlib import Path

from gov import closure as closures
from gov import records
from gov.retrieval import authority, code_route, fusion, graph_route, lexical, semantic
from gov.retrieval import rerank as rr
from gov.retrieval import retrieve as rt

V = json.loads(os.environ.get("GOV_RX") or "{}")
CACHE = Path(os.environ["GOV_RX_CACHE"])
CACHE.mkdir(parents=True, exist_ok=True)
_db = sqlite3.connect(CACHE / "cache.db", timeout=60)
_db.execute("CREATE TABLE IF NOT EXISTS memo (k TEXT PRIMARY KEY, v BLOB)")
_db.execute("CREATE TABLE IF NOT EXISTS score (k TEXT PRIMARY KEY, s REAL)")
STATE = {"query": None, "root": None, "order": None, "chunks": None, "final": {}}
ROUTE_ORDER = ("lexical", "semantic", "closure", "code")


def _key(*parts) -> str:
    return hashlib.sha256(repr(parts).encode()).hexdigest()


def _answered(value) -> bool:
    """A route's answer worth keeping: never an unavailable facet (an embedder or index that did not answer)."""
    if isinstance(value, dict) and value.get("available") is False:
        return False
    if isinstance(value, tuple) and len(value) == 2 and isinstance(value[1], dict) \
            and value[1].get("available") is False:
        return False
    return True


def _memo(name, fn, key_of):
    def wrapped(*a, **kw):
        key = _key(name, *key_of(*a, **kw))
        row = _db.execute("SELECT v FROM memo WHERE k = ?", (key,)).fetchone()
        if row:
            return pickle.loads(row[0])
        value = fn(*a, **kw)
        if not _answered(value):
            return value
        _db.execute("INSERT OR REPLACE INTO memo VALUES (?, ?)", (key, pickle.dumps(value)))
        _db.commit()
        return value
    return wrapped


# ---- the caches of the routes (pure functions of their arguments on the fixed store)
_lex_search, _sem_search = lexical.search, semantic.search


_lex_memo = _memo("lex", _lex_search, lambda r, q, refresh=True: (q, lexical.TOP_K))
_sem_memo = _memo("sem", _sem_search, lambda r, q, refresh=True: (q, semantic.TOP_K, semantic.INSTRUCTION))
_STOP = frozenset("a an the of in on at to for by with from and or is are was were be been do does did which what who "
                  "whom whose where when why how may must can could should would will shall it its this that these "
                  "those there their they them as into about before after than then".split())


def _expanded(root, query: str) -> str:
    """``query`` with the record ids the record route finds in it (a W2 id's ticket, a title's record) appended,
    those it does not already hold (method 5, DEC-1067 (3))."""
    found = graph_route.start_ids(root, query, records.records(root))
    extra = [rid for rid in found if rid not in query]
    return query + (" " + " ".join(extra) if extra else "")


def _phrasings(query: str) -> list[str]:
    """Deterministic phrasings (method 6): the question; its content words (no stopwords, no question mark); and,
    when it names record ids the record route resolves, the question with them (no model call)."""
    words = [w for w in re.findall(r"[\w./-]+", query) if w.lower() not in _STOP]
    out = [query, " ".join(words)]
    if STATE["root"] is not None:
        out.append(_expanded(STATE["root"], query))
    return list(dict.fromkeys(p for p in out if p.strip()))


def _rrf_lists(lists: list[list[dict]], k: float = 60.0) -> list[dict]:
    score, first = {}, {}
    for hits in lists:
        seen = set()
        for rank, h in enumerate(hits, 1):
            if h["chunk_id"] in seen:
                continue
            seen.add(h["chunk_id"])
            score[h["chunk_id"]] = score.get(h["chunk_id"], 0.0) + 1 / (k + rank)
            first.setdefault(h["chunk_id"], h)
    return [first[c] for c in sorted(score, key=lambda c: -score[c])]


def _lex(root, query, refresh=True):
    STATE["query"], STATE["root"] = query, Path(root)
    asked = _expanded(root, query) if V.get("expand") in ("lex", "both") else query
    if not V.get("phrasings"):
        return _lex_memo(root, asked, refresh)
    answers = [_lex_memo(root, p, refresh) for p in _phrasings(query)]
    if not all(a.get("available", True) for a in answers):
        return answers[0]
    return {**answers[0], "ranked": _rrf_lists([a.get("ranked", a["hits"]) for a in answers])}


def _sem(root, query, refresh=True):
    asked = _expanded(root, query) if V.get("expand") in ("sem", "both") else query
    if not V.get("phrasings"):
        return _sem_memo(root, asked, refresh)
    answers = [_sem_memo(root, p, refresh) for p in _phrasings(query)]
    if not all(a.get("available", True) for a in answers):
        return answers[0]
    return {**answers[0], "hits": _rrf_lists([a["hits"] for a in answers])[:semantic.TOP_K]}


lexical.search = _lex
lexical.TOP_K = int(V.get("lex_k", lexical.TOP_K))
semantic.TOP_K = int(V.get("sem_k", semantic.TOP_K))
if V.get("qinstr"):  # method 4: a repository-specific instruction for the query embedder (the query side only)
    semantic.INSTRUCTION = ("Instruct: Given a question about this software repository's code, tickets, decisions, "
                            "contract and plans, retrieve the passage that answers it\nQuery: ")
semantic.search = _sem
_chunks = lexical.chunks
lexical.chunks = lambda root, path=None: (_memo("chunks", _chunks, lambda r, p=None: (p,))(root, path))
graph_route.start_ids = _memo("start", graph_route.start_ids, lambda r, q, known: (q,))
_closure = _memo("closure", closures.closure, lambda r, start, depth: (tuple(start), depth))


def _closure_capture(root, start, depth):
    STATE["start"] = set(start)  # the records the question names: its ticket, its ids, the record route's start ids
    return _closure(root, start, depth)


closures.closure = _closure_capture
code_route.route = _memo("code", code_route.route, lambda r, q, chunks: (q,))
records.records = _memo("records", records.records, lambda r, **kw: (sorted(kw.items()),))
records.edges = _memo("edges", records.edges, lambda r, **kw: (sorted(kw.items()),))
_order = authority.order


def _capture_order(*a, **kw):
    STATE["order"] = _order(*a, **kw)
    return STATE["order"]


authority.order = _capture_order
rt.authority.order = _capture_order

# ---- the reranker: the shared service only, its scores cached by (question, text)
rr._start = lambda *_a, **_k: (_ for _ in ()).throw(ConnectionError("rx: the harness never starts the service"))
rr._started = lambda _interp: (None, None, "rx: the harness allows no private reranker")
# ACT-RERANK-TRIAL-1 4.1 (DEC-1069 (11)-(13)): GOV_RX_RERANK_DIR names the trial service's folder; the client's
# socket, lock and log folder (rr._cache) is that folder for this whole process, so no request reaches the live
# service; an absent trial socket stops the harness at once (no fallback: no start, no private reranker).
TRIAL = os.environ.get("GOV_RX_RERANK_DIR")
if TRIAL:
    if not (Path(TRIAL) / rr.SOCKET).is_socket():
        sys.exit(f"rx: no trial reranker socket at {Path(TRIAL) / rr.SOCKET}: stopped (no fallback to the live "
                 f"service or a private reranker)")
    if not os.environ.get("GOV_RX_RERANK_MODEL"):
        sys.exit("rx: GOV_RX_RERANK_DIR needs GOV_RX_RERANK_MODEL (the trial service's model, for the score cache)")
    rr._cache = lambda: Path(TRIAL)
MODEL = os.environ.get("GOV_RX_RERANK_MODEL") or f"{rr.MODEL}@{rr.REVISION}"
# SCORE-ONCE (DEC-1081 (3), the CTO's copy of f38402a7): GOV_RX_COMBINE replays a declared rule over the scores the
# window kept, one cache per model, and never calls a reranker: {"models": {name: "<model>@<rev>"}, "caches": {name:
# "<folder holding cache.db>"}, "rule": {...}}; see ``combine``. A text one of the rule's models did not score stops
# the run (no fallback, no service).
COMBINE = json.loads(os.environ.get("GOV_RX_COMBINE") or "null")
if COMBINE and TRIAL:
    sys.exit("rx: GOV_RX_COMBINE replays kept scores and calls no reranker: not with GOV_RX_RERANK_DIR")
_db.execute("CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)")
if not COMBINE:
    _held = _db.execute("SELECT v FROM meta WHERE k = 'rerank_model'").fetchone()
    if _held and _held[0] != MODEL:
        sys.exit(f"rx: the cache {CACHE} holds the scores of {_held[0]}, not {MODEL}: refused (use a fresh "
                 f"GOV_RX_CACHE)")
    _db.execute("INSERT OR REPLACE INTO meta VALUES ('rerank_model', ?)", (MODEL,))
    _db.commit()
_service = None if COMBINE else rr.default_reranker()


def _mm(values: list[float]) -> list[float]:
    """Min-max over one pass's list; all equal: 1.0 each (as ``_fuse``)."""
    lo, hi = (min(values), max(values)) if values else (0.0, 1.0)
    return [(v - lo) / (hi - lo) if hi > lo else 1.0 for v in values]


def rule_models(rule: dict) -> list[str]:
    kind = rule["kind"]
    names = {"alone": [rule.get("m")], "by_type": [rule.get("code"), rule.get("other")],
             "cascade": [rule.get("first"), rule.get("second")], "merge": [rule.get("a"), rule.get("b")]}.get(kind)
    if names is None or not all(names):
        raise ValueError(f"rx: an unknown or incomplete rule {rule}")
    return list(dict.fromkeys(names))


def combine(rule: dict, by_model: dict, is_code: bool) -> list[float]:
    """One pass's scores, in the texts' order, from each model's raw scores of the same texts (DEC-1081 (3)):
    - ``alone`` {m}: m's raw scores, as its own run;
    - ``by_type`` {code, other}: the ``code`` model's raw scores for a question the code route answers (it names a
      symbol the code graph holds: the product's own test, ``routing``), the ``other``'s for the rest;
    - ``cascade`` {first, top, second}: ``first`` orders the list; its first ``top`` (ties in the given order) are
      ordered by ``second``, min-max within them into [0.5, 1]; the rest keep ``first``'s order, min-max within them
      into [0, 0.4995]; so the head stays ahead of the rest before the lift;
    - ``merge`` {a, b, w (0.5)}: w x min-max(a) + (1 - w) x min-max(b) over the pass."""
    kind = rule["kind"]
    if kind == "alone":
        return [float(s) for s in by_model[rule["m"]]]
    if kind == "by_type":
        return [float(s) for s in by_model[rule["code"] if is_code else rule["other"]]]
    if kind == "cascade":
        a, b, n = by_model[rule["first"]], by_model[rule["second"]], int(rule["top"])
        order = sorted(range(len(a)), key=lambda i: (-a[i], i))
        head, rest = order[:n], order[n:]
        out = [0.0] * len(a)
        for i, v in zip(head, _mm([b[i] for i in head])):
            out[i] = 0.5 + 0.5 * v
        for i, v in zip(rest, _mm([a[i] for i in rest])):
            out[i] = 0.4995 * v
        return out
    if kind == "merge":
        w = float(rule.get("w", 0.5))
        return [w * x + (1 - w) * y for x, y in zip(_mm(by_model[rule["a"]]), _mm(by_model[rule["b"]]))]
    raise ValueError(f"rx: unknown rule kind {kind}")


_combine_db = {}
if COMBINE:
    if any(Path(c).resolve() == CACHE.resolve() for c in COMBINE["caches"].values()):
        sys.exit("rx: a replay's GOV_RX_CACHE must not be one of the kept caches it reads: refused")
    for _name in rule_models(COMBINE["rule"]):
        _combine_db[_name] = sqlite3.connect(f"file:{Path(COMBINE['caches'][_name]) / 'cache.db'}?mode=ro", uri=True)
        # a model's own cache marks it ``rerank_model``; a live two-model cache also marks ``rerank_model2`` (LIVE)
        _rows = [r[0] for r in _combine_db[_name].execute(
            "SELECT v FROM meta WHERE k IN ('rerank_model', 'rerank_model2') ORDER BY k").fetchall()]
        if COMBINE["models"][_name] not in _rows:
            sys.exit(f"rx: the cache for {_name} holds {_rows[0] if _rows else None}, not {COMBINE['models'][_name]}: "
                     f"refused")

# LIVE (D4B-SCORE-ONCE §4: a two-model cell measured as it would run, both models loaded). GOV_RX_RERANK_DIR2 names a
# second trial service's folder and GOV_RX_RERANK_MODEL2 its model; with GOV_RX_LIVE_RULE, a ``combine`` rule over
# the names "one" (GOV_RX_RERANK_DIR's service, GOV_RX_RERANK_MODEL) and "two" (GOV_RX_RERANK_DIR2's), ``scores``
# asks the services the rule names for the same texts, each in its own request bounds (one: GOV_RX_BATCH,
# GOV_RX_REQUEST_CHARS, GOV_RX_MODEL_CUT; two: GOV_RX_BATCH2, GOV_RX_REQUEST_CHARS2, GOV_RX_MODEL_CUT2), and returns
# the rule's scores. Each model's scores are kept under its own key, as a single model's, in this one cache (marked
# ``rerank_model`` and ``rerank_model2``), so a live run replays with GOV_RX_COMBINE ({"models": {"one": MODEL,
# "two": MODEL2}, "caches": {"one": C, "two": C}}). Every request is the product client's (connect within 2 s, the
# answer within GOV_RERANK_TIMEOUT_S, 30 s) to that folder's socket only: never a start, never a fallback; a missing,
# silent or failing service stops the run. GOV_RX_LIVE_PARALLEL=1 asks the two services at once (default: one, then
# two). Per request: ``LIVE<TAB>name<TAB>seconds`` and ``LIVEGPU<TAB>name<TAB>seconds`` (the harness's GPU read).
# All four unset: nothing here acts and nothing above changes.
TRIAL2 = os.environ.get("GOV_RX_RERANK_DIR2")
LIVE = None
if TRIAL2 or os.environ.get("GOV_RX_LIVE_RULE") or os.environ.get("GOV_RX_RERANK_MODEL2"):
    if not (TRIAL and TRIAL2 and os.environ.get("GOV_RX_LIVE_RULE") and os.environ.get("GOV_RX_RERANK_MODEL2")):
        sys.exit("rx: the live two-model mode needs GOV_RX_RERANK_DIR, GOV_RX_RERANK_MODEL, GOV_RX_RERANK_DIR2, "
                 "GOV_RX_RERANK_MODEL2 and GOV_RX_LIVE_RULE together: refused")
    if Path(TRIAL2).resolve() == Path(TRIAL).resolve():
        sys.exit("rx: GOV_RX_RERANK_DIR2 is GOV_RX_RERANK_DIR: two services, two folders: refused")
    if not (Path(TRIAL2) / rr.SOCKET).is_socket():
        sys.exit(f"rx: no trial reranker socket at {Path(TRIAL2) / rr.SOCKET}: stopped (no fallback to the live "
                 f"service or a private reranker)")
    MODEL2 = os.environ["GOV_RX_RERANK_MODEL2"]
    if MODEL2 == MODEL:
        sys.exit("rx: GOV_RX_RERANK_MODEL2 is GOV_RX_RERANK_MODEL: the two scores would share one key: refused")
    try:
        _live_rule = json.loads(os.environ["GOV_RX_LIVE_RULE"])
        _live_names = rule_models(_live_rule)
    except (ValueError, KeyError, TypeError, AttributeError) as _error:
        sys.exit(f"rx: GOV_RX_LIVE_RULE is not a rule ({_error}): refused")
    if not set(_live_names) <= {"one", "two"}:
        sys.exit(f"rx: GOV_RX_LIVE_RULE names {_live_names}; the live models are 'one' and 'two': refused")
    _held2 = _db.execute("SELECT v FROM meta WHERE k = 'rerank_model2'").fetchone()
    if _held2 and _held2[0] != MODEL2:
        sys.exit(f"rx: the cache {CACHE} holds the scores of {_held2[0]} as its second model, not {MODEL2}: refused "
                 f"(use a fresh GOV_RX_CACHE)")
    _db.execute("INSERT OR REPLACE INTO meta VALUES ('rerank_model2', ?)", (MODEL2,))
    _db.commit()
    LIVE = {"rule": _live_rule, "names": _live_names, "parallel": os.environ.get("GOV_RX_LIVE_PARALLEL") == "1",
            "one": {"dir": TRIAL, "model": MODEL, "cut": int(os.environ.get("GOV_RX_MODEL_CUT", "0"))},
            "two": {"dir": TRIAL2, "model": MODEL2, "cut": int(os.environ.get("GOV_RX_MODEL_CUT2", "0"))}}


def _live_bounds(name: str) -> tuple[int, int]:
    """The request bounds of a live model: one's are BATCH and REQUEST_CHARS, two's BATCH2 and REQUEST_CHARS2."""
    if name == "one":
        return BATCH, REQUEST_CHARS
    return BATCH2, REQUEST_CHARS2


def _ask_live(folder: str, query: str, texts: list[str]) -> list[float]:
    """One request to the trial service at ``folder``'s socket, as the product's client asks (``rr._ask``: connect
    within ``rr.CONNECT_S``, the answer within GOV_RERANK_TIMEOUT_S, 30 s by default); never a start, never a
    fallback: any failure raises."""
    import socket
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
        conn.settimeout(rr.CONNECT_S)
        conn.connect(str(Path(folder) / rr.SOCKET))
        conn.settimeout(float(os.environ.get("GOV_RERANK_TIMEOUT_S", "30")))
        conn.sendall((json.dumps([query, texts]) + "\n").encode())
        line = conn.makefile("rb").readline()
    if not line:
        raise ConnectionError("the service closed the connection without an answer")
    answer = json.loads(line)
    if "error" in answer:
        raise RuntimeError(f"the service refused the request: {answer['error']}")
    if not isinstance(answer.get("scores"), list) or len(answer["scores"]) != len(texts):
        raise ValueError("the service's answer does not match the request")
    return [float(s) for s in answer["scores"]]


def _live_fetch(name: str, query: str, asked: list[str]) -> list[float]:
    """Model ``name``'s scores of ``asked`` (texts not in the cache), in their order, in its own request bounds;
    a request that fails stops the run (in a thread too: the SystemExit reaches the caller through its future)."""
    import time
    svc = LIVE[name]
    batch, chars = _live_bounds(name)
    cut = sum(1 for t in asked if len(t) > chars)
    if cut:
        _log(f"TRUNC\t{cut}\t{chars}\t{name}")
    if svc["cut"] and any(len(t) > svc["cut"] for t in asked):
        _log(f"MODELCUT\t{sum(1 for t in asked if len(t) > svc['cut'])}\t{svc['cut']}\t{name}")
    got: list = [None] * len(asked)
    for order in _requests(asked, batch, chars):
        t0 = time.monotonic()
        _gpu_wait()
        t1 = time.monotonic()
        _log(f"LIVEGPU\t{name}\t{t1 - t0:.3f}")
        try:
            part = _ask_live(svc["dir"], query, [asked[j][:chars] for j in order])
        except Exception as error:  # missing, silent (past the answer timeout), refusing or garbled: stop loudly
            _log(f"LIVEFAIL\t{name}\t{type(error).__name__}: {error}")
            sys.exit(f"rx: the trial reranker '{name}' at {svc['dir']} did not score ({type(error).__name__}: "
                     f"{error}): stopped")
        _log(f"LIVE\t{name}\t{time.monotonic() - t1:.3f}")
        for j, value in zip(order, part):  # each score back at its text's place: the unbatched order
            got[j] = value
    return got


def _live_scores(query: str, texts: list[str]) -> list[float]:
    """LIVE: the rule's scores of ``texts``, each named model's own scores from this cache or its service."""
    import time
    t0 = time.monotonic()
    plan = {}
    for name in LIVE["names"]:  # the cache is read and written in this thread only (sqlite's own rule)
        keys = [_key("rr", LIVE[name]["model"], query, t) for t in texts]
        have = {}
        for i in range(0, len(keys), 500):
            part = keys[i:i + 500]
            have.update(_db.execute(f"SELECT k, s FROM score WHERE k IN ({','.join('?' * len(part))})",
                                    part).fetchall())
        plan[name] = (keys, have, [i for i, k in enumerate(keys) if k not in have])
    asking = [n for n in LIVE["names"] if plan[n][2]]
    if LIVE["parallel"] and len(asking) > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(len(asking)) as pool:
            futures = {n: pool.submit(_live_fetch, n, query, [texts[i] for i in plan[n][2]]) for n in asking}
            fetched = {n: f.result() for n, f in futures.items()}
    else:
        fetched = {n: _live_fetch(n, query, [texts[i] for i in plan[n][2]]) for n in asking}
    by_model = {}
    for name in LIVE["names"]:
        keys, have, missing = plan[name]
        for i, s in zip(missing, fetched.get(name, [])):
            have[keys[i]] = float(s)
            _db.execute("INSERT OR REPLACE INTO score VALUES (?, ?)", (keys[i], float(s)))
        by_model[name] = [have[k] for k in keys]
    _db.commit()
    _log("live\t" + "\t".join(f"{n}:{len(texts)}:{len(plan[n][2])}" for n in LIVE["names"])
         + f"\t{time.monotonic() - t0:.3f}")
    return combine(LIVE["rule"], by_model, bool((STATE.get("routes") or {}).get("code")))


def _kept(name: str, query: str, texts: list[str]) -> list[float]:
    """The model's kept scores of ``texts``; a text the window did not score stops the run (any call: within one
    variant a follow-up call reranks the same fused head as the first, so a missing text is a fault, never filled)."""
    keys = [_key("rr", COMBINE["models"][name], query, t) for t in texts]
    have = {}
    for i in range(0, len(keys), 500):
        part = keys[i:i + 500]
        have.update(_combine_db[name].execute(f"SELECT k, s FROM score WHERE k IN ({','.join('?' * len(part))})",
                                              part).fetchall())
    missing = sum(1 for k in keys if k not in have)
    if missing:
        sys.exit(f"rx: {missing} of {len(keys)} texts were not scored by {name} in the window: stopped")
    return [have[k] for k in keys]


def scores(query: str, texts: list[str]) -> list[float] | None:
    if COMBINE:
        rule = COMBINE["rule"]
        by_model = {name: _kept(name, query, texts) for name in rule_models(rule)}
        _log(f"combine\t{rule['kind']}\t{len(texts)}")
        return combine(rule, by_model, bool((STATE.get("routes") or {}).get("code")))
    if LIVE:
        return _live_scores(query, texts)
    keys = [_key("rr", MODEL, query, t) for t in texts]
    have = {}
    for i in range(0, len(keys), 500):
        part = keys[i:i + 500]
        have.update(_db.execute(f"SELECT k, s FROM score WHERE k IN ({','.join('?' * len(part))})", part).fetchall())
    missing = [i for i, k in enumerate(keys) if k not in have]
    by = "cache"
    if missing:
        asked = [texts[i] for i in missing]
        cut = sum(1 for t in asked if len(t) > REQUEST_CHARS)
        if cut:  # SCORE-ONCE: a text read only up to the request bound is counted, never silent
            _log(f"TRUNC\t{cut}\t{REQUEST_CHARS}")
        model_cut = int(os.environ.get("GOV_RX_MODEL_CUT", "0"))  # the model's own cut (zerank: 10,000 characters)
        if model_cut and any(len(t) > model_cut for t in asked):
            _log(f"MODELCUT\t{sum(1 for t in asked if len(t) > model_cut)}\t{model_cut}")
        got = [None] * len(asked)
        for order in _requests(asked):  # the CTO's limit (05:45): count x longest text <= REQUEST_CHARS, <= 16
            _gpu_wait()
            part = _service(query, [asked[j][:REQUEST_CHARS] for j in order]) if _service else None
            by = rr.last_outcome()["by"]
            if part is None or by != "service" or len(part) != len(order):
                _log(f"UNSCORED\t{by}\t{len(missing)}")
                if TRIAL:  # the trial service did not answer: stop loudly, never rank on without it
                    sys.exit(f"rx: the trial reranker at {TRIAL} did not score ({rr.last_outcome().get('reason')}): "
                             f"stopped")
                return None
            for j, value in zip(order, part):  # each score back at its text's place: the unbatched order
                got[j] = value
        for i, s in zip(missing, got):
            have[keys[i]] = float(s)
            _db.execute("INSERT OR REPLACE INTO score VALUES (?, ?)", (keys[i], float(s)))
        _db.commit()
    _log(f"{by}\t{len(texts)}\t{len(missing)}")
    return [have[k] for k in keys]


# texts per request to the shared service: the product's cap (DEC-1067 (f)); SCORE-ONCE: GOV_RX_BATCH and
# GOV_RX_REQUEST_CHARS narrow them for one model's window run (the 4B: 8 and 12,000, DEC-1079 (a))
BATCH = int(os.environ.get("GOV_RX_BATCH", "16"))
REQUEST_CHARS = int(os.environ.get("GOV_RX_REQUEST_CHARS", "24000"))  # the CTO's limit (2026-11-04 04:02)
# LIVE: the second service's own bounds and model cut (gte and zerank: 16 and 24,000, the defaults)
BATCH2 = int(os.environ.get("GOV_RX_BATCH2", "16"))
REQUEST_CHARS2 = int(os.environ.get("GOV_RX_REQUEST_CHARS2", "24000"))
GPU_LIMIT_MIB = 15000  # the CTO's wait line (04:02), a margin below the backstop's 15,872: nothing sent at or above


def _requests(texts: list[str], batch: int | None = None, chars: int | None = None) -> list[list[int]]:
    """The requests for ``texts`` as lists of their indexes: every request at most BATCH texts and at most
    REQUEST_CHARS by count x its longest text (the reranker pads each text to the longest in its batch; the CTO's
    limit, 2026-11-04 05:45), fewest requests (longest first, each request filled while the bound holds). A text
    above the budget is read up to it (REQUEST_CHARS characters) and goes alone. The caller puts each score back at
    its index, so the scores come in the unbatched order. LIVE: ``batch`` and ``chars`` give another model's own
    bounds (unset: BATCH and REQUEST_CHARS, as before)."""
    batch = BATCH if batch is None else int(batch)
    chars = REQUEST_CHARS if chars is None else int(chars)
    lengths = [min(len(t), chars) for t in texts]
    out: list[list[int]] = []
    for i in sorted(range(len(texts)), key=lambda i: (-lengths[i], i)):
        if out and len(out[-1]) < batch and (len(out[-1]) + 1) * max(lengths[out[-1][0]], 1) <= chars:
            out[-1].append(i)  # longest first: the request's first text is its longest
        else:
            out.append([i])
    return out


def _gpu_used() -> int | None:
    import subprocess
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=10).stdout
        return int(out.split()[0])
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        return None


FLAG = "/tmp/gov-os-research-wait.flag"  # the CTO's handshake (04:20): touched here, removed by the CTO's watcher


def _gpu_wait() -> None:
    """Before every request to the shared reranker: reads the GPU's memory (one GPU line per request in the run's
    log); at or above the line, sends nothing, touches the CTO's flag and waits until the watcher removes it (it
    restarts the shared reranker, class 3), then goes on. Each wait and reset is a line in ``gpu-waits.txt``."""
    import time
    used = _gpu_used()
    _log(f"GPU\t{used} MiB before a request")
    stop = os.environ.get("GOV_RX_GPU_LIMIT_MIB")
    if stop:  # ACT-RERANK-TRIAL-1: at or above the limit (or unreadable) the run stops; it never waits for a reset
        if used is None or used >= int(stop):
            _gpulog(f"STOP\tgpu {used} MiB at or above GOV_RX_GPU_LIMIT_MIB {stop} before a request: the run stops")
            sys.exit(f"rx: GPU at {used} MiB, at or above GOV_RX_GPU_LIMIT_MIB {stop}: stopped before the request")
        return
    if used is None or used < GPU_LIMIT_MIB:
        return
    t0 = time.time()
    Path(FLAG).touch()
    _gpulog(f"WAIT\tgpu {used} MiB at or above {GPU_LIMIT_MIB}: flag touched, nothing sent")
    while os.path.exists(FLAG):
        time.sleep(5)
    used = _gpu_used()
    _gpulog(f"RESET\tflag removed after {time.time() - t0:.0f} s; gpu {used} MiB; going on")
    _log(f"WAIT\t{time.time() - t0:.0f} s for the CTO's reset, then {used} MiB")


def _gpulog(line: str) -> None:
    import time
    if os.environ.get("GOV_RX_GPULOG"):
        with open(os.environ["GOV_RX_GPULOG"], "a", encoding="utf-8") as out:
            out.write(f"{os.environ.get('GOV_RX_NAME', '')} {time.strftime('%H:%M:%S')} {line}\n")


def _log(line: str) -> None:
    if os.environ.get("GOV_RX_LOG"):
        with open(os.environ["GOV_RX_LOG"], "a", encoding="utf-8") as log:
            log.write(line + "\n")


CHARS = int(V.get("chars", rt.RERANK_CHARS))
rt.RERANK_CHARS = CHARS
_files: dict[str, list[bytes]] = {}


def _text(chunk: dict) -> str:
    rel = chunk["path"]
    if rel not in _files:
        _files[rel] = (STATE["root"] / rel).read_bytes().splitlines(keepends=True)
    body = b"".join(_files[rel][chunk["start_line"] - 1:chunk["end_line"]])
    return _decorate(chunk, f"[path: {rel}]\n{body.decode('utf-8', 'replace')[:CHARS]}")


_MD_HEAD = re.compile(r"(#{1,6})\s+(.*\S)")
_PY_HEAD = re.compile(r"(\s*)(?:async\s+)?(def|class)\s+(\w+)")
_FRONT_TITLE = re.compile(r"^title:\s*['\"]?(.*?)['\"]?\s*$", re.MULTILINE)
_heads: dict[str, list] = {}
_titles: dict[str, str | None] = {}


def _section(rel: str, line: int) -> str | None:
    """The heading path above ``line``: Markdown headings (H1 > H2 > ...), or a Python file's enclosing class and
    def; None for other files or none found."""
    if rel not in _heads:
        lines = (STATE["root"] / rel).read_text(encoding="utf-8", errors="replace").splitlines()
        found = []
        if rel.endswith(".md"):
            fence = False
            for n, text in enumerate(lines, 1):
                if text.startswith("```"):
                    fence = not fence
                m = None if fence else _MD_HEAD.match(text)
                if m:
                    found.append((n, len(m.group(1)), m.group(2)[:120]))
        elif rel.endswith(".py"):
            for n, text in enumerate(lines, 1):
                m = _PY_HEAD.match(text)
                if m:
                    found.append((n, len(m.group(1)) // 4 + 1, f"{m.group(2)} {m.group(3)}"))
        _heads[rel] = found
    stack: list[tuple[int, str]] = []
    for n, level, title in _heads[rel]:
        if n > line:
            break
        stack = [s for s in stack if s[0] < level] + [(level, title)]
    return " > ".join(t for _, t in stack) or None


def _title(chunk: dict) -> str | None:
    order, rel = STATE["order"], chunk["path"]
    if order is not None and rel == order.register:
        return ((order.entry_of(rel, chunk["start_line"]) or {}).get("title"))
    if rel not in _titles:
        head = (STATE["root"] / rel).read_text(encoding="utf-8", errors="replace")[:4000]
        m = _FRONT_TITLE.search(head.split("\n---", 2)[1]) if head.startswith("---") and "\n---" in head[3:] else None
        _titles[rel] = m.group(1) if m else None
    return _titles[rel]


def _decorate(chunk: dict, text: str) -> str:
    """Method 3: the reranker's text with the chunk's record title and section beside its path (``decorate``)."""
    if not V.get("decorate"):
        return text
    first, _, rest = text.partition("\n")
    where = (STATE["chunks"] or {}).get(chunk.get("chunk_id"), chunk)
    extra = []
    try:
        title, section = _title(where), _section(where["path"], where["start_line"])
    except (OSError, KeyError, TypeError):
        title = section = None
    if title:
        extra.append(f"[title: {title}]")
    if section:
        extra.append(f"[section: {section}]")
    return "\n".join([first, *extra, rest])


# ---- the fusion
_rrf = rt.rrf
EXCLUDE = V.get("exclude", [])


def _excluded(path: str) -> bool:
    return any(fnmatch.fnmatch(path, glob) for glob in EXCLUDE)


def _sem_rank(hits: list[dict]) -> list[dict]:
    """``hits`` ranked by the cosine of their stored vectors to the question's (unembedded chunks last)."""
    ids = [h["chunk_id"] for h in hits]
    key = _key("semrank", STATE["query"], tuple(ids))
    row = _db.execute("SELECT v FROM memo WHERE k = ?", (key,)).fetchone()
    if row:
        dist = pickle.loads(row[0])
    else:
        vector, _reason = semantic.query_vector(STATE["root"], STATE["query"])
        dist = {}
        if vector is not None:  # the cosine distance, as sqlite_vec's vec_distance_cosine, over the stored float32s
            q = array("f", vector)
            qn = math.sqrt(sum(x * x for x in q)) or 1.0
            conn = semantic._open(STATE["root"])
            try:
                for i in range(0, len(ids), 500):
                    part = ids[i:i + 500]
                    for cid, blob in conn.execute(f"SELECT chunk_id, embedding FROM semantic_vector "
                                                  f"WHERE chunk_id IN ({','.join('?' * len(part))})", part):
                        v = array("f", blob)
                        vn = math.sqrt(sum(x * x for x in v)) or 1.0
                        dist[cid] = 1.0 - sum(a * b for a, b in zip(q, v)) / (qn * vn)
            finally:
                conn.close()
        _db.execute("INSERT OR REPLACE INTO memo VALUES (?, ?)", (key, pickle.dumps(dist)))
        _db.commit()
    ranked = sorted(hits, key=lambda h: (dist.get(h["chunk_id"], 9.0), ids.index(h["chunk_id"])))
    return [{**h, "distance": dist.get(h["chunk_id"])} for h in ranked]


def _named(closure_hits: list[dict]) -> list[dict]:
    """The closure's chunks that belong to a record the question names (not to a record reached from it), ranked
    by their vectors' cosine to the question: a register chunk by its entry, any other by its file's record."""
    order, start = STATE["order"], STATE.get("start") or set()
    if order is None or not start:
        return []
    path_id = {r["path"]: r["id"] for r in records.records(STATE["root"]) if r.get("span") is None}
    own = []
    for h in closure_hits:
        chunk = (STATE["chunks"] or {}).get(h["chunk_id"], h)
        rid = ((order.entry_of(chunk["path"], chunk["start_line"]) or {}).get("id") if chunk["path"] == order.register
               else path_id.get(chunk["path"]))
        if rid in start:
            own.append(h)
    if own and V.get("named_by") == "rr":  # the reranker picks the named record's best chunks (whole chunks read)
        got = scores(_rquery(STATE["query"]), [_text((STATE["chunks"] or {}).get(h["chunk_id"], h)) for h in own])
        if got is not None:
            return [h for _, _, h in sorted(zip(got, range(len(own)), own), key=lambda t: (-t[0], t[1]))]
    return _sem_rank(own) if own else []


def _prepare(routes: dict) -> dict:
    out = {}
    if V.get("named") and routes.get("closure"):
        named = _named([h for h in routes["closure"] if not _excluded(h["path"])])
        if named:
            out["named"] = named[:int(V["named"])]  # a route of its own: weight 0 in the fusion, used by ``front``
    for name, hits in routes.items():
        hits = [h for h in hits if not _excluded(h["path"])]
        mode = V.get(name, "set") if name in ("closure", "code") else None
        if mode == "off" or float(V.get("w", {}).get(name, 1.0)) == 0:
            continue
        if mode == "sem":
            hits = _sem_rank(hits)
        top = V.get(f"{name}_top")
        if top is not None:
            hits = hits[:int(top)]
        out[name] = hits
    return out


def _own_score(name: str, hit: dict, rank: int, n: int) -> float | None:
    if name == "semantic" or (name in ("closure", "code") and hit.get("distance") is not None):
        return 1.0 - float(hit["distance"])
    if name == "lexical" and hit.get("bm25") is not None:
        return -float(hit["bm25"]) + (1000.0 if hit.get("exact") else 0.0)
    return None


def _fuse(routes: dict) -> list[dict]:
    weights, k = V.get("w", {}), float(V.get("k", fusion.RRF_K))
    fused: dict[str, dict] = {}
    for name, hits in routes.items():
        uniq: dict[str, dict] = {}
        for hit in hits:
            uniq.setdefault(hit["chunk_id"], hit)
        items = list(uniq.items())
        w = float(weights.get(name, 0.0 if name == "named" else 1.0))
        if w == 0:
            continue
        if V.get("fuse", "rrf") == "minmax":
            raw = [_own_score(name, h, r, len(items)) for r, (_, h) in enumerate(items, 1)]
            if any(s is None for s in raw):
                raw = [1.0 - (r - 1) / max(len(items), 1) for r in range(1, len(items) + 1)]
            lo, hi = (min(raw), max(raw)) if raw else (0, 1)
            norm = [(s - lo) / (hi - lo) if hi > lo else 1.0 for s in raw]
        else:
            norm = [1 / (k + r) for r in range(1, len(items) + 1)]
        for (cid, hit), s in zip(items, norm):
            entry = fused.setdefault(cid, {**hit, "score": 0.0, "routes": []})
            entry["score"] += w * s
            entry["routes"].append(name)
    return sorted(fused.values(), key=lambda e: -e["score"])


def _lift(hits: list[dict], score: str, lift: float) -> list[dict]:
    order = STATE["order"]
    if order is None or order.block is None or lift == 0:
        return sorted(hits, key=lambda h: -h[score])
    chunks = STATE["chunks"] or {}

    def adjusted(h):
        where = chunks.get(h["chunk_id"], h)
        return h[score] + lift * order.steps(where["path"], where.get("start_line"))
    return sorted(hits, key=lambda h: -adjusted(h))


def _steps(h) -> int:
    order = STATE["order"]
    if order is None or order.block is None:
        return 0
    where = (STATE["chunks"] or {}).get(h["chunk_id"], h)
    return order.steps(where["path"], where.get("start_line"))


def _quota(fused: list[dict], routes: dict) -> list[dict]:
    n = int(V["quota"])
    names = [r for r in ROUTE_ORDER if r in routes and r in V.get("quota_routes", ROUTE_ORDER)]
    by_id = {e["chunk_id"]: e for e in fused}
    head, seen = [], set()
    for rank in range(n):
        for name in names:
            uniq = list(dict.fromkeys(h["chunk_id"] for h in routes[name]))
            if rank < len(uniq) and uniq[rank] not in seen:
                seen.add(uniq[rank])
                head.append(by_id[uniq[rank]])
    return head + [e for e in fused if e["chunk_id"] not in seen]


CUSTOM = bool(set(V) - {"exclude", "chars", "sem_k", "lex_k", "sem_uncut"}) or bool(EXCLUDE)

# DEC-1070 (7), lever L1: the product fuses the meaning route's phrasings and cuts the fused list to semantic.TOP_K
# (retrieve._phrased's cut); ``sem_uncut`` keeps every phrasing's hits, fused, uncut. The product's own fusion stays.
_phrased = rt._phrased


def _phrased_rx(search, root, asked, key, cut=None):
    return _phrased(search, root, asked, key, cut=None if V.get("sem_uncut") else cut)


rt._phrased = _phrased_rx


def _rerank_text() -> str:
    """The text the depth rerank is given. Default (as every v456 figure was measured): ``STATE["query"]``, which on
    a tree with ``routing.phrasings`` is the last phrasing the lexical route was asked (L5's finding, a5c0c34f).
    SCORE-ONCE: ``"rq": "question"`` gives the question as retrieve was asked it, as the product's page rerank does
    (``gov retrieve`` passes it on a continuation too); a call with no question at all keeps the default."""
    if V.get("rq") == "question" and STATE.get("question"):
        return STATE["question"]
    return STATE["query"]


def _fusion(routes: dict, **kw) -> list[dict]:
    STATE["routes"] = routes = _prepare(routes)
    if not CUSTOM:
        return _rrf(routes, **kw)
    fused = _fuse(routes)
    fused = _lift(fused, "score", float(V.get("lift_f", 0.004)))
    if "quota" in V:
        fused = _quota(fused, routes)
    depth = V.get("depth")
    final = {}
    if depth and V.get("rerank", True):
        head = [h for h in fused[:int(depth)] if STATE["chunks"] and h["chunk_id"] in STATE["chunks"]]
        got = scores(_rquery(_rerank_text()), [_text(STATE["chunks"][h["chunk_id"]]) for h in head]) if head else None
        if got is not None:
            order = _final(head, got)
            final = {cid: -i for i, cid in enumerate(order)}
            ids = set(order)
            fused = [h for cid in order for h in head if h["chunk_id"] == cid] + \
                    [h for h in fused if h["chunk_id"] not in ids]
    STATE["final"] = final
    # the shipped Order.fused lift is applied here already; give a score that keeps this order under its lift
    n = len(fused)
    return [{**h, "score": float(n - i)} for i, h in enumerate(fused)]


def _final(cands: list[dict], raw: list[float]) -> list[str]:
    """The chunk ids of ``cands`` (in fused order) in their final order: rerank score with the authority lift,
    blended with the fused rank, pins applied."""
    lift_r = float(V.get("lift_r", 1.0))
    agree = float(V.get("agree", 0))  # method 7: route agreement added to the score, per route beyond the first
    if COMBINE and raw:  # SCORE-ONCE L3: each pass's raw range, logged, to set the normalised lift from the baseline
        _log(f"RANGE\t{max(raw) - min(raw):.6f}\t{len(raw)}")
    base = raw
    if V.get("lift_norm") is not None:  # SCORE-ONCE L3: the lift on the pass's min-max normalised score, the same step
        base, lift_r = _mm(list(raw)), float(V["lift_norm"])  # for every model and cell
    z = [s + lift_r * _steps(c) + agree * max(0, len(c.get("routes") or []) - 1) for s, c in zip(base, cands)]
    # as the shipped path: by the raw score (ties in the order given), then stably by the lifted score (bf16 ties)
    by_rerank = sorted(sorted(range(len(cands)), key=lambda i: -raw[i]), key=lambda i: -z[i])
    blend = V.get("blend")
    if blend:
        a, c = float(blend.get("w", 0.5)), float(blend.get("k", 10))
        rpos = {i: r for r, i in enumerate(by_rerank, 1)}
        val = [a / (c + rpos[i]) + (1 - a) / (c + i + 1) for i in range(len(cands))]
        by_final = sorted(range(len(cands)), key=lambda i: -val[i])
    else:
        by_final = by_rerank
    ids = [cands[i]["chunk_id"] for i in by_final]
    for name, n in reversed(list(V.get("front", {}).items())):  # a route's first n hits ahead, in its own order
        firsts = [h["chunk_id"] for h in (STATE["routes"].get(name) or [])]
        firsts = [cid for cid in list(dict.fromkeys(firsts))[:int(n)] if cid in ids]
        ids = firsts + [cid for cid in ids if cid not in firsts]
    for name in V.get("pin", []):
        hits = STATE["routes"].get(name) or []
        if not hits:
            continue
        top = hits[0]["chunk_id"]
        at = int(V.get("pin_at", 3))
        if top in ids and ids.index(top) >= at:
            ids.remove(top)
            ids.insert(at - 1, top)
    cap = V.get("perfile")  # method 8: at most n chunks of one file in the first 10; the rest after them
    if cap:
        head, rest, per = [], [], {}
        path_of = {c["chunk_id"]: c["path"] for c in cands}
        for cid in ids:
            p = path_of.get(cid)
            if len(head) < 10 and per.get(p, 0) < int(cap):
                head.append(cid)
                per[p] = per.get(p, 0) + 1
            else:
                rest.append(cid)
        ids = head + rest
    return ids


rt.rrf = _fusion


def _rquery(query: str) -> str:
    """Method 4, the reranker's side: the service's prompt is fixed (the model card's web-search instruction), so a
    repository-specific instruction is given at query time, in the model's own template words, before the query."""
    if not V.get("rinstr"):
        return query
    return ("<Instruct>: Given a question about this software repository, judge whether the passage (code, ticket, "
            "decision, contract or plan) states the answer\n<Query>: " + query)


def _rerank(query, candidates, reranker=None):
    cands = [dict(c) for c in candidates]
    if not V.get("rerank", True) or not cands:
        rr._note("unavailable", None, "rx: no rerank in this variant")
        return cands
    if STATE["final"]:  # reranked globally already: this page in that order
        known = STATE["final"]
        rr._note("service", "cache", None)
        out = sorted(cands, key=lambda c: -known.get(c["chunk_id"], -10 ** 9))
        return [{**c, "rerank_score": float(known.get(c["chunk_id"], -10 ** 9))} for c in out]
    got = scores(_rquery(query), [_decorate(c, c["text"]) for c in cands])
    if got is None:
        rr._note("unavailable", None, "rx: the service did not score")
        return cands
    rr._note("service", "cache", None)
    if not CUSTOM:  # the shipped order: by score, ties in the order given; Order.reranked lifts after
        ranked = sorted(zip(got, cands), key=lambda p: -p[0])
        return [{**c, "rerank_score": s} for s, c in ranked]
    order = _final(cands, got)
    pos = {cid: i for i, cid in enumerate(order)}
    out = sorted(cands, key=lambda c: pos[c["chunk_id"]])
    return [{**c, "rerank_score": float(len(out) - i)} for i, c in enumerate(out)]


rt.rerank = _rerank
if CUSTOM:  # the lifts are this file's, inside _fusion and _final
    authority.Order.fused = lambda self, fused, chunks: fused
    authority.Order.reranked = lambda self, ranked: ranked
_chunks_rt = lexical.chunks


def _chunks_capture(root, path=None):
    out = _chunks_rt(root, path)
    if path is None:
        STATE["chunks"] = {c["chunk_id"]: c for c in out}
    return out


lexical.chunks = _chunks_capture
_retrieve = rt.retrieve


def _retrieve_wrapped(*a, **kw):
    STATE["question"] = kw.get("query", a[1] if len(a) > 1 else None)  # the question as retrieve was asked it
    bundle = _retrieve(*a, **kw)
    if V.get("dedup"):
        kept = []
        for item in bundle["evidence"]:
            if any(o["path"] == item["path"] and o["start_line"] <= item["start_line"]
                   and item["end_line"] <= o["end_line"] for o in kept):
                continue
            kept.append(item)
        bundle["evidence"] = kept
    if V.get("dedup_text"):  # D4B-STRUCTURE E1: one place per identical text across files, the higher-ranked kept
        seen, kept = set(), []
        for item in bundle["evidence"]:
            key = hashlib.sha256(" ".join(str(item.get("text", "")).split()).encode()).hexdigest()
            if len(str(item.get("text", ""))) > 80 and key in seen:
                continue
            seen.add(key)
            kept.append(item)
        bundle["evidence"] = kept
    return bundle


rt.retrieve = _retrieve_wrapped

# SCORE-ONCE, for L2's replays (DEC-1079 L2): the stages after the rerank switched off one at a time, by the variant
# alone. ``routing``: {code_first, named_first} overrides the root's settings (0: that half off); ``ahead_types``: []
# keeps failure and lesson records in place (DEC-424's move off). Absent, nothing is patched.
if "routing" in V:
    from gov.retrieval import routing as _routing
    _settings = _routing.settings
    _want = {k: int(v) for k, v in V["routing"].items()}
    # code_first acts twice in the product: before the fusion (the code route sorted by cosine, when truthy) and after
    # the rerank (its first n moved ahead). L2 switches off only the move: code_first: 0 here keeps the setting truthy
    # (a sentinel, so the fused head and the 40 texts reranked stay as measured) and makes firsts() return nothing for it.
    _SENTINEL = 10 ** 6
    if _want.get("code_first") == 0:
        _want["code_first"] = _SENTINEL
        _firsts = _routing.firsts
        _routing.firsts = lambda ids, count: [] if count == _SENTINEL else _firsts(ids, count)
    _routing.settings = lambda root: {**_settings(root), **_want}
if "ahead_types" in V:
    rt.AHEAD_TYPES = frozenset(V["ahead_types"])

from gov.cli.main import main  # noqa: E402

if os.environ.get("GOV_RX_NO_MAIN") != "1":  # the stand-in check imports this file without running gov
    sys.exit(main(sys.argv[1:]))
