"""Tests of the live window's two helpers: live_searches.py (with a stand-in harness and stand-in questions) and
live_probe.py (its shapes, and its peak mode against a socket stand-in with the GPU read replaced). No reranker, no
GPU, no real question is read.

    python3 test_live_tools.py
"""
import importlib.util
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"{'ok  ' if ok else 'FAIL'} {name}{': ' + str(detail) if detail and not ok else ''}")


tmp = Path(tempfile.mkdtemp(prefix="lt-"))
clone = tmp / "clone"
qdir = clone / "fixtures/evaluation/memory-retrieval/visible"
qdir.mkdir(parents=True)
(clone / "src").mkdir()
QUESTIONS = {"q01": ("first stand-in question", {"ticket": "W2-1", "ids": ["DEC-1", "DEC-2"], "radius": 2}),
             "q02": ("second stand-in question FAIL", {}),
             "q03": ("third stand-in question UNRANKED", {}),
             "q04": ("fourth stand-in question", {}),
             "q05": ("fifth stand-in question", {}),
             "q06": ("sixth, never asked at n 5", {})}
for name, (q, extra) in QUESTIONS.items():
    (qdir / f"{name}.yaml").write_text(json.dumps({"question": q, **extra}))  # JSON is YAML
seen = tmp / "seen"  # the stand-in harness's record of its arguments and times (outside the driver's folder)
seen.mkdir()
fake = tmp / "fake_rx.py"
fake.write_text(f"""import json, os, sys, time
args = sys.argv[1:]
t0 = time.time(); time.sleep(0.4)
q = args[-2]
n = len(os.listdir({str(seen)!r}))
json.dump({{"args": args, "t0": t0, "t1": time.time(), "env": {{k: os.environ.get(k) for k in
           ("GOV_RX", "GOV_RX_CACHE", "GOV_TICKET", "GOV_ROLE", "GOV_RX_RERANK_DIR2")}}}},
          open(os.path.join({str(seen)!r}, f"{{n}}-{{os.getpid()}}.json"), "w"))
log = open(os.environ["GOV_RX_LOG"], "a")
log.write("LIVEGPU\\tone\\t0.050\\nLIVE\\tone\\t0.200\\nLIVEGPU\\ttwo\\t0.050\\nLIVE\\ttwo\\t0.100\\n")
if "FAIL" in q:
    log.write("LIVEFAIL\\ttwo\\tTimeoutError: timed out\\n"); log.close()
    sys.exit("rx: the trial reranker 'two' did not score: stopped")
log.close()
print(json.dumps({{"ok": True, "result": {{"rerank": {{"by": "unavailable" if "UNRANKED" in q else "service"}},
                  "evidence": [{{"path": "a", "start_line": 1, "end_line": 2, "text": "x"}}]}}}}))
""")
DRIVER = HERE / "live_searches.py"
VAR = '{"depth":40,"lift_norm":0.0766}'


def drive(mode, n, out, questions=None, extra_env=None):
    cmd = [sys.executable, str(DRIVER), mode, str(n), "--clone", str(clone), "--rx", str(fake), "--variant", VAR,
           "--out", str(out)] + (["--questions", str(questions)] if questions else [])
    env = {**os.environ, "GOV_TICKET": "W2-99", "GOV_RX_RERANK_DIR2": "/x/run2", **(extra_env or {})}
    return subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)


def records():
    out = [json.loads(p.read_text()) for p in seen.iterdir()]
    for p in seen.iterdir():
        p.unlink()
    return out


# D1. alone: one at a time, the measure's first-call arguments, a fresh cache each, the summary's figures
r = drive("alone", 5, tmp / "out-alone")
recs = sorted(records(), key=lambda d: d["t0"])
s = json.loads((tmp / "out-alone/summary-alone.json").read_text()) if r.returncode == 0 else {}
check("D1 alone: 5 searches, never two at once", len(recs) == 5 and all(a["t1"] <= b["t0"] for a, b in
      zip(recs, recs[1:])), r.stderr[-300:])
first = next((d for d in recs if d["args"][-2] == QUESTIONS["q01"][0]), None)
check("D1b the first call's arguments: ticket, ids, radius, 10, 6000, the question, --json",
      first and first["args"] == ["retrieve", "--ticket", "W2-1", "--id", "DEC-1", "--id", "DEC-2", "--radius", "2",
                                  "--batch-size", "10", "--bundle-budget", "6000", QUESTIONS["q01"][0], "--json"],
      first and first["args"])
check("D1c each search: its own fresh cache, the variant, GOV_TICKET dropped, the live switches passed",
      len({d["env"]["GOV_RX_CACHE"] for d in recs}) == 5 and all(d["env"]["GOV_RX"] == VAR
      and d["env"]["GOV_TICKET"] is None and d["env"]["GOV_ROLE"] == "orchestrator"
      and d["env"]["GOV_RX_RERANK_DIR2"] == "/x/run2" for d in recs), [d["env"] for d in recs])
