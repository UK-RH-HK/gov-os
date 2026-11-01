#!/usr/bin/env python3
"""The dispatcher (owner, 2026-11-01: tonight's top priority). A plain program, no AI, outside any Claude session.

    python3 dispatcher.py tick [--dry]     # one pass (cron every minute, or loop.sh); a second concurrent pass exits
    python3 dispatcher.py status           # prints status.txt

Each pass, in order (a step's error is logged, shown in the status, and the pass goes on; a step never acts on an
error in its own checks; every external command has a 60 s limit, a timeout counting as a failed check):
  1. the truth: running leads from the processes (the launch form's identity marker and a lead worktree as the
     working folder), load, memory, the gate, the disk gate, the heavy slots held, the queue busy, the main tree;
  2. returns: every non-empty ../log/*-A5-*.json (and every log started.txt names) not in ../log/returns-seen.txt
     becomes an inbox item; a started lead with no process and no return after 5 minutes becomes one too, once;
  3. start at most one lead, never within 120 s of the last start: the first ready.txt entry passing every check, in
     the owner's launch form (tools/launch_when_gate_opens.sh, as lead_chain2.sh starts it), recorded before launch;
  4. land: land.txt claimed by an atomic rename, every line in one tools/land.py call, only when the queue is free,
     no close runs, the main tree is clean and on w2/integrate; its outcome becomes land-done.txt and an inbox item;
  5. status.json and status.txt; 6. inbox-stale.txt (stable content) while an inbox item is unread 30 minutes.
It never starts what is not in ready.txt and never lands what is not in land.txt (the CTO's lists).
Every external command and path can be replaced through DISPATCH_* variables, for the tests only.
"""
import fcntl
import glob
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

E = os.environ.get
ORCH = Path(E("DISPATCH_ORCH", "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"))
D = Path(E("DISPATCH_DIR", str(ORCH / "dispatch")))
REPO = Path(E("DISPATCH_REPO", "/home/usain/Dynamic-Agentic-Engineering-OS"))
WT = Path(E("DISPATCH_WORKTREES", "/home/usain/gov-os-worktrees"))
LOG = ORCH / "log"
BRIEFS = ORCH / "briefs"
STAGGER_S = int(E("DISPATCH_STAGGER_S", "120"))
STALE_S = int(E("DISPATCH_STALE_S", "1800"))
NEVER_RAN_S = int(E("DISPATCH_NEVER_RAN_S", "300"))
TIMEOUT_S = int(E("DISPATCH_TIMEOUT_S", "60"))
SLOTS = [Path(f"/tmp/gov-os-heavy-slot-{n}.lock") for n in (1, 2, 3)]
RUN_LOCK = ORCH / "merge-queue" / "run.lock"
MARKER = 'GOV_ROLE":"orchestrator","GOV_TICKET'  # the launch form's identity, as gate_check.py counts leads
LOGNAME = re.compile(r"^[A-Za-z0-9][\w.-]*-A5-[\w.-]+\.json$")


def now():
    return float(E("DISPATCH_NOW") or time.time())


def stamp(t=None):
    return datetime.fromtimestamp(t if t is not None else now()).strftime("%Y-%m-%d %H:%M:%S")


def fstamp():
    return datetime.fromtimestamp(now()).strftime("%Y%m%d-%H%M%S")


def log(msg):
    D.mkdir(parents=True, exist_ok=True)
    with open(D / "dispatch.log", "a") as f:
        f.write(f"{stamp()} {msg}\n")


