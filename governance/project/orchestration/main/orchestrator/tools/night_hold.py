"""The night hold (DEC-1138 (3): "no new lead run starts after 03:00; the leads wind down before the nightly (04:00) and
resume after it ends"; CTO scratch tool, stdlib only; run forever, one look every 60 s).

From 03:00 local time (Europe/London = UTC now) until the nightly has ended for today, or 07:30 at the latest, every live
line of dispatch/ready.txt that is not a running lead's own started line is commented as `#HELD-NIGHT <line>` (in place;
atomic rewrite under dispatch/ready.lock; a copy kept as ready.txt.pre-hold-<stamp>); a line the CTO adds while held is
held at the next look. When the nightly has ended (or at 07:30) only this tool's own `#HELD-NIGHT ` lines are
uncommented (re-labelled `#HELD-MEM ` if mem_hold.py is holding at that moment). Running leads are never touched; the
tool signals nothing.

"The nightly has ended for today" (the first that holds):
  * log/nightly/status.txt has a `<YYYY-MM-DD> ran|FAILED|MISSED | ...` line for today (nightly_check.sh writes it at
    08:00 or later, so this is the late backstop); or
  * today's night run folder log/nightly/<YYYYMMDD>-HHMM (HHMM 0300-0759) has a run.txt with a `verdict:` line, or one that
    says `NOT STARTED` (nightly_restart.sh gave up) or `nightly_restart.sh: the run was` (killed, capped, timed out), and
    the marker ORCH/NIGHTLY-RUNNING is not today's (nightly.sh's trap, or nightly_restart.sh, removes it); or
  * today's log/nightly/restart/<YYYY-MM-DD>.log, after its last `start (pid`, says `run ended` or `RUN ENDED` or
    `REFUSED`, and the marker is not today's.
The window is evaluated on the local clock; nothing before 03:00 or from 07:30 is held.

    night_hold.py [--every 60] [--orch <dir>]    run forever
    night_hold.py --release-now                  release this tool's own holds at once and exit (use after stopping it)
"""
import argparse
import glob
import os
import re
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hold_lib as H  # noqa: E402

NAME = "night-hold"
START_HM, END_HM = (3, 0), (7, 30)


def in_window(now):
    hm = (now.hour, now.minute)
    return START_HM <= hm < END_HM


def marker_is_today(cfg, label):
    try:
        first = open(os.path.join(cfg.orch, "NIGHTLY-RUNNING")).read().split()
    except OSError:
        return False
    return bool(first) and first[0] == label


def nightly_ended(cfg, now):
    """(True, evidence) when today's nightly has ended, else (False, why not)."""
    label = now.strftime("%Y-%m-%d")
    day = now.strftime("%Y%m%d")
    try:
        for line in open(os.path.join(cfg.nightly, "status.txt")):
            if re.match(rf"^{label} (ran|FAILED|MISSED)\b", line):
                return True, f"status.txt: {line.strip()[:100]}"
    except OSError:
        pass
    running = marker_is_today(cfg, label)
    for d in sorted(glob.glob(os.path.join(cfg.nightly, f"{day}-0[3-7][0-9][0-9]"))):
        try:
            txt = open(os.path.join(d, "run.txt")).read()
        except OSError:
            continue
        if re.search(r"^verdict:", txt, re.M) or "NOT STARTED" in txt or "nightly_restart.sh: the run was" in txt:
            if not running:
                return True, f"{os.path.basename(d)}/run.txt holds its end"
    try:
        lines = open(os.path.join(cfg.nightly, "restart", f"{now.strftime('%Y-%m-%d')}.log")).read().splitlines()
    except OSError:
        lines = []
    last = max((i for i, l in enumerate(lines) if "nightly_restart: start (pid" in l), default=None)
    if last is not None and not running:
        for l in lines[last + 1:]:
            if re.search(r"nightly_restart: (run ended|RUN ENDED|REFUSED)", l):
                return True, f"restart log: {l[-100:]}"
    return False, "the nightly has not ended" + (" (its marker is today's)" if running else "")


