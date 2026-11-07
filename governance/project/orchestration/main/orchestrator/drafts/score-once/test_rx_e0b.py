"""E0b's harness fixes (E0-DECLARATION §E0b), on re-pin window 4's code: the pinned gov at pin-bcea09060ebc. Each case
imports rx.py in a fresh process of the pin's own python (GOV_RX_NO_MAIN=1) with HOME a temporary folder, so no
reranker client can reach a service; every scorer and search is a stub. No GPU, no question read.

    python3 -m pytest -q -p no:cacheprovider test_rx_e0b.py

1. the searches take window 4's ``depth`` / ``top_k`` and honour it (and the older call form still works);
2. the route answers are keyed by the store's root and fingerprints head (another store's: refused, and never reused);
3. GOV_RX_LIVE_MISSING=1 scores a replay's missing texts on the live service, counted; the default stays strict;
4. the product's pool: a variant of its own on a pool-on clone is refused unless GOV_RX_POOL_OFF=1;
5. seed_scores.py: a cache of the kept scores only.
"""
import hashlib
import json
import os
import pickle
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
RX = HERE / "rx.py"
SEED = HERE / "seed_scores.py"
PIN_PY = Path.home() / ".local/share/gov-os/pin-bcea09060ebc/bin/python3"
LIVE_MODEL = "Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473"
GTE = "Alibaba-NLP/gte-reranker-modernbert-base@f7481e6055501a30fb19d090657df9ec1f79ab2c"

pytestmark = pytest.mark.skipif(not PIN_PY.is_file(), reason="the window-4 pin's python is not on this machine")


def run(code: str, env: dict, home: Path) -> subprocess.CompletedProcess:
    """``code`` run after rx.py is imported as ``rx`` by the pin's python; the last stdout line is the answer."""
    prog = ("import importlib.util, sys, json\n"
            f"spec = importlib.util.spec_from_file_location('rx', {str(RX)!r})\n"
            "rx = importlib.util.module_from_spec(spec); spec.loader.exec_module(rx)\n" + code)
    full = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and k != "PYTHONPATH"}
    full.update({"HOME": str(home), "GOV_RX_NO_MAIN": "1", **env})
    return subprocess.run([str(PIN_PY), "-c", prog], capture_output=True, text=True, env=full, timeout=120)


