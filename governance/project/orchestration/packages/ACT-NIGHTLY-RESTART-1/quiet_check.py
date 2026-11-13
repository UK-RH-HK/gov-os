#!/usr/bin/env python3
"""Is anything else running on this machine? (ACT-NIGHTLY-RESTART-1; DEC-1132 (4): "in the quiet hours, with nothing
else running".) Reads only; prints one reason a line and exits 1 when anything runs, prints "quiet" and exits 0 when
nothing does. Standard library only.

    quiet_check.py [--no-load] [--own-off]   --no-load leaves out the load test, --own-off accepts dispatch/OFF as the
                                     wrapper's own (its second look, just after it wrote the switch; the status is then not read)

What counts as something else running (each from a source that already exists on this machine):
  - a lead, a landing, a close, a rebuild or any other job: the dispatcher's own status.json (its truth since DEC-1008:
    lead_count, jobs, land_running, close_running, queue_busy, outside_slot, pending_launches, slots_held), which must
    be fresh (3 minutes) unless the dispatcher is switched OFF by the CTO (then the CTO's hold is the reason);
  - the same, seen without the dispatcher: a process working in a ticket worktree, in the runs, evaluation or walled-
    session folders, or running close_build.py, land.py, merge_queue.py, heavy_slot.sh, rebuild_slot.sh, launch_worker.sh,
    launch_now.sh, operator_run.py, `gov rebuild` or pytest (this process's own chain left out);
  - a heavy-job slot, a rebuild lock or the merge queue's lock held (each probed without waiting, then let go);
  - the marker files: NIGHTLY-RUNNING (another nightly), CLOSE-RUNNING, log/act-in-progress.txt (an ACT), the operator's
    commit freeze (install/act-in-progress.txt), MEASURE-RUNNING (a memory measure: the convention a measure writes;
    nothing writes it today, see the ACT);
  - the main tree: a merge in progress, any change, or w2/integrate's head under 5 minutes old (nightly.sh's own rule);
  - the load: 1-minute load average of 3 or more (the day-mode bar of nightly.sh), unless --no-load;
  - more than 100 rg processes (DEC-1132 (3): the 11-11 storm).
Test hooks (never set by cron): NR_ORCH, NR_REPO, NR_STATUS, NR_SLOT_DIR, NR_REBUILD_GLOB, NR_OPERATOR_FREEZE, NR_PROC (a
JSON list of {"cmd", "cwd"}), NR_LOAD, NR_RG_COUNT, NR_NOW.
"""
import fcntl
import glob
import json
import os
import subprocess
import sys
import time
from datetime import datetime

E = os.environ.get
REPO = E("NR_REPO", "/home/usain/Dynamic-Agentic-Engineering-OS")
ORCH = E("NR_ORCH", REPO + "/.gov-runtime/scratch/orchestrator")
STATUS = E("NR_STATUS", ORCH + "/dispatch/status.json")
SLOT_DIR = E("NR_SLOT_DIR", "/tmp")
REBUILD_GLOB = E("NR_REBUILD_GLOB", "/tmp/gov-os-rebuild*.lock")
OP_FREEZE = E("NR_OPERATOR_FREEZE", "/home/usain/gov-os-operator/install/act-in-progress.txt")
HOME = "/home/usain"
STATUS_MAX_AGE_S = 180
HEAD_MIN_AGE_S = 300
LOAD_BAR = 3.0
RG_MAX = 100
# folders whose processes are somebody else's work; the store worktrees are the integration store's refresh, not a lead
BUSY_ROOTS = (HOME + "/gov-os-worktrees/", HOME + "/gov-os-runs/", HOME + "/gov-os-eval/", HOME + "/gov-os-writer/",
              HOME + "/gov-os-checker/", HOME + "/gov-os-wall-trees/")
NOT_A_JOB = ("W2-00-store",)   # a worktree folder name starting with this is the store's, not a lead's
OWN_RUNS = HOME + "/gov-os-runs/W2-00/nightly/"   # the nightly's own clones
JOB_SCRIPTS = ("close_build.py", "land.py", "merge_queue.py", "heavy_slot.sh", "rebuild_slot.sh", "launch_worker.sh",
               "launch_now.sh", "operator_run.py")


def now():
    return float(E("NR_NOW") or time.time())


def own_chain():
    pids, p = set(), os.getpid()
    while p > 1:
        pids.add(p)
        try:
            p = int(next(l.split()[1] for l in open(f"/proc/{p}/status") if l.startswith("PPid:")))
        except (OSError, StopIteration, ValueError):
            break
    return pids


def processes():
    fake = E("NR_PROC")
    if fake is not None:
        return [(0, p["cmd"].split(), p.get("cwd", "")) for p in json.load(open(fake))]
    skip, out = own_chain(), []
    for d in glob.glob("/proc/[0-9]*"):
        pid = int(d.rsplit("/", 1)[1])
        if pid in skip:
            continue
        try:
            argv = [a.decode("utf-8", "replace") for a in open(d + "/cmdline", "rb").read().split(b"\0") if a]
            cwd = os.readlink(d + "/cwd")
        except OSError:
            continue
        if argv:
            out.append((pid, argv, cwd))
    return out


