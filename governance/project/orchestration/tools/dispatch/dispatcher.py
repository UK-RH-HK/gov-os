#!/usr/bin/env python3
"""The dispatcher (owner, 2026-11-01: tonight's top priority). A plain program, no AI, outside any Claude session.
Its code is committed here (DEC-1010 item 6); its state stays in .gov-runtime/scratch/orchestrator/dispatch/.

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
CODE = Path(__file__).resolve().parent  # the committed code (DEC-1010 item 6): this folder
# the dispatcher's state (ready.txt, land.txt, inbox/, status, peaks.json, config.json, started.txt, logs, locks, OFF)
# stays in the scratch folder; DISPATCH_STATE (or the older DISPATCH_DIR) moves it, for the tests only
D = STATE = Path(E("DISPATCH_STATE") or E("DISPATCH_DIR") or str(ORCH / "dispatch"))
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
    return any(any(a.endswith(("launch_when_gate_opens.sh", "launch_now.sh")) for a in argv) and w2 in argv
               for argv, _ in procs)


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
    try:
        c = config()
    except Exception as exc:
        c = None
        t["config_error"] = f"config: {exc!r}"[:200]
    facts = proc_facts()
    leads = {}
    for f in facts:
        w2 = lead_w2(f["argv"], f["cwd"])
        if w2:
            leads[w2] = f
    t["lead_ticket_ids"] = [lead_ticket(f["argv"]) for f in leads.values()]
    t["lead_rss_kb"] = {w2: tree_rss(facts, f) for w2, f in leads.items()}
    t["outside_slot"] = heavy_outside_slots(facts, c["outside_slot_limit_s"])
    # F1: a launcher waiting, or a start under 10 minutes old with no lead process and no return, is a lead
    pending = set()
    for argv, _ in procs:
        if any(a.endswith(("launch_when_gate_opens.sh", "launch_now.sh")) for a in argv):
            for a in argv:
                if re.fullmatch(r"W2-[0-9A-Za-z]+", a):
                    pending.add(a)
    for e in started():
        if len(e) < 5:
            continue
        try:
            age = now() - datetime.strptime(" ".join(e[:2]), "%Y-%m-%d %H:%M:%S").timestamp()
        except ValueError:
            age = 0
        lp = LOG / e[-1]
        if age < 600 and not (lp.exists() and lp.stat().st_size > 0):
            pending.add(e[2])
    t["pending_launches"] = sorted(pending - set(t["leads"]))
    t["services_kb"] = services_resident(facts)
    try:
        t["busy_cores"], t["embedding_cores"], t["cpu_measuring"] = real_cpu(facts, bool(E("DISPATCH_DRY_FLAG")))
    except Exception as exc:  # fail closed: without the real CPU, admission refuses
        t["busy_cores"], t["embedding_cores"], t["cpu_measuring"] = None, None, False
        t["cpu_error"] = f"real CPU unreadable: {exc!r}"[:160]
    t["nproc"] = nproc()
    t["rerankers_outside_kb"] = rerankers_outside_leads(facts)
    t["outside_reranker_possible"] = bool(t["rerankers_outside_kb"]) or t["land_running"] or t["close_running"] \
        or t["queue_busy"]
    try:
        pk = peaks(c, bool(E("DISPATCH_DRY_FLAG"))) if c else None
    except Exception as exc:
        pk = None
        t["config_error"] = f"peaks: {exc!r}"[:200]
    t["_c"], t["_pk"] = c, pk
    try:
        t["peaks"] = ({"computed": pk["computed"], "lead_p95_mb": pk["lead"]["rss_kb_p95"] // 1024,
                       "lead_max_mb": pk["lead"]["rss_kb_max"] // 1024} if pk else None)
    except Exception as exc:  # F3: a bad peaks value refuses admission, it never stops the tick
        t["peaks"] = None
        t["config_error"] = f"peaks.json unreadable: {exc!r}"[:200]
    t["admit"], t["admit_reason"] = admit_safely(t, None)  # the status shows the admission of a plain newcomer
    return t



# ---- DEC-1008 item 5: admission by each job's peak ----------------------------------------------------------------

CONFIG = D / "config.json"
PEAKS = D / "peaks.json"
KINDS_HIST = Path(E("DISPATCH_KINDS", str(LOG / "capacity/kinds.jsonl")))
LEADMEM_HIST = Path(E("DISPATCH_LEADMEM", str(LOG / "lead-mem.jsonl")))
GATE_CONFIG = Path(E("DISPATCH_GATE_CONFIG", str(ORCH / "tools/gate-config.json")))
HEAVY = ("gov.context.context_check", "gov.retrieval.retrieve_check", "gov.check.schema", "gov.retrieval.measure")


def config():
    c = {"K": 2, "outside_slot_limit_s": 300, "peaks_refresh_s": 3600, "peaks_max_age_s": 7 * 86400,
         "history_days": 7, "memory_rule": "slots", "min_outside_samples": 120,
         "cpu_margin": 2}
    try:
        c.update(json.loads(CONFIG.read_text()))
    except (OSError, ValueError):
        pass
    try:
        conf = Path(E("DISPATCH_SLOTS_CONF", str(ORCH / "tools/heavy_slots.conf"))).read_text()
        m = re.search(r"^SLOTS=(\d+)", conf, re.M)
        c.setdefault("slots", int(m.group(1)) if m else 3)
    except OSError:
        c.setdefault("slots", 3)
    return c


def proc_facts():
    """[{argv, cwd, pid, ppid, age_s, rss_kb}] (DISPATCH_FAKE_PROCS entries may carry pid, ppid, age_s, rss_kb)."""
    fake = E("DISPATCH_FAKE_PROCS")
    if fake is not None:
        out = []
        for i, p in enumerate(json.loads(Path(fake).read_text())):
            out.append({"argv": p["cmd"].split(), "cwd": p.get("cwd", ""), "pid": p.get("pid", 1000 + i),
                        "ppid": p.get("ppid", 1), "age_s": p.get("age_s", 0), "rss_kb": p.get("rss_kb", 0),
                        "cpu_ticks": p.get("cpu_ticks", 0)})
        return out
    try:
        uptime = float(Path("/proc/uptime").read_text().split()[0])
    except (OSError, ValueError):
        uptime = 0.0
    hz = os.sysconf("SC_CLK_TCK")
    out = []
    for p in glob.glob("/proc/[0-9]*"):
        try:
            argv = [a.decode("utf-8", "replace") for a in Path(p, "cmdline").read_bytes().split(b"\0") if a]
            stat = Path(p, "stat").read_text().rsplit(")", 1)[1].split()
            rss = re.search(r"^VmRSS:\s+(\d+)", Path(p, "status").read_text(), re.M)
            cwd = os.readlink(p + "/cwd")
        except OSError:
            continue
        if argv:
            out.append({"argv": argv, "cwd": cwd, "pid": int(p.rsplit("/", 1)[1]), "ppid": int(stat[1]),
                        "age_s": max(0.0, uptime - int(stat[19]) / hz), "rss_kb": int(rss.group(1)) if rss else 0,
                        "cpu_ticks": int(stat[11]) + int(stat[12])})
    return out


SERVICES = {"embedding": ("llama-server",), "codegraph": ("codebase-memory-mcp",)}  # shared; rerankers are not here:
# a reranker is a child of whoever calls gov retrieve (a lead, whose peak covers it; a queue or close run, inside a slot
# run; the CTO's session, inside the base), so counting it again would double count (measured 2026-11-01).


def under_lead(facts, f):
    by_pid = {x["pid"]: x for x in facts}
    seen, cur = set(), f
    while cur and cur["pid"] not in seen:
        seen.add(cur["pid"])
        if lead_w2(cur["argv"], cur["cwd"]) or (any(MARKER in a for a in cur["argv"])):
            return True
        cur = by_pid.get(cur["ppid"])
    return False


def rerankers_outside_leads(facts):
    """The memory of rerankers whose process is not inside a lead's tree (a queue or close run's, the CTO's)."""
    return sum(f["rss_kb"] for f in facts if f["argv"] and "reranker-venv" in f["argv"][0] and not under_lead(facts, f))


