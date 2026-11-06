"""Tests of the score-once harness copy's live two-model mode (rx.py: GOV_RX_RERANK_DIR2, GOV_RX_RERANK_MODEL2,
GOV_RX_LIVE_RULE, GOV_RX_BATCH2, GOV_RX_REQUEST_CHARS2, GOV_RX_LIVE_PARALLEL). Two socket stand-ins in this process
speak the trial service's protocol ([query, [text, ...]] in, {"scores": [...], "device": ...} out); each case imports
rx.py in a fresh process with GOV_RX_NO_MAIN=1 and its GPU read replaced. No reranker, no GPU, no question is read.

    python3 test_rx_live.py
"""
import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RX = HERE / "rx.py"
CLONE_SRC = Path.home() / "gov-os-runs/D4B/g1/repo/src"
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"{'ok  ' if ok else 'FAIL'} {name}{': ' + str(detail) if detail and not ok else ''}")


class StandIn:
    """A trial service's socket: one request at a time, first come first served, as rerank_service.py. ``mode``:
    ``ok`` (scores by ``fn``), ``silent`` (reads the request, never answers), ``close`` (closes without an answer),
    ``error`` (answers an error)."""

    def __init__(self, folder: Path, fn, mode="ok", delay=0.0):
        folder.mkdir(parents=True, exist_ok=True)
        self.path, self.fn, self.mode, self.delay = folder / "rerank.sock", fn, mode, delay
        self.reqs = []  # (started, ended, texts)
        self.halt = threading.Event()
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(str(self.path))
        self.sock.listen(64)
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while not self.halt.is_set():
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            with conn:
                line = conn.makefile("rb").readline()
                if not line:
                    continue
                started = time.time()
                query, texts = json.loads(line)
                if self.mode == "silent":
                    self.reqs.append((started, None, texts))
                    self.halt.wait(20)
                    continue
                if self.mode == "close":
                    self.reqs.append((started, time.time(), texts))
                    continue
                time.sleep(self.delay)
                answer = ({"error": "ValueError: stand-in refuses", "device": "cpu"} if self.mode == "error"
                          else {"scores": [self.fn(query, t) for t in texts], "device": "cpu"})
                try:
                    conn.sendall((json.dumps(answer) + "\n").encode())
                except OSError:
                    pass
                self.reqs.append((started, time.time(), texts))

    def close(self):
        self.halt.set()
        self.sock.close()
        if self.path.exists():
            self.path.unlink()


def f_one(query, text):  # stand-in scores: any deterministic function of what was sent
    return (sum(map(ord, text)) % 97) / 10.0 - 4.0


def f_two(query, text):
    return ((len(text) * 31 + ord(text[0])) % 13) / 13.0


def key(model, query, text):
    return hashlib.sha256(repr(("rr", model, query, text)).encode()).hexdigest()


def mm(v):
    lo, hi = min(v), max(v)
    return [(x - lo) / (hi - lo) if hi > lo else 1.0 for x in v]


tmp = Path(tempfile.mkdtemp(prefix="rxl-"))
home = tmp / "home"  # the product client's interpreter check and its log, inside the test's own folder
(home / ".local/share/gov-os/reranker-venv/bin").mkdir(parents=True)
(home / ".local/share/gov-os/reranker-venv/bin/python").write_text("")
MA, MB = "A@1", "B@2"
# varied lengths, so the requests are longest first and the scores must come back in the texts' own order
TEXTS = [f"{i}:" + "x" * n for i, n in enumerate([300, 13000, 50, 2500, 2500, 900, 7000, 120, 1600, 40, 3100, 610])]
Q = "q"
n_case = [0]


def run(code: str, env: dict) -> subprocess.CompletedProcess:
    """``code`` run after rx.py is imported as module ``rx`` (GOV_RX_NO_MAIN=1), with the GPU read replaced."""
    prog = ("import importlib.util, sys, json\n"
            f"sys.path.insert(0, {str(CLONE_SRC)!r})\n"
            f"spec = importlib.util.spec_from_file_location('rx', {str(RX)!r})\n"
            "rx = importlib.util.module_from_spec(spec); spec.loader.exec_module(rx)\n"
            "rx._gpu_used = lambda: int(rx.os.environ.get('FAKE_GPU_MIB', '1000'))\n" + code)
    full = {k: v for k, v in os.environ.items() if not k.startswith("GOV_RX") and not k.startswith("GOV_RERANK")}
    full.update({"GOV_RX_NO_MAIN": "1", "HOME": str(home), **env})
    return subprocess.run([sys.executable, "-c", prog], capture_output=True, text=True, env=full, timeout=120)