def answer(r: subprocess.CompletedProcess):
    assert r.returncode == 0, r.stderr[-1500:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def store(root: Path, head: str | None, table: bool = True) -> Path:
    """A stand-in clone root whose store holds a fingerprints row at ``head`` (none: an empty table)."""
    (root / ".gov-runtime").mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(root / ".gov-runtime" / "store.db")
    db.execute("DROP TABLE IF EXISTS fingerprints")
    if table:
        db.execute("CREATE TABLE fingerprints (head TEXT, code TEXT, records TEXT, kind TEXT)")
        if head:
            db.execute("INSERT INTO fingerprints VALUES (?, 'c', 'r', 'rebuild')", (head,))
    db.commit()
    db.close()
    return root


def key(*parts) -> str:
    return hashlib.sha256(repr(parts).encode()).hexdigest()


# a stub search that records each call (query, top_k) and answers with no hits
STUBS = ("seen = []\n"
         "def stub(kind):\n"
         "    def search(root, q, refresh=True, **kw):\n"
         "        seen.append([kind, q, kw.get('top_k')])\n"
         "        return {'available': True, 'reason': None, 'hits': [], 'ranked': []}\n"
         "    return search\n"
         "rx._lex_search, rx._sem_search = stub('lex'), stub('sem')\n"
         "from gov.retrieval import lexical, semantic\n"
         "from gov.retrieval import retrieve as rt\n")


# ---------------------------------------------------------------- 1. window 4's depth / top_k
def test_1a_phrased_takes_depth_and_passes_it_as_top_k(tmp_path):
    code = ("calls = []\n"
            "def search(root, q, refresh=True, top_k=None):\n"
            "    calls.append([q, refresh, top_k])\n"
            "    return {'available': True, 'reason': None, 'hits': [{'chunk_id': q + str(i)} for i in range(3)]}\n"
            "from gov.retrieval import retrieve as rt\n"
            "a = rt._phrased(search, 'r', ['a', 'b'], 'hits', cut=2, depth=60)\n"
            "b = rt._phrased(search, 'r', ['a'], 'hits', depth=0)\n"
            "print(json.dumps([calls, len(a['hits']), len(b['hits']), rt._phrased is rx._phrased_rx]))")
    calls, n_cut, n_one, patched = answer(run(code, {"GOV_RX_CACHE": str(tmp_path / "c")}, tmp_path))
    assert patched
    assert calls == [["a", False, 60], ["b", False, 60], ["a", False, None]]  # window 4's call shape, honoured
    assert (n_cut, n_one) == (2, 3)  # the cut kept as the product's
    calls, n_cut, _, _ = answer(run(code, {"GOV_RX_CACHE": str(tmp_path / "c2"), "GOV_RX": '{"sem_uncut": true}'},
                                    tmp_path))
    assert n_cut == 6 and calls[0] == ["a", False, 60]  # sem_uncut still uncuts, the depth still passed


def test_1b_the_harness_searches_honour_top_k_keyed_by_depth(tmp_path):
    root = store(tmp_path / "clone", "h1")
    code = (STUBS + f"root = {str(root)!r}\n"
            "lexical.search(root, 'q', refresh=False, top_k=60)\n"
            "lexical.search(root, 'q', refresh=False, top_k=60)\n"  # the same depth: from the cache
            "lexical.search(root, 'q', refresh=False)\n"  # another depth (TOP_K): asked afresh
            "semantic.search(root, 'q', refresh=False, top_k=60)\n"
            "rt._phrased(lexical.search, root, ['p'], 'ranked', depth=60)\n"  # retrieve.py:324's form, end to end
            "rt._phrased(semantic.search, root, ['p'], 'hits', cut=60, depth=60)\n"
            "print(json.dumps(seen))")
    seen = answer(run(code, {"GOV_RX_CACHE": str(tmp_path / "c")}, tmp_path))
    assert seen == [["lex", "q", 60], ["lex", "q", None], ["sem", "q", 60], ["lex", "p", 60], ["sem", "p", 60]]


def test_1c_the_older_call_form_still_works(tmp_path):
    code = ("def old(root, q, refresh=True):\n"  # a search before W2-32 S11: no top_k
            "    return {'available': True, 'reason': None, 'hits': [{'chunk_id': 'x'}]}\n"
            "a = rx._phrased_rx(old, 'r', ['a'], 'hits', cut=None)\n"
            "rx._phrased, rx._PHRASED_DEPTH = (lambda search, root, asked, key, cut=None: 'old form'), False\n"
            "b = rx._phrased_rx(old, 'r', ['a'], 'hits', cut=5)\n"
            "print(json.dumps([a['hits'], b]))\n"
            "rx._phrased_rx(old, 'r', ['a'], 'hits', depth=60)\n")  # a depth into a retrieve that takes none: stop
    r = run(code, {"GOV_RX_CACHE": str(tmp_path / "c")}, tmp_path)
    assert json.loads(r.stdout.strip().splitlines()[-1]) == [[{"chunk_id": "x"}], "old form"]
    assert r.returncode != 0 and "takes none" in r.stderr


# ---------------------------------------------------------------- 2. route answers keyed by the store
def test_2a_answers_keyed_by_store_root_and_head(tmp_path):
    a, b = store(tmp_path / "a", "h1"), store(tmp_path / "b", "h2")
    cache = tmp_path / "c"
    env = {"GOV_RX_CACHE": str(cache)}
    twice = STUBS + "lexical.search(R, 'q'); lexical.search(R, 'q'); print(json.dumps(seen))\n"
    assert answer(run(f"R = {str(a)!r}\n" + twice, env, tmp_path)) == [["lex", "q", None]]  # stored, then reused
    db = sqlite3.connect(cache / "cache.db")
    assert json.loads(db.execute("SELECT v FROM meta WHERE k = 'store'").fetchone()[0]) == [str(a.resolve()), "h1"]
    db.close()
    r = run(f"R = {str(b)!r}\n" + twice, env, tmp_path)  # a new clone on the same cache: refused
    assert r.returncode != 0 and "holds the route answers of the store" in r.stderr
    store(a, "h3")  # the same root, its store rebuilt at another commit: refused too
    r = run(f"R = {str(a)!r}\n" + twice, env, tmp_path)
    assert r.returncode != 0 and "holds the route answers of the store" in r.stderr
    db = sqlite3.connect(cache / "cache.db")  # and with the claim removed, another store's answer is never returned
    db.execute("DELETE FROM meta WHERE k = 'store'")
    db.commit()
    db.close()
    assert answer(run(f"R = {str(b)!r}\n" + twice, env, tmp_path)) == [["lex", "q", None]]


def test_2b_no_store_stores_nothing_and_a_headless_store_is_refused(tmp_path):
    bare = tmp_path / "bare"
    bare.mkdir()
    code = STUBS + f"R = {str(bare)!r}\nlexical.search(R, 'q'); lexical.search(R, 'q'); print(json.dumps(seen))\n"
    assert len(answer(run(code, {"GOV_RX_CACHE": str(tmp_path / "c")}, tmp_path))) == 2
    db = sqlite3.connect(tmp_path / "c" / "cache.db")
    assert db.execute("SELECT count(*) FROM memo").fetchone()[0] == 0
    db.close()
    headless = store(tmp_path / "old", None)
    code = STUBS + f"lexical.search({str(headless)!r}, 'q')\n"
    r = run(code, {"GOV_RX_CACHE": str(tmp_path / "c2")}, tmp_path)
    assert r.returncode != 0 and "no fingerprints head" in r.stderr


def test_2c_a_cache_filled_before_the_store_key(tmp_path):
    root = store(tmp_path / "g1", "e884675b465e")
    cache = tmp_path / "legacy"
    cache.mkdir()
    db = sqlite3.connect(cache / "cache.db")
    db.execute("CREATE TABLE memo (k TEXT PRIMARY KEY, v BLOB)")
    db.execute("CREATE TABLE score (k TEXT PRIMARY KEY, s REAL)")
    db.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
    kept = {"available": True, "reason": None, "hits": [], "ranked": [{"chunk_id": "kept"}]}
    db.execute("INSERT INTO memo VALUES (?, ?)", (key("lex", "q", 30), pickle.dumps(kept)))  # the old key form
    db.commit()
    db.close()
    code = STUBS + f"got = lexical.search({str(root)!r}, 'q')\nprint(json.dumps([seen, got['ranked']]))\n"
    r = run(code, {"GOV_RX_CACHE": str(cache)}, tmp_path)
    assert r.returncode != 0 and "keyed without their store" in r.stderr
    seen, ranked = answer(run(code, {"GOV_RX_CACHE": str(cache), "GOV_RX_LEGACY_STORE": "1"}, tmp_path))
    assert seen == [] and ranked == [{"chunk_id": "kept"}]  # replayed as before, on its own clone
    r = run("pass", {"GOV_RX_CACHE": str(tmp_path / "fresh")}, tmp_path)  # a fresh cache takes the store key
    assert r.returncode == 0
    r = run("pass", {"GOV_RX_CACHE": str(tmp_path / "fresh"), "GOV_RX_LEGACY_STORE": "1"}, tmp_path)
    assert r.returncode != 0 and "refused" in r.stderr  # never two key forms in one cache


# ---------------------------------------------------------------- 3. GOV_RX_LIVE_MISSING
def kept_cache(folder: Path, model: str, scores: dict) -> str:
    folder.mkdir(parents=True)
    db = sqlite3.connect(folder / "cache.db")
    db.execute("CREATE TABLE score (k TEXT PRIMARY KEY, s REAL)")
    db.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
    db.execute("INSERT INTO meta VALUES ('rerank_model', ?)", (model,))
    for text, s in scores.items():
        db.execute("INSERT INTO score VALUES (?, ?)", (key("rr", model, "q", text), s))
    db.commit()
    db.close()
    return str(folder)


SERVICE = ("asked = []\n"
           "def service(q, ts):\n"
           "    asked.extend(ts)\n"
           "    return [float(len(t)) for t in ts]\n"
           "rx.rr.last_outcome = lambda: {'by': 'service', 'device': 'cuda', 'reason': None}\n"
           "rx._gpu_wait = lambda: None\nrx.STATE['routes'] = {}\n")


def combine_env(tmp_path: Path, own: str, rule: dict, caches: dict, models: dict, **extra) -> dict:
    return {"GOV_RX_CACHE": str(tmp_path / own), "GOV_RX_LOG": str(tmp_path / f"{own}.log"),
            "GOV_RX_COMBINE": json.dumps({"models": models, "caches": caches, "rule": rule}), **extra}


def test_3a_default_strict_and_flag_scores_missing_live_counted(tmp_path):
    q06 = kept_cache(tmp_path / "q06", LIVE_MODEL, {"t1": 0.9, "t2": 0.1})
    rule, caches, models = {"kind": "alone", "m": "q06"}, {"q06": q06}, {"q06": LIVE_MODEL}
    probe = SERVICE + "rx._service = service\nprint(json.dumps([rx.scores('q', ['t1', 't2', 'three']), asked]))\n"
    r = run(probe, combine_env(tmp_path, "strict", rule, caches, models), tmp_path)  # unset: a missing text stops
    assert r.returncode != 0 and "1 of 3 texts were not scored by q06 in the window" in r.stderr
    env = combine_env(tmp_path, "own", rule, caches, models, GOV_RX_LIVE_MISSING="1")
    got, asked = answer(run(probe, env, tmp_path))
    assert got == [0.9, 0.1, 5.0] and asked == ["three"]  # only the missing text, in its place
    assert "LIVEMISS\t1\tq06\t3" in (tmp_path / "own.log").read_text()
    db = sqlite3.connect(tmp_path / "own" / "cache.db")  # kept in the replay's own cache, never in a kept one
    assert db.execute("SELECT s FROM score WHERE k = ?", (key("rr", LIVE_MODEL, "q", "three"),)).fetchone() == (5.0,)
    db.close()
    db = sqlite3.connect(Path(q06) / "cache.db")
    assert db.execute("SELECT count(*) FROM score").fetchone()[0] == 2
    db.close()
    # a strict replay on that own cache reads the live score from it, counted, and calls no service
    probe2 = "rx.STATE['routes'] = {}\nprint(json.dumps([rx.scores('q', ['t1', 't2', 'three']), rx._service is None]))\n"
    env2 = combine_env(tmp_path, "own", rule, caches, models)
    assert answer(run(probe2, env2, tmp_path)) == [[0.9, 0.1, 5.0], True]
    assert "OWNCACHE\t1\tq06" in (tmp_path / "own.log").read_text()


def test_3b_flag_builds_no_client_when_nothing_is_missing(tmp_path):
    q06 = kept_cache(tmp_path / "q06", LIVE_MODEL, {"t1": 0.9})
    env = combine_env(tmp_path, "own", {"kind": "alone", "m": "q06"}, {"q06": q06}, {"q06": LIVE_MODEL},
                      GOV_RX_LIVE_MISSING="1")
    probe = ("rx.STATE['routes'] = {}\n"
             "print(json.dumps([rx.scores('q', ['t1']), rx._service is None, rx.LIVE_MODEL]))\n")
    assert answer(run(probe, env, tmp_path)) == [[0.9], True, LIVE_MODEL]


def test_3c_flag_refusals(tmp_path):
    gte = kept_cache(tmp_path / "gte", GTE, {"t1": 0.5})
    q06 = kept_cache(tmp_path / "q06", LIVE_MODEL, {"t1": 0.9})
    r = run("pass", combine_env(tmp_path, "a", {"kind": "alone", "m": "gte"}, {"gte": gte}, {"gte": GTE},
                                GOV_RX_LIVE_MISSING="1"), tmp_path)
    assert r.returncode != 0 and "no model of the rule is it" in r.stderr  # no rule model is the live one
    r = run("pass", {"GOV_RX_CACHE": str(tmp_path / "b"), "GOV_RX_LIVE_MISSING": "1"}, tmp_path)
    assert r.returncode != 0 and "replay (GOV_RX_COMBINE) only" in r.stderr
    # a merge of q06 and gte: a text gte never scored still stops, named
    env = combine_env(tmp_path, "c", {"kind": "merge", "a": "q06", "b": "gte"}, {"q06": q06, "gte": gte},
                      {"q06": LIVE_MODEL, "gte": GTE}, GOV_RX_LIVE_MISSING="1")
    r = run(SERVICE + "rx._service = service\nrx.scores('q', ['t1', 'new'])\n", env, tmp_path)
    assert r.returncode != 0 and "not scored by gte" in r.stderr and "live service's model" in r.stderr


def test_3d_a_service_that_does_not_score_stops_and_keeps_nothing(tmp_path):
    q06 = kept_cache(tmp_path / "q06", LIVE_MODEL, {"t1": 0.9})
    env = combine_env(tmp_path, "own", {"kind": "alone", "m": "q06"}, {"q06": q06}, {"q06": LIVE_MODEL},
                      GOV_RX_LIVE_MISSING="1")
    probe = (SERVICE + "rx._service = lambda q, ts: None\n"
             "rx.rr.last_outcome = lambda: {'by': 'unavailable', 'reason': 'down'}\n"
             "rx.scores('q', ['t1', 'new'])\n")
    r = run(probe, env, tmp_path)
    assert r.returncode != 0 and "live reranker service did not score (unavailable: down)" in r.stderr
    db = sqlite3.connect(tmp_path / "own" / "cache.db")
    assert db.execute("SELECT count(*) FROM score").fetchone()[0] == 0
    db.close()


# ---------------------------------------------------------------- 4. the product's pool
POOL_ON = "pool:\n  meaning_uncut: true\n  route_depth: 60\n  rerank_depth: 40\n  per_file_first10: 2\n  drop_nested: true\n"


def pool_root(tmp_path: Path, text: str) -> Path:
    root = tmp_path / "clone"
    (root / "governance/project").mkdir(parents=True, exist_ok=True)
    (root / "governance/project/retrieval.yaml").write_text(text)
    return root


def test_4_pool_refused_under_a_variant_unless_switched_off(tmp_path):
    root = pool_root(tmp_path, POOL_ON)
    probe = (f"from gov.retrieval import retrieve as rt\n"
             f"print(json.dumps([rt.pool.settings is rx._pool_rx, rt.pool.settings(rx.Path({str(root)!r}))]))\n")
    v456 = json.dumps({"sem_uncut": True, "sem_k": 60, "lex_k": 60, "depth": 40, "perfile": 2, "dedup": True,
                       "rq": "question"})
    r = run(probe, {"GOV_RX_CACHE": str(tmp_path / "a"), "GOV_RX": v456}, tmp_path)
    assert r.returncode != 0 and "the product's pool is on" in r.stderr and "GOV_RX_POOL_OFF=1" in r.stderr
    log = tmp_path / "b.log"
    patched, got = answer(run(probe, {"GOV_RX_CACHE": str(tmp_path / "b"), "GOV_RX": v456, "GOV_RX_POOL_OFF": "1",
                                      "GOV_RX_LOG": str(log)}, tmp_path))
    assert patched and got == {"meaning_uncut": False, "route_depth": 0, "rerank_depth": 0, "per_file_first10": 0,
                               "drop_nested": False}
    assert log.read_text().startswith("POOL\toff\tmeaning_uncut=True,route_depth=60")
    _, got = answer(run(probe, {"GOV_RX_CACHE": str(tmp_path / "c")}, tmp_path))  # {}: the clone's pool as it is
    assert got["route_depth"] == 60 and got["rerank_depth"] == 40
    bad = pool_root(tmp_path, "pool: 5\n")  # an invalid file is still refused under the switch
    r = run(probe, {"GOV_RX_CACHE": str(tmp_path / "d"), "GOV_RX": v456, "GOV_RX_POOL_OFF": "1"}, tmp_path)
    assert r.returncode != 0 and "GovError" in r.stderr and "'pool': must be a map" in r.stderr, (bad, r.stderr[-500:])


# ---------------------------------------------------------------- 5. seed_scores.py
def test_5_seed_keeps_scores_only(tmp_path):
    a = kept_cache(tmp_path / "a", LIVE_MODEL, {"t1": 0.9, "t2": 0.1})
    b = kept_cache(tmp_path / "b", LIVE_MODEL, {"t2": 0.2, "t3": 0.3})
    db = sqlite3.connect(Path(a) / "cache.db")  # a kept cache with route answers: they are not carried
    db.execute("CREATE TABLE memo (k TEXT PRIMARY KEY, v BLOB)")
    db.execute("INSERT INTO memo VALUES ('x', x'00')")
    db.commit()
    db.close()
    r = subprocess.run([sys.executable, str(SEED), str(tmp_path / "seed"), a, b], capture_output=True, text=True)
    assert r.returncode == 0 and "3 score rows" in r.stdout and "conflicts 1" in r.stdout, r.stderr
    db = sqlite3.connect(tmp_path / "seed" / "cache.db")
    assert db.execute("SELECT count(*) FROM memo").fetchone()[0] == 0
    assert dict(db.execute("SELECT k, v FROM meta").fetchall()) == {"rerank_model": LIVE_MODEL, "memo_keys": "store"}
    assert db.execute("SELECT s FROM score WHERE k = ?", (key("rr", LIVE_MODEL, "q", "t2"),)).fetchone() == (0.1,)
    db.close()
    r = subprocess.run([sys.executable, str(SEED), str(tmp_path / "seed"), a], capture_output=True, text=True)
    assert r.returncode != 0 and "exists" in r.stderr
    g = kept_cache(tmp_path / "g", GTE, {"t1": 0.5})
    r = subprocess.run([sys.executable, str(SEED), str(tmp_path / "mixed"), a, g], capture_output=True, text=True)
    assert r.returncode != 0 and "one model per cache" in r.stderr
    # the seed serves as a replay's kept cache, and as a window run's own cache, with no refusal
    env = combine_env(tmp_path, "own", {"kind": "alone", "m": "q06"}, {"q06": str(tmp_path / "seed")},
                      {"q06": LIVE_MODEL})
    assert answer(run("rx.STATE['routes'] = {}\nprint(json.dumps(rx.scores('q', ['t1', 't3'])))\n", env,
                      tmp_path)) == [0.9, 0.3]
    assert run("pass", {"GOV_RX_CACHE": str(tmp_path / "seed")}, tmp_path).returncode == 0
