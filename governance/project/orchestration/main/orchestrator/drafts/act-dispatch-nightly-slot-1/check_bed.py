import importlib.util, json, os, sys, tempfile, time
from pathlib import Path
S = Path("governance/project/orchestration/tools/dispatch/dispatcher.py").resolve()
T = Path(tempfile.mkdtemp())
orch, proc, slots, runs = T / "orch", T / "proc", T / "slots", T / "runs" / "nightly"
for p in (orch, proc, slots, runs / "20261113-0404", T / "wt"):
    p.mkdir(parents=True)
(proc / "locks").write_text("")
now = time.time()
os.environ.update(DISPATCH_ORCH=str(orch), DISPATCH_STATE=str(orch / "dispatch"), DISPATCH_PROC=str(proc),
                  DISPATCH_SLOT_GLOB=str(slots / "gov-os-heavy-slot-*.lock"), DISPATCH_NIGHTLY_RUNS=str(runs),
                  DISPATCH_NOW=str(now), DISPATCH_WORKTREES=str(T / "wt"), DISPATCH_REPO=str(T))
spec = importlib.util.spec_from_file_location("dispatcher_bed", S)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
LOCKED = "pos:\t0\nflags:\t0100001\nmnt_id:\t82\nino:\t7\nlock:\t1: FLOCK  ADVISORY  WRITE 0 08:30:7 0 EOF\n"
FREE = "pos:\t0\nflags:\t0100001\nmnt_id:\t82\nino:\t7\n"
SH = "/bin/bash /r/governance/project/orchestration/nightly/nightly.sh night"


def plant(marker_age=600, info=LOCKED, slot="gov-os-heavy-slot-1.lock", cwd=None, script=SH, parent=900):
    import shutil
    shutil.rmtree(proc / "900", ignore_errors=True)
    for sub in ("fd", "fdinfo"):
        (proc / "900" / sub).mkdir(parents=True)
    (slots / slot).write_text("")
    (proc / "900" / "fd" / "10").symlink_to(slots / slot)
    (proc / "900" / "fdinfo" / "10").write_text(info)
    m = orch / "NIGHTLY-RUNNING"
    m.unlink(missing_ok=True)
    if marker_age is not None:
        m.write_text("x\n")
        os.utime(m, (now - marker_age, now - marker_age))
    clone = str(runs / "20261113-0404")
    c = clone if cwd is None else cwd
    return [{"argv": script.split(), "cwd": clone, "pid": 900, "ppid": 1, "age_s": 1500, "rss_kb": 0},
            {"argv": "python3 -m pytest tests -n auto -q".split(), "cwd": c, "pid": 901, "ppid": parent, "age_s": 1200,
             "rss_kb": 0},
            {"argv": ["/usr/bin/python3", "-u", "-c", "x"], "cwd": c, "pid": 902, "ppid": 901, "age_s": 1190, "rss_kb": 0}]


def outside(facts):
    return " ".join(d.heavy_outside_slots(facts, 300))


bad = []
if outside(plant()) != "":
    bad.append("the nightly's run in its clone under its held slot is outside: " + outside(plant()))
for name, kw in (("no marker", dict(marker_age=None)), ("stale marker", dict(marker_age=360 * 60 + 1)),
                 ("no lock held", dict(info=FREE)), ("not a slot file", dict(slot="other.lock")),
                 ("outside the runs", dict(cwd=str(T / "wt"))), ("the runs root itself", dict(cwd=str(runs))),
                 ("not nightly.sh", dict(script="/bin/bash /r/x/nightly/other.sh night")),
                 ("not its child", dict(parent=1))):
    if "pid 901" not in outside(plant(**kw)):
        bad.append(f"{name}: the run counted as in a slot")
other = plant() + [{"argv": "python3 -m gov.context.context_check".split(), "cwd": str(T / "wt"), "pid": 500, "ppid": 1,
                    "age_s": 400, "rss_kb": 0}]
if "pid 500" not in outside(other) or "pid 901" in outside(other):
    bad.append("a heavy step elsewhere is not named beside the nightly: " + outside(other))
slot = [{"argv": "bash /x/tools/heavy_slot.sh python3 -m gov.context.context_check".split(), "cwd": "/", "pid": 600,
         "ppid": 1, "age_s": 900, "rss_kb": 0},
        {"argv": "python3 -m gov.context.context_check".split(), "cwd": str(T / "wt"), "pid": 601, "ppid": 600,
         "age_s": 900, "rss_kb": 0}]
if outside(slot) != "":
    bad.append("a step under heavy_slot.sh is outside: " + outside(slot))
import shutil
shutil.rmtree(T)
print("; ".join(bad) or "dispatcher: the nightly's run counts as in a slot only with all three (its clone, a fresh "
      "marker, nightly.sh holding a slot); each missing one, and any other heavy step, stays outside")
sys.exit(1 if bad else 0)