def live_env(a: StandIn, b: StandIn, rule=None, cache=None, **extra):
    n_case[0] += 1
    return {"GOV_RX_CACHE": str(cache or tmp / f"cache-{n_case[0]}"), "GOV_RX_LOG": str(tmp / f"rx-{n_case[0]}.log"),
            "GOV_RX_RERANK_DIR": str(a.path.parent), "GOV_RX_RERANK_MODEL": MA,
            "GOV_RX_RERANK_DIR2": str(b.path.parent), "GOV_RX_RERANK_MODEL2": MB,
            "GOV_RX_LIVE_RULE": json.dumps(rule or {"kind": "merge", "a": "one", "b": "two"}),
            "GOV_RX_GPU_LIMIT_MIB": "14255", "GOV_RX_BATCH": "8", "GOV_RX_REQUEST_CHARS": "12000", **extra}


SCORE = f"rx.STATE['routes'] = {{}}\nprint(json.dumps(rx.scores({Q!r}, {TEXTS!r})))"


def scored(env):
    r = run(SCORE, env)
    return (json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None), r


def log_of(env):
    p = Path(env["GOV_RX_LOG"])
    return p.read_text().splitlines() if p.exists() else []


raw_one = [f_one(Q, t[:12000]) for t in TEXTS]  # one reads up to its bound (12,000), two up to 24,000
raw_two = [f_two(Q, t[:24000]) for t in TEXTS]
one, two = StandIn(tmp / "run", f_one), StandIn(tmp / "run2", f_two)

# L1. the merge: 0.5 x min-max(one) + 0.5 x min-max(two), in the texts' own order
env1 = live_env(one, two)
got, r = scored(env1)
want = [0.5 * x + 0.5 * y for x, y in zip(mm(raw_one), mm(raw_two))]
check("L1 merge of the two services' scores, in the texts' order", got and all(abs(x - y) < 1e-12 for x, y in
      zip(got, want)), r.stderr[-400:] or got)
w07 = [0.7 * x + 0.3 * y for x, y in zip(mm(raw_one), mm(raw_two))]
got07, r = scored(live_env(one, two, {"kind": "merge", "a": "one", "b": "two", "w": 0.7}))
check("L1b the rule's a is one (GOV_RX_RERANK_DIR), b is two (GOV_RX_RERANK_DIR2)", got07 and all(
      abs(x - y) < 1e-12 for x, y in zip(got07, w07)), r.stderr[-400:] or got07)

# L2. each service got every text once, in its own bounds (one 8 and 12,000; two 16 and 24,000), cut at its bound
reqs_one, reqs_two = [q[2] for q in one.reqs[:]], [q[2] for q in two.reqs[:]]


def per_run(reqs):
    """The requests of the first run (L1): every text once; the second run (L1b, a fresh cache) repeats them."""
    seen, out = 0, []
    for texts in reqs:
        if seen >= len(TEXTS):
            break
        out.append(texts)
        seen += len(texts)
    return out


r1, r2 = per_run(reqs_one), per_run(reqs_two)
sent1 = sorted(t for q in r1 for t in q)
sent2 = sorted(t for q in r2 for t in q)
check("L2 one: every text once, at most 8 a request and 12,000 padded, cut at 12,000",
      sent1 == sorted(t[:12000] for t in TEXTS) and max(len(q) for q in r1) <= 8
      and max(len(q) * max(map(len, q)) for q in r1) <= 12000, [(len(q), max(map(len, q))) for q in r1])
check("L2b two: every text once, at most 16 a request and 24,000 padded, read whole here",
      sent2 == sorted(TEXTS) and max(len(q) for q in r2) <= 16
      and max(len(q) * max(map(len, q)) for q in r2) <= 24000, [(len(q), max(map(len, q))) for q in r2])

# L3. the log: per request LIVE<TAB>name<TAB>seconds and its GPU read, one pass line
lines = log_of(env1)
live1 = [x for x in lines if x.startswith("LIVE\tone\t")]
live2 = [x for x in lines if x.startswith("LIVE\ttwo\t")]
check("L3 LIVE<TAB>one/two<TAB>seconds, one line per request to each", len(live1) == len(r1) and len(live2) == len(r2)
      and all(float(x.split("\t")[2]) >= 0 for x in live1 + live2), lines)
check("L3b a GPU-read line per request, and one pass line", sum(x.startswith("LIVEGPU\t") for x in lines)
      == len(r1) + len(r2) and sum(x.startswith("live\t") for x in lines) == 1
      and any(x.startswith("TRUNC\t1\t12000\tone") for x in lines), lines)

