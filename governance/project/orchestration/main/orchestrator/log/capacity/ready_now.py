"""CAPACITY-1: how many of Wave 2's remaining tickets are ready to start now, and what holds each of the rest.
State read 2026-10-31 15:20 (processes, chain log, close log); dependencies and paths from tickets.json."""
import json
import os

import sim

HERE = os.path.dirname(os.path.abspath(__file__))
t = json.load(open(os.path.join(HERE, "tickets.json")))
by = {v["wbs"]: v for v in t.values()}
nodes = sim.build()

RUNNING = {"W2-67", "W2-05", "W2-95", "W2-96", "W2-107"}           # lead processes at 15:20
RETURNED = {"W2-108": "returned PACKAGES: built and accepted, its scoped check held 90 min by the load gate"}
CLOSING = {"W2-106", "W2-84", "W2-76", "W2-49"}                    # batch of four, refused 15:19 (11 reds)
MERGED = {"W2-16"}
QUEUED = {"W2-110", "W2-105", "W2-52", "W2-109"}                   # in the launch chain, waiting on the gate
SEQ = {  # sequencing rules that are not depends_on lines (PLAN-GROWTH-1, WBS, DEC-957, K9)
    "W2-60a": "after W2-11 round 1 (DEC-957; W2-33 r1 before its merge)",
    "W2-13": "memory chain: after W2-108 (same files)",
    "W2-33": "after W2-11 (r1)",
    "W2-100": "after ACT 2", "W2-101": "after ACT 2",
    "W2-23": "after W2-52", "W2-83a": "after W2-52",
    "W2-60b": "launcher.py chain: after W2-60a", "W2-82": "launcher.py chain: after W2-60b",
    "W2-21": "launcher.py chain: after W2-82",
    "W2-55": "src/gov/context/** shared: after W2-04",
    "W2-91": "after W2-86",
    "W2-27": "K9: EXAMIN's copy after all its 43 dependencies and the three layers",
}
active = RUNNING | set(RETURNED) | CLOSING | MERGED | QUEUED
rows = []
for w, n in sorted(nodes.items()):
    if not w.startswith("W2"):
        continue
    v = by[w]
    if w in RUNNING:
        rows.append((w, "running", "lead running now"))
        continue
    if w in RETURNED:
        rows.append((w, "running", RETURNED[w]))
        continue
    if w in CLOSING:
        rows.append((w, "closing", "in the batch of four; close refused 15:19, 11 reds traced to the batch"))
        continue
    if w in MERGED:
        rows.append((w, "closing", "merged, not yet closed"))
        continue
    open_deps_w = sorted(d for d in n["deps"] if d.startswith("W2") and d not in CLOSING | MERGED)
    stack_only = open_deps_w == [] and any(d in CLOSING | MERGED for d in n["deps"])
    if open_deps_w:
        rows.append((w, "dependency", ", ".join(open_deps_w[:6]) + (" ..." if len(open_deps_w) > 6 else "")
                     + f" ({len(open_deps_w)} open)"))
        continue
    if w in SEQ:
        rows.append((w, "sequencing", SEQ[w]))
        continue
    clash = sorted(h for h in active if h in nodes and h != w and sim.overlap(n["paths"], nodes[h]["paths"]))
    if clash:
        rows.append((w, "paths", "shares files with " + ", ".join(clash)))
        continue
    if w in QUEUED:
        rows.append((w, "ready (queued)", "in the launch chain; the load gate holds it"))
        continue
    rows.append((w, "ready", v["status"] + (" (stacked on a merged, closing base, DEC-786)" if stack_only else "")))

from collections import Counter
c = Counter(r[1] for r in rows)
print("remaining", len(rows), dict(c))
for r in rows:
    print(f"{r[0]:8s} {r[1]:15s} {r[2]}")
json.dump(rows, open(os.path.join(HERE, "ready_now.json"), "w"), indent=1)