check("D1d the summary: failed 1, timed out 1, unranked 1; median, p90 and per-service seconds",
      s.get("failed") == 1 and s.get("timeouts") == 1 and s.get("unranked") == 1 and s.get("median_s", 0) >= 0.4
      and s.get("p90_s", 0) >= s.get("median_s", 9) and abs(s.get("median_one_s", 0) - 0.2) < 1e-9
      and abs(s.get("median_two_s", 0) - 0.1) < 1e-9
      and abs(s["median_s"] - s["median_less_gpu_reads_s"] - 0.1) < 0.02, {k: v for k, v in s.items() if k != "rows"})
check("D1e the printed summary line", "5 searches alone: median" in r.stdout and "failed 1, unranked 1" in r.stdout,
      r.stdout[-400:])
texts = [p.read_text(errors="replace") for p in (tmp / "out-alone").rglob("*") if p.is_file()]
check("D1f no question text in the driver's folder", not any(q in t for t in texts for q, _ in QUESTIONS.values()))

# D2. once: all started together
r = drive("once", 5, tmp / "out-once")
recs = records()
s = json.loads((tmp / "out-once/summary-once.json").read_text()) if r.returncode == 0 else {}
overlap_all = max(d["t0"] for d in recs) < min(d["t1"] for d in recs) if recs else False
check("D2 once: the 5 searches run at once", len(recs) == 5 and overlap_all, r.stderr[-300:])
check("D2b once: the summary line (median, slowest, failed, timed out, unranked)",
      "5 at once:" in r.stdout and "failed 1, requests timed out (past 30 s) 1, unranked 1" in r.stdout
      and s.get("slowest_s", 0) >= s.get("median_s", 9), r.stdout[-400:])

# D3. the hidden-half rule: a hidden or memory-verdict or gov-os-eval folder is refused, nothing run
for bad in (tmp / "x/memory-verdict/hidden", tmp / "gov-os-eval/fixtures/visible"):
    bad.mkdir(parents=True)
    r = drive("alone", 1, tmp / "out-bad", questions=bad)
    check(f"D3 refused: {bad.relative_to(tmp)}", r.returncode != 0 and "refused" in r.stderr and not records(),
          r.stderr[-300:])

# D4. too few questions: stopped, not a short run
r = drive("alone", 7, tmp / "out-few")
check("D4 7 asked of 6: stopped", r.returncode != 0 and "6 questions" in r.stderr and not records(), r.stderr[-200:])

# P. the probe copy: the original's five shapes when unset; the 4B's bound when set
spec = importlib.util.spec_from_file_location("live_probe", HERE / "live_probe.py")
lp = importlib.util.module_from_spec(spec); spec.loader.exec_module(lp)
spec0 = importlib.util.spec_from_file_location("orig_probe", HERE.parent / "rerank-trial/rerank_trial_probe.py")
op = importlib.util.module_from_spec(spec0); spec0.loader.exec_module(op)
text = "".join(chr(97 + (i * 7) % 26) for i in range(60000))
check("P1 unset: the same shapes as the original probe", lp.shapes(text) == op.shapes(text))
b = lp.shapes(text, 12000, 8)
check("P2 the 4B's bound: counts 1, 2, 4, 8, each at most 12,000 padded", [len(t) for _, t in b] == [1, 2, 4, 8]
      and all(len(t) * (len(lp.QUERY) + max(map(len, t))) <= 12000 for _, t in b), [(n, len(t)) for n, t in b])


class Stand:
    def __init__(self, path, mode="ok"):
        self.sizes, self.mode = [], mode
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); self.s.bind(str(path)); self.s.listen(8)
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while True:
            try:
                c, _ = self.s.accept()
            except OSError:
                return
            with c:
                q, texts = json.loads(c.makefile("rb").readline())
                self.sizes.append(len(texts) * max(len(q) + len(t) for t in texts))
                ans = {"scores": [0.0] * len(texts)} if self.mode == "ok" else {"error": "no"}
                c.sendall((json.dumps(ans) + "\n").encode())


lp.gpu_used = lambda: 1000  # the GPU read replaced: no nvidia-smi in a test
lp.corpus = lambda: text
sock = tmp / "p.sock"
st = Stand(sock)
rc = lp.main(["p", str(sock), "peak", "--limit", "14255", "--bound", "12000", "--max-texts", "8"])
check("P3 peak at the 4B's bound: 4 shapes sent, each within 12,000, exit 0", rc == 0 and len(st.sizes) == 4
      and max(st.sizes) <= 12000, (rc, st.sizes))
sock2 = tmp / "p2.sock"
Stand(sock2, mode="error")
rc = lp.main(["p", str(sock2), "peak"])
check("P4 peak: a shape refused exits 5 (not a pass)", rc == 5, rc)
lp.gpu_used = lambda: 14255
rc = lp.main(["p", str(sock), "peak"])
check("P5 peak: the GPU at the limit stops before a shape (exit 3)", rc == 3, rc)
n = len(st.sizes)
rc = lp.main(["p", str(sock), "warm"])
check("P6 warm: one request of one short text, exit 0", rc == 0 and len(st.sizes) == n + 1
      and st.sizes[-1] == len(lp.QUERY) + len(lp.WARM_TEXT), (rc, st.sizes[n:]))
rc = lp.main(["p", str(sock2), "warm"])
check("P7 warm: not answered exits 5", rc == 5, rc)

print(f"{sum(results)} of {len(results)} passed")
sys.exit(0 if all(results) else 1)