# L4. the cache: each model's raw scores under its own key, the cache marked with both models
db = sqlite3.connect(f"file:{env1['GOV_RX_CACHE']}/cache.db?mode=ro", uri=True)
rows = dict(db.execute("SELECT k, s FROM score").fetchall())
meta = dict(db.execute("SELECT k, v FROM meta").fetchall())
db.close()
check("L4 each model's scores under its own key (model, question, text)", len(rows) == 2 * len(TEXTS)
      and all(abs(rows[key(MA, Q, t)] - s) < 1e-12 for t, s in zip(TEXTS, raw_one))
      and all(abs(rows[key(MB, Q, t)] - s) < 1e-12 for t, s in zip(TEXTS, raw_two)), len(rows))
check("L4b the cache is marked rerank_model one, rerank_model2 two", meta.get("rerank_model") == MA
      and meta.get("rerank_model2") == MB, meta)
before = (len(one.reqs), len(two.reqs))
again, r = scored({**live_env(one, two), "GOV_RX_CACHE": env1["GOV_RX_CACHE"]})
check("L4c a second live run on that cache asks no service and gives the same scores", again == got
      and (len(one.reqs), len(two.reqs)) == before, r.stderr[-300:])
replay_env = {"GOV_RX_CACHE": str(tmp / "replay"), "GOV_RX_COMBINE": json.dumps(
    {"models": {"one": MA, "two": MB}, "caches": {"one": env1["GOV_RX_CACHE"], "two": env1["GOV_RX_CACHE"]},
     "rule": {"kind": "merge", "a": "one", "b": "two"}})}
r = run(SCORE, replay_env)
replayed = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
check("L4d the live cache replays with GOV_RX_COMBINE to the same scores", replayed == got, r.stderr[-300:])

# L5. a silent service stops the run loudly; nothing of the pass is cached
silent = StandIn(tmp / "run-silent", f_two, mode="silent")
env5 = live_env(one, silent, GOV_RERANK_TIMEOUT_S="1")
t0 = time.time()
got5, r = scored(env5)
db = sqlite3.connect(f"file:{env5['GOV_RX_CACHE']}/cache.db?mode=ro", uri=True)
n5 = db.execute("SELECT COUNT(*) FROM score").fetchone()[0]
db.close()
check("L5 a silent service stops the run (the answer timeout), naming it", got5 is None and r.returncode != 0
      and "'two'" in r.stderr and "TimeoutError" in r.stderr and time.time() - t0 < 60, r.stderr[-300:])
check("L5b its LIVEFAIL line, and no score of the pass cached", any(x.startswith("LIVEFAIL\ttwo\tTimeoutError")
      for x in log_of(env5)) and n5 == 0, (log_of(env5), n5))
silent.close()
closer = StandIn(tmp / "run-close", f_two, mode="close")
got, r = scored(live_env(one, closer))
check("L5c a service that closes without an answer stops the run", got is None and r.returncode != 0
      and "without an answer" in r.stderr, r.stderr[-300:])
closer.close()
refuser = StandIn(tmp / "run-error", f_two, mode="error")
got, r = scored(live_env(refuser, two))
check("L5d a service that answers an error stops the run, naming it", got is None and r.returncode != 0
      and "'one'" in r.stderr and "stand-in refuses" in r.stderr, r.stderr[-300:])
refuser.close()

# L6. a missing service: at import (no socket), or gone before the request
(tmp / "run-none").mkdir()
env6 = live_env(one, two)
env6["GOV_RX_RERANK_DIR2"] = str(tmp / "run-none")
r = run("pass", env6)
check("L6 no second socket: stopped at once", r.returncode != 0 and "no trial reranker socket" in r.stderr,
      r.stderr[-300:])
gone = StandIn(tmp / "run-gone", f_two)
r = run(f"rx.STATE['routes'] = {{}}\nimport socket\nrx.os.unlink({str(gone.path)!r})\n"
        f"print(rx.scores({Q!r}, {TEXTS!r}))", live_env(one, gone))
check("L6b a service gone after the start: stopped at the request", r.returncode != 0
      and "did not score (FileNotFoundError" in r.stderr, r.stderr[-300:])
gone.close()

# L7. a half-set or wrong switch is refused, never a silent single-model run
base7 = live_env(one, two)
cases = {
    "no rule": {k: v for k, v in base7.items() if k != "GOV_RX_LIVE_RULE"},
    "no second folder": {k: v for k, v in base7.items() if k != "GOV_RX_RERANK_DIR2"},
    "no second model": {k: v for k, v in base7.items() if k != "GOV_RX_RERANK_MODEL2"},
    "no first folder": {k: v for k, v in base7.items() if k != "GOV_RX_RERANK_DIR"},
    "the same folder twice": {**base7, "GOV_RX_RERANK_DIR2": base7["GOV_RX_RERANK_DIR"]},
    "the same model twice": {**base7, "GOV_RX_RERANK_MODEL2": MA},
    "a rule naming another model": {**base7, "GOV_RX_LIVE_RULE": json.dumps({"kind": "merge", "a": "one", "b": "x"})},
    "a rule that is not JSON": {**base7, "GOV_RX_LIVE_RULE": "merge"},
}
bad = [name for name, e in cases.items() if (lambda p: p.returncode == 0 or "refused" not in p.stderr)(run("pass", e))]
check("L7 each half-set or wrong switch is refused", not bad, bad)
r = run("pass", {**live_env(one, two), "GOV_RX_CACHE": env1["GOV_RX_CACHE"], "GOV_RX_RERANK_MODEL2": "C@3"})
check("L7b a cache whose second model is another is refused", r.returncode != 0 and "second model" in r.stderr,
      r.stderr[-300:])