def services_resident(facts):
    out = {}
    for kind, names in SERVICES.items():
        out[kind] = sum(f["rss_kb"] for f in facts if f["argv"] and os.path.basename(f["argv"][0]).startswith(names))
    return out


def admit_safely(t, newcomer_tid):
    """F3: a bad peaks.json or config never raises out of the tick: it refuses, naming why."""
    if t.get("config_error"):
        return False, "not admitted: " + t["config_error"]
    try:
        return admission(t, t["_c"], t["_pk"], newcomer_tid)
    except Exception as exc:
        return False, f"admission error: {exc!r}"[:200]


def cpu_sample():
    """(busy jiffies, total jiffies) of the whole machine from /proc/stat: busy = user + nice + system + irq + softirq
    + steal (iowait and idle are not busy)."""
    f = [int(x) for x in Path(E("DISPATCH_PROCSTAT", "/proc/stat")).read_text().splitlines()[0].split()[1:9]]
    user, nice, system, idle, iowait, irq, softirq, steal = (f + [0] * 8)[:8]
    busy = user + nice + system + irq + softirq + steal
    return busy, busy + idle + iowait


def nproc():
    return int(E("DISPATCH_NPROC") or os.cpu_count() or 1)


def embedding_ticks(facts):
    """{pid: utime + stime jiffies} of the shared embedding server's processes."""
    return {str(f["pid"]): f.get("cpu_ticks", 0) for f in facts
            if f["argv"] and os.path.basename(f["argv"][0]).startswith(SERVICES["embedding"])}


