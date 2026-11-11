"""The memory hold for every lead's next launch (DEC-1138 (2): "the hold below 5 GB available, applied to any lead's next
launch"; CTO scratch tool, stdlib only; run forever, one sample every 15 s).

Below 5 GB MemAvailable (one sample):
  (a) a brake file log/brake/<W2>.json for every W2 with a running lead or a live ready.txt line
      (launch_worker.sh refuses a new worker for that W2 while the file exists). A brake file written by anyone else
      (the runaway brake, a person) is never overwritten and never removed by this tool. Written with O_EXCL.
  (b) every live ready.txt line that is not a running lead's own started line becomes `#HELD-MEM <line>` (in place,
      atomic rewrite under dispatch/ready.lock, a copy kept as ready.txt.pre-hold-<stamp>), so the dispatcher starts no
      new lead. While the hold lasts, a line the CTO adds or a lead that appears is held at the next sample.
At 5.5 GB or more on two samples in a row: this tool's own brake files are removed, then its own `#HELD-MEM ` lines are
uncommented (re-labelled `#HELD-NIGHT ` if night_hold.py is holding at that moment, so the night's hold is never opened).
Each hold, extension and release goes to log/mem-hold.jsonl and (hold, release) to an inbox item
dispatch/inbox/<stamp>-mem-hold.txt. Nothing is killed or signalled; no process is matched by name.
A running worker is never stopped: the hold only stops what would START.

    mem_hold.py [--every 15] [--orch <dir>]      run forever
    mem_hold.py --release-now                    release this tool's own holds at once and exit (use after stopping it)
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hold_lib as H  # noqa: E402

NAME = "mem-hold"
BY = "mem_hold.py"
FLOOR_KB = 5 * 1024 * 1024
RELEASE_KB = int(5.5 * 1024 * 1024)


class MemHold:
    def __init__(self, cfg, meminfo=None, leads=None, now=time.time):
        self.cfg = cfg
        self.meminfo = meminfo or H.mem_available_kb
        self.leads = leads or (lambda: H.running_leads(cfg))
        self.now = now
        self.jsonl = os.path.join(cfg.log, "mem-hold.jsonl")
        self.state_path = os.path.join(cfg.log, "mem-hold.state.json")
        self.ok_run = 0
        # a restart while holding takes the hold up again from the files, never from memory
        self.holding = bool(self.own_brakes()) or H.count_held(cfg, H.MEM_PREFIX) > 0
        if self.holding:
            H.set_active(cfg, NAME, True, "resumed")

    # -- own brake files
    def brake_path(self, w2):
        return os.path.join(self.cfg.brake, f"{w2}.json")

    def own_brakes(self):
        out = []
        try:
            names = sorted(os.listdir(self.cfg.brake))
        except OSError:
            return out
        for n in names:
            if n.endswith(".json"):
                d = H.read_json(os.path.join(self.cfg.brake, n))
                if isinstance(d, dict) and d.get("by") == BY:
                    out.append(n[:-5])
        return out

    def write_brake(self, w2, avail_kb):
        """True when this tool wrote the file, False when one by anyone else is there (kept as it is)."""
        os.makedirs(self.cfg.brake, exist_ok=True)
        p = self.brake_path(w2)
        body = {"W2": w2, "brake": "memory-hold (DEC-1138 (2))", "at": H.stamp(self.now()),
                "reason": f"MemAvailable {avail_kb // 1024} MB is below 5 GB: no new lead and no new worker for {w2} "
                          "(launch_worker refuses) until two samples at 5.5 GB or more",
                "mem_available_mb": avail_kb // 1024, "by": BY}
        try:
            with open(p, "x") as f:
                json.dump(body, f)
            return True
        except FileExistsError:
            return False

    # -- one pass over what must be held
    def apply_hold(self, avail_kb):
        leads = self.leads()
        started = H.started_logs(self.cfg)
        skip = lambda l: H.is_running_lead_line(l, leads, started)  # noqa: E731
        info, changed = H.rewrite_ready(self.cfg, lambda ls: H.hold_live_lines(ls, H.MEM_PREFIX, skip), backup=True)
        w2s = sorted(set(leads) | set(info.get("live_w2", [])))
        new_brakes, foreign = [], []
        for w in w2s:
            if self.write_brake(w, avail_kb):
                new_brakes.append(w)
            elif w not in self.own_brakes():
                foreign.append(w)
        return {"leads": leads, "lines_held": info.get("held", []), "brakes_written": new_brakes,
                "foreign_brakes_kept": foreign, "backup": info.get("backup")}

    def hold(self, avail_kb):
        r = self.apply_hold(avail_kb)
        self.holding, self.ok_run = True, 0
        H.set_active(self.cfg, NAME, True, f"MemAvailable {avail_kb // 1024} MB")
        row = {"at": H.stamp(self.now()), "event": "hold", "avail_mb": avail_kb // 1024, **r}
        H.jsonl(self.jsonl, row)
        H.inbox_item(self.cfg, "mem-hold",
                     "log: mem-hold.jsonl\nHold: memory\n"
                     f"status: MemAvailable {avail_kb // 1024} MB is below 5 GB (DEC-1138 (2)). No new lead and no new "
                     f"worker starts until two samples at 5.5 GB or more. Brake files: {', '.join(r['brakes_written']) or 'none new'}; "
                     f"ready.txt lines held as #HELD-MEM: {len(r['lines_held'])}; running leads (not stopped): "
                     f"{', '.join(r['leads']) or 'none'}."
                     + (f" Brakes by others left as they are: {', '.join(r['foreign_brakes_kept'])}." if r["foreign_brakes_kept"] else "")
                     + "\n", self.now())
        return row

    def extend(self, avail_kb):
        r = self.apply_hold(avail_kb)
        if r["lines_held"] or r["brakes_written"]:
            row = {"at": H.stamp(self.now()), "event": "extend", "avail_mb": avail_kb // 1024, **r}
            H.jsonl(self.jsonl, row)
            return row
        return None

    def release(self, avail_kb):
        """Own brake files first (nothing can start with a brake on and no line), then the lines."""
        removed = []
        for w in self.own_brakes():
            try:
                os.remove(self.brake_path(w))
                removed.append(w)
            except OSError:
                pass
        handover = H.NIGHT_PREFIX if H.is_active(self.cfg, "night-hold") else None
        info, _ = H.rewrite_ready(self.cfg, lambda ls: H.release_lines(ls, H.MEM_PREFIX, handover))
        self.holding, self.ok_run = False, 0
        H.set_active(self.cfg, NAME, False)
        row = {"at": H.stamp(self.now()), "event": "release", "avail_mb": None if avail_kb is None else avail_kb // 1024,
               "brakes_removed": removed, "lines_released": info.get("released", []),
               "handed_to_night_hold": bool(handover)}
        H.jsonl(self.jsonl, row)
        H.inbox_item(self.cfg, "mem-hold",
                     "log: mem-hold.jsonl\nHold: memory released\n"
                     f"status: MemAvailable {'unknown' if avail_kb is None else str(avail_kb // 1024) + ' MB'} (5.5 GB or more twice in a row). "
                     f"Brake files removed: {', '.join(removed) or 'none'}; ready.txt lines uncommented: {len(row['lines_released'])}"
                     + (" (re-labelled #HELD-NIGHT: the night hold is on)" if handover else "") + ".\n", self.now())
        return row

    def step(self):
        """One sample. Returns the event row or None."""
        avail = self.meminfo()
        ev = None
        if avail is not None:
            if not self.holding:
                if avail < FLOOR_KB:
                    ev = self.hold(avail)
            else:
                self.ok_run = self.ok_run + 1 if avail >= RELEASE_KB else 0
                if self.ok_run >= 2:
                    ev = self.release(avail)
                else:
                    ev = self.extend(avail)
        H.write_json_atomic(self.state_path, {"pid": os.getpid(), "at": H.stamp(self.now()),
                                              "avail_mb": None if avail is None else avail // 1024,
                                              "holding": self.holding, "ok_run": self.ok_run})
        return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--every", type=float, default=15.0)
    ap.add_argument("--orch", default=H.DEFAULT_ORCH)
    ap.add_argument("--release-now", action="store_true")
    ap.add_argument("--wt", default=H.DEFAULT_WT, help="worktrees folder (a test hook)")
    ap.add_argument("--meminfo", default="/proc/meminfo", help="meminfo file (a test hook)")
    a = ap.parse_args()
    cfg = H.Cfg(a.orch, a.wt)
    m = MemHold(cfg, meminfo=lambda: H.mem_available_kb(a.meminfo))
    if a.release_now:
        if m.holding:
            print(m.release(m.meminfo()))
        else:
            print("nothing held by mem_hold.py")
        return
    print(f"{H.stamp()} mem_hold.py pid {os.getpid()} every {a.every} s, hold below {FLOOR_KB // 1024} MB, "
          f"release at {RELEASE_KB // 1024} MB twice", flush=True)
    while True:
        try:
            m.step()
        except Exception as exc:  # a failed pass is logged and tried again; the loop never ends on its own
            try:
                H.jsonl(m.jsonl, {"at": H.stamp(), "event": "error", "error": repr(exc)[:300]})
            except OSError:
                pass
        time.sleep(a.every)


if __name__ == "__main__":
    main()