class R:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def sh(cmd, **kw):
    """Every external command with a time limit; a timeout is a failed command (124)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S, **kw)
        return R(r.returncode, r.stdout, r.stderr)
    except subprocess.TimeoutExpired:
        return R(124, "", f"timed out after {TIMEOUT_S} s: {' '.join(map(str, cmd))[:120]}")


# ---- 1. the truth -------------------------------------------------------------------------------------------------

def processes():
    """[(argv, cwd)] of every process (DISPATCH_FAKE_PROCS: a JSON list of {"cmd", "cwd"} for the tests)."""
    fake = E("DISPATCH_FAKE_PROCS")
    if fake is not None:
        return [(p["cmd"].split(), p.get("cwd", "")) for p in json.loads(Path(fake).read_text())]
    out = []
    for p in glob.glob("/proc/[0-9]*"):
        try:
            argv = [a.decode("utf-8", "replace") for a in Path(p, "cmdline").read_bytes().split(b"\0") if a]
            cwd = os.readlink(p + "/cwd")
        except OSError:
            continue
        if argv:
            out.append((argv, cwd))
    return out


def lead_w2(argv, cwd):
    """The W2 of a lead process: the launch form's identity marker in its arguments and a lead worktree as its folder."""
    if not any(MARKER in a for a in argv):
        return None
    if not cwd.startswith(str(WT) + "/"):
        return None
    name = cwd[len(str(WT)) + 1:].split("/")[0]
    if not name or name.endswith("-tests") or name.startswith("W2-00-"):
        return None
    return name


def running_leads(procs):
    return sorted({w for w in (lead_w2(a, c) for a, c in procs) if w})


def runs_script(argv, name):
    """An interpreter running a script whose path ends with /<name> (or is <name>)."""
    if not argv or not os.path.basename(argv[0]).startswith(("python", "setsid")):
        return False
    return any(a == name or a.endswith("/" + name) for a in argv[1:4])


def launcher_pending(procs, w2):
    return any(any(a.endswith("launch_when_gate_opens.sh") for a in argv) and w2 in argv for argv, _ in procs)


def lock_held(path):
    """Whether any process holds a lock on the file (read from /proc/locks; never takes the lock itself)."""
    fake = E("DISPATCH_FAKE_HELD")
    if fake is not None:
        return str(path) in json.loads(Path(fake).read_text())
    try:
        ino = os.stat(path).st_ino
    except OSError:
        return False
    try:
        for line in Path("/proc/locks").read_text().splitlines():
            dev = [x for x in line.split() if x.count(":") == 2]
            if dev and dev[0].rsplit(":", 1)[1] == str(ino):
                return True
    except OSError:
        return True  # cannot tell: busy (fail closed)
    return False


def gate():
    r = sh(shlex.split(E("DISPATCH_GATE_CMD", f"python3 {ORCH}/tools/gate_check.py")))
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())[:300]


def disk():
    r = sh(shlex.split(E("DISPATCH_DISK_CMD", f"bash {ORCH}/tools/disk_gate.sh")))
    return r.returncode == 0, (r.stderr.strip() or r.stdout.strip())[:200]


def tree_clean(path, tracked_only=False):
    r = sh(["git", "-C", str(path), "status", "--porcelain"] + (["--untracked-files=no"] if tracked_only else []))
    return r.returncode == 0 and not r.stdout.strip()


def truth():
    procs = processes()
    t = {"time": stamp(), "leads": running_leads(procs)}
    t["lead_count"] = len(t["leads"])
    try:
        t["load"] = [float(x) for x in Path(E("DISPATCH_LOADAVG", "/proc/loadavg")).read_text().split()[:3]]
    except (OSError, ValueError):
        t["load"] = None
    try:
        m = re.search(r"MemAvailable:\s+(\d+)", Path(E("DISPATCH_MEMINFO", "/proc/meminfo")).read_text())
        t["mem_available_mb"] = int(m.group(1)) // 1024 if m else None
    except OSError:
        t["mem_available_mb"] = None
    t["gate_open"], t["gate"] = gate()
    t["disk_open"], t["disk"] = disk()
    t["slots_held"] = [s.name for s in SLOTS if lock_held(s)]
    t["land_running"] = any(runs_script(a, "land.py") for a, _ in procs)
    t["close_running"] = any(runs_script(a, "close_build.py") for a, _ in procs)
    t["queue_busy"] = lock_held(RUN_LOCK) or t["land_running"]
    t["main_clean"] = tree_clean(REPO)
    br = sh(["git", "-C", str(REPO), "rev-parse", "--abbrev-ref", "HEAD"])
    t["main_branch"] = br.stdout.strip() if br.returncode == 0 else None
    t["_procs"] = procs
    return t