def real_cpu(facts, dry=False):
    """(busy cores, the embedding server's cores, measuring) since the last pass, from /proc deltas over at most 3
    minutes. With no earlier sample, or one older than 3 minutes, the sample is recorded and `measuring` is True: the
    pass refuses every start (fail closed), and the next pass has a real interval. A dry pass records nothing."""
    prev_f = D / "cpu_prev.json"
    busy, total = cpu_sample()
    emb, t_now = embedding_ticks(facts), now()
    rec = {"t": t_now, "busy": busy, "total": total, "emb": emb}
    try:
        prev = json.loads(prev_f.read_text())
        usable = 0 < t_now - prev["t"] <= 180 and total > prev["total"]
    except (OSError, ValueError, KeyError):
        prev, usable = None, False
    if not dry:
        D.mkdir(parents=True, exist_ok=True)
        prev_f.write_text(json.dumps(rec))
    if not usable:
        return None, None, True
    n = nproc()
    busy_cores = n * (busy - prev["busy"]) / (total - prev["total"])
    hz = os.sysconf("SC_CLK_TCK")
    wall = t_now - prev["t"]
    emb_cores = sum(max(0, ticks - prev.get("emb", {}).get(pid, ticks)) for pid, ticks in emb.items()) / hz / wall
    return round(busy_cores, 2), round(emb_cores, 2), False


def lead_ticket(argv):
    for a in argv:
        m = re.search(r'"GOV_TICKET":"([^"]+)"', a)
        if m and MARKER in a:
            return m.group(1)
    return None


def tree_rss(facts, root):
    kids = {}
    for f in facts:
        kids.setdefault(f["ppid"], []).append(f)
    total, stack = 0, [root]
    while stack:
        f = stack.pop()
        total += f["rss_kb"]
        stack.extend(kids.get(f["pid"], []))
    return total


def in_slot(facts, f):
    """Whether a process runs under a heavy-job slot (an ancestor's arguments name a gov-os-heavy-slot lock)."""
    by_pid = {x["pid"]: x for x in facts}
    seen, cur = set(), f
    while cur and cur["pid"] not in seen:
        seen.add(cur["pid"])
        if any("gov-os-heavy-slot" in a or a.endswith("heavy_slot.sh") or a.endswith("rebuild_slot.sh")
               or a.endswith("verify_lock.sh") for a in cur["argv"]):
            return True
        cur = by_pid.get(cur["ppid"])
    return False


def is_gov_check(a):
    """`gov check` by the shim (~/.local/bin/gov check, or an interpreter running it) or `python -m gov.cli.main check`."""
    for i, x in enumerate(a[:4]):
        if (os.path.basename(x) == "gov" or x == "gov.cli.main") and i + 1 < len(a) and a[i + 1] == "check":
            return True
    return False


def is_pytest(a):
    """pytest by its script (also through its shebang: an interpreter then .../pytest) or `python -m pytest`."""
    return bool(a) and (any(os.path.basename(x) in ("pytest", "py.test") for x in a[:4]) or
                        any(a[i] == "-m" and i + 1 < len(a) and a[i + 1] == "pytest" for i in range(min(4, len(a)))))


