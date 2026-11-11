#!/usr/bin/env python3
"""The memory guard (DRAFT for the maintenance window; MEMORY-PROTECTION-1, layer 2).

Why: on 11-11 at 14:18 about 2,161 ripgrep (rg) processes of about 9 MB each used the whole 24 GB; the kernel chose the
biggest single process (the editor server, 873 MB) instead, which freed nothing, and WSL went down. This guard looks once a
second and deals with that one failure early, before the kernel is involved. It never touches a Gov OS session, server,
lead, test run or the editor: only `rg`.

What it does (all thresholds are environment settings, MG_*):
  level 1 WATCH  more than 100 rg, or memory stall (PSI "full" avg10) above 1 %: one inbox item (P2), at most every 10 min.
  level 2 MARK   more than 150 rg, or (20+ rg and available memory under 5 GiB, or stall above 5 %): every rg gets
                 oom_score_adj 1000, so if the kernel does have to kill, it kills an rg first. An unprivileged process may
                 raise this value for its own processes, never lower it below 0 (tested).
  level 3 STOP   more than 300 rg, or (50+ rg and available memory under 3 GiB, or stall above 20 %): SIGKILL every rg,
                 by pid (taken from /proc, exe name checked, same user, start time re-checked just before the kill), one
                 inbox item (P1) with the parents (pid, command, cwd) and the exe path so the spawner is known. Only when
                 MG_STOP=1 (the owner's decision D1: it is a stop chosen by the program's name, an exception to L-0075).
  separately     available memory under 3 GiB with few rg, or any one program name with 400+ processes: one inbox item (P1)
                 with the top memory users and per-name totals. Alert only: nothing is killed.
Everything is logged to log/mem-guard.txt; the file log/mem-guard.alive is touched every 10 s (the recovery check).

Run:  python3 -I mem_guard.py            (loop)       python3 -I mem_guard.py --once [--dry-run]
      python3 -I mem_guard.py --selftest (no /proc writes)
Rehearsal: MG_CGROUP=<scope cgroup dir> MG_LIMIT_MB=<n> reads that cgroup instead of the machine; MG_INBOX / MG_LOG / MG_ALIVE
point the outputs at a throwaway folder.
"""
import json
import os
import signal
import sys
import time

ORCH = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"


def env(name, default, cast=float):
    v = os.environ.get(name)
    return cast(v) if v not in (None, "") else default


CFG = {
    "period": env("MG_PERIOD", 1.0),
    "watch_rg": env("MG_WATCH_RG", 100, int),
    "mark_rg": env("MG_MARK_RG", 150, int),
    "stop_rg": env("MG_STOP_RG", 300, int),
    "mark_min_rg": env("MG_MARK_MIN_RG", 20, int),
    "stop_min_rg": env("MG_STOP_MIN_RG", 50, int),
    "mark_avail_kb": env("MG_MARK_AVAIL_GB", 5.0) * 1048576,
    "stop_avail_kb": env("MG_STOP_AVAIL_GB", 3.0) * 1048576,
    "low_avail_kb": env("MG_LOW_AVAIL_GB", 3.0) * 1048576,
    "psi_watch": env("MG_PSI_WATCH", 1.0),
    "psi_mark": env("MG_PSI_MARK", 5.0),
    "psi_stop": env("MG_PSI_STOP", 20.0),
    "name_storm": env("MG_NAME_STORM", 400, int),
    "stop_enabled": env("MG_STOP", 0, int) == 1,
    "alert_every_s": env("MG_ALERT_EVERY_S", 600, int),
}
INBOX = os.environ.get("MG_INBOX", ORCH + "/dispatch/inbox")
LOG = os.environ.get("MG_LOG", ORCH + "/log/mem-guard.txt")
ALIVE = os.environ.get("MG_ALIVE", ORCH + "/log/mem-guard.alive")
CGROUP = os.environ.get("MG_CGROUP", "")
LIMIT_KB = env("MG_LIMIT_MB", 0.0) * 1024
ME = os.getuid()


def now():
    return time.strftime("%F %T")


def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write("%s %s\n" % (now(), msg))
    except OSError:
        pass