# ---- 2. returns ---------------------------------------------------------------------------------------------------

def read_list(path):
    out = []
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line.split())
    return out


def started():
    return read_list(D / "started.txt")


def inbox_item(name, body):
    (D / "inbox").mkdir(parents=True, exist_ok=True)
    item = D / "inbox" / f"{fstamp()}-{name}.txt"
    item.write_text(body)
    return item


def collect_returns(t, dry=False):
    seen_f = LOG / "returns-seen.txt"
    seen = set(seen_f.read_text().split()) if seen_f.exists() else set()
    paths = {p.name: p for p in LOG.glob("*-A5-*.json")}
    for e in started():
        if len(e) >= 5:
            paths.setdefault(e[-1], LOG / e[-1])
    new = []
    for name, p in sorted(paths.items(), key=lambda kv: kv[1].stat().st_mtime if kv[1].exists() else 0):
        if name in seen or not p.exists() or p.stat().st_size == 0:
            continue
        if dry:  # a dry pass marks nothing seen (the CTO's own watcher still sees it)
            log(f"would collect the return {name}")
            new.append(name)
            continue
        try:
            result = json.loads(p.read_text()).get("result", "")
        except ValueError:
            result = p.read_text()[:2000]
        w2 = name.split("-A5-")[0]
        st = re.search(r"^\s*status:\s*(.+)$", result, re.M)
        item = inbox_item(p.stem, f"log: {name}\nW2: {w2}\nstatus: {st.group(1)[:300] if st else '(no status line)'}"
                                  f"\n\n{result[:600]}\n")
        with open(seen_f, "a") as f:
            f.write(name + "\n")
        seen.add(name)
        new.append(name)
        log(f"return: {name} -> inbox/{item.name}")
    # F4: a lead started more than 5 minutes ago with no process, no launcher waiting and no return: once, to the CTO
    reported_f = D / "never-ran.txt"
    reported = set(reported_f.read_text().split()) if reported_f.exists() else set()
    for e in started():
        if len(e) < 5 or e[-1] in reported:
            continue
        w2, logf = e[2], e[-1]
        try:
            age = now() - datetime.strptime(" ".join(e[:2]), "%Y-%m-%d %H:%M:%S").timestamp()
        except ValueError:
            continue
        lp = LOG / logf
        if age < NEVER_RAN_S or w2 in t["leads"] or launcher_pending(t["_procs"], w2) or \
                (lp.exists() and lp.stat().st_size > 0):
            continue
        if dry:
            log(f"would report {w2} {logf}: started but never ran")
            continue
        inbox_item(f"{w2}-never-ran", f"log: {logf}\nW2: {w2}\nstatus: started but never ran ({int(age // 60)} min, "
                                      f"no lead process and no return); not retried until re-listed with a new log\n")
        with open(reported_f, "a") as f:
            f.write(logf + "\n")
        log(f"started but never ran: {w2} {logf}")
    return new


def unread():
    return sorted((D / "inbox").glob("*.txt")) if (D / "inbox").is_dir() else []


# ---- 3. start -----------------------------------------------------------------------------------------------------

def ticket_status(text):
    m = re.search(r"^status:\s*(\S+)", text.split("\n---", 1)[0] if text.startswith("---") else text, re.M)
    return m.group(1) if m else None


