#!/usr/bin/env python3
"""P2-PERF-0001 per-family sweep.

Runs every certification family as its OWN process with --test-threads=1, in a bounded
pool of K concurrent families. Rationale:

  * --test-threads=1 inside a family makes per-test line-arrival deltas a SOUND measure
    of that test's duration (no intra-family overlap).
  * separate processes across families let the 20 cores be used, so the whole 244-test
    suite is measured in roughly serial_wall/K instead of the ~8035 s a single serial
    run costs (P2-AR-0069).
  * the contention this introduces is QUANTIFIED, not assumed: `brownfield` was measured
    alone first (318.45 s clean), and is re-measured inside the pool. The ratio is the
    contention factor reported alongside every number.

Isolation argument for running families as concurrent processes: each test builds its
scratch root via common::tmp(), whose name contains the PID and a nanosecond clock, and
derives XDG_STATE_HOME per repository root (common::machine_state_home, sha256 of the
root path). Distinct processes therefore cannot collide on either. This is the same
per-project-not-per-process property the suite already relies on for its threads.

Load average is sampled every 5 s throughout and stored, so any number can be checked
against the machine load at the time it was produced.
"""
import json
import os
import subprocess
import sys
import threading
import time

BIN = sys.argv[1]
OUT = sys.argv[2]
K = int(sys.argv[3])
PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timed_run.py")

# Families ordered longest-first (static `gov` invocation-site count as the packing
# heuristic), so the pool drains evenly and the tail is short.
FAMILIES = [
    "repair", "ws03", "repair2", "ws05r3", "srr", "migration", "repair3", "ws04r3",
    "ws05", "ws03_r3", "r4_residual", "ws04r2", "ws08_r2", "ws06r3", "ws08_r3", "ws07",
    "ws06", "integration_r3", "ws08", "failure_injection", "greenfield", "upstream",
    "brownfield", "section6", "r2_f3", "update", "r2_wsa", "r2_toolbind",
    "r2_failclosed", "r2_wse", "multi_machine", "r2_wsc", "arch", "ws01r4", "r2_wsd",
    "r2_wsb", "r2_wsg", "r2_wsf",
]

os.makedirs(OUT, exist_ok=True)
lock = threading.Lock()
queue = list(FAMILIES)
results = []
stop_sampler = threading.Event()


def sampler():
    with open(f"{OUT}/loadavg.tsv", "w") as f:
        f.write("epoch\tload1\tload5\tload15\n")
        while not stop_sampler.is_set():
            with open("/proc/loadavg") as lf:
                p = lf.read().split()
            f.write(f"{time.time():.0f}\t{p[0]}\t{p[1]}\t{p[2]}\n")
            f.flush()
            stop_sampler.wait(5)


def worker(wid):
    while True:
        with lock:
            if not queue:
                return
            fam = queue.pop(0)
        t0 = time.time()
        env = dict(os.environ)
        env["TMPDIR"] = "/tmp"  # ext4, the default condition
        rc = subprocess.run(
            [sys.executable, PY, f"fam-{fam}", OUT, "serial", BIN,
             "--test-threads=1", f"{fam}::"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
        ).returncode
        dt = time.time() - t0
        with lock:
            results.append((fam, rc, round(dt, 1)))
            print(f"[{len(results):2d}/{len(FAMILIES)}] {fam:<20} "
                  f"wall={dt:7.1f}s rc={rc} load={open('/proc/loadavg').read().split()[0]}",
                  flush=True)


ts = threading.Thread(target=sampler, daemon=True)
ts.start()
start = time.time()
threads = [threading.Thread(target=worker, args=(i,)) for i in range(K)]
for t in threads:
    t.start()
for t in threads:
    t.join()
stop_sampler.set()
total = time.time() - start

with open(f"{OUT}/sweep-summary.json", "w") as f:
    json.dump({"pool_size": K, "total_wall_s": round(total, 1),
               "families": [{"family": f, "rc": r, "wall_s": d} for f, r, d in results]},
              f, indent=2)
print(f"\nSWEEP TOTAL WALL: {total:.1f}s with pool K={K}")
bad = [r for r in results if r[1] != 0]
print("NON-ZERO EXIT FAMILIES:", bad if bad else "none")
