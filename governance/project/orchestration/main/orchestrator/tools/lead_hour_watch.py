"""The owner's three-lead watch (chat, 2026-11-11 ~18:45): over the first hour with three leads running, record the
lowest MemAvailable and each lead's peak memory; if MemAvailable falls below 5 GB, hold the third lead's next phase
until it recovers.

Per lead, memory is the summed RSS of every process whose working directory is in that ticket's worktrees
(~/gov-os-worktrees/<W2> and <W2>-*), so the lead's workers count even though each runs in its own process group.
The hold is the brake file launch_worker.sh already honours (log/brake/<W2>.json: it refuses new workers while the
file exists); a running worker is never stopped. Released after two samples in a row at 5.5 GB or more.
Usage: lead_hour_watch.py --until <epoch> --hold <W2> <W2> [<W2> ...]
"""
import argparse, json, os, time

ORCH = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"
WT = "/home/usain/gov-os-worktrees"
LOG = f"{ORCH}/log/lead-hour-watch.jsonl"
SUMMARY = f"{ORCH}/log/lead-hour-watch-summary.json"
FLOOR_KB, RELEASE_KB = 5 * 1024 * 1024, int(5.5 * 1024 * 1024)


def mem_available_kb():
    for line in open("/proc/meminfo"):
        if line.startswith("MemAvailable:"):
            return int(line.split()[1])
    return None


def per_lead_rss_kb(w2s):
    out = {w: 0 for w in w2s}
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            cwd = os.readlink(f"/proc/{pid}/cwd")
            with open(f"/proc/{pid}/status") as f:
                rss = next((int(l.split()[1]) for l in f if l.startswith("VmRSS:")), 0)
        except OSError:
            continue
        for w in w2s:
            base = f"{WT}/{w}"
            if cwd == base or cwd.startswith(base + "/") or cwd.startswith(base + "-"):
                out[w] += rss
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--until", type=float, required=True)
    ap.add_argument("--hold", required=True, help="the W2 id whose next phase is held below the floor")
    ap.add_argument("--every", type=float, default=30.0)
    ap.add_argument("w2s", nargs="+")
    a = ap.parse_args()
    brake = f"{ORCH}/log/brake/{a.hold}.json"
    low, low_at, peaks, holding, ok_run, events = None, None, {w: (0, None) for w in a.w2s}, False, 0, []
    while time.time() < a.until:
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        avail = mem_available_kb()
        leads = per_lead_rss_kb(a.w2s)
        if avail is not None and (low is None or avail < low):
            low, low_at = avail, now
        for w, kb in leads.items():
            if kb > peaks[w][0]:
                peaks[w] = (kb, now)
        if avail is not None and avail < FLOOR_KB and not holding:
            if not os.path.exists(brake):
                os.makedirs(os.path.dirname(brake), exist_ok=True)
                json.dump({"W2": a.hold, "brake": "memory-hold (the owner, 11-11)", "at": now,
                           "status": f"MemAvailable {avail // 1024} MB below 5 GB: the third lead's next phase held "
                                     "(launch_worker refuses new workers) until two samples at 5.5 GB or more",
                           "by": "lead_hour_watch.py"}, open(brake, "w"))
                holding = True
                events.append({"at": now, "event": "hold", "avail_mb": avail // 1024})
        if holding:
            ok_run = ok_run + 1 if avail is not None and avail >= RELEASE_KB else 0
            if ok_run >= 2:
                try:
                    d = json.load(open(brake))
                    if d.get("by") == "lead_hour_watch.py":
                        os.remove(brake)
                except (OSError, ValueError):
                    pass
                holding, ok_run = False, 0
                events.append({"at": now, "event": "release", "avail_mb": avail // 1024})
        with open(LOG, "a") as f:
            f.write(json.dumps({"at": now, "avail_mb": None if avail is None else avail // 1024,
                                "leads_mb": {w: kb // 1024 for w, kb in leads.items()}, "holding": holding}) + "\n")
        summary = {"window_end": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(a.until)),
                   "lowest_avail_mb": None if low is None else low // 1024, "lowest_at": low_at,
                   "peaks_mb": {w: {"mb": kb // 1024, "at": at} for w, (kb, at) in peaks.items()},
                   "holding": holding, "events": events}
        json.dump(summary, open(SUMMARY, "w"), indent=1)
        time.sleep(a.every)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
