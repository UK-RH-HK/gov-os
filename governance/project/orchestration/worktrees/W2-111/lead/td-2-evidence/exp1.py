"""Scratch experiment (W2-111 run 2): the real W1-02 hook beside candidate reference jobs, interleaved one-for-one.
usage: python3 exp1.py <label> <iterations>   (run through heavy_slot.sh; writes td/exp1-<label>.json)"""
import json, os, resource, subprocess, sys, tempfile, time
from pathlib import Path

W = Path("/home/usain/gov-os-worktrees/W2-111-tests")
sys.path.insert(0, str(W / "tests/acceptance/W1-02"))
import w1_02_support as S

label, iters = sys.argv[1], int(sys.argv[2])
LOOP = int(os.environ.get("EXP_LOOP", "400000"))


def cpu():
    u = resource.getrusage(resource.RUSAGE_CHILDREN)
    return u.ru_utime + u.ru_stime


def timed(argv, **kw):
    c0, t0 = cpu(), time.perf_counter()
    subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, **kw)
    return cpu() - c0, time.perf_counter() - t0


REFS = {
    "start": [sys.executable, "-c", "pass"],
    "loop": [sys.executable, "-c", f"x=0\nfor i in range({LOOP}):\n x+=i*i%7"],
    "mix": [sys.executable, "-c",
            "import json,re,subprocess,pathlib,hashlib,ast,dataclasses,argparse\n"
            "subprocess.run(['git','--version'],capture_output=True)\n"
            f"x=0\nfor i in range({LOOP//4}):\n x+=i*i%7"],
}

base = Path(tempfile.mkdtemp(prefix="exp1-"))
sandbox = S.make_sandbox(base / "sandbox")
project = S.make_project(base / "project")


def hook():
    r = S.run_hook(project, "Write", S.edit_tool_input("Write", project / "src/gov/guard/decide.py"), sandbox,
                   role=S.ENGINEER, ticket=S.TICKET_ID)
    assert r.decision == "allow", r.describe()
    return r.cpu_seconds, r.seconds


for _ in range(3):
    hook()
    for a in REFS.values():
        timed(a)
rows = []
for i in range(iters):
    row = {"i": i, "t": time.time()}
    for name, argv in REFS.items():
        row[name] = timed(argv)
    row["hook"] = hook()
    rows.append(row)
out = W / f".gov-runtime/scratch/td/exp1-{label}.json"
out.write_text(json.dumps({"loop": LOOP, "load": open("/proc/loadavg").read(), "rows": rows}))
import statistics as st
def p95(v):
    v = sorted(v); return v[max(0, -(-95 * len(v) // 100) - 1)]
print(label, "load", open("/proc/loadavg").read().strip(), "affinity", len(os.sched_getaffinity(0)))
for name in list(REFS) + ["hook"]:
    c = [r[name][0] * 1000 for r in rows]; w = [r[name][1] * 1000 for r in rows]
    print(f"{name:6} cpu ms: min {min(c):6.1f} med {st.median(c):6.1f} p95 {p95(c):6.1f} | wall med {st.median(w):6.1f} p95 {p95(w):6.1f}")
import shutil; shutil.rmtree(base, ignore_errors=True)