def why_not(entry, t, inbox_w2s, started_logs):
    """None when the entry may start; else the reason it waits."""
    if len(entry) != 4:
        return f"malformed line {' '.join(entry)}"
    w2, tid, brief, logf = entry
    if not LOGNAME.match(logf):
        return f"log name {logf!r} is not a lead log (<W2>-A5-<run>.json)"
    if w2 in t["leads"]:
        return "running"
    if launcher_pending(t["_procs"], w2):
        return "its launcher is waiting for the gate"
    if logf in started_logs:
        return f"already started for {logf}"
    lp = LOG / logf
    if lp.exists() and lp.stat().st_size > 0:
        return f"{logf} already holds a return"
    if w2 in inbox_w2s:
        return "an unread inbox item for it (waits for the CTO)"
    on_int = sh(["git", "-C", str(REPO), "show", f"w2/integrate:.tickets/{tid}.md"])
    if on_int.returncode or ticket_status(on_int.stdout) != "in_progress":
        return "claim not committed on w2/integrate (status not in_progress there)"
    wt = WT / w2
    if not wt.is_dir():
        return "no worktree"
    try:
        if ticket_status((wt / ".tickets" / f"{tid}.md").read_text()) != "in_progress":
            return "the worktree's ticket file does not read in_progress (merge w2/integrate into it)"
    except OSError:
        return "the worktree has no ticket file"
    if not tree_clean(wt, tracked_only=True):
        return "the worktree has tracked changes (or git failed)"
    bp = BRIEFS / brief
    if not bp.is_file():
        return f"no brief {brief}"
    if "@@" in bp.read_text():
        return "the brief holds an @@ placeholder"
    if not t["gate_open"]:
        return "gate shut: " + t["gate"][:160]
    if not t["disk_open"]:
        return "disk gate shut"
    return None


def launch(w2, tid, brief, logf):
    cmd = E("DISPATCH_LAUNCH_CMD")
    errf = LOG / f"{w2}-{datetime.fromtimestamp(now()).strftime('%Y%m%d-%H%M')}-launch.txt"
    argv = (shlex.split(cmd) if cmd else ["setsid", "-f", "bash", str(ORCH / "tools/launch_when_gate_opens.sh")]) \
        + [w2, tid, brief, logf]
    with open(errf, "a") as err, open(os.devnull) as nul:
        try:
            return subprocess.run(argv, stdin=nul, stdout=subprocess.DEVNULL, stderr=err, timeout=TIMEOUT_S).returncode
        except subprocess.TimeoutExpired:
            return 124


def start_one(t, dry):
    st = started()
    if st:
        try:
            last = datetime.strptime(" ".join(st[-1][:2]), "%Y-%m-%d %H:%M:%S").timestamp()
        except ValueError:
            last = now()  # F8: an unreadable time counts as now (the stagger is kept)
        if now() - last < STAGGER_S:
            return None, {"stagger": f"last start {int(now() - last)} s ago (< {STAGGER_S} s)"}
    started_logs = {e[-1] for e in st if len(e) >= 5}
    inbox_w2s = set()
    for item in unread():
        m = re.search(r"^W2: (\S+)", item.read_text(), re.M)
        if m:
            inbox_w2s.add(m.group(1))
    waits = {}
    for entry in read_list(D / "ready.txt"):
        try:
            reason = why_not(entry, t, inbox_w2s, started_logs)
        except Exception as exc:  # fail closed: an error in a check never starts
            reason = f"check error: {exc!r}"[:200]
        if reason:
            waits[" ".join(entry[:2])] = reason
            continue
        w2, tid, brief, logf = entry
        if dry:
            log(f"would start {w2} ({tid}) {brief} -> {logf}")
            return w2, waits
        with open(D / "started.txt", "a") as f:  # F4: recorded before the launch, so it is never launched twice
            f.write(f"{stamp()} {w2} {brief} {logf}\n")
        rc = launch(w2, tid, brief, logf)
        log(f"started {w2} ({tid}) {brief} -> {logf} (launcher exit {rc})")
        return w2, waits
    return None, waits


# ---- 4. land ------------------------------------------------------------------------------------------------------

