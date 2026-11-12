"""ACT-DISPATCH-1's dry-tick rehearsal: the dispatcher run in a planted world (a planted repository, worktrees, briefs, a
copy of the live config.json, planted /proc-like inputs, a stub launcher) and never the live dispatch folder.

    python3 dry_tick.py <dispatcher.py> <work dir> <live config.json>

Three scenarios, each printed as plain lines (no head, pid or date), so the same run on the old and the new dispatcher
can be compared:
  CAP     five leads run (the live config's max_leads), six ready lines: a `tick --dry`; the sixth line's wait reason.
  IDLE    two leads run, four ready lines whose logs were used; real passes: one pass, a pass with the gate shut, the
          same cause again, a pass 7 hours later; the inbox items written and the reported file's cause.
  FORECAST three heavy slots held by low-load jobs (planted jobs-load.json), a quiet machine, one startable line: a
          `tick --dry`; whether the lead is admitted and the forecast's CPU term.
Exit 0 always (it only reports); the rehearsal's checker compares the lines."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TESTS = Path(__file__).resolve()
CLONE = Path(os.environ["DT_CLONE"])
sys.path.insert(0, str(CLONE / "tests/unit/orchestration"))
sys.dont_write_bytecode = True
import test_dispatcher as td  # noqa: E402  (the suite's planted-world helpers, not its tests)

TOOL, WORK, LIVE_CONFIG = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3])
NOW = td.NOW
GB = 1024 * 1024
N = 6


def world(name, config, procs, started=(), meminfo_gb=24):
    root = WORK / name
    shutil.rmtree(root, ignore_errors=True)
    repo, wt, orch = root / "repo", root / "wt", root / "orch"
    for p in (repo, wt):
        p.mkdir(parents=True)
    td.git(repo, "init", "-q", "-b", "w2/integrate")
    (repo / ".tickets").mkdir()
    for i in range(1, N + 1):
        (repo / ".tickets" / f"T-{i}.md").write_text(td.ticket(f"T-{i}", "in_progress"))
    td.git(repo, "add", "-A")
    td.git(repo, "commit", "-q", "-m", "tickets")
    for i in range(1, N + 1):
        td.git(repo, "worktree", "add", "-q", str(wt / f"W2-{i}"), "-b", f"w2/W2-{i}", "w2/integrate")
    for sub in ("log", "briefs", "dispatch", "tools", "merge-queue"):
        (orch / sub).mkdir(parents=True)
    for i in range(1, N + 1):
        (orch / "briefs" / f"B{i}.md").write_text("a brief\n")
    launcher, lander, calls = root / "launch.py", root / "land.py", root / "calls.txt"
    launcher.write_text(f"import sys\nopen({str(calls)!r}, 'a').write('launch ' + ' '.join(sys.argv[1:]) + '\\n')\n")
    lander.write_text("import sys\n")
    for f, txt in (("loadavg", "3.0 4.0 5.0 1/100 1\n"), ("meminfo", f"MemAvailable:   {meminfo_gb * GB} kB\n"),
                   ("procstat", td.PROCSTAT.format(busy=1150, iowait=0, idle=9000))):
        (root / f).write_text(txt)
    for d in ("proc", "slots"):
        (root / d).mkdir()
    (root / "proc" / "locks").write_text("")
    (root / "held.json").write_text("[]")
    (root / "procs.json").write_text(json.dumps(procs))
    (orch / "tools" / "gate-config.json").write_text(json.dumps({"floor_kb": 3 * GB}))
    (orch / "tools" / "heavy_slots.conf").write_text("SLOTS=3\nWORKERS=6\n")
    srv, mode = td.fake_embed_server()
    env = dict(os.environ, DISPATCH_ORCH=str(orch), DISPATCH_STATE=str(orch / "dispatch"), DISPATCH_REPO=str(repo),
               DISPATCH_PROCSTAT=str(root / "procstat"), DISPATCH_NPROC="20", DISPATCH_GUARD_CMD="true", DISPATCH_GUARD_SYNC="1",
               DISPATCH_EMBED_URL=mode["url"], DISPATCH_SLOT_GLOB=str(root / "slots/gov-os-heavy-slot-*.lock"),
               DISPATCH_PROC=str(root / "proc"), DISPATCH_NVIDIA_SMI=str(root / "nvidia-smi"),
               DISPATCH_GPU_LOG_SHARED=str(root / "s1.log"), DISPATCH_GPU_LOG_QUERY=str(root / "s2.log"),
               DISPATCH_SS=str(root / "ss"), DISPATCH_RERANK_GLOB=str(root / "rerank/gov-os-rerank-gpu-*.lock"),
               DISPATCH_GPU_SHARED_CMD=str(root / "shared-counter"), DISPATCH_RERANK_HOOK=str(td.plant_hook(root, td.OLD_HOOK)),
               DISPATCH_WORKTREES=str(wt), DISPATCH_FAKE_PROCS=str(root / "procs.json"), DISPATCH_FAKE_HELD=str(root / "held.json"),
               DISPATCH_GATE_CMD="echo OPEN", DISPATCH_DISK_CMD="true", DISPATCH_SLOTS_CONF=str(orch / "tools/heavy_slots.conf"),
               DISPATCH_LAUNCH_CMD=f"{sys.executable} {launcher}", DISPATCH_LAND_CMD=f"{sys.executable} {lander}",
               DISPATCH_LOADAVG=str(root / "loadavg"), DISPATCH_MEMINFO=str(root / "meminfo"), DISPATCH_NOW=str(NOW),
               DISPATCH_TEST="")
    d = orch / "dispatch"
    cfg = json.loads(Path(LIVE_CONFIG).read_text())  # the live configuration, copied (read only)
    cfg.update(config)
    (d / "config.json").write_text(json.dumps(cfg))
    (d / "started.txt").write_text("".join(f"{x}\n" for x in started))
    return type("W", (), dict(root=root, d=d, env=env, calls=calls, procs=root / "procs.json", srv=srv, orch=orch))


def lead(w2, i):
    return {"cmd": td.LEAD.format(f"T-{i}"), "pid": 100 + i, "cwd": str(WORK / "x"), "rss_kb": 300_000, "age_s": 5000}


def plant_lead_cwds(w, procs):
    for p, i in zip(procs, range(1, 99)):
        p["cwd"] = str(w.root / "wt" / f"W2-{p['pid'] - 100}")
    w.procs.write_text(json.dumps(procs))


def tick(w, *extra, now=NOW, **env):
    e = dict(w.env, DISPATCH_NOW=str(now), **{k: str(v) for k, v in env.items()})
    stat = Path(e["DISPATCH_PROCSTAT"])
    f = [int(x) for x in stat.read_text().splitlines()[0].split()[1:9]]
    busy, total = f[0] + f[1] + f[2] + f[5] + f[6] + f[7], sum(f[:8])
    (w.d / "cpu_prev.json").write_text(json.dumps({"t": now - 60, "busy": busy - 150, "total": total - 1000, "emb": {}}))
    r = subprocess.run([sys.executable, str(TOOL), "tick", *extra], capture_output=True, text=True, env=e)
    if r.returncode:
        print("tick failed:", r.stderr[-300:])
    return json.loads((w.d / "status.json").read_text())


def lines_of(path, skip=0):
    return [x[20:] for x in path.read_text().splitlines()[skip:]] if path.exists() else []


def idle_items(w):
    return sorted((w.d / "inbox").glob("*-idle-headroom*.txt")) if (w.d / "inbox").is_dir() else []


print("== CAP: five leads run, six ready lines, max_leads", json.loads(Path(LIVE_CONFIG).read_text()).get("max_leads"))
procs = [lead(f"W2-{i}", i) for i in range(1, 6)]
w = world("cap", {}, procs)
plant_lead_cwds(w, procs)
(w.d / "ready.txt").write_text("".join(f"W2-{i} T-{i} B{i}.md W2-{i}-A5-run1.json\n" for i in range(1, 7)))
s = tick(w, "--dry")
for k, v in s["ready_waits"].items():
    print(f"  {k}: {v}")
print("  leads running:", s["lead_count"], "| max_leads:", s["max_leads"], "| started this tick:", s["started_this_tick"])
print("  dispatch.log:", "; ".join(lines_of(w.d / "dispatch.log")) or "(nothing logged in a dry pass beyond its decision)")
w.srv.shutdown()

print("== IDLE: two leads run, four ready lines whose logs were used (cap read from the live config)")
procs = [lead(f"W2-{i}", i) for i in range(1, 3)]
started = [f"2026-11-11 {7 + i}:00:00 W2-{i} B{i}.md W2-{i}-A5-run1.json".replace(" 7:", " 07:").replace(" 8:", " 08:")
           .replace(" 9:", " 09:") for i in range(3, 7)]
w = world("idle", {}, procs, started)
plant_lead_cwds(w, procs)
(w.d / "ready.txt").write_text("".join(f"W2-{i} T-{i} B{i}.md W2-{i}-A5-run1.json\n" for i in range(3, 7)))
for label, kw in (("pass 1", {}), ("pass 2, one minute later", {"now": NOW + 60}),
                  ("pass 3, gate shut (idle does not hold)", {"now": NOW + 120, "DISPATCH_GATE_CMD": "false"}),
                  ("pass 4, gate open, same waiting set", {"now": NOW + 180}),
                  ("pass 5, 7 hours later", {"now": NOW + 7 * 3600})):
    s = tick(w, **kw)
    state = (w.d / "idle-headroom-reported.json")
    rec = json.loads(state.read_text()) if state.exists() and state.read_text().strip() else {}
    print(f"  {label}: inbox idle items {len(idle_items(w))}; remembered: "
          f"{rec.get('cause') or ('(old form) ' + ', '.join(sorted(rec))[:40] if rec else '(none)')}")
last = idle_items(w)[-1].read_text().splitlines() if idle_items(w) else []
print("  last item:", " | ".join(x[:150] for x in last[:3]))
print("  dispatch.log idle lines:", len([x for x in lines_of(w.d / "dispatch.log") if "idle with headroom" in x]))
w.srv.shutdown()

print("== FORECAST: three heavy slots held by low-load jobs (measured 0.05 cores for 10 minutes), one startable line")
slot = lambda n: {"cmd": f"flock -n -o /tmp/gov-os-heavy-slot-{n}.lock tail -f /dev/null", "pid": 600 + n, "ppid": 1,
                  "cwd": str(WORK), "age_s": 3000, "rss_kb": 50_000, "cpu_ticks": 100}
w = world("forecast", {}, [slot(n) for n in (1, 2, 3)], meminfo_gb=16)
(w.d / "ready.txt").write_text("W2-1 T-1 B1.md W2-1-A5-run1.json\n")
(w.d / "jobs-load.json").write_text(json.dumps({f"{600 + n}:test": {"first": NOW - 900, "s": [[NOW - 60 * (8 - k), 0.05] for k in range(8)]}
                                              for n in (1, 2, 3)}))
s = tick(w, "--dry")
cpu = s["forecast"]["lead"]["resources"]["cpu"]
print("  jobs:", ", ".join(f"{j['kind']} {j['phase']}" for j in s["jobs"]))
print("  forecast lead ok:", s["forecast"]["lead"]["ok"], "|", cpu["text"])
print("  the line:", s["ready_waits"].get("W2-1 T-1") or "startable (would start)",
      "| dispatch.log:", "; ".join(lines_of(w.d / "dispatch.log")) or "-")
w.srv.shutdown()