def single_file_pytest(a):
    """One target that is a file or a test in a file: not a heavy step (the brief's rule). Only `.py` and `.py::`
    arguments count as targets (an option's value such as `--junitxml /tmp/x.xml` is not one); a folder target, or
    none (pytest then collects the whole tree), is heavy."""
    start = next((i + 2 for i in range(len(a) - 1) if a[i] == "-m" and a[i + 1] == "pytest"),
                 next((i + 1 for i, x in enumerate(a[:4]) if os.path.basename(x) in ("pytest", "py.test")), 1))
    rest = a[start:]
    args = [x for i, x in enumerate(rest)  # an argument right after a bare `--option` is that option's value
            if not x.startswith("-") and not (i and rest[i - 1].startswith("--") and "=" not in rest[i - 1])]
    targets = [x for x in args if x.endswith(".py") or ".py::" in x]
    folders = [x for x in args if x not in targets]
    return len(targets) == 1 and not folders


def heavy_outside_slots(facts, limit_s):
    found = []
    for f in facts:
        a = f["argv"]
        heavy = any(h in a for h in HEAVY) or is_gov_check(a) or (is_pytest(a) and not single_file_pytest(a))
        if heavy and f["age_s"] > limit_s and not in_slot(facts, f):
            found.append(f"{' '.join(a[:4])[:80]} (pid {f['pid']}, {int(f['age_s'] // 60)} min, {f['cwd'][-40:]})")
    return found


def pct(values, q):
    v = sorted(values)
    return v[min(len(v) - 1, int(q * (len(v) - 1) + 0.5))] if v else None