def finalise_land(t, dry):
    infl = D / "land-inflight.txt"
    meta = json.loads(infl.read_text())
    if t["land_running"]:
        return "in flight"
    if dry:
        return "would finalise"
    lines = [l for l in (D / "land-inflight.lines").read_text().split() if l] \
        if (D / "land-inflight.lines").exists() else meta.get("lines", [])
    out = Path(meta["out"]).read_text() if Path(meta["out"]).exists() else ""
    outcome = {}
    for line in lines:
        w2 = line.split("=")[0]
        m = re.search(rf"^{re.escape(w2)}: (not landed.*)$", out, re.M)
        if re.search(rf"^CLOSED {re.escape(w2)}\b", out, re.M):
            outcome[line] = "CLOSED"
        elif m:
            outcome[line] = m.group(1)[:200]
        elif re.search(rf"^{re.escape(w2)}: LANDED BUT NOT CLOSED", out, re.M):
            outcome[line] = "LANDED BUT NOT CLOSED"
        else:
            outcome[line] = "no outcome in the output (refused or stopped)"
    with open(D / "land-done.txt", "a") as f:
        for line, o in outcome.items():
            f.write(f"{stamp()} {line} {o}\n")
    body = "log: " + meta["out"] + "\nW2: (land batch)\nstatus: " + "; ".join(f"{k} {v}" for k, v in outcome.items())
    if any(v != "CLOSED" for v in outcome.values()):
        body += "\n\nlast output:\n" + out[-400:]
    inbox_item("land", body + "\n")
    done = fstamp()
    infl.rename(D / f"land-inflight-{done}.done.json")
    if (D / "land-inflight.lines").exists():
        (D / "land-inflight.lines").rename(D / f"land-inflight-{done}.done.lines")
    log(f"land finished: {outcome}")
    return "finished"


def land_step(t, dry):
    if (D / "land-inflight.txt").exists():
        return finalise_land(t, dry)
    if not read_list(D / "land.txt"):
        return "nothing to land"
    if t["queue_busy"]:
        return "queue busy"
    if t["close_running"]:
        return "a close is running"
    if not t["main_clean"]:
        return "main tree not clean"
    if t["main_branch"] != "w2/integrate":
        return f"the main tree is on {t['main_branch']!r}, not w2/integrate"
    if dry:
        log(f"would land {[' '.join(e) for e in read_list(D / 'land.txt')]}")
        return "would land"
    claimed = D / "land-inflight.lines"
    os.rename(D / "land.txt", claimed)  # F2: claimed atomically; a land.txt the CTO writes from now on is untouched
    lines = [" ".join(e) for e in read_list(claimed)]

    def give_back(why):
        if (D / "land.txt").exists():  # the CTO wrote a new one meanwhile: append ours back to it
            with open(D / "land.txt", "a") as f:
                f.write("".join(l + "\n" for l in lines))
            claimed.rename(D / f"land-refused-{fstamp()}.lines")
        else:
            claimed.rename(D / "land.txt")
        log(f"land refused: {why}; lines given back")
        return f"refused: {why} (nothing landed)"

    for line in lines:
        if not re.fullmatch(r"W2-[0-9A-Za-z]+=[0-9a-f]{7,40}", line):
            return give_back(f"malformed land.txt line {line!r}")
    out = LOG / f"land-dispatch-{fstamp()}.out"
    (D / "land-inflight.txt").write_text(json.dumps({"lines": lines, "out": str(out), "started": stamp()}))
    cmd = E("DISPATCH_LAND_CMD")
    argv = (shlex.split(cmd) if cmd else ["setsid", "-f", sys.executable, str(ORCH / "tools/land.py")]) + lines
    with open(out, "w") as o, open(os.devnull) as nul:
        try:
            rc = subprocess.run(argv, stdin=nul, stdout=o, stderr=subprocess.STDOUT, cwd=str(REPO),
                                timeout=TIMEOUT_S).returncode
        except subprocess.TimeoutExpired:
            rc = 124
    log(f"land started: {lines} -> {out.name} (launcher exit {rc})")
    if E("DISPATCH_TEST_FAIL_AFTER_LAUNCH"):
        raise RuntimeError("test: an error right after the launch")
    return "started"


# ---- 5, 6. status and escalation ------------------------------------------------------------------------------------

