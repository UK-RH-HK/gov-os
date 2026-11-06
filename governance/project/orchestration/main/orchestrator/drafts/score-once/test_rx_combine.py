"""Tests of the score-once harness copy's additions (rx.py: GOV_RX_COMBINE, GOV_RX_BATCH, GOV_RX_REQUEST_CHARS, the
``routing`` and ``ahead_types`` variant keys). Each case imports rx.py in a fresh process with GOV_RX_NO_MAIN=1 on
stand-in caches; no reranker, no GPU, no question is read.

    python3 test_rx_combine.py
"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RX = HERE / "rx.py"
CLONE_SRC = Path.home() / "gov-os-runs/D4B/g1/repo/src"
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"{'ok  ' if ok else 'FAIL'} {name}{': ' + str(detail) if detail and not ok else ''}")


def run(code: str, env: dict) -> subprocess.CompletedProcess:
    """``code`` run after rx.py is imported as module ``rx`` (GOV_RX_NO_MAIN=1)."""
    prog = ("import importlib.util, sys, json\n"
            f"sys.path.insert(0, {str(CLONE_SRC)!r})\n"
            f"spec = importlib.util.spec_from_file_location('rx', {str(RX)!r})\n"
            "rx = importlib.util.module_from_spec(spec); spec.loader.exec_module(rx)\n" + code)
    full = {k: v for k, v in os.environ.items() if not k.startswith("GOV_RX")}
    full.update({"GOV_RX_NO_MAIN": "1", **env})
    return subprocess.run([sys.executable, "-c", prog], capture_output=True, text=True, env=full, timeout=120)


def key(model, query, text):
    import hashlib
    return hashlib.sha256(repr(("rr", model, query, text)).encode()).hexdigest()


tmp = Path(tempfile.mkdtemp(prefix="rx-combine-"))
models = {"a": "A@1", "b": "B@2"}
texts = ["t1", "t2", "t3", "t4"]
raw = {"a": [0.9, 0.1, 0.5, 0.7], "b": [0.2, 0.8, 0.6, 0.1]}
caches = {}
for name in ("a", "b"):
    d = tmp / f"cache-{name}"; d.mkdir()
    db = sqlite3.connect(d / "cache.db")
    db.execute("CREATE TABLE score (k TEXT PRIMARY KEY, s REAL)")
    db.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
    db.execute("INSERT INTO meta VALUES ('rerank_model', ?)", (models[name],))
    for t, s in zip(texts, raw[name]):
        db.execute("INSERT INTO score VALUES (?, ?)", (key(models[name], "q", t), s))
    db.commit(); db.close()
    caches[name] = str(d)


def combine_env(rule, **extra):
    return {"GOV_RX_CACHE": str(tmp / f"replay-{len(results)}"),
            "GOV_RX_COMBINE": json.dumps({"models": models, "caches": caches, "rule": rule}), **extra}


def scored(rule, code_routes=False):
    r = run(f"rx.STATE['routes'] = {{'code': [1]}} if {code_routes} else {{}}\n"
            f"print(json.dumps(rx.scores('q', {texts!r})))", combine_env(rule))
    return (json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None), r


# 1. alone: the model's raw scores, exactly
got, r = scored({"kind": "alone", "m": "b"})
check("1 alone gives the model's kept raw scores", got == raw["b"], r.stderr[-300:])

# 2. by type: the code model on a question the code route answers, the other's otherwise
got_code, _ = scored({"kind": "by_type", "code": "a", "other": "b"}, code_routes=True)
got_other, _ = scored({"kind": "by_type", "code": "a", "other": "b"}, code_routes=False)
check("2 by_type: the code model where the code route answers", got_code == raw["a"])
check("2b by_type: the other model elsewhere", got_other == raw["b"])

# 3. cascade: first orders, its top 2 reordered by second into [0.5, 1], the rest below in first's order
got, r = scored({"kind": "cascade", "first": "a", "top": 2, "second": "b"})
order = sorted(range(4), key=lambda i: -got[i]) if got else []
# a's top 2: t1 (0.9), t4 (0.7); b ranks t1 (0.2) over t4 (0.1); the rest by a: t3 (0.5), t2 (0.1)
check("3 cascade: the head reordered by the second, the rest in the first's order", order == [0, 3, 2, 1], got)
check("3b cascade: the head in [0.5, 1], the rest below 0.5", got and min(got[0], got[3]) >= 0.5
      and max(got[1], got[2]) < 0.5, got)

# 4. merge: equal weights on min-max scores
got, r = scored({"kind": "merge", "a": "a", "b": "b"})
mm = lambda v: [(x - min(v)) / (max(v) - min(v)) for x in v]
want = [0.5 * x + 0.5 * y for x, y in zip(mm(raw["a"]), mm(raw["b"]))]
check("4 merge: 0.5 x min-max(a) + 0.5 x min-max(b)", got and all(abs(x - y) < 1e-12 for x, y in zip(got, want)), got)

# 5. a text not scored in the window stops the run loudly
r = run("rx.STATE['routes'] = {}\nrx.scores('q', ['t1', 'never scored'])", combine_env({"kind": "alone", "m": "a"}))
check("5 an unscored text stops the run", r.returncode != 0 and "not scored by a in the window" in r.stderr, r.stderr[-300:])

# 6. a cache holding another model's scores is refused
bad = dict(models, a="Other@9")
r = run("pass", {"GOV_RX_CACHE": str(tmp / "replay-bad"),
                 "GOV_RX_COMBINE": json.dumps({"models": bad, "caches": caches, "rule": {"kind": "alone", "m": "a"}})})
check("6 a cache of another model is refused", r.returncode != 0 and "refused" in r.stderr, r.stderr[-300:])

# 7. combine mode never builds the reranker client and never writes a score row
r = run("print(rx._service is None)", combine_env({"kind": "alone", "m": "a"}))
check("7 no reranker client in combine mode", r.stdout.strip().endswith("True"), r.stderr[-300:])
before = {n: (Path(c) / "cache.db").stat().st_mtime_ns for n, c in caches.items()}
scored({"kind": "merge", "a": "a", "b": "b"})
check("7b the kept caches are read only (unchanged)", before == {n: (Path(c) / "cache.db").stat().st_mtime_ns
                                                              for n, c in caches.items()})

# 8. the request bounds: 16 and 24,000 by default; 8 and 12,000 when set; every request within them
probe = ("ts = ['x' * 1400] * 20 + ['y' * 3000] * 5\n"
         "reqs = rx._requests(ts)\n"
         "print(json.dumps([rx.BATCH, rx.REQUEST_CHARS, max(len(q) for q in reqs), "
         "max(len(q) * max(len(ts[i]) for i in q) for q in reqs), sorted(i for q in reqs for i in q) == list(range(25))]))")
base = {"GOV_RX_CACHE": str(tmp / "plain"), "GOV_RX_RERANK_MODEL": "A@1"}
r = run(probe, base)
d = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
check("8 default bounds 16 and 24,000, every text once", d and d[0] == 16 and d[1] == 24000 and d[2] <= 16
      and d[3] <= 24000 and d[4], r.stderr[-300:] or d)
r = run(probe, {**base, "GOV_RX_CACHE": str(tmp / "plain2"), "GOV_RX_BATCH": "8", "GOV_RX_REQUEST_CHARS": "12000"})
d = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
check("8b the 4B's bounds 8 and 12,000, every text once", d and d[0] == 8 and d[1] == 12000 and d[2] <= 8
      and d[3] <= 12000 and d[4], r.stderr[-300:] or d)

# 9. the routing override and the ahead types, only when the variant names them
r = run("from gov.retrieval import routing, retrieve\n"
        "print(json.dumps([routing.settings.__name__, sorted(retrieve.AHEAD_TYPES)]))",
        {**base, "GOV_RX_CACHE": str(tmp / "plain3"), "GOV_RX": json.dumps({"depth": 40})})
d = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
check("9 absent, nothing patched", d == ["settings", ["failure", "lesson"]], r.stderr[-300:] or d)
r = run("from gov.retrieval import retrieve, routing\n"
        f"s = routing.settings(rx.Path({str(CLONE_SRC.parent)!r}))\n"
        "print(json.dumps([s, sorted(retrieve.AHEAD_TYPES), routing.firsts(['a', 'b', 'c'], s['code_first']), "
        "routing.firsts(['a', 'b', 'c'], 2)]))",
        {**base, "GOV_RX_CACHE": str(tmp / "plain4"),
         "GOV_RX": json.dumps({"depth": 40, "routing": {"code_first": 0, "named_first": 0}, "ahead_types": []})})
d = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
check("9b code_first 0: the setting stays truthy (the pre-fusion sort kept), the move returns nothing",
      d and d[0].get("code_first") == 10 ** 6 and d[2] == [] and d[3] == ["a", "b"], r.stderr[-300:] or d)
check("9c named_first 0 and the ahead types empty", d and d[0].get("named_first") == 0 and d[1] == [], d)

# 10. a replay must not write into a kept cache
r = run("pass", {"GOV_RX_CACHE": caches["a"],
                 "GOV_RX_COMBINE": json.dumps({"models": models, "caches": caches, "rule": {"kind": "alone", "m": "a"}})})
check("10 a replay whose cache is a kept cache is refused", r.returncode != 0 and "must not be one of the kept caches"
      in r.stderr, r.stderr[-300:])

# 11. the model's own cut is counted (GOV_RX_MODEL_CUT), and never without the switch
probe11 = ("rx._service = lambda q, ts: [0.0] * len(ts)\n"
           "rx.rr.last_outcome = lambda: {'by': 'service'}\nrx._gpu_wait = lambda: None\n"
           "rx.scores('q', ['x' * 50, 'y' * 20000, 'z' * 11000])\nprint(open(rx.os.environ['GOV_RX_LOG']).read())")
log = tmp / "rx11.log"
r = run(probe11, {**base, "GOV_RX_CACHE": str(tmp / "plain11"), "GOV_RX_LOG": str(log), "GOV_RX_MODEL_CUT": "10000"})
check("11 the model's cut is counted per text", "MODELCUT\t2\t10000" in r.stdout and "TRUNC\t0" not in r.stdout,
      r.stdout[-300:] + r.stderr[-300:])

# 12. the depth rerank's text: the last lexical phrasing by default (as measured), the question with "rq": "question"
probe12 = ("rx._retrieve = lambda *a, **kw: {'evidence': []}\n"
           "rx._retrieve_wrapped('root', 'What decides a close?')\n"
           "rx.STATE['query'] = 'decides close'\n"
           "print(json.dumps([rx.STATE['question'], rx._rerank_text()]))")
r = run(probe12, {**base, "GOV_RX_CACHE": str(tmp / "plain12"), "GOV_RX": json.dumps({"depth": 40})})
d = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
check("12 default: the depth rerank is given the last phrasing, as every v456 figure",
      d == ["What decides a close?", "decides close"], r.stderr[-300:] or d)
r = run(probe12, {**base, "GOV_RX_CACHE": str(tmp / "plain12b"), "GOV_RX": json.dumps({"depth": 40, "rq": "question"})})
d = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
check("12b rq question: the depth rerank is given the question as retrieve was asked", d == ["What decides a close?",
      "What decides a close?"], r.stderr[-300:] or d)
probe12c = ("rx._retrieve = lambda *a, **kw: {'evidence': []}\n"
            "rx._retrieve_wrapped('root', query=None, continuation='x')\n"
            "rx.STATE['query'] = 'kept'\nprint(json.dumps(rx._rerank_text()))")
r = run(probe12c, {**base, "GOV_RX_CACHE": str(tmp / "plain12c"), "GOV_RX": json.dumps({"depth": 40, "rq": "question"})})
check("12c a call with no question (a continuation) keeps the default", r.returncode == 0
      and r.stdout.strip().splitlines()[-1] == '"kept"', r.stderr[-300:] or r.stdout)

# 14. L3: with lift_norm, the lift is added to the pass's min-max normalised score; without it, to the raw score
probe14 = ("rx._steps = lambda c: c['steps']\nrx.STATE['routes'] = {}\n"
           "cands = [{'chunk_id': 'a', 'steps': 0, 'path': 'p'}, {'chunk_id': 'b', 'steps': 1, 'path': 'q'}, "
           "{'chunk_id': 'c', 'steps': 0, 'path': 'r'}]\n"
           "print(json.dumps(rx._final(cands, [10.0, 0.0, 5.0])))")
r = run(probe14, {**base, "GOV_RX_CACHE": str(tmp / "plain14"), "GOV_RX": json.dumps({"depth": 40, "lift_norm": 0.6})})
d = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
# normalised: a 1.0, b 0.0 + 0.6 = 0.6, c 0.5 -> a, b, c
check("14 lift_norm: the step on the normalised score (a, b, c)", d == ["a", "b", "c"], r.stderr[-300:] or d)
r = run(probe14, {**base, "GOV_RX_CACHE": str(tmp / "plain14b"), "GOV_RX": json.dumps({"depth": 40})})
d = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
# raw: a 10, b 0 + 1.0 = 1, c 5 -> a, c, b
check("14b without it: the step on the raw score, as measured (a, c, b)", d == ["a", "c", "b"], r.stderr[-300:] or d)

# 13. no fill: an unscored text stops the run in a follow-up call too (v4's fill withdrawn)
r = run("import sys\nsys.argv.append('--continue')\nrx.STATE['routes'] = {}\nrx.scores('q', ['t1', 'never scored'])",
        combine_env({"kind": "alone", "m": "a"}))
check("13 a follow-up call with an unscored text stops too", r.returncode != 0 and "not scored by a" in r.stderr,
      r.stderr[-300:])

print(f"{sum(results)} of {len(results)} passed")
sys.exit(0 if all(results) else 1)