# L8. without the new switches nothing changes: the single trial path through one, as before
n_two = len(two.reqs)
env8 = {"GOV_RX_CACHE": str(tmp / "single"), "GOV_RX_LOG": str(tmp / "single.log"),
        "GOV_RX_RERANK_DIR": str(one.path.parent), "GOV_RX_RERANK_MODEL": MA, "GOV_RX_GPU_LIMIT_MIB": "14255",
        "GOV_RX_BATCH": "8", "GOV_RX_REQUEST_CHARS": "12000"}
r = run(f"rx.STATE['routes'] = {{}}\nprint(json.dumps([rx.LIVE, rx.scores({Q!r}, {TEXTS!r})]))", env8)
d = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
lines8 = log_of(env8)
db = sqlite3.connect(f"file:{tmp / 'single'}/cache.db?mode=ro", uri=True)
meta8 = dict(db.execute("SELECT k, v FROM meta").fetchall())
db.close()
check("L8 without the switches: LIVE off, the trial path gives one's raw scores", d and d[0] is None
      and all(abs(x - y) < 1e-12 for x, y in zip(d[1], raw_one)), r.stderr[-300:] or d)
check("L8b ... no LIVE line, its own log lines, the second service never asked, no second model marked",
      not any(x.startswith(("LIVE", "live")) for x in lines8) and f"service\t{len(TEXTS)}\t{len(TEXTS)}" in lines8
      and len(two.reqs) == n_two and "rerank_model2" not in meta8, (lines8, meta8))
r = run("print(json.dumps([rx.LIVE, rx.BATCH2, rx.REQUEST_CHARS2, rx._requests(['a' * 10] * 20) == "
        "rx._requests(['a' * 10] * 20, rx.BATCH, rx.REQUEST_CHARS)]))",
        {"GOV_RX_CACHE": str(tmp / "plain"), "GOV_RX_RERANK_MODEL": MA})
d = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
check("L8c no trial switch at all: LIVE off, the second bounds at their defaults, _requests as before",
      d == [None, 16, 24000, True], r.stderr[-300:] or d)

# L9. GOV_RX_LIVE_PARALLEL=1: the same scores, the two services asked at once
slow1, slow2 = StandIn(tmp / "run-p1", f_one, delay=0.4), StandIn(tmp / "run-p2", f_two, delay=0.4)
got9, r = scored(live_env(slow1, slow2, GOV_RX_LIVE_PARALLEL="1"))
overlap = any(a0 < b1 and b0 < a1 for a0, a1, _ in slow1.reqs for b0, b1, _ in slow2.reqs)
check("L9 parallel: the same scores as one-then-two", got9 is not None and all(abs(x - y) < 1e-12 for x, y in
      zip(got9, want)), r.stderr[-300:])
check("L9b parallel: the two services' requests overlap in time", overlap)
s1, s2 = StandIn(tmp / "run-s1", f_one, delay=0.2), StandIn(tmp / "run-s2", f_two, delay=0.2)
scored(live_env(s1, s2))
check("L9c default (one, then two): no overlap", not any(a0 < b1 and b0 < a1 for a0, a1, _ in s1.reqs
                                                          for b0, b1, _ in s2.reqs))
silent_p = StandIn(tmp / "run-sp", f_two, mode="silent")
got, r = scored(live_env(one, silent_p, GOV_RX_LIVE_PARALLEL="1", GOV_RERANK_TIMEOUT_S="1"))
check("L9d parallel: a silent service still stops the run", got is None and r.returncode != 0
      and "'two'" in r.stderr, r.stderr[-300:])
for s in (slow1, slow2, s1, s2, silent_p):
    s.close()

# L10. the GPU limit stops a live run before any request
n1, n2 = len(one.reqs), len(two.reqs)
got, r = scored(live_env(one, two, FAKE_GPU_MIB="14255"))
check("L10 GPU at the limit: stopped before any request to either service", got is None and r.returncode != 0
      and "GOV_RX_GPU_LIMIT_MIB" in r.stderr and (len(one.reqs), len(two.reqs)) == (n1, n2), r.stderr[-300:])

one.close()
two.close()
print(f"{sum(results)} of {len(results)} passed")
sys.exit(0 if all(results) else 1)