# ---- readings ---------------------------------------------------------------------------------------------------
def meminfo():
    d = {}
    with open("/proc/meminfo") as f:
        for line in f:
            k, _, v = line.partition(":")
            d[k] = int(v.split()[0])
    return d


def psi_full10():
    try:
        with open("/proc/pressure/memory") as f:
            for line in f:
                if line.startswith("full"):
                    return float(line.split("avg10=")[1].split()[0])
    except (OSError, IndexError, ValueError):
        pass
    return 0.0


def cgroup_pids():
    with open(CGROUP + "/cgroup.procs") as f:
        return {int(x) for x in f.read().split()}


def figures():
    """(available_kb, swap_free_kb, psi_full10). In rehearsal: the limit minus the cgroup's use."""
    if CGROUP:
        cur = int(open(CGROUP + "/memory.current").read()) // 1024
        return max(LIMIT_KB - cur, 0.0), 1e9, 0.0
    m = meminfo()
    return m["MemAvailable"], m["SwapFree"], psi_full10()


def stat_fields(pid):
    """(ppid, starttime) from /proc/<pid>/stat; the command name may hold spaces, so split after the last ')'."""
    with open("/proc/%d/stat" % pid) as f:
        s = f.read()
    rest = s[s.rindex(")") + 2:].split()
    return int(rest[1]), int(rest[19])


def scan():
    """Every process of this user: (pid, comm, ppid, starttime, rss_kb). Cheap: one small read per process."""
    only = cgroup_pids() if CGROUP else None
    out = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if only is not None and pid not in only:
            continue
        try:
            if os.stat("/proc/%d" % pid).st_uid != ME:
                continue
            with open("/proc/%d/comm" % pid) as f:
                comm = f.read().strip()
            ppid, st = stat_fields(pid)
            rss = 0
            if comm != "rg":
                with open("/proc/%d/statm" % pid) as f:
                    rss = int(f.read().split()[1]) * 4
            out.append((pid, comm, ppid, st, rss))
        except (OSError, ValueError, IndexError):
            continue
    return out


def exe_base(pid):
    try:
        return os.path.basename(os.readlink("/proc/%d/exe" % pid))
    except OSError:
        return ""


# ---- the decision (pure; replayed in the self-test) --------------------------------------------------------------------
def decide(rg_n, avail_kb, psi_full, cfg=CFG):
    """0 quiet, 1 watch, 2 mark, 3 stop (rg only)."""
    if rg_n > cfg["stop_rg"] or (rg_n >= cfg["stop_min_rg"] and (avail_kb < cfg["stop_avail_kb"] or psi_full > cfg["psi_stop"])):
        return 3
    if rg_n > cfg["mark_rg"] or (rg_n >= cfg["mark_min_rg"] and (avail_kb < cfg["mark_avail_kb"] or psi_full > cfg["psi_mark"])):
        return 2
    if rg_n > cfg["watch_rg"] or psi_full > cfg["psi_watch"]:
        return 1
    return 0


# ---- actions ----------------------------------------------------------------------------------------------------------
def parents_report(rgs, procs, limit=8):
    by = {}
    for pid, _c, ppid, _s, _r in rgs:
        by[ppid] = by.get(ppid, 0) + 1
    names = {p[0]: p[1] for p in procs}
    lines = []
    for ppid, n in sorted(by.items(), key=lambda kv: -kv[1])[:limit]:
        try:
            cwd = os.readlink("/proc/%d/cwd" % ppid)
        except OSError:
            cwd = "?"
        try:
            cmd = open("/proc/%d/cmdline" % ppid).read().replace("\0", " ")[:160]
        except OSError:
            cmd = names.get(ppid, "?")
        lines.append("  %5d children  parent %d  cwd %s  %s" % (n, ppid, cwd, cmd))
    exes = {}
    for pid, *_ in rgs[:200]:
        try:
            e = os.readlink("/proc/%d/exe" % pid)
        except OSError:
            continue
        exes[e] = exes.get(e, 0) + 1
    lines.append("  rg binaries (of the first 200): " + "; ".join("%s x%d" % kv for kv in exes.items()))
    return "\n".join(lines)