class NightHold:
    def __init__(self, cfg, now=datetime.now, leads=None):
        self.cfg = cfg
        self.now = now
        self.leads = leads or (lambda: H.running_leads(cfg))
        self.jsonl = os.path.join(cfg.log, "night-hold.jsonl")
        self.state_path = os.path.join(cfg.log, "night-hold.state.json")
        self.holding = H.count_held(cfg, H.NIGHT_PREFIX) > 0 or H.is_active(cfg, NAME)
        if self.holding:
            H.set_active(cfg, NAME, True, "resumed")

    def stamp(self):
        return self.now().strftime("%Y-%m-%d %H:%M:%S")

    def _apply(self):
        leads = self.leads()
        started = H.started_logs(self.cfg)
        skip = lambda l: H.is_running_lead_line(l, leads, started)  # noqa: E731
        return H.rewrite_ready(self.cfg, lambda ls: H.hold_live_lines(ls, H.NIGHT_PREFIX, skip), backup=True), leads

    def hold(self, why):
        (info, _), leads = self._apply()
        self.holding = True
        H.set_active(self.cfg, NAME, True, why)
        row = {"at": self.stamp(), "event": "hold", "why": why, "lines_held": info.get("held", []),
               "running_leads_untouched": leads, "backup": info.get("backup")}
        H.jsonl(self.jsonl, row)
        H.inbox_item(self.cfg, "night-hold",
                     "log: night-hold.jsonl\nHold: night\n"
                     f"status: {why}. No new lead starts (DEC-1138 (3)); ready.txt lines held as #HELD-NIGHT: "
                     f"{len(row['lines_held'])}; running leads (not stopped): {', '.join(leads) or 'none'}. They are "
                     "released when the nightly has ended, or at 07:30.\n", self.now().timestamp())
        return row

    def extend(self):
        (info, changed), leads = self._apply()
        if info.get("held"):
            row = {"at": self.stamp(), "event": "extend", "lines_held": info["held"], "backup": info.get("backup")}
            H.jsonl(self.jsonl, row)
            return row
        return None

    def release(self, why):
        handover = H.MEM_PREFIX if H.is_active(self.cfg, "mem-hold") else None
        info, _ = H.rewrite_ready(self.cfg, lambda ls: H.release_lines(ls, H.NIGHT_PREFIX, handover))
        self.holding = False
        H.set_active(self.cfg, NAME, False)
        row = {"at": self.stamp(), "event": "release", "why": why, "lines_released": info.get("released", []),
               "handed_to_mem_hold": bool(handover)}
        H.jsonl(self.jsonl, row)
        H.inbox_item(self.cfg, "night-hold",
                     "log: night-hold.jsonl\nHold: night released\n"
                     f"status: {why}. ready.txt lines uncommented: {len(row['lines_released'])}"
                     + (" (re-labelled #HELD-MEM: the memory hold is on)" if handover else "")
                     + ". Leads may start again.\n", self.now().timestamp())
        return row

    def step(self):
        n = self.now()
        inw = in_window(n)
        ended, ev = nightly_ended(self.cfg, n) if inw else (False, "outside 03:00-07:30")
        ev_row = None
        if inw and not ended:
            ev_row = self.extend() if self.holding else self.hold("from 03:00 until the nightly has ended")
        elif self.holding:
            ev_row = self.release(f"the nightly has ended ({ev})" if inw else "07:30 reached (the window is over)")
        H.write_json_atomic(self.state_path, {"pid": os.getpid(), "at": self.stamp(), "holding": self.holding,
                                              "in_window": inw, "nightly": ev})
        return ev_row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--every", type=float, default=60.0)
    ap.add_argument("--orch", default=H.DEFAULT_ORCH)
    ap.add_argument("--wt", default=H.DEFAULT_WT, help="worktrees folder (a test hook)")
    ap.add_argument("--now", default=None, help="a fixed local time YYYY-MM-DDTHH:MM:SS (a test hook)")
    ap.add_argument("--release-now", action="store_true")
    a = ap.parse_args()
    now = (lambda: datetime.fromisoformat(a.now)) if a.now else datetime.now
    nh = NightHold(H.Cfg(a.orch, a.wt), now=now)
    if a.release_now:
        print(nh.release("released by hand (--release-now)") if nh.holding else "nothing held by night_hold.py")
        return
    print(f"{nh.stamp()} night_hold.py pid {os.getpid()} every {a.every} s, window 03:00-07:30 local", flush=True)
    while True:
        try:
            nh.step()
        except Exception as exc:  # a failed look is logged and tried again; the loop never ends on its own
            try:
                H.jsonl(nh.jsonl, {"at": nh.stamp(), "event": "error", "error": repr(exc)[:300]})
            except OSError:
                pass
        time.sleep(a.every)


if __name__ == "__main__":
    main()
