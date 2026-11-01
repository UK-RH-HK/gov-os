"""The resource gate (owner, DEC-942 item 2; memory rule DEC-947, changed by DEC-960 and DEC-961). Exit 0 if open,
1 if shut; prints one line with every figure and the reason.
    python3 gate_check.py              room for one more lead
    python3 gate_check.py --full-run   room for one full test run (a close's, the nightly's, a lead's) to start now
  load:   min(load1, load15) < nproc (a short peak does not hold launches; 15 minutes above nproc does, DEC-942 item 3)
  memory: MemAvailable + what the running leads hold >= floor + each running lead at what it uses (at least its
          working size) + the newcomer: one working size for a lead, one full run's measured peak for a full run.
          Nothing is set aside for a full run that has not started (owner, DEC-961): a full run checks this gate
          itself before it starts and waits until there is room. The figures are in gate-config.json.
A line ending "memory-only" means memory alone shut the gate while the CPU was idle (load1 < nproc / 2).
The disk gate is checked separately (disk_gate.sh)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lead_mem import snapshot  # noqa: E402

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gate-config.json")) as f:
    cfg = json.load(f)
floor, verify, work = cfg["floor_kb"], cfg["verification_peak_kb"], cfg["working_kb"]
s = snapshot()
nproc, (l1, _, l15) = s["nproc"], s["load"]
n = len(s["leads_kb"])
held = sum(s["leads_kb"].values())
have = s["mem_available_kb"] + held

full_run = "--full-run" in sys.argv
# Running leads count at what they use, at least their working size (a lead in its own full run counts at that
# run's size, so nothing is counted twice, DEC-960); a close's or the nightly's run is already out of MemAvailable.
running = sum(max(work, kb) for kb in s["leads_kb"].values())
newcomer = verify if full_run else work
need = floor + running + newcomer
load_ok = min(l1, l15) < nproc
mem_ok = have >= need
why = []
if not load_ok:
    why.append("load %.1f/%.1f >= nproc %d" % (l1, l15, nproc))
if not mem_ok:
    why.append("memory: available %d kB + leads' %d kB < need %d kB (floor %d, %d running lead(s) at %d, the new %s %d)"
               % (s["mem_available_kb"], held, need, floor, n, running, "full run" if full_run else "lead", newcomer))
tail = " memory-only" if (load_ok and not mem_ok and l1 < nproc / 2) else ""
print("%s%s leads=%d load=%.1f/%.1f nproc=%d have=%dkB need=%dkB%s%s" % (
    "OPEN" if load_ok and mem_ok else "SHUT", " full-run" if full_run else "", n, l1, l15, nproc, have, need,
    (": " + "; ".join(why)) if why else "", tail))
sys.exit(0 if load_ok and mem_ok else 1)