def process_reasons():
    out = []
    for pid, argv, cwd in processes():
        head = argv[:4]
        base = [os.path.basename(a) for a in head]
        why = None
        if any(cwd.startswith(r) for r in BUSY_ROOTS) and not cwd.startswith(OWN_RUNS):
            first = cwd[len(next(r for r in BUSY_ROOTS if cwd.startswith(r))):].split("/")[0]
            if not first.startswith(NOT_A_JOB):
                why = f"a process works in {cwd}"
        if why is None and any(b in JOB_SCRIPTS for b in base):
            why = "a job script runs: " + " ".join(base[:3])
        prog = os.path.basename(argv[0])
        is_py = prog.startswith("python")
        module = argv[argv.index("-m") + 1] if is_py and "-m" in argv[1:5] and argv.index("-m") + 1 < len(argv) else ""
        script = os.path.basename(argv[1]) if is_py and len(argv) > 1 else ""
        if why is None and (prog in ("pytest", "py.test") or module == "pytest" or script in ("pytest", "py.test")):
            why = "a test run: " + " ".join(argv[:4])[:100]
        if why is None and ((module == "gov.cli.main" and "rebuild" in argv[1:8]) or (prog == "gov" and "rebuild" in argv[1:3])):
            why = "a rebuild: " + " ".join(argv[:5])[:100]
        if why:
            out.append(f"{why} (pid {pid})" if pid else why)
    return out[:8]


def status_reasons(own_off=False):
    off = os.path.exists(os.path.join(os.path.dirname(STATUS), "OFF"))
    if off and not own_off:
        return ["the dispatcher is switched OFF (the CTO's hold: dispatch/OFF)"]
    if off:   # the wrapper's own switch is there (its second look): the status file is not refreshed while it is
        return []
    try:
        s = json.load(open(STATUS))
        age = now() - datetime.strptime(s["time"], "%Y-%m-%d %H:%M:%S").timestamp()
    except (OSError, ValueError, KeyError):
        return ["the dispatcher's status cannot be read: leads cannot be counted"]
    if age > STATUS_MAX_AGE_S:
        return [f"the dispatcher's status is {int(age)} s old (over {STATUS_MAX_AGE_S}): leads cannot be counted"]
    out = []
    if s.get("lead_count"):
        out.append(f"{s['lead_count']} lead(s) running: {', '.join(map(str, s.get('leads', [])))[:80]}")
    for j in s.get("jobs") or []:
        out.append(f"job {j.get('kind')} {j.get('name')} ({j.get('phase')})")
    for key, text in (("land_running", "a landing runs"), ("close_running", "a close runs"),
                      ("queue_busy", "the merge queue is busy"), ("outside_slot", "a heavy step runs outside a slot"),
                      ("pending_launches", "a lead is launching")):
        if s.get(key):
            out.append(text)
    if s.get("slots_held"):
        out.append("heavy slot(s) held: " + ", ".join(s["slots_held"]))
    return out


def lock_busy(path):
    try:
        fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return False
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except OSError:
        return True
    finally:
        os.close(fd)


def lock_reasons():
    out = [f"heavy slot {n} is held" for n in (1, 2, 3) if lock_busy(f"{SLOT_DIR}/gov-os-heavy-slot-{n}.lock")]
    out += [f"a rebuild lock is held: {os.path.basename(p)}" for p in sorted(glob.glob(REBUILD_GLOB)) if lock_busy(p)]
    rl = ORCH + "/merge-queue/run.lock"
    if os.path.exists(rl) and lock_busy(rl):
        out.append("the merge queue's run lock is held")
    return out


def file_reasons():
    out = []
    for name, text in (("NIGHTLY-RUNNING", "another nightly holds NIGHTLY-RUNNING"), ("CLOSE-RUNNING", "a close is running (CLOSE-RUNNING)"),
                       ("MEASURE-RUNNING", "a memory measure is running (MEASURE-RUNNING)"),
                       ("log/act-in-progress.txt", "an ACT is in progress (log/act-in-progress.txt)")):
        if os.path.exists(os.path.join(ORCH, name)):
            out.append(text)
    if os.path.exists(OP_FREEZE):
        out.append("the operator's commit freeze exists (install/act-in-progress.txt)")
    return out


def git(*a):
    r = subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout


def tree_reasons():
    out = []
    if os.path.exists(REPO + "/.git/MERGE_HEAD"):
        out.append("a merge is in progress in the main tree")
    try:
        rc, dirty = git("status", "--porcelain")
        if rc == 0 and dirty.strip():
            out.append("the main tree is not clean")
        rc, ct = git("log", "-1", "--format=%ct", "w2/integrate")
        if rc == 0 and now() - int(ct) < HEAD_MIN_AGE_S:
            out.append("w2/integrate's head is under 5 minutes old")
    except (subprocess.SubprocessError, ValueError):
        out.append("the main tree cannot be read")
    return out


def rg_count():
    if E("NR_RG_COUNT") is not None:
        return int(E("NR_RG_COUNT"))
    n = 0
    for d in glob.glob("/proc/[0-9]*/comm"):
        try:
            n += open(d).read().strip() == "rg"
        except OSError:
            pass
    return n


def main(argv):
    reasons = status_reasons("--own-off" in argv) + process_reasons() + lock_reasons() + file_reasons() + tree_reasons()
    if "--no-load" not in argv:
        try:
            load = float(E("NR_LOAD") or open("/proc/loadavg").read().split()[0])
        except (OSError, ValueError):
            load = 0.0
        if load >= LOAD_BAR:
            reasons.append(f"load {load:.1f} (the bar is {LOAD_BAR:.0f})")
    n = rg_count()
    if n > RG_MAX:
        reasons.append(f"{n} rg processes (over {RG_MAX})")
    if reasons:
        print("\n".join(dict.fromkeys(reasons)))
        return 1
    print("quiet")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
