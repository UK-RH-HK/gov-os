"""ACT-DISPATCH-1's behaviour check of the forecast's CPU term (run from the repository root with `python3 -I - < this file`,
in the manifest as a here-document). Imports balancer.py (pure functions, no file read or written) and asks the forecast
for a lead start beside three held heavy slots, 3.0 cores busy of the band's 18. Prints 4 and exits 0 when: with no
measure the slots count at their whole peak and the start is refused on CPU; the same slots measured at 0.05 cores count at
the floor and the start is admitted; a slot measured at 5.5 cores is still counted at that; the switch off (no floor) keeps
the whole peak."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path("governance/project/orchestration/tools/dispatch").resolve()))
import balancer as lb  # noqa: E402

GB = 1024 * 1024
pk = lb.phase_peaks([])


def slot(cpu, recent=None):
    j = {"kind": "slot", "name": "pid 1", "phase": "test", "cpu": cpu, "rss_kb": GB, "rr": 0}
    if recent is not None:
        j["recent_cpu"] = recent
    return j


def ask(jobs, **kw):
    s = {"busy_cores": 3.0, "band_hi": 18, "mem_available_kb": 16 * GB, "floor_kb": 3 * GB,
         "gpu": {"used_mib": 5734, "total_mib": 16303}, "headroom_mib": 2048, "rr_held": 0, "rr_slots": 2, "jobs": jobs}
    s.update(kw)
    return lb.forecast(s, pk, "lead")


quiet = [slot(0.05, 0.05), slot(0.8, 0.8), slot(0.03, 0.03)]
a = ask([slot(0.05), slot(0.8), slot(0.03)], held_floor=1.0)
assert not a["ok"] and a["binding"] == "CPU", a["reason"]
b = ask(quiet, held_floor=1.0)
assert b["ok"] and b["resources"]["cpu"]["need"] < 9 and "3 of them at their measured load" in b["resources"]["cpu"]["text"], b["reason"]
c = ask([slot(0.05, 5.5), slot(0.8, 0.8), slot(0.03, 0.03)], held_floor=1.0)
assert c["resources"]["cpu"]["need"] > b["resources"]["cpu"]["need"] + 4, c["reason"]
e = ask(quiet)
assert not e["ok"] and e["resources"]["cpu"]["need"] == a["resources"]["cpu"]["need"], e["reason"]
print(4)
