"""The resource gate for one more lead, measured on WSL as it is (owner, DEC-942 item 2; memory rule DEC-947). Exit 0
if open, 1 if shut; prints one line with every figure and the reason.
  load:   min(load1, load15) < nproc (a short peak does not hold launches; 15 minutes above nproc does, DEC-942 item 3)
  memory: MemAvailable + what the running leads already hold >= floor + one verification run's peak (reserved once:
          the verification lock lets one full test run happen at a time) + a working size for each running lead and
          for the new one. The three figures are in gate-config.json, re-measured weekly.
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
need = floor + verify + (n + 1) * work
load_ok = min(l1, l15) < nproc
mem_ok = have >= need
why = []
if not load_ok:
    why.append("load %.1f/%.1f >= nproc %d" % (l1, l15, nproc))
if not mem_ok:
    why.append("memory: available %d kB + leads' %d kB < floor %d + verification %d + %d x working %d kB" % (
        s["mem_available_kb"], held, floor, verify, n + 1, work))
tail = " memory-only" if (load_ok and not mem_ok and l1 < nproc / 2) else ""
print("%s leads=%d load=%.1f/%.1f nproc=%d have=%dkB need=%dkB%s%s" % (
    "OPEN" if load_ok and mem_ok else "SHUT", n, l1, l15, nproc, have, need, (": " + "; ".join(why)) if why else "", tail))
sys.exit(0 if load_ok and mem_ok else 1)