def inbox_item(tag, status, body, dry):
    name = "%s/%s-%s.txt" % (INBOX, time.strftime("%Y%m%d-%H%M%S"), tag)
    text = "log: mem-guard.txt\nMemory: %s\nstatus: %s\n\n%s\n" % (tag, status, body)
    if dry:
        log("DRY-RUN would write %s: %s" % (name, status))
        return
    try:
        os.makedirs(INBOX, exist_ok=True)
        with open(name, "w") as f:
            f.write(text)
    except OSError as e:
        log("inbox write failed: %s" % e)


def mark(rgs, dry):
    done = 0
    for pid, *_ in rgs:
        try:
            with open("/proc/%d/oom_score_adj" % pid) as f:
                if int(f.read()) >= 1000:
                    continue
            if not dry:
                with open("/proc/%d/oom_score_adj" % pid, "w") as f:
                    f.write("1000")
            done += 1
        except (OSError, ValueError):
            continue
    return done


def stop(rgs, dry):
    """SIGKILL by pid. The start time is read again just before, so a reused pid is never hit."""
    killed = 0
    for pid, comm, _ppid, st, _r in rgs:
        try:
            if exe_base(pid) != "rg" or stat_fields(pid)[1] != st:
                continue
            if not dry:
                os.kill(pid, signal.SIGKILL)
            killed += 1
        except (OSError, ValueError, IndexError):
            continue
    return killed


def name_totals(procs):
    tot = {}
    for _pid, comm, _pp, _st, rss in procs:
        c = tot.setdefault(comm, [0, 0])
        c[0] += 1
        c[1] += rss
    return tot