def compute_peaks(days):
    """Each kind's p95 and max of CPU (cores) and memory (kB), from the last `days` of history; a lead's own max."""
    cutoff = datetime.fromtimestamp(now() - days * 86400).strftime("%Y-%m-%dT%H:%M:%S")
    kinds, rebuild_emb, leads, own = {}, [], [], {}
    if KINDS_HIST.exists():
        for line in KINDS_HIST.read_text().splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("t", "") < cutoff:
                continue
            ks = r.get("kinds", {})
            for k, v in ks.items():
                kinds.setdefault(k, {"cpu": [], "rss_kb": []})
                kinds[k]["cpu"].append(v.get("cpu", 0))
                kinds[k]["rss_kb"].append(v.get("rss_kb", 0))
            if ks.get("rebuild", {}).get("n", 0) > 0:
                rebuild_emb.append((ks["rebuild"].get("cpu", 0) + ks.get("embedding", {}).get("cpu", 0),
                                    ks["rebuild"].get("rss_kb", 0) + ks.get("embedding", {}).get("rss_kb", 0)))
    minute_runs, per_run = {}, []
    if KINDS_HIST.exists():
        for line in KINDS_HIST.read_text().splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("t", "") < cutoff:
                continue
            tr = r.get("kinds", {}).get("test_run", {})
            minute_runs[r["t"][:16]] = tr.get("n", 0)
            if tr.get("n", 0) > 0:
                per_run.append(tr.get("rss_kb", 0) / max(1, -(-tr["n"] // 7)))  # 1 main + 6 workers a slot run
    outside, inside, own_out = [], [], {}
    if LEADMEM_HIST.exists():
        for line in LEADMEM_HIST.read_text().splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("t", "") < cutoff:
                continue
            runs = minute_runs.get(r["t"][:16])
            for tid, kb in (r.get("leads_kb") or {}).items():
                leads.append(kb)
                own[tid] = max(own.get(tid, 0), kb)
                if runs == 0:  # no test run anywhere on the machine that minute: every lead was outside verification
                    outside.append(kb)
                    own_out[tid] = max(own_out.get(tid, 0), kb)
                elif runs is not None:
                    inside.append(kb)
    out = {"computed": stamp(), "days": days, "kinds": {}}
    for k, v in kinds.items():
        out["kinds"][k] = {"cpu_p95": pct(v["cpu"], 0.95), "cpu_max": max(v["cpu"]),
                           "rss_kb_p95": pct(v["rss_kb"], 0.95), "rss_kb_max": max(v["rss_kb"]), "samples": len(v["cpu"])}
    if rebuild_emb:
        out["kinds"]["rebuild_with_embedding"] = {
            "cpu_p95": pct([c for c, _ in rebuild_emb], 0.95), "cpu_max": max(c for c, _ in rebuild_emb),
            "rss_kb_p95": pct([m for _, m in rebuild_emb], 0.95), "rss_kb_max": max(m for _, m in rebuild_emb),
            "samples": len(rebuild_emb)}
    if leads:
        out["lead"] = {"rss_kb_p95": pct(leads, 0.95), "rss_kb_max": max(leads), "samples": len(leads)}
    out["lead_own_max_kb"] = own
    if outside:
        out["lead_outside"] = {"rss_kb_p95": pct(outside, 0.95), "rss_kb_max": max(outside), "samples": len(outside)}
        out["lead_own_outside_max_kb"] = own_out
    if inside:
        out["lead_inside"] = {"rss_kb_p95": pct(inside, 0.95), "rss_kb_max": max(inside), "samples": len(inside)}
    if per_run:
        out["test_run_per_slot"] = {"rss_kb_p95": pct(per_run, 0.95), "rss_kb_max": max(per_run), "samples": len(per_run)}
    # a slot run's memory: the larger of the test run's own share and the leads' rise while test runs ran (the
    # rerankers and services a run starts are sampled under other kinds)
    if outside and inside:
        rise = pct(inside, 0.95) - pct(outside, 0.95)
        out["slot_run_kb"] = max(rise, out.get("test_run_per_slot", {}).get("rss_kb_p95", 0))
    return out


def peaks(c, dry):
    """peaks.json, refreshed at most hourly; None when missing or older than peaks_max_age_s (the fallback)."""
    try:
        cur = json.loads(PEAKS.read_text())
        age = now() - datetime.strptime(cur["computed"], "%Y-%m-%d %H:%M:%S").timestamp()
    except (OSError, ValueError, KeyError):
        cur, age = None, None
    if (cur is None or age >= c["peaks_refresh_s"]) and not dry and E("DISPATCH_NO_PEAKS_REFRESH") is None:
        try:
            fresh = compute_peaks(c["history_days"])
            if fresh.get("lead"):
                PEAKS.write_text(json.dumps(fresh, indent=1))
                cur, age = fresh, 0
        except Exception as exc:
            log(f"peaks refresh failed: {exc!r}")
    if cur is None or age is None or age > c["peaks_max_age_s"] or not cur.get("lead"):
        return None
    return cur


def admission(t, c, pk, newcomer_tid=None):
    """The real CPU first, for every admission (DEC-1010 item 7; review: the fallback included); then the rules."""
    if t.get("cpu_error"):
        return False, t["cpu_error"]
    if t.get("cpu_measuring"):
        return False, "real CPU: measuring (first pass, or the last sample is over 3 minutes old); no start this pass"
    emb_p95 = ((pk or {}).get("kinds", {}).get("embedding", {}).get("cpu_p95") or 0)
    emb_room = max(0.0, emb_p95 - (t.get("embedding_cores") or 0))
    limit = t["nproc"] - c["cpu_margin"]
    if t["busy_cores"] + emb_room >= limit:
        return False, (f"real CPU: {t['busy_cores']} busy cores + {round(emb_room, 2)} for the embedding server's p95 "
                       f">= {t['nproc']} - margin {c['cpu_margin']}")
    return _admission_rules(t, c, pk, newcomer_tid)


def _admission_rules(t, c, pk, newcomer_tid=None):
    """(admit, reason). Memory: available + the leads' current memory >= floor + each running lead's peak + the new
    lead's peak; CPU: running leads < slots x K; never while a heavy step runs outside a slot. No peaks: gate_check."""
    if pk is None:
        return t["gate_open"], "fallback to gate_check (peaks.json missing or older than 7 days): " + t["gate"][:120]
    if t["outside_slot"]:
        return False, f"a heavy step runs outside a slot over {c['outside_slot_limit_s'] // 60} min: {t['outside_slot'][0]}"
    cap = c["slots"] * c["K"]
    running = t["lead_count"] + len(t.get("pending_launches", []))
    if running >= cap:
        return False, (f"{t['lead_count']} leads running and {len(t.get('pending_launches', []))} launching, the CPU rule "
                       f"allows {cap} ({c['slots']} slots x K {c['K']})")
    try:
        floor = json.loads(GATE_CONFIG.read_text())["floor_kb"]
    except (OSError, ValueError, KeyError):
        return False, "no floor in gate-config.json (fail closed)"
    have = (t["mem_available_mb"] or 0) * 1024 + sum(t["lead_rss_kb"].values())
    rule = c.get("memory_rule", "slots")
    lo = pk.get("lead_outside")
    # F2: the shared services' headroom (each at most its p95 above what it holds now), counted once
    headroom = sum(max(0, (pk.get("kinds", {}).get(k, {}).get("rss_kb_p95") or 0) - t.get("services_kb", {}).get(k, 0))
                   for k in SERVICES)
    # a reranker outside every lead tree (a queue or close run's, which no lead's peak covers): its kind's p95 above
    # what such rerankers hold now, while a queue or close run, or such a reranker, exists (review of 2026-11-01)
    if t.get("outside_reranker_possible"):
        headroom += max(0, (pk.get("kinds", {}).get("reranker", {}).get("rss_kb_p95") or 0)
                        - t.get("rerankers_outside_kb", 0))
    pending = len(t.get("pending_launches", []))
    if rule == "slots":
        if not (lo and lo["samples"] >= c["min_outside_samples"] and pk.get("slot_run_kb")):  # F4: too little history
            return t["gate_open"], ("fallback to gate_check (fewer than "
                                    f"{c['min_outside_samples']} minutes outside verification): " + t["gate"][:120])
        p95, own = lo["rss_kb_p95"], pk.get("lead_own_outside_max_kb", {})
        slots_kb = c["slots"] * pk["slot_run_kb"]
        how_lead = "outside verification"
    else:  # the literal rule (DEC-1008 item 5 as written)
        p95, own = pk["lead"]["rss_kb_p95"], pk.get("lead_own_max_kb", {})
        slots_kb = 0
        how_lead = "all samples"
    newcomer = max(p95, own.get(newcomer_tid or "", 0))  # F4: the newcomer at the larger of p95 and its own max
    need = floor + newcomer + sum(max(p95, own.get(tid or "", 0)) for tid in t["lead_ticket_ids"]) \
        + pending * p95 + slots_kb + headroom
    how = (f"{rule} rule: floor + {len(t['lead_ticket_ids'])} running + {pending} launching at {p95 // 1024} MB "
           f"({how_lead}) or their own max + the newcomer {newcomer // 1024} MB"
           + (f" + {c['slots']} slot runs at {pk['slot_run_kb'] // 1024} MB" if slots_kb else "")
           + f" + services' headroom {headroom // 1024} MB")
    if have < need:
        return False, f"memory: available + leads' {have // 1024} MB < {need // 1024} MB ({how})"
    return True, f"admits: {t['lead_count']} of {cap} leads; memory {have // 1024} MB >= {need // 1024} MB ({how})"

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
    ok, why = admit_safely(t, tid)
    if not ok:
        return "not admitted: " + why[:200]
    if not t["disk_open"]:
        return "disk gate shut"
    return None


def default_launch_argv():
    """The owner's launch form without the gate wait (admission is the dispatcher's): dispatch/launch_now.sh."""
    return ["setsid", "-f", "bash", str(CODE / "launch_now.sh")]


def launch(w2, tid, brief, logf):
    cmd = E("DISPATCH_LAUNCH_CMD")
    errf = LOG / f"{w2}-{datetime.fromtimestamp(now()).strftime('%Y%m%d-%H%M')}-launch.txt"
    argv = (shlex.split(cmd) if cmd else default_launch_argv()) \
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
        f"load {load}; real busy cores {t.get('busy_cores')} of {t.get('nproc')} (the embedding server "
        f"{t.get('embedding_cores')}); memory available {t.get('mem_available_mb')} MB; gate_check (for comparison) {'open' if t['gate_open'] else 'SHUT'}"
        f" ({t['gate'][:120]}); disk {'open' if t['disk_open'] else 'SHUT'}",
        f"admission (by peaks, DEC-1008 item 5): {t['admit_reason'][:200]}",
        (f"peaks {t['peaks']['computed']}: a lead p95 {t['peaks']['lead_p95_mb']} MB, max {t['peaks']['lead_max_mb']} MB"
         if t.get("peaks") else "peaks: none (gate_check decides)"),
        ("FINDING: heavy step(s) outside a slot: " + "; ".join(t["outside_slot"][:3])) if t["outside_slot"] else
        "heavy steps outside a slot: none",
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


def state_is_code():
    st, code = STATE.resolve(), CODE.resolve()
    return st == code or code in st.parents


def main(argv):
    if not argv or argv[0] not in ("tick", "status"):
        sys.exit("usage: dispatcher.py tick [--dry] | status")
    if state_is_code() and E("DISPATCH_TEST") != "1":
        sys.exit(f"dispatcher: refused: the state folder {STATE} is the code folder or inside it (a stray "
                 "DISPATCH_STATE or DISPATCH_DIR?); nothing done")
    if argv[0] == "status":
        p = D / "status.txt"
        print(p.read_text() if p.exists() else "no status yet")
        return 0
    if "--dry" in argv:
        os.environ["DISPATCH_DRY_FLAG"] = "1"
    return tick("--dry" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