def write_status(t, started_w2, waits, land_state, new_returns, failures):
    items = unread()
    oldest_item = min(items, key=lambda i: i.stat().st_mtime) if items else None
    age = int(now() - oldest_item.stat().st_mtime) if oldest_item else None
    s = {k: v for k, v in t.items() if not k.startswith("_")}
    s.update(inbox_unread=len(items), inbox_oldest_age_s=age, started_this_tick=started_w2, ready_waits=waits,
             land=land_state, land_pending=[" ".join(e) for e in read_list(D / "land.txt")], new_returns=new_returns,
             last_start=(" ".join(started()[-1][:3]) if started() else None), failures=failures)
    (D / "status.json").write_text(json.dumps(s, indent=1))
    load = "/".join(f"{x:.1f}" for x in t["load"]) if t.get("load") else "?"
    txt = ([f"TICK FAILED in part: {'; '.join(failures)} at {s['time']}"] if failures else []) + [
        f"dispatcher {s['time']}",
        f"leads running ({t['lead_count']}, from the processes): {', '.join(t['leads']) or 'none'}",
        f"load {load} of 20; memory available {t.get('mem_available_mb')} MB; gate {'open' if t['gate_open'] else 'SHUT'}"
        f" ({t['gate'][:120]}); disk {'open' if t['disk_open'] else 'SHUT'}",
        f"heavy slots held: {', '.join(t['slots_held']) or 'none'}; queue {'busy' if t['queue_busy'] else 'free'};"
        f" land: {land_state}; main tree {'clean' if t['main_clean'] else 'NOT clean'} on {t.get('main_branch')}",
        f"inbox unread: {len(items)}" + (f" (oldest {age // 60} min)" if age is not None else ""),
        "ready list: " + ("; ".join(f"{k}: {v}" for k, v in list(waits.items())[:8]) or "nothing waiting")
        + (f"; started {started_w2}" if started_w2 else "")]
    (D / "status.txt").write_text("\n".join(txt) + "\n")
    stale = D / "inbox-stale.txt"
    if age is not None and age >= STALE_S:
        if not stale.exists():  # F1: stable content, written once per stall (the sentinel keys on it)
            stale.write_text(f"{len(items)} inbox item(s) unread; the oldest {oldest_item.name}\n")
    elif stale.exists():
        os.unlink(stale)


def fail_status(why):
    D.mkdir(parents=True, exist_ok=True)
    (D / "status.txt").write_text(f"TICK FAILED: {why} at {stamp()} (this status is not current)\n")


def tick(dry):
    D.mkdir(parents=True, exist_ok=True)
    lock = open(D / "tick.lock", "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log("tick: another tick is running; nothing done")
        return 0
    if (D / "OFF").exists():
        log("tick: OFF present; nothing done")
        return 0
    new, started_w2, waits, land_state, failures = [], None, {}, "not checked", []
    try:
        t = truth()
    except Exception as exc:
        log(f"truth failed: {exc!r}; nothing started or landed this tick")
        fail_status(f"reading the truth: {exc!r}"[:300])
        return 1
    try:
        new = collect_returns(t, dry)
    except Exception as exc:
        failures.append(f"returns: {exc!r}"[:200])
        log(f"returns failed: {exc!r}")
    try:
        started_w2, waits = start_one(t, dry)
    except Exception as exc:
        failures.append(f"start: {exc!r}"[:200])
        log(f"start failed: {exc!r}")
    try:
        land_state = land_step(t, dry)
    except Exception as exc:
        land_state = f"error: {exc!r}"[:200]
        failures.append(f"land: {exc!r}"[:200])
        log(f"land failed: {exc!r}")
    try:
        write_status(t, started_w2, waits, land_state, new, failures)
    except Exception as exc:
        log(f"status failed: {exc!r}")
        fail_status(f"writing the status: {exc!r}"[:300])
    return 0


def main(argv):
    if not argv or argv[0] not in ("tick", "status"):
        sys.exit("usage: dispatcher.py tick [--dry] | status")
    if argv[0] == "status":
        p = D / "status.txt"
        print(p.read_text() if p.exists() else "no status yet")
        return 0
    return tick("--dry" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