def step(state, dry):
    avail, swap_free, psi = figures()
    procs = scan()
    rgs = [p for p in procs if p[1] == "rg" and exe_base(p[0]) == "rg"]
    n = len(rgs)
    lvl = decide(n, avail, psi)
    t = time.time()
    if lvl >= 2 and state.get("marked_at", 0) + 2 < t:
        m = mark(rgs, dry)
        state["marked_at"] = t
        if m:
            log("MARK %d rg set to oom_score_adj 1000 (rg %d, available %d MB, stall %.1f%%)" % (m, n, avail // 1024, psi))
    if lvl == 3 and CFG["stop_enabled"]:
        pids = [p[0] for p in rgs]
        report = parents_report(rgs, procs)
        k = stop(rgs, dry)
        log("STOP %d rg killed by pid (rg %d, available %d MB, stall %.1f%%); first pids %s" % (k, n, avail // 1024, psi, pids[:12]))
        if state.get("stop_alert_at", 0) + CFG["alert_every_s"] < t:
            state["stop_alert_at"] = t
            inbox_item("rg-stopped", "P1: mem_guard killed %d rg (they were %d; available %d MB; stall %.1f%%); the spawner follows"
                       % (k, n, avail // 1024, psi), "parents (children, pid, cwd, command):\n" + report, dry)
    elif lvl >= 1 and state.get("watch_alert_at", 0) + CFG["alert_every_s"] < t:
        state["watch_alert_at"] = t
        tag = "rg-stop-needed" if lvl == 3 else "rg-watch"
        inbox_item(tag, "%s: %d rg processes (level %d%s); available %d MB; stall %.1f%%"
                   % ("P1" if lvl >= 2 else "P2", n, lvl, ", stop is OFF (MG_STOP=0)" if lvl == 3 else "", avail // 1024, psi),
                   "parents (children, pid, cwd, command):\n" + parents_report(rgs, procs), dry)
        log("level %d: %d rg, available %d MB, stall %.1f%%" % (lvl, n, avail // 1024, psi))
    # not rg: low memory, or one program name with a very large count (alert only)
    tot = name_totals(procs)
    storm = [(c, v) for c, v in tot.items() if c != "rg" and v[0] >= CFG["name_storm"]]
    if (avail < CFG["low_avail_kb"] or storm) and state.get("low_alert_at", 0) + CFG["alert_every_s"] < t:
        state["low_alert_at"] = t
        top = sorted(procs, key=lambda p: -p[4])[:8]
        body = "top memory users (pid, name, MB):\n" + "\n".join("  %d  %s  %d" % (p[0], p[1], p[4] // 1024) for p in top)
        body += "\nper-name totals (count, MB), largest 8:\n" + "\n".join(
            "  %s  %d  %d" % (c, v[0], v[1] // 1024) for c, v in sorted(tot.items(), key=lambda kv: -kv[1][1])[:8])
        inbox_item("memory-low", "P1: available %d MB%s; nothing was killed" % (
            avail // 1024, "; storm of %s" % [c for c, _ in storm] if storm else ""), body, dry)
        log("ALERT memory low or name storm: available %d MB, storm %s" % (avail // 1024, [c for c, _ in storm]))
    if lvl == 0 and state.get("last_lvl", 0) > 0:
        log("level back to 0 (rg %d, available %d MB)" % (n, avail // 1024))
    state["last_lvl"] = lvl
    return n, avail, psi, lvl


def selftest():
    """Replays 14:18 against decide() and checks the thresholds' edges. No /proc writes, no kills."""
    gb = 1048576
    ok = True

    def chk(name, got, want):
        nonlocal ok
        flag = "ok " if got == want else "BAD"
        ok &= got == want
        print("%s %-58s got %s want %s" % (flag, name, got, want))

    chk("quiet day: 4 rg, 16 GB available", decide(4, 16 * gb, 0.0), 0)
    chk("busy lead: 30 rg, 6 GB available, stall 0", decide(30, 6 * gb, 0.0), 0)
    chk("101 rg", decide(101, 16 * gb, 0.0), 1)
    chk("151 rg", decide(151, 16 * gb, 0.0), 2)
    chk("301 rg", decide(301, 16 * gb, 0.0), 3)
    chk("60 rg, 2.5 GB available", decide(60, 2.5 * gb, 0.0), 3)
    chk("25 rg, 4 GB available", decide(25, 4 * gb, 0.0), 2)
    chk("2 rg, 1 GB available (not an rg problem)", decide(2, 1 * gb, 0.0), 0)
    chk("60 rg, stall 25 %", decide(60, 16 * gb, 25.0), 3)
    # 14:18 replay: 2,161 rg of 9.6 MB over 42 s (14:18:05 to 14:18:47) = 51 per second, one check per second
    rate, base_avail_gb, rg_gb = 2161 / 42.0, 16.0, 0.0096
    first = {}
    for sec in range(0, 43):
        n = int(rate * sec)
        avail = (base_avail_gb - n * rg_gb) * gb
        lv = decide(n, avail, 0.0)
        for L in (1, 2, 3):
            if lv >= L and L not in first:
                first[L] = (sec, n, round(avail / gb, 1))
    print("replay (51 rg/s from 14:18:05, 16 GB available at the start): first level 1/2/3 at (second, rg, GB available):", first)
    chk("the replay reaches STOP before 8 seconds", first.get(3, (99,))[0] <= 8, True)
    return 0 if ok else 1


def main():
    dry = "--dry-run" in sys.argv
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    state = {}
    if "--once" in sys.argv:
        t0 = time.time()
        n, avail, psi, lvl = step(state, dry)
        print(json.dumps({"rg": n, "available_mb": int(avail // 1024), "stall_full_avg10": psi, "level": lvl,
                          "stop_enabled": CFG["stop_enabled"], "dry_run": dry, "step_ms": round((time.time() - t0) * 1000, 1)}))
        return
    log("guard started (pid %d; watch>%d mark>%d stop>%d rg; stop %s; period %ss)" % (
        os.getpid(), CFG["watch_rg"], CFG["mark_rg"], CFG["stop_rg"], "ON" if CFG["stop_enabled"] else "OFF", CFG["period"]))
    last_alive = 0.0
    while True:
        try:
            step(state, dry)
        except Exception as e:  # never let a read error end the guard
            log("step error: %r" % (e,))
        t = time.time()
        if t - last_alive > 10:
            last_alive = t
            try:
                with open(ALIVE, "w") as f:
                    f.write("%s %d\n" % (now(), os.getpid()))
            except OSError:
                pass
        time.sleep(CFG["period"])


if __name__ == "__main__":
    main()
