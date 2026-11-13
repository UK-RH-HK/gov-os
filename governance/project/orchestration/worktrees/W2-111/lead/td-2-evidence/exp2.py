"""Scratch experiment 2 (W2-111 run 2): real hooks (W1-02 engineer-allow, W2-57-like designer read) beside reference jobs,
interleaved one-for-one; CPU = RUSAGE_CHILDREN delta, wall = perf_counter.
usage: python3 exp2.py <label> <iterations> [loop150]"""
import json, os, resource, subprocess, sys, tempfile, time, statistics as st
from pathlib import Path

W = Path("/home/usain/gov-os-worktrees/W2-111-tests")
sys.path.insert(0, str(W / "tests/acceptance/W1-02"))
import w1_02_support as S

label, iters = sys.argv[1], int(sys.argv[2])
LOOP = int(os.environ.get("EXP_LOOP", "400000"))
L150 = int(os.environ.get("EXP_L150", "1500000"))


def cpu():
    u = resource.getrusage(resource.RUSAGE_CHILDREN)
    return u.ru_utime + u.ru_stime


def timed(argv, stdin=None):
    c0, t0 = cpu(), time.perf_counter()
    subprocess.run(argv, input=stdin, capture_output=True, text=True)
    return cpu() - c0, time.perf_counter() - t0

STUB = ("import sys,json\nd=json.load(sys.stdin)\n"
        "print(json.dumps({'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'allow'}}))")
REFS = {
    "stub": [sys.executable, "-c", STUB],
    "start": [sys.executable, "-c", "pass"],
    "loop": [sys.executable, "-c", f"x=0\nfor i in range({LOOP}):\n x+=i*i%7"],
    "mix": [sys.executable, "-c",
            "import json,re,subprocess,pathlib,hashlib,ast,dataclasses,argparse\n"
            "subprocess.run(['git','--version'],capture_output=True)\n"
            f"x=0\nfor i in range({LOOP//4}):\n x+=i*i%7"],
    "plant150": [sys.executable, "-c", f"x=0\nfor i in range({L150}):\n x+=i*i%7"],
}

base = Path(tempfile.mkdtemp(prefix="exp2-"))
sandbox = S.make_sandbox(base / "sandbox")
project = S.make_project(base / "project")
S.git(project, "branch", "-m", "main", "w2/integrate")
S.git(project, "checkout", "-q", "-b", f"w2/{S.TICKET_WBS_ID}")
for k in range(120):
    (project / "src/gov/guard" / f"change_{k:03d}.py").write_text(f"VALUE = {k}\n")
S.git(project, "add", "-A"); S.git(project, "commit", "-q", "-m", "work")

def hook_eng():
    r = S.run_hook(project, "Write", S.edit_tool_input("Write", project / "src/gov/guard/decide.py"), sandbox,
                   role=S.ENGINEER, ticket=S.TICKET_ID)
    assert r.decision == "allow", r.describe(); return r.cpu_seconds, r.seconds

def hook_des():
    r = S.run_hook(project, "Read", {"file_path": str(project / "README.md")}, sandbox,
                   role=S.TEST_DESIGNER, ticket=S.TICKET_ID)
    assert r.decision == "allow", r.describe(); return r.cpu_seconds, r.seconds

HOOKS = {"hook_eng": hook_eng, "hook_des": hook_des}
for _ in range(3):
    for f in HOOKS.values(): f()
    for a in REFS.values(): timed(a, stdin="{}")
rows = []
for i in range(iters):
    row = {"i": i, "t": time.time(), "la": open("/proc/loadavg").read().split()[0]}
    for name, argv in REFS.items(): row[name] = timed(argv, stdin="{}")
    for name, f in HOOKS.items(): row[name] = f()
    rows.append(row)
out = W / f".gov-runtime/scratch/td/exp2-{label}.json"
out.write_text(json.dumps({"loop": LOOP, "l150": L150, "rows": rows, "load_end": open("/proc/loadavg").read()}))
def p95(v):
    v = sorted(v); return v[max(0, -(-95 * len(v) // 100) - 1)]
print(label, "load_end", open("/proc/loadavg").read().strip(), "affinity", len(os.sched_getaffinity(0)))
for name in list(REFS) + list(HOOKS):
    c = [r[name][0] * 1000 for r in rows]; w = [r[name][1] * 1000 for r in rows]
    print(f"{name:9} cpu ms: min {min(c):6.1f} p05 {sorted(c)[len(c)//20]:6.1f} med {st.median(c):6.1f} p95 {p95(c):6.1f} | wall med {st.median(w):6.1f} p95 {p95(w):6.1f}")
import shutil; shutil.rmtree(base, ignore_errors=True)
