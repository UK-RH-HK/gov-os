#!/usr/bin/env python3
"""The dispatcher (owner, 2026-11-01: tonight's top priority). A plain program, no AI, outside any Claude session.
Its code is committed here (DEC-1010 item 6); its state stays in .gov-runtime/scratch/orchestrator/dispatch/.

    python3 dispatcher.py tick [--dry]     # one pass (cron every minute, or loop.sh); a second concurrent pass exits
    python3 dispatcher.py status           # prints status.txt
    python3 dispatcher.py harvest          # the guard harvest alone (a pass starts it detached, after its decisions)

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
     from `nightly_hold_from` (03:15) until the nightly has started (or `nightly_hold_until`, 05:30) nothing is
     claimed (DEC-1018 item 1); a landing already in flight is finalised as usual;
  5. the guard harvest, when due: detached, with its own lock and time limit, after the start and land decisions;
     its last result is shown in the status, and a failure or timeout is one of the pass's failures;
  5b. the embedding servers' health (DEC-1015 item 2; by progress, DEC-1032): each server's runner judged by the tasks
     it completes (its log) and the requests waiting on it (`ss`): BUSY while tasks complete, IDLE when nothing waits,
     HUNG only when requests have waited `embed_stall_s` with no task or 2xx request during that wait, FAILING after
     `embed_fail_after` failed requests in a row (4xx/5xx, no 2xx since), NOT RUNNING when nothing listens; the
     test request only as the fallback when the shared server's log is unreadable, every `embed_check_every` passes
     (one Server: item, one line in inbox-stale.txt, once per incident); while the shared server is HUNG, FAILING or
     NOT RUNNING, step 3 starts nothing (the last pass's state); a restart only when `embed_restart_cmd` is configured, the
     incident has lasted `embed_restart_after_s`, at most one per 30 minutes;
  5c. the heavy-slot holders' progress: a holder whose process tree's CPU time has not grown for `slot_idle_s` is
     IDLE (one Slot: item and one line, once per holder); never killed;
  5d. the GPU (DEC-1030), every `gpu_check_every` passes: its memory, utilisation and holders (nvidia-smi, classified
     by command line and parents), each embedding server's layers on the GPU from its log (read on from a saved
     offset); a new CUDA error, or a load with 0 or only part of its layers where the GPU is expected, is one
     gpu-alert item and one gpu: line at once, once per incident; an unreadable nvidia-smi is a status line, never a
     failure;
  6. status.json and status.txt; 7. inbox-stale.txt, one stable line per cause (the sentinel's watch silent, the
     embedding server HUNG, a GPU alert unread or 0 layers, a slot holder IDLE, an inbox item unread 30 minutes),
     each written once per stall.
Admission (step 3, DEC-1032) needs room on every resource, each from measured peaks: the real CPU, memory (with the
lead cap derived from it), GPU memory (from the last pass's read), and counts the rerankers; the heavy slots it
reckons with follow where the shared embedder runs (`slots_gpu` on the GPU, `slots_cpu` otherwise). The status's
`Balance:` line shows them all.
It never starts what is not in ready.txt and never lands what is not in land.txt (the CTO's lists).
Every external command and path can be replaced through DISPATCH_* variables, for the tests only.
"""
import fcntl
import glob
import hashlib
import http.client
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime
import urllib.error
import urllib.request
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
SLOT_GLOB = E("DISPATCH_SLOT_GLOB", "/tmp/gov-os-heavy-slot-*.lock")  # the slot-progress pass (DEC-1015 item 2)
PROC = Path(E("DISPATCH_PROC", "/proc"))  # the process table that pass reads; a planted one in the tests
EMBED_URL = "http://127.0.0.1:11434/api/embed"
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


def sh(cmd, limit=None, **kw):
    """Every external command with a time limit (TIMEOUT_S unless `limit`); a timeout is a failed command (124)."""
    limit = limit or TIMEOUT_S
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=limit, **kw)
        return R(r.returncode, r.stdout, r.stderr)
    except subprocess.TimeoutExpired:
        return R(124, "", f"timed out after {limit} s: {' '.join(map(str, cmd))[:120]}")


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
    t["closing_w2s"] = sorted({x for a, _ in procs if runs_script(a, "close_build.py")
                               for x in a if re.fullmatch(r"W2-[0-9A-Za-z]+", x)})
    t["queue_busy"] = lock_held(RUN_LOCK) or t["land_running"]
    t["main_clean"] = tree_clean(REPO)
    st = sh(["git", "-C", str(REPO), "status", "--porcelain"])
    t["main_dirty"] = [l[3:] for l in st.stdout.splitlines() if l.strip()] if st.returncode == 0 else ["(git failed)"]
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
    try:  # DEC-1032: the rerankers, the GPU as the last pass read it, and the heavy slots by the embedder's device
        t["rerankers"] = rerankers(facts, c or {})
        t["reranker_reserve"] = reranker_reserve(t["rerankers"], c or {}, pk, bool(E("DISPATCH_DRY_FLAG")))
        t["gpu_last"] = gpu_last(c or {})
        t["slots_target"], t["slots_device"] = slots_by_device(c or {})
    except Exception as exc:  # fail closed: admission refuses, naming why
        t["config_error"] = f"balance: {exc!r}"[:200]
    t["admit"], t["admit_reason"] = admit_safely(t, None)  # the status shows the admission of a plain newcomer
    try:
        t["lead_cap"] = lead_cap(t, c, t["_pk"]) if c and t["_pk"] else None
    except Exception:  # noqa: BLE001 - shown as unknown; admission already said why
        t["lead_cap"] = None
    return t



# ---- DEC-1008 item 5: admission by each job's peak ----------------------------------------------------------------

CONFIG = D / "config.json"
PEAKS = D / "peaks.json"
KINDS_HIST = Path(E("DISPATCH_KINDS", str(LOG / "capacity/kinds.jsonl")))
LEADMEM_HIST = Path(E("DISPATCH_LEADMEM", str(LOG / "lead-mem.jsonl")))
GATE_CONFIG = Path(E("DISPATCH_GATE_CONFIG", str(ORCH / "tools/gate-config.json")))
HEAVY = ("gov.context.context_check", "gov.retrieval.retrieve_check", "gov.check.schema", "gov.retrieval.measure")


def config():
    c = {"K": 2,  # no longer used: the lead cap comes from memory (DEC-1032), not slots x K
         "outside_slot_limit_s": 300, "peaks_refresh_s": 3600, "peaks_max_age_s": 7 * 86400,
         "history_days": 7, "memory_rule": "slots", "min_outside_samples": 120,
         "cpu_margin": 2,
         # DEC-1015 item 2: the embedding server's health, and the slot holders' progress
         "embed_check_every": 5, "embed_timeout_s": 30, "embed_hung_after": 3, "embed_restart_cmd": None,
         "embed_restart_after_s": 900, "embed_restart_min_gap_s": 1800, "embed_model": "qwen3-embedding:0.6b",
         "embed_url": EMBED_URL, "slot_idle_s": 900,
         # DEC-1032: each embedding server judged by its runner's progress (its log, gpu_logs) and the requests
         # waiting on its port (`ss`); the test request above only as the fallback, every embed_check_every passes
         "embed_stall_s": 180, "embed_ports": dict(EMBED_PORTS), "embed_ss": "ss", "embed_fail_after": 3,
         "embed_fail_clear_s": 300,
         # DEC-1030: the GPU, its holders and each embedding model's layers (gpu_logs and gpu_expected merge per server)
         "gpu_smi": GPU_SMI, "gpu_smi_timeout_s": 10, "gpu_logs": dict(GPU_LOGS), "gpu_expected": dict(GPU_EXPECTED),
         "gpu_check_every": 1, "gpu_alert_gap_s": 0, "gpu_log_baseline_mb": 32, "gpu_log_read_max_mb": 64,
         # DEC-1032: the whole machine balanced by measured peaks: the CPU band shown, GPU memory in admission (the
         # last pass's read, at most gpu_state_max_age_s old), the rerankers' GPU slots (their lock files), the heavy
         # slots by the shared embedder's device
         "cpu_band": [14, 18], "gpu_headroom_mib": 2048, "reranker_gpu_mib": 3584, "rerank_gpu_slots": 2,
         "rerank_gpu_glob": RERANK_GPU_GLOB, "gpu_state_max_age_s": 300, "slots_gpu": 3, "slots_cpu": 2,
         # review of v4.6, F4: the rerankers' memory reserved at most as the allowed number (rerank_gpu_slots: the rest
         # end, DEC-1033) x one reranker's measured peak, from the dispatcher's own samples since this time; the
         # rerankers' 7-day p95 only while fewer than reranker_min_samples
         "reranker_era_from": "2026-11-02 13:00", "reranker_min_samples": 30, "reranker_min_span_s": 86400,
         # DEC-1018 item 1: no landing claimed from this time until the nightly has started, or until the second
         "nightly_hold_from": "03:15", "nightly_hold_until": "05:30"}
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


def is_reranker(argv):
    """A reranker process: the reranker environment's interpreter, or `rerank_worker` among its first arguments."""
    return bool(argv) and ("reranker-venv" in argv[0] or any("rerank_worker" in a for a in argv[1:4]))


def rerankers(facts, c):
    """DEC-1032: the rerankers counted: how many, their RSS (all, and outside every lead tree), and how many hold a GPU
    slot (the holders of the `rerank_gpu_glob` lock files in the lock table; None when it is unreadable)."""
    rr = [f for f in facts if is_reranker(f["argv"])]
    try:
        held = len(lock_holders(E("DISPATCH_RERANK_GLOB") or c.get("rerank_gpu_glob") or RERANK_GPU_GLOB))
    except OSError:
        held = None
    return {"n": len(rr), "rss_kb": sum(f["rss_kb"] for f in rr), "each_kb": [f["rss_kb"] for f in rr],
            "outside_kb": sum(f["rss_kb"] for f in rr if not under_lead(facts, f)),
            "gpu_held": held, "gpu_slots": int(c.get("rerank_gpu_slots", 2))}


def reranker_reserve(rr, c, pk, dry):
    """Review of v4.6, F4 (DEC-1033: at most `rerank_gpu_slots` rerankers, on the GPU; the rest end): the memory kept
    for rerankers outside the leads is at most the allowed number x one reranker's measured peak, the largest RSS of
    any reranker process in the dispatcher's own samples (one a reranker a pass, reranker-peak.json) since
    `reranker_era_from`; and never more than the rerankers' p95 when one is known. Until the samples number
    `reranker_min_samples` (30) AND span `reranker_min_span_s` (86400: a day's load, round 2 G2) it is the rerankers'
    p95 (peaks.json), as before. A dry pass records nothing. {kb, how, samples, span_s, peak_kb, allowed}."""
    era = str(c.get("reranker_era_from", "2026-11-02 13:00"))
    era_t = datetime.strptime(era, "%Y-%m-%d %H:%M").timestamp()
    st = load_json("reranker-peak.json", {})
    if st.get("era") != era or not all(isinstance(st.get(k), (int, float)) for k in ("samples", "max_kb")):
        st = {"era": era, "samples": 0, "max_kb": 0}  # a new era, or a damaged record (G3): counted afresh
    each = [kb for kb in rr.get("each_kb", []) if kb > 0]
    if not dry and each and now() >= era_t:
        st.setdefault("first_at", now())
        st.update(samples=st["samples"] + len(each), max_kb=max([st["max_kb"]] + each), at=stamp())
        D.mkdir(parents=True, exist_ok=True)
        tmp = D / "reranker-peak.json.tmp"
        tmp.write_text(json.dumps(st))
        os.replace(tmp, D / "reranker-peak.json")
    p95 = ((pk or {}).get("kinds", {}).get("reranker", {}).get("rss_kb_p95") or 0)
    allowed, need = int(c.get("rerank_gpu_slots", 2)), int(c.get("reranker_min_samples", 30))
    span, need_span = now() - float(st.get("first_at") or now()), float(c.get("reranker_min_span_s", 86400))
    if st["samples"] >= need and span >= need_span:
        kb = allowed * st["max_kb"]
        how = f"{allowed} x the {st['max_kb'] // 1024} MB peak ({st['samples']} samples since {era})"
        if p95 and p95 < kb:
            kb, how = p95, f"the rerankers' p95, under {how}"
    else:
        kb, how = p95, (f"the rerankers' p95 ({st['samples']} of {need} samples, {span / 3600:.1f} of "
                        f"{need_span / 3600:.0f} h, since {era})")
    return {"kb": kb, "how": how, "samples": st["samples"], "span_s": round(span), "peak_kb": st["max_kb"],
            "allowed": allowed}


def gpu_last(c):
    """The GPU as the last pass read it (gpu-health.json): {used_mib, total_mib, free_mib, age_s, holders}, or None when
    unread, unreadable, or older than `gpu_state_max_age_s` (300)."""
    g = load_json("gpu-health.json", {}).get("gpu") or {}
    if not g.get("ok") or g.get("used_mib") is None or not g.get("total_mib"):
        return None
    age = now() - float(g.get("at") or 0)
    if age > float(c.get("gpu_state_max_age_s", 300)):
        return None
    counts = {}
    for h in g.get("holders") or []:
        counts[h.get("kind", "other")] = counts.get(h.get("kind", "other"), 0) + 1
    return {"used_mib": g["used_mib"], "total_mib": g["total_mib"], "free_mib": g["total_mib"] - g["used_mib"],
            "age_s": round(age), "holders": counts}


def slots_by_device(c):
    """DEC-1032: the heavy slots follow where the shared embedder runs: all its layers on the GPU, `slots_gpu` (3);
    none or only part, `slots_cpu` (2); not known yet (no load line seen), heavy_slots.conf's number. (target, device)"""
    lay = (load_json("gpu-health.json", {}).get("layers") or {}).get("shared")
    if not lay or not lay.get("y"):
        return int(c.get("slots", 3)), "unknown"
    if lay["x"] >= lay["y"]:
        return int(c.get("slots_gpu", 3)), f"gpu {lay['x']}/{lay['y']}"
    return int(c.get("slots_cpu", 2)), ("cpu" if lay["x"] == 0 else "partial") + f" {lay['x']}/{lay['y']}"


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
    gpu_ok, gpu_why = gpu_room(t, c)  # DEC-1032: GPU memory, for every admission too
    if not gpu_ok:
        return False, gpu_why
    ok, why = _admission_rules(t, c, pk, newcomer_tid)
    return ok, (f"{why}; {gpu_why}" if ok else why)


def gpu_room(t, c):
    """DEC-1032: (room, reason). The GPU's free memory (the last pass's read) must cover the newcomer's expected GPU
    need: one reranker's share (`reranker_gpu_mib`) while a GPU reranker slot is free (a lead's reranker then takes
    it), else none; plus `gpu_headroom_mib` (2048). A GPU not read in the last `gpu_state_max_age_s` is not judged
    (said so): the GPU watch alerts on it apart, and its absence is not a shortage."""
    g = t.get("gpu_last")
    if not g:
        return True, "GPU memory: not judged (no GPU read in the last pass)"
    rr = t.get("rerankers") or {}
    held, slots = rr.get("gpu_held"), rr.get("gpu_slots", int(c.get("rerank_gpu_slots", 2)))
    free_slot = held is None or held < slots  # the lock table unreadable: priced as if a slot were free
    share = int(c.get("reranker_gpu_mib", 3584)) if free_slot else 0
    need = share + int(c.get("gpu_headroom_mib", 2048))
    how = (f"a reranker's {share} MiB (a GPU reranker slot free: {'?' if held is None else held} of {slots} held)"
           if share else f"no reranker share (all {slots} GPU reranker slots held)") \
        + f" + headroom {int(c.get('gpu_headroom_mib', 2048))} MiB"
    if g["free_mib"] < need:
        return False, f"GPU memory: {g['free_mib']} MiB free < {need} MiB ({how})"
    return True, f"GPU memory {g['free_mib']} MiB free >= {need} MiB"


def memory_room(t, c, pk):
    """The memory rule's parts: {floor, have, p95, own, slots_n, slots_kb, headroom, rule, how_lead}, or (None, why)
    when the rule cannot price (no floor: refuse; too little history: gate_check decides)."""
    try:
        floor = json.loads(GATE_CONFIG.read_text())["floor_kb"]
    except (OSError, ValueError, KeyError):
        return None, (False, "no floor in gate-config.json (fail closed)")
    have = (t["mem_available_mb"] or 0) * 1024 + sum(t["lead_rss_kb"].values())
    rule = c.get("memory_rule", "slots")
    lo = pk.get("lead_outside")
    # F2: the shared services' headroom (each at most its p95 above what it holds now), counted once
    headroom = sum(max(0, (pk.get("kinds", {}).get(k, {}).get("rss_kb_p95") or 0) - t.get("services_kb", {}).get(k, 0))
                   for k in SERVICES)
    # a reranker outside every lead tree (a queue or close run's, which no lead's peak covers): its kind's p95 above
    # what such rerankers hold now, while a queue or close run, or such a reranker, exists (review of 2026-11-01);
    # a reranker inside a lead's tree is in that lead's current memory and its peak (DEC-1032: all are counted)
    if t.get("outside_reranker_possible"):  # F4: re-priced for DEC-1033 (reranker_reserve), the old p95 as fallback
        reserve = (t.get("reranker_reserve") or {}).get("kb")
        if reserve is None:
            reserve = pk.get("kinds", {}).get("reranker", {}).get("rss_kb_p95") or 0
        headroom += max(0, reserve - t.get("rerankers_outside_kb", 0))
    if rule == "slots":
        if not (lo and lo["samples"] >= c["min_outside_samples"] and pk.get("slot_run_kb")):  # F4: too little history
            return None, (t["gate_open"], ("fallback to gate_check (fewer than "
                                           f"{c['min_outside_samples']} minutes outside verification): "
                                           + t["gate"][:120]))
        p95, own = lo["rss_kb_p95"], pk.get("lead_own_outside_max_kb", {})
        # DEC-1032: the slots by the embedder's device, never fewer than the slots held now
        slots_n = max(int(t.get("slots_target") or c["slots"]), len(t.get("slots_held") or []))
        slots_kb = slots_n * pk["slot_run_kb"]
        how_lead = "outside verification"
    else:  # the literal rule (DEC-1008 item 5 as written)
        p95, own = pk["lead"]["rss_kb_p95"], pk.get("lead_own_max_kb", {})
        slots_n, slots_kb = 0, 0
        how_lead = "all samples"
    return dict(floor=floor, have=have, p95=p95, own=own, slots_n=slots_n, slots_kb=slots_kb, headroom=headroom,
                rule=rule, how_lead=how_lead), None


def lead_cap(t, c, pk):
    """DEC-1032: the lead cap from memory, replacing slots x K: floor(room / a lead's p95), where room is the memory
    the leads may hold (available + the leads' current trees - the floor - the slot runs - the services' headroom).
    {cap, room_kb, p95_kb} or None when the memory rule cannot price."""
    m, _ = memory_room(t, c, pk)
    if not m or not m["p95"]:
        return None
    room = m["have"] - m["floor"] - m["slots_kb"] - m["headroom"]
    return {"cap": max(0, int(room // m["p95"])), "room_kb": room, "p95_kb": m["p95"]}


def _admission_rules(t, c, pk, newcomer_tid=None):
    """(admit, reason). Never while a heavy step runs outside a slot; the lead cap from memory (DEC-1032); memory:
    available + the leads' current memory >= floor + each running lead's peak + the new lead's peak + the slot runs +
    the services' headroom. No peaks: gate_check."""
    if pk is None:
        return t["gate_open"], "fallback to gate_check (peaks.json missing or older than 7 days): " + t["gate"][:120]
    if t["outside_slot"]:
        return False, f"a heavy step runs outside a slot over {c['outside_slot_limit_s'] // 60} min: {t['outside_slot'][0]}"
    m, verdict = memory_room(t, c, pk)
    if m is None:
        return verdict
    floor, have, p95, own, headroom = m["floor"], m["have"], m["p95"], m["own"], m["headroom"]
    pending = len(t.get("pending_launches", []))
    running = t["lead_count"] + pending
    room = have - floor - m["slots_kb"] - headroom
    cap = max(0, int(room // p95)) if p95 else 0
    if running + 1 > cap:
        return False, (f"memory: lead cap {cap} ({m['rule']} rule: {room // 1024} MB of room / {p95 // 1024} MB a lead, "
                       f"{m['how_lead']}): {t['lead_count']} leads running and {pending} launching")
    newcomer = max(p95, own.get(newcomer_tid or "", 0))  # F4: the newcomer at the larger of p95 and its own max
    need = floor + newcomer + sum(max(p95, own.get(tid or "", 0)) for tid in t["lead_ticket_ids"]) \
        + pending * p95 + m["slots_kb"] + headroom
    rr = t.get("rerankers") or {}
    how = (f"{m['rule']} rule: floor + {len(t['lead_ticket_ids'])} running + {pending} launching at {p95 // 1024} MB "
           f"({m['how_lead']}) or their own max + the newcomer {newcomer // 1024} MB"
           + (f" + {m['slots_n']} slot runs at {pk['slot_run_kb'] // 1024} MB" if m["slots_kb"] else "")
           + f" + services' headroom {headroom // 1024} MB"
           + (f"; rerankers {rr.get('n', 0)} at {rr.get('rss_kb', 0) // 1024} MB now, "
              f"{rr.get('outside_kb', 0) // 1024} MB outside the leads" if rr else ""))
    if have < need:
        return False, f"memory: available + leads' {have // 1024} MB < {need // 1024} MB ({how})"
    return True, (f"admits: {t['lead_count']} of {cap} leads (cap from memory); memory {have // 1024} MB >= "
                  f"{need // 1024} MB ({how})")

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
    item, n = D / "inbox" / f"{fstamp()}-{name}.txt", 1
    while True:  # F5 (v4 review): never overwrite an item (a name used twice in one second gets -2, -3, ...)
        try:
            with open(item, "x") as f:
                f.write(body)
            return item
        except FileExistsError:
            n += 1
            item = D / "inbox" / f"{fstamp()}-{name}-{n}.txt"


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


KEY = re.compile(r"baseline|measure|figures|hit@5|findings report|probe record|research record|PACKAGE|returns? PACKAGES",
                 re.I)


def seen_set(name):
    f = D / name
    return set(f.read_text().splitlines()) if f.exists() else set()


def mark_seen(name, items):
    if items:
        with open(D / name, "a") as f:
            f.write("".join(i + "\n" for i in items))


def change_key(wt, h, tree, subj):
    """F5 (v4 review): what a commit changes, kept across a rebase: its stable patch-id; else (no patch-id, as for
    an empty commit) its subject plus its tree."""
    show = sh(["git", "-C", str(wt), "show", "--format=", h])
    if show.returncode == 0 and show.stdout:
        pid = sh(["git", "-C", str(wt), "patch-id", "--stable"], input=show.stdout)
        if pid.returncode == 0 and pid.stdout.split():
            return "patch " + pid.stdout.split()[0]
    return "tree " + tree + " " + hashlib.sha1(subj.encode()).hexdigest()[:12]


def watch_interim(dry):
    """A lead's new commit (not on w2/integrate) whose subject marks a key result: one inbox item, once. A worktree
    seen for the first time has its history marked seen silently. A key result is known by what it changes (its
    patch-id), so the same commit rebased is not reported again."""
    seen = seen_set("interim-seen.txt")
    known = {x.split()[0] for x in seen if x}
    new_seen, found = [], []
    for wt in sorted(WT.glob("*")) if WT.is_dir() else []:
        name = wt.name
        if not wt.is_dir() or name.endswith("-tests") or name.startswith("W2-00-") or not (wt / ".git").exists():
            continue
        r = sh(["git", "-C", str(wt), "log", "--format=%h%x09%T%x09%s", "-20", "HEAD", "--not", "w2/integrate"])
        if r.returncode:
            continue
        first = name not in known
        if first:
            new_seen.append(f"{name} (watched)")
        for line in r.stdout.splitlines():
            h, _, rest = line.partition("\t")
            tree, _, subj = rest.partition("\t")
            if f"{name} {h}" in seen:
                continue
            new_seen.append(f"{name} {h}")
            if not KEY.search(subj):
                continue
            ck = f"{name} {change_key(wt, h, tree, subj)}"  # only for key results: two short commands each
            if ck in seen or ck in new_seen:
                continue
            new_seen.append(ck)
            if not first:
                found.append((name, h, subj))
    if dry:
        for n, h, subj in found:
            log(f"would report an interim result: {n} {h} {subj[:80]}")
        return [f"{n} {h}" for n, h, _ in found]
    mark_seen("interim-seen.txt", new_seen)
    for n, h, subj in found:
        inbox_item(f"{n}-interim-{h}", f"log: (interim)\nInterim: {n}\nstatus: interim result {h}: {subj[:200]}\n")
        log(f"interim result: {n} {h} {subj[:80]}")
    return [f"{n} {h}" for n, h, _ in found]


def judged(line):
    """F3 (v4 review): a refusal row that already carries a verdict (the harvest marks known patterns) or a judgement
    (a row written by hand) needs no judging."""
    try:
        r = json.loads(line)
    except ValueError:
        return False
    return isinstance(r, dict) and bool(r.get("verdict") or r.get("judgement"))


def watch_guard(dry):
    """The guard's refusals: every new, unjudged line of log/guard-refusals.jsonl becomes one inbox item. The first
    pass only notes where the file ends; a file shorter than the offset (rewritten or reset) is re-baselined to its
    end, with no items. The harvest that appends to the file runs apart (guard_harvest), after the pass's decisions."""
    off_f, gl = D / "guard-offset.txt", LOG / "guard-refusals.jsonl"
    if not gl.exists():
        return []
    lines = gl.read_text().splitlines()
    try:
        off = int(off_f.read_text())
    except (OSError, ValueError):
        if not dry:
            off_f.write_text(str(len(lines)))
        return []
    if len(lines) < off:  # F3: shrunk: never replay old rows as a flood
        if not dry:
            off_f.write_text(str(len(lines)))
            log(f"guard refusals: the file shrank from {off} to {len(lines)} lines; re-baselined, no items")
        return []
    new = [(off + i, line) for i, line in enumerate(lines[off:]) if line.strip() and not judged(line)]
    if dry:
        return [line for _, line in new]
    for n, line in new:
        inbox_item(f"guard-{n}", f"log: guard-refusals.jsonl line {n + 1}\nGuard: refusal\nstatus: a guard "
                                 f"refusal to judge (DEC-958)\n\n{line[:600]}\n")
    if len(lines) > off:  # F3: the offset is written only when the file grew
        off_f.write_text(str(len(lines)))
    if new:
        log(f"guard refusals: {len(new)} new")
    return [line for _, line in new]


def harvest():
    """The guard harvest itself (python3 dispatcher.py harvest): one at a time under dispatch/guard-harvest.lock, with
    the `guard_harvest_timeout_s` limit (300); its result goes to dispatch/guard-harvest.json."""
    D.mkdir(parents=True, exist_ok=True)
    lock = open(D / "guard-harvest.lock", "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log("guard harvest: another harvest is running; nothing done")
        return 0
    try:
        limit = int(config().get("guard_harvest_timeout_s", 300))
    except Exception:
        limit = 300
    cmd = shlex.split(E("DISPATCH_GUARD_CMD", f"python3 {ORCH}/tools/guard_refusals.py --quiet"))
    t0 = time.time()
    try:
        r = sh(cmd, limit=limit)
    except OSError as exc:
        r = R(127, "", repr(exc))
    rec = {"at": stamp(), "rc": r.returncode, "secs": round(time.time() - t0, 1), "limit_s": limit,
           "tail": (r.stderr or r.stdout).strip()[-300:]}
    (D / "guard-harvest.json").write_text(json.dumps(rec) + "\n")
    log(f"guard harvest: rc {r.returncode} in {rec['secs']} s")
    return r.returncode


def guard_harvest(dry, c):
    """F2 (v4 review): the harvest out of the pass's critical path. When due (every `guard_harvest_s`, 600) and no
    harvest runs, it starts detached (its own session); DISPATCH_GUARD_SYNC=1 runs it in the pass (the tests)."""
    if dry:
        return "dry: no harvest"
    last_f = D / "guard-harvested.txt"
    try:
        last = float(last_f.read_text())
    except (OSError, ValueError):
        last = 0.0
    if now() - last < c.get("guard_harvest_s", 600):
        return "not due"
    if lock_held(D / "guard-harvest.lock"):
        return "a harvest is still running"
    last_f.write_text(str(now()))
    if E("DISPATCH_GUARD_SYNC") == "1":
        harvest()
        return "ran in the pass"
    subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "harvest"], start_new_session=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "started detached"


def harvest_result():
    """The last harvest's record, and its failure line (a non-zero exit or a timeout) or None."""
    try:
        rec = json.loads((D / "guard-harvest.json").read_text())
    except (OSError, ValueError):
        return None, None
    if not isinstance(rec, dict):
        return None, "guard harvest: its record is unreadable"
    rc = rec.get("rc")
    if rc == 0:
        return rec, None
    why = "timed out" if rc == 124 else f"exit {rc}"
    return rec, f"guard harvest: {why} at {rec.get('at')}: {str(rec.get('tail', ''))[-120:]}"


def watch_nightly(dry):
    """The nightly's end: log/nightly/status.txt gains a line for today: one inbox item, once."""
    st = LOG / "nightly" / "status.txt"
    if not st.exists():
        return []
    today = datetime.fromtimestamp(now()).strftime("%Y-%m-%d")
    seen = seen_set("nightly-seen.txt")
    new = [l for l in st.read_text().splitlines() if l.startswith(today) and l not in seen]
    if dry or not new:
        return new
    for l in new:
        inbox_item(f"nightly-{hashlib.sha1(l.encode()).hexdigest()[:8]}",
                   f"log: nightly/status.txt\nNightly: {today}\nstatus: {l[:300]}\n")
    mark_seen("nightly-seen.txt", new)
    log(f"nightly: {len(new)} new status line(s) for {today}")
    return new


def sentinel_silent():
    """(2) The watcher watched: while dispatch/sentinel-expected exists, the sentinel's watch writes log/deadman.log
    each pass; its newest line older than 2 hours (or none) is a silence."""
    if not (D / "sentinel-expected").exists():
        return None
    dl = LOG / "deadman.log"
    try:
        with open(dl, "rb") as f:  # the tail only: the log grows each pass
            f.seek(max(0, os.path.getsize(dl) - 65536))
            tail = [l for l in f.read().decode("utf-8", "replace").splitlines() if l.strip()]
    except OSError:
        tail = []
    if not tail:
        return "the sentinel's watch has written nothing to log/deadman.log"
    last = age = None
    for line in reversed(tail):  # F4 (v4 review): a malformed line falls back to the newest parseable one
        try:
            at = json.loads(line)["at"]
            age = now() - datetime.strptime(at, "%Y-%m-%d %H:%M:%S").timestamp()
            last = at
            break
        except (ValueError, KeyError, TypeError, IndexError):
            continue
    if last is None:
        return "the sentinel's watch log is unreadable (no parseable line in log/deadman.log)"
    if age > 7200:
        return f"the sentinel's watch is silent since {last} ({int(age // 60)} min)"
    return None


# ---- 5b. the embedding server's health (DEC-1015 item 2) ----------------------------------------------------------------

def load_json(name, default):
    try:
        v = json.loads((D / name).read_text())
        return v if isinstance(v, type(default)) else default
    except (OSError, ValueError):
        return default


def embed_probe(c):
    """One test request: ("ok" | "timeout" | "fail" | "down", seconds, why). "down": nothing listens (refused)."""
    url = E("DISPATCH_EMBED_URL") or c.get("embed_url") or EMBED_URL
    body = json.dumps({"model": c.get("embed_model", "qwen3-embedding:0.6b"), "input": "dispatcher health check"}).encode()  # no keep_alive: the server's own setting stays
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never through a proxy
    t0 = time.time()
    try:
        with opener.open(req, timeout=float(c.get("embed_timeout_s", 30))) as r:
            data = json.loads(r.read() or b"{}")
        secs = round(time.time() - t0, 2)
        if isinstance(data, dict) and data.get("embeddings"):
            return "ok", secs, ""
        return "fail", secs, "an answer with no embeddings"
    except urllib.error.URLError as exc:
        secs = round(time.time() - t0, 2)
        if isinstance(exc.reason, ConnectionRefusedError):
            return "down", secs, "connection refused"
        if isinstance(exc.reason, TimeoutError):
            return "timeout", secs, f"no answer in {c.get('embed_timeout_s', 30)} s"
        return "fail", secs, str(exc)[:200]
    except TimeoutError:
        return "timeout", round(time.time() - t0, 2), f"no answer in {c.get('embed_timeout_s', 30)} s"
    except (OSError, ValueError, http.client.HTTPException) as exc:
        return "fail", round(time.time() - t0, 2), repr(exc)[:200]


def ss_connections(c, ports):
    """DEC-1032: {port: {listening, waiting, oldest_s}} from one `ss -Htnia` call (limit 10 s), or None when it is
    unreadable. A request waits on a client socket (ESTAB, its peer the server's port) that has sent and has had no
    answer since: no byte received, or its last send newer than its last receive; an idle keep-alive connection (its
    answer received after its last send) does not wait. oldest_s: the time since the oldest waiting request was sent."""
    exe = E("DISPATCH_SS") or c.get("embed_ss") or "ss"
    filt = "( " + " or ".join(f"sport = :{p} or dport = :{p}" for p in ports) + " )"
    try:
        r = sh([exe, "-Htnia", filt], limit=10)
    except OSError:
        return None
    if r.returncode:
        return None
    out = {p: {"listening": False, "waiting": 0, "oldest_s": 0.0} for p in ports}
    port_of = lambda addr: int(addr.rsplit(":", 1)[1]) if addr.rsplit(":", 1)[-1].isdigit() else None
    client = None
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        if line[0] in " \t":  # the socket's details (-i), after its line
            if client is None:
                continue
            info = dict(re.findall(r"\b(\w+):(\d+(?:\.\d+)?)", line))
            sent = float(info.get("bytes_sent", 0)) > 0  # F3: -i always prints lastsnd; a request sends bytes
            snd, rcv = float(info.get("lastsnd", 0)), float(info.get("lastrcv", float("inf")))
            if sent and (float(info.get("bytes_received", 0)) == 0 or snd < rcv):
                out[client]["waiting"] += 1
                out[client]["oldest_s"] = max(out[client]["oldest_s"], round(snd / 1000, 1))
            client = None
            continue
        f = line.split()
        client = None
        if len(f) < 5:
            continue
        local, peer = port_of(f[3]), port_of(f[4])
        if f[0] == "LISTEN" and local in out:
            out[local]["listening"] = True
        elif f[0] == "ESTAB" and peer in out:
            client = peer
    return out


def judge_progress(name, path, port, sv, conns, c):
    """DEC-1032: one server judged by its runner's progress. The log read on from its saved offset (the first read
    starts at its end): tasks done (`release: ... stop processing`) and requests done (`[GIN] ... POST /api/embed`)
    since the last pass, a minute's rate of each; the requests waiting on its port (ss). Progress is a task done or a
    2xx request (F2). BUSY while there is progress; IDLE when nothing waits; WAITING when requests wait and none has
    waited `embed_stall_s` without progress; HUNG only when requests have waited `embed_stall_s` (180) with no
    progress during that wait: the stall clock starts when the wait starts (the oldest waiting request's send, or the
    first pass that saw a request waiting), or at the last progress if later, never earlier (F1: a first request after
    an idle spell is not HUNG); FAILING when `embed_fail_after` (3) requests in a row have failed (4xx/5xx) with no 2xx
    since (F2); NOT RUNNING when nothing has listened on its port for `embed_hung_after` (3) passes. An unreadable
    log, or unreadable connections with no progress for `embed_stall_s`, leaves it not judged (sv["judged"] False:
    the shared server then falls back to the test request). Returns the state."""
    t = now()
    lines, off, first = gpu_log_new(name, path, sv.get("off"), c, False, baseline_mb=0)
    if off is None:
        sv.update(judged=False, why="its log is unreadable")
        return sv.get("state")
    sv["off"] = off
    tasks, ok, failed, client, last_code = 0, 0, 0, 0, None
    run = int(sv.get("fails_in_a_row") or 0)
    for l in lines:
        if TASK_DONE.search(l):
            tasks += 1
            continue
        if TASK_FAILED.search(l):  # G1: a runner task's failure is the server's
            failed, run, last_code = failed + 1, run + 1, "a runner task error"
            continue
        m = REQ_DONE.search(l)
        if m:
            code = int(m.group(1))
            if 200 <= code < 300:
                ok, run = ok + 1, 0
            elif code >= 500:
                failed, run, last_code = failed + 1, run + 1, code
            elif code >= 400:
                client += 1  # G1: the client's (a bad input, a wrong model, gave up): not progress, not a failure
    if failed:
        sv["last_fail_at"] = t
    if run and not failed and t - float(sv.get("last_fail_at") or t) >= float(c.get("embed_fail_clear_s", 300)):
        log(f"embedding server {name}: {run} failed requests in a row, then none for "
            f"{int(t - sv['last_fail_at'])} s: the run ends")
        run = 0  # G1: a failure run decays after embed_fail_clear_s with no new failure
    if run and not sv.get("fails_in_a_row"):
        sv["fail_run_since"] = t
    sv["fails_in_a_row"], sv["last_fail_code"] = run, last_code or (sv.get("last_fail_code") if run else None)
    sv["client_errors"] = client
    prev = sv.get("read_at")
    if first or not prev or not 0 < t - prev <= 600:
        sv["tasks_per_min"] = sv["requests_per_min"] = sv["failed_per_min"] = None
    else:
        k = 60 / (t - prev)
        sv["tasks_per_min"], sv["requests_per_min"], sv["failed_per_min"] = round(tasks * k), round(ok * k), \
            round(failed * k)
    sv["read_at"] = t
    progress = tasks or ok
    if first or not sv.get("last_progress_at") or progress:
        sv["last_progress_at"] = t  # the first read: a stall is measured from here at the earliest (a restart)
    stall = float(c.get("embed_stall_s", 180))
    conn = conns.get(port) if conns is not None else None
    if conn and conn["waiting"]:  # F1: when this wait began: kept while requests go on waiting
        sv["wait_since"] = sv.get("wait_since") or t - float(conn["oldest_s"] or 0)
    elif conn:
        sv["wait_since"] = None
    stalled_from = max(sv["last_progress_at"], sv.get("wait_since") or t)
    quiet = t - sv["last_progress_at"]
    sv.update(judged=True, why="", quiet_s=round(quiet), waiting=conn["waiting"] if conn else None,
              oldest_wait_s=conn["oldest_s"] if conn else None, listening=conn["listening"] if conn else None,
              stalled_s=round(t - stalled_from) if conn and conn["waiting"] else 0)
    sv["down_passes"] = sv.get("down_passes", 0) + 1 if conn and not conn["listening"] else 0
    if conn and sv["down_passes"] >= int(c.get("embed_hung_after", 3)):
        state = "NOT RUNNING"
    elif conn and not conn["listening"]:
        state = "NOT LISTENING"  # under embed_hung_after passes: a restart, most likely
    elif run >= int(c.get("embed_fail_after", 3)):
        state = "FAILING"
    elif progress:
        state = "BUSY"
    elif conn is None:
        if quiet >= stall:  # cannot tell waiting from idle: not judged
            sv.update(judged=False, why=f"its connections are unreadable and no progress for {int(quiet)} s")
        state = "IDLE"
    elif conn["waiting"]:
        state = "HUNG" if t - stalled_from >= stall else "WAITING"
    else:
        state = "IDLE"
    label = "the embedding server" if name == "shared" else f"the {name} embedding server"
    if state in SERVER_DOWN and not sv.get("hung_since"):
        sv["hung_since"] = {"HUNG": stalled_from, "FAILING": sv.get("fail_run_since") or t}.get(state, t)
        detail = {"HUNG": f"{conn['waiting'] if conn else '?'} request(s) waiting on port {port} (the oldest sent "
                          f"{conn['oldest_s'] if conn else '?'} s ago) and no task completed for "
                          f"{int(t - stalled_from)} s of that wait in its log (nor a successful request)",
                  "FAILING": f"{run} requests in a row failed on /api/embed (the last with status "
                             f"{sv.get('last_fail_code')}) and none succeeded since"}.get(
            state, f"nothing listens on port {port} ({sv['down_passes']} passes)")
        inbox_item("server-" + ("" if name == "shared" else name + "-") + state.lower().replace(" ", "-"),
                   f"log: {os.path.basename(path)}\nServer: {label}\nstatus: {state} since {stamp(sv['hung_since'])}: "
                   f"{detail}; " + ("starts are held; rebuilds and heavy steps that need it wait\n" if name == "shared"
                                    else "starts are not held (the shared server decides)\n"))
        log(f"embedding server {name}: {state} since {stamp(sv['hung_since'])} ({detail})")
    elif sv.get("hung_since") and ((state in ("BUSY", "IDLE") and sv.get("judged"))
                                   or (sv.get("state") == "FAILING" and state not in SERVER_DOWN)):
        # a stall clears on progress or idleness; a failure run (G1) clears when it ends: a 2xx, or no new failure
        # for embed_fail_clear_s
        log(f"embedding server {name}: {state} again after {sv.get('state')} since {stamp(sv['hung_since'])}")
        sv["hung_since"] = None
    elif sv.get("hung_since"):
        state = sv.get("state") or state  # the incident holds until it progresses or idles
    sv["state"] = state
    return state


def watch_embedding(dry, c):
    """DEC-1032: each embedding server (`gpu_logs`, on its `embed_ports` port) judged by its runner's progress
    (judge_progress), every pass; the shared server's state is the one that holds starts. When the shared server
    cannot be judged by progress (its log unreadable), the fallback is DEC-1015's test request, at most every
    `embed_check_every` passes (5; limit `embed_timeout_s`): `embed_hung_after` failures or timeouts in a row make it
    HUNG. Either way one Server: item and a stable inbox-stale line, once per incident; both clear when it progresses
    (or answers). A restart only with `embed_restart_cmd` configured, HUNG for `embed_restart_after_s`, no progress or
    answer within that window, and no restart in the last `embed_restart_min_gap_s` (1800)."""
    if dry:
        return None
    st = load_json("embed-health.json", {})
    st["passes"] = st.get("passes", 0) + 1
    servers = st.setdefault("servers", {})
    ports = {k: int(v) for k, v in dict(EMBED_PORTS, **(c.get("embed_ports") or {})).items()}
    logs = {k: v for k, v in gpu_logs(c).items() if k in ports}
    conns = ss_connections(c, sorted({ports[k] for k in logs})) if logs else None
    for name, path in logs.items():
        try:
            judge_progress(name, path, ports[name], servers.setdefault(name, {}), conns, c)
        except Exception as exc:  # noqa: BLE001 - one server's error never stops the other's judgement
            servers.setdefault(name, {}).update(judged=False, why=f"error: {exc!r}"[:160])
            log(f"embedding server {name}: progress check failed: {exc!r}")
    shared = servers.get("shared") or {}
    if shared.get("judged"):
        if st.get("how") == "probe" and st.get("hung_since") and shared["state"] not in SERVER_DOWN:
            log(f"embedding server: {shared['state']} by its progress after {st.get('state')} by the test request")
        every = max(1, int(c.get("embed_check_every", 5)))
        last = st.get("last_probe_pass")
        if shared["state"] == "FAILING" and (last is None or not 0 <= st["passes"] - last < every):
            # G1: while FAILING, the test request (at most every embed_check_every passes) can clear it
            st["last_probe_pass"] = st["passes"]
            res, secs, why = embed_probe(c)
            st.update(last_check_at=now(), last_result=res, last_secs=secs, last_why=why)
            if res == "ok":
                log(f"embedding server shared: the test request answered in {secs} s: FAILING since "
                    f"{stamp(shared['hung_since'])} cleared")
                shared.update(fails_in_a_row=0, hung_since=None, state="IDLE", last_fail_at=None)
        st.update(how="progress", state=shared["state"], hung_since=shared.get("hung_since"),
                  last_ok_at=shared.get("last_progress_at"))
        if st["state"] in SERVER_DOWN:
            restart_if_due(st, c)
        (D / "embed-health.json").write_text(json.dumps(st))
        return st
    if st.get("how") == "progress":  # back to the test request: its own count starts afresh
        st.update(fails=0, first_fail_at=None, hung_since=None)
    st["how"] = "probe"
    every = max(1, int(c.get("embed_check_every", 5)))
    last = st.get("last_probe_pass")
    if last is not None and 0 <= st["passes"] - last < every:
        (D / "embed-health.json").write_text(json.dumps(st))
        return st
    st["last_probe_pass"] = st["passes"]
    res, secs, why = embed_probe(c)
    st.update(last_check_at=now(), last_result=res, last_secs=secs, last_why=why)
    if res == "ok":
        if st.get("hung_since"):
            log(f"embedding server: answering again after {st.get('state')} since {stamp(st['hung_since'])}")
        st.update(fails=0, first_fail_at=None, hung_since=None, last_ok_at=now(), state="healthy")
    else:  # a failure, a timeout or a refusal: `embed_hung_after` in a row is an incident (hung_since: its start)
        st["fails"] = st.get("fails", 0) + 1
        st["first_fail_at"] = st.get("first_fail_at") or now()
        bad = "NOT RUNNING" if res == "down" else "HUNG"
        if st["fails"] >= int(c.get("embed_hung_after", 3)) and not st.get("hung_since"):
            st["hung_since"] = st["first_fail_at"]
            inbox_item("server-" + bad.lower().replace(" ", "-"),
                       f"log: dispatch.log\nServer: the embedding server\nstatus: {bad} since "
                       f"{stamp(st['hung_since'])}: {st['fails']} failed test requests in a row ({why}); "
                       "starts are held; rebuilds and heavy steps that need it wait\n")
            log(f"embedding server: {bad} since {stamp(st['hung_since'])} ({why})")
        st["state"] = bad if st.get("hung_since") else "failing"
        restart_if_due(st, c)
    (D / "embed-health.json").write_text(json.dumps(st))
    return st


def restart_if_due(st, c):
    cmd = c.get("embed_restart_cmd")
    if not cmd or not st.get("hung_since"):
        return
    after = float(c.get("embed_restart_after_s", 900))
    if now() - st["hung_since"] < after or (st.get("last_ok_at") or 0) >= now() - after:
        return  # never while it answered within the window
    if now() - (st.get("last_restart_at") or 0) < float(c.get("embed_restart_min_gap_s", 1800)):
        return
    argv = shlex.split(cmd) if isinstance(cmd, str) else [str(x) for x in cmd]
    try:
        r = sh(argv)
    except OSError as exc:
        r = R(127, "", repr(exc))
    st["last_restart_at"] = now()
    st["restarts"] = st.get("restarts", 0) + 1
    tail = (r.stderr or r.stdout).strip()[-200:]
    log(f"embedding server: restarted ({' '.join(argv)[:120]}): rc {r.returncode} {tail}")
    inbox_item("server-restart", f"log: dispatch.log\nServer: the embedding server\nstatus: restarted after "
                                 f"{st.get('state')} since {stamp(st['hung_since'])}: rc {r.returncode}\n\n{tail}\n")


def probe_line(st):
    if not st or "last_result" not in st:
        return "not checked yet"
    if st.get("state") == "healthy":
        return f"healthy ({st.get('last_secs')} s)"
    if st.get("state") in ("HUNG", "NOT RUNNING"):
        return (f"{st['state']} since {stamp(st['hung_since'])} ({st.get('fails')} failed checks; "
                f"{st.get('last_why')}); starts held")
    return f"failing ({st.get('fails')} in a row; {st.get('last_why')})"


def server_line(name, sv, short=False):
    """`shared BUSY 3120 tasks/min (2 waiting, the oldest 1.2 s)`, `query HUNG since ...`, `query not judged (...)`."""
    if not sv:
        return f"{name} not checked yet"
    if not sv.get("judged") and not sv.get("hung_since"):
        return f"{name} not judged ({sv.get('why') or 'no reading yet'})"
    st = sv.get("state") or "?"
    if st in SERVER_DOWN and sv.get("hung_since"):
        return (f"{name} {st} since {stamp(sv['hung_since'])}" + ("" if short else
                (f" ({sv.get('fails_in_a_row')} failed requests in a row, the last {sv.get('last_fail_code')})"
                 if st == "FAILING" else f" ({sv.get('waiting')} waiting, {sv.get('stalled_s')} s with no progress)")
                + ("; starts held" if name == "shared" else "")))
    rate = sv.get("tasks_per_min")
    line = f"{name} {st} {'?' if rate is None else rate} tasks/min"
    if sv.get("waiting") and not short:
        line += f" ({sv['waiting']} waiting, the oldest {sv.get('oldest_wait_s')} s)"
    return line


def embed_line(st, short=False):
    """The shared server first (by progress, or the test request's line), then the others by progress."""
    servers = (st or {}).get("servers") or {}
    if not st or ("last_result" not in st and not servers):
        return "not checked yet"
    if st.get("how") == "progress":
        parts = [server_line("shared", servers.get("shared"), short)]
    else:
        parts = [("shared by the test request: " if short else "") + probe_line(st)]
    parts += [server_line(n, sv, short) for n, sv in servers.items() if n != "shared"]
    return "; ".join(parts)


SERVER_DOWN = ("HUNG", "NOT RUNNING", "FAILING")  # FAILING: by progress only (F2); the test request's is "failing"


# ---- 5d. the GPU, its holders and each embedding model's layers (DEC-1030) ---------------------------------------------

GPU_SMI = "/usr/lib/wsl/lib/nvidia-smi"
GPU_LOGS = {"shared": "/home/usain/.ollama/serve-11434.log", "query": "/home/usain/.ollama/serve-11435.log"}
GPU_EXPECTED = {"shared": True, "query": False}  # the query server is CPU-only by design (DEC-798)
GPU_ERROR = re.compile(r"CUDA error|out of memory|cudaMalloc failed", re.I)
GPU_LOAD = re.compile(r"load_tensors: offloaded (\d+)/(\d+) layers to GPU")
GPU_KINDS = ("embedder shared", "embedder query", "embedder other", "reranker", "other")
SHARED_HOSTS = ("", "127.0.0.1:11434", "localhost:11434", "0.0.0.0:11434", ":11434")
RERANK_GPU_GLOB = "/tmp/gov-os-rerank-gpu-*.lock"  # gov_reranker_gpu_slot.py's lock files (ACT-RERANK-GPU-SLOTS-1)
EMBED_PORTS = {"shared": 11434, "query": 11435}
# DEC-1032: the runner's per-input task done (llama-server `slot release: ... stop processing`), and a request done
# (Ollama's `[GIN] <time> | <status> | ... | POST "/api/embed"` line). Progress is a task done or a 2xx request (review
# of v4.6, F2). A server failure is a 5xx request or a runner task's failure (llama.cpp's `send_error: task id = N,
# error: ...`; none in the shared log since 2026-11-01 21:51); a 4xx (400 a bad input, 404 a wrong model, 499 the
# client gave up) is the client's: neither progress nor a failure (round 2, G1)
TASK_DONE = re.compile(r"\brelease: +id +\d+ \| task -?\d+ \| stop processing")
TASK_FAILED = re.compile(r"\bsend_error: +task id = -?\d+, error:")
REQ_DONE = re.compile(r"^\[GIN\] [^|]*\|\s*(\d{3})\s*\|.*\|\s*POST\s+\"/api/embed\"")


def gpu_logs(c):
    """{server: log path}: the defaults, `gpu_logs` in config.json, then DISPATCH_GPU_LOG_<SERVER> (the tests)."""
    logs = dict(GPU_LOGS, **(c.get("gpu_logs") or {}))
    return {k: E(f"DISPATCH_GPU_LOG_{k.upper()}") or v for k, v in logs.items()}


def gpu_smi(c, query):
    """One nvidia-smi query (limit `gpu_smi_timeout_s`): (lines, None) or (None, why)."""
    exe = E("DISPATCH_NVIDIA_SMI") or c.get("gpu_smi") or GPU_SMI
    try:
        r = sh([exe, query, "--format=csv,noheader" + (",nounits" if "query-gpu" in query else "")],
               limit=float(c.get("gpu_smi_timeout_s", 10)))
    except OSError as exc:
        return None, f"{os.path.basename(exe)}: {exc.strerror or exc!r}"[:160]
    if r.returncode:
        return None, f"nvidia-smi exit {r.returncode}: {(r.stderr or r.stdout).strip()[:120]}"
    return [l.strip() for l in r.stdout.splitlines() if l.strip()], None


def mib(text):
    """'1234 MiB', '1234' -> 1234; '[N/A]', 'N/A' (WSL) -> None."""
    m = re.match(r"\s*(\d+(?:\.\d+)?)", text or "")
    return int(float(m.group(1))) if m else None


def proc_read(pid):
    """{argv, ppid, env: OLLAMA_HOST only} of a pid from PROC (a planted one in the tests), or None."""
    d = PROC / str(pid)
    try:
        argv = [a.decode("utf-8", "replace") for a in (d / "cmdline").read_bytes().split(b"\0") if a]
        text = (d / "stat").read_text()
        ppid = int(text[text.rindex(")") + 2:].split()[1])
    except (OSError, ValueError, IndexError):
        return None
    env = {}
    try:
        for kv in (d / "environ").read_bytes().split(b"\0"):
            if kv.startswith(b"OLLAMA_HOST="):  # only this variable is kept: the environment may hold secrets
                env["OLLAMA_HOST"] = kv.split(b"=", 1)[1].decode("utf-8", "replace")
    except OSError:
        pass
    return {"argv": argv, "ppid": ppid, "env": env}


def gpu_holder_kind(pid):
    """A GPU holder's kind by its command line and parents: an ollama server or llama-server is the shared embedder
    when its `ollama serve` has no OLLAMA_HOST or 127.0.0.1:11434, the query embedder with 127.0.0.1:11435, another
    embedder otherwise (a private test server); a process whose command line holds `rerank` is a reranker."""
    info = proc_read(pid)
    if not info or not info["argv"]:
        return "other"  # not in this process table (on WSL nvidia-smi may list a pid of the host)
    base = os.path.basename(info["argv"][0])
    if base.startswith(("llama-server", "ollama")):
        cur, seen = info, set()
        while cur and len(seen) < 16:
            a = cur["argv"]
            if a and os.path.basename(a[0]).startswith("ollama") and "serve" in a[1:3]:
                host = re.sub(r"^https?://", "", cur["env"].get("OLLAMA_HOST", "")).rstrip("/")
                if host in SHARED_HOSTS:
                    return "embedder shared"
                return "embedder query" if host in ("127.0.0.1:11435", "localhost:11435") else "embedder other"
            seen.add(cur["ppid"])
            cur = proc_read(cur["ppid"]) if cur["ppid"] > 1 else None
        return "embedder other"
    if "rerank" in " ".join(info["argv"]).lower():  # gov.retrieval.rerank_worker, by -m or by its path
        return "reranker"
    return "other"


def gpu_read(c):
    """The GPU's state: name, memory used/total (MiB), utilisation, and its holders [{pid, name, mib, kind}]. A
    missing or failing nvidia-smi is {"ok": False, "why": ...}, never an exception. Two queries, the second only
    when the first answered (nvidia-smi takes one --query-* switch per call)."""
    lines, why = gpu_smi(c, "--query-gpu=name,memory.used,memory.total,utilization.gpu")
    if not lines:
        return {"ok": False, "why": why or "nvidia-smi: an empty answer", "at": now()}
    f = [x.strip() for x in lines[0].split(",")]
    if len(f) < 4:
        return {"ok": False, "why": f"nvidia-smi: unreadable line {lines[0][:80]!r}", "at": now()}
    g = {"ok": True, "at": now(), "name": f[0], "used_mib": mib(f[1]), "total_mib": mib(f[2]), "util": mib(f[3]),
         "holders": []}
    apps, why = gpu_smi(c, "--query-compute-apps=pid,process_name,used_memory")
    if apps is None:
        g["holders_why"] = why
        return g
    for line in apps:
        p = [x.strip() for x in line.split(",")]
        if not p[0].isdigit():
            continue
        pid = int(p[0])  # kept though its memory reads [N/A] (WSL)
        g["holders"].append({"pid": pid, "name": p[1] if len(p) > 1 else "?",
                             "mib": mib(p[2]) if len(p) > 2 else None, "kind": gpu_holder_kind(pid)})
    return g


def gpu_log_new(name, path, off, c, dry, baseline_mb=None):
    """The complete lines a server's log gained since its saved offset {path, off, ino}: (lines, new offset, first).
    The first read (or a new path) takes only the last `gpu_log_baseline_mb` (32; `baseline_mb` when given: 0 for the
    progress watch) to learn the current layers; an offset past the end, or a new inode, is a truncated or rotated
    log: from 0; at most `gpu_log_read_max_mb` (64) a pass (the rest skipped). A partial last line waits for the next
    pass. A missing log: ([], None, False)."""
    try:
        st = os.stat(path)
    except OSError:
        return [], None, False
    size, first = st.st_size, not off or off.get("path") != path
    if first:
        base = c.get("gpu_log_baseline_mb", 32) if baseline_mb is None else baseline_mb
        start = max(0, size - int(float(base) * 2 ** 20))
    elif off.get("off", 0) > size or off.get("ino") != st.st_ino:
        if not dry:
            log(f"gpu watch: the {name} log was truncated or rotated (offset {off.get('off')}, size {size}): from 0")
        start = 0
    else:
        start = off["off"]
    cap = int(float(c.get("gpu_log_read_max_mb", 64)) * 2 ** 20)
    capped = size - start > cap
    if capped:
        start = size - cap
    with open(path, "rb") as fh:
        fh.seek(start)
        data = fh.read(size - start)
    end = data.rfind(b"\n") + 1
    lines = data[:end].decode("utf-8", "replace").splitlines()
    if start and (first or capped) and lines:  # began mid-line
        lines = lines[1:]
    return lines, {"path": path, "off": start + end, "ino": st.st_ino}, first


def gpu_line(g):
    """`RTX 5070 Ti 3.5/15.9 GB, 5 %; holders: embedder shared (1), reranker (0)` or `unreadable (why)`."""
    if not g:
        return "not checked yet"
    if not g.get("ok"):
        return f"unreadable ({g.get('why')})"
    name = re.sub(r"^(NVIDIA )?(GeForce )?", "", g.get("name") or "?")
    gb = lambda m: "?" if m is None else f"{m / 1024:.1f}"
    counts = {k: 0 for k in GPU_KINDS}
    for h in g.get("holders", []):
        counts[h.get("kind", "other")] = counts.get(h.get("kind", "other"), 0) + 1
    shown = ", ".join(f"{k} ({n})" for k, n in counts.items() if n or k in ("embedder shared", "reranker"))
    hold = f"holders unreadable ({g['holders_why']})" if g.get("holders_why") else f"holders: {shown}"
    return f"{name} {gb(g.get('used_mib'))}/{gb(g.get('total_mib'))} GB, {g.get('util')} %; {hold}"


def layers_line(st, c):
    expected = dict(GPU_EXPECTED, **(c.get("gpu_expected") or {}))
    out = []
    for name in gpu_logs(c):
        lay = (st.get("layers") or {}).get(name)
        if not expected.get(name, True) and (not lay or lay["x"] == 0):
            out.append(f"{name} cpu-only by design")
        elif lay:
            out.append(f"{name} {lay['x']}/{lay['y']}" + ("" if expected.get(name, True) else " (expected cpu-only)"))
        else:
            out.append(f"{name} ?")
    return "layers: " + ", ".join(out)


def gpu_status_line(st, c):
    line = f"GPU: {gpu_line(st.get('gpu'))}; {layers_line(st, c)}"
    recent = [a for a in st.get("alerts", []) if now() - a.get("at", 0) < 86400]
    if recent:
        line += f"; last alert {stamp(recent[-1]['at'])}: {recent[-1]['what']}"
    return line


def watch_gpu(dry, c):
    """Each `gpu_check_every` passes (1): the GPU's state (nvidia-smi) and holders; each server's log read on from its
    saved offset (gpu-health.json), the latest `load_tensors: offloaded X/Y` kept per server. A new `CUDA error`
    (`out of memory`, `cudaMalloc failed`) line, or a load with 0 layers on a server that expects the GPU
    (`gpu_expected`), writes one gpu-alert item at once, with the lines, the GPU's state and its holders; once per
    incident: errors more than `gpu_alert_gap_s` (0: every pass that finds new error lines alerts, DEC-1030) after the
    last are a new incident; a 0-layer incident lasts
    until a load with layers on the GPU. A dry pass reads nothing."""
    if dry:
        return None
    st = load_json("gpu-health.json", {})
    recovering = not st and (D / "gpu-health.json").exists()  # present but unreadable (review F2)
    if recovering:
        log("gpu watch: gpu-health.json unreadable: the recent logs are re-read with their errors counted")
    st["passes"] = st.get("passes", 0) + 1
    every = max(1, int(c.get("gpu_check_every", 1)))
    if (st["passes"] - 1) % every:
        gpu_save(st)
        return st
    try:
        g = st["gpu"] = gpu_read(c)
    except Exception as exc:  # noqa: BLE001 - the logs are read whatever the GPU read did (review F1)
        g = st["gpu"] = {"ok": False, "why": f"the GPU read failed: {exc.__class__.__name__}", "at": now()}
    expected = dict(GPU_EXPECTED, **(c.get("gpu_expected") or {}))
    offs, layers = st.setdefault("offsets", {}), st.setdefault("layers", {})
    # zero_since: since when a server that expects the GPU has had a short load (0 layers, or only part: DEC-1032)
    err_last, zero_since = st.setdefault("error_last_at", {}), st.setdefault("zero_since", {})
    gap = float(c.get("gpu_alert_gap_s", 0))
    reasons, evidence, what = [], [], []
    for name, path in gpu_logs(c).items():
        lines, off, first = gpu_log_new(name, path, offs.get(name), c, dry)
        if off:
            offs[name] = off
        zero_load = False
        for line in lines:
            m = GPU_LOAD.search(line)
            if m:
                x, y = int(m.group(1)), int(m.group(2))
                layers[name] = {"x": x, "y": y, "at": now()}
                if x < y and not first:
                    zero_load = True
                    evidence.append(f"{name}: {line.strip()[:300]}")
                elif x >= y and expected.get(name, True) and zero_since.get(name) and not first:
                    zero_since.pop(name)  # a full load ends the incident, though a short one follows in this pass
                    log(f"gpu watch: the {name} server has all {x}/{y} layers on the GPU again")
        errors = [] if first and not recovering else [l for l in lines if GPU_ERROR.search(l)]
        if errors:
            if now() - err_last.get(name, float("-inf")) >= gap:
                reasons.append(f"{len(errors)} new CUDA error line(s) in the {name} server's log")
                what.append(f"CUDA error ({name})")
                evidence.extend(f"{name}: {l.strip()[:300]}" for l in errors[:20])
            else:
                log(f"gpu watch: {len(errors)} more CUDA error line(s) in the {name} log (same incident)")
            err_last[name] = now()
        lay = layers.get(name)
        if expected.get(name, True) and lay and lay["x"] < lay["y"]:
            if (zero_load or first) and not zero_since.get(name):
                if lay["x"] == 0:
                    reasons.append(f"the {name} server loaded its model with 0/{lay['y']} layers on the GPU (CPU "
                                   "only, 30-100x slower)")
                    what.append(f"0 layers ({name})")
                else:  # DEC-1032: a partial load runs the rest on the CPU, as slow as the slowest part
                    reasons.append(f"the {name} server loaded its model with only {lay['x']}/{lay['y']} layers on "
                                   "the GPU (the rest on the CPU: GPU memory short)")
                    what.append(f"partial {lay['x']}/{lay['y']} layers ({name})")
                if first:
                    evidence.append(f"{name}: load_tensors: offloaded {lay['x']}/{lay['y']} layers to GPU (the "
                                    "latest load)")
            zero_since[name] = zero_since.get(name) or now()
        elif lay and lay["x"] >= lay["y"] and zero_since.pop(name, None):
            log(f"gpu watch: the {name} server has all {lay['x']}/{lay['y']} layers on the GPU again")
        elif lay and not expected.get(name, True):
            zero_since.pop(name, None)  # expected on the CPU (configured since): no incident holds
    if reasons:
        state = gpu_line(g)
        holders = "\n".join(f"  pid {h['pid']} {h['kind']} ({h['name']}, "
                            f"{'?' if h['mib'] is None else str(h['mib']) + ' MiB'})" for h in g.get("holders", []))
        logs = ", ".join(os.path.basename(gpu_logs(c)[n]) for n in gpu_logs(c) if any(w.endswith(f"({n})")
                                                                                         for w in what))
        item = inbox_item("gpu-alert",
                          f"log: {logs}\nGPU: {'; '.join(what)}\nstatus: {'; '.join(reasons)}; the GPU now: {state}\n"
                          "\nlines:\n" + "\n".join(f"  {e}" for e in evidence[:40]) +
                          f"\n\nthe GPU at that moment: {state}\n{layers_line(st, c)}\nholders:\n"
                          + (holders or "  none listed") + "\n")
        st["alerts"] = (st.get("alerts", []) + [{"at": now(), "what": "; ".join(what), "item": item.name}])[-20:]
        st["stale"] = {"since": now(), "what": "; ".join(what), "item": item.name}
        log(f"gpu watch: ALERT {'; '.join(what)} -> inbox/{item.name}")
    gpu_save(st)
    return st


def gpu_save(st):
    """gpu-health.json written whole or not at all (a temporary file, then a rename; review F2)."""
    tmp = D / "gpu-health.json.tmp"
    tmp.write_text(json.dumps(st))
    os.replace(tmp, D / "gpu-health.json")


def gpu_stale_line(st):
    """The `gpu:` line of inbox-stale.txt while the last alert's item is unread or a 0-layer incident holds."""
    s = st.get("stale")
    if s and ((D / "inbox" / s.get("item", "")).is_file() or st.get("zero_since")):
        return f"gpu: the GPU {s['what']} since {stamp(s['since'])}"
    return None


# ---- 5c. the heavy-slot holders' progress (DEC-1015 item 2) ---------------------------------------------------------

def slot_name(path):
    m = re.search(r"slot-([\w]+)\.lock$", str(path))
    return m.group(1) if m else Path(path).name


def slot_holders():
    """{slot path: [holder pid]} from the lock table (a waiter, "->", is not a holder)."""
    return lock_holders(SLOT_GLOB)


def lock_holders(pattern):
    """{lock file: [holder pid]} for the files matching `pattern`, from the lock table (a waiter, "->", is not a
    holder); the heavy slots' and the rerankers' GPU slots' (DEC-1032). An unreadable table raises OSError."""
    locks = (PROC / "locks").read_text().splitlines()
    out = {}
    for p in sorted(glob.glob(pattern)):
        try:
            ino = str(os.stat(p).st_ino)
        except OSError:
            continue
        for line in locks:
            f = line.split()
            if "->" in f:
                continue
            dev = [i for i, x in enumerate(f) if x.count(":") == 2]
            if dev and f[dev[0]].rsplit(":", 1)[1] == ino and f[dev[0] - 1].isdigit():
                out.setdefault(p, []).append(int(f[dev[0] - 1]))
    return out


def proc_table():
    """{pid: (ppid, utime + stime in clock ticks, start time)}."""
    t = {}
    for d in PROC.glob("[0-9]*"):
        try:
            text = (d / "stat").read_text()
            rest = text[text.rindex(")") + 2:].split()
            t[int(d.name)] = (int(rest[1]), int(rest[11]) + int(rest[12]), rest[19])
        except (OSError, ValueError, IndexError):
            continue
    return t


def tree_cpu(table, pid):
    kids = {}
    for p, (pp, _, _) in table.items():
        kids.setdefault(pp, []).append(p)
    total, todo, seen = 0, [pid], set()
    while todo:
        p = todo.pop()
        if p in seen or p not in table:
            continue
        seen.add(p)
        total += table[p][1]
        todo.extend(kids.get(p, []))
    return total


def watch_slots(dry, c, embed):
    """Each heavy-slot holder's process tree's CPU time, against the last sample (slot-progress.json). Not grown for
    `slot_idle_s` (900): IDLE, one Slot: item naming the slot, the pid, the command, the tree and the idle time, once
    per holder; it clears when the CPU grows or the holder ends. A holder is never killed."""
    holders = slot_holders()
    prev = load_json("slot-progress.json", {})
    table = proc_table() if holders else {}
    limit = float(c.get("slot_idle_s", 900))
    cur = {}
    for path, pids in holders.items():
        for pid in pids:
            if pid not in table:
                continue
            key = f"{pid}:{table[pid][2]}"  # the start time: a reused pid is a new holder
            cpu, p = tree_cpu(table, pid), prev.get(key)
            grew = p is None or cpu > p.get("cpu", -1)
            try:
                cmd = (PROC / str(pid) / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
            except OSError:
                cmd = "?"
            try:
                cwd = os.readlink(PROC / str(pid) / "cwd")
            except OSError:
                cwd = "?"
            e = dict(slot=slot_name(path), pid=pid, cpu=cpu, since=now() if grew else p["since"],
                     reported=False if grew else p.get("reported", False), cmd=cmd.strip()[:200], cwd=cwd)
            idle = now() - e["since"]
            if idle >= limit and not e["reported"] and not dry:
                hung = embed and embed.get("state") == "HUNG"
                inbox_item(f"slot-{e['slot']}-idle-{pid}",
                           f"log: dispatch.log\nSlot: heavy slot {e['slot']}\nstatus: its holder is IDLE: no CPU "
                           f"time for {int(idle // 60)} min (since {stamp(e['since'])}); pid {pid}; command "
                           f"{e['cmd'][:160]}; tree {cwd}"
                           + (f"; likely waiting on the embedding server, HUNG since {stamp(embed['hung_since'])}"
                              if hung else "") + "; not killed: the CTO decides\n")
                log(f"slot {e['slot']}: holder {pid} idle {int(idle // 60)} min")
                e["reported"] = True
            cur[key] = e
    if not dry:
        (D / "slot-progress.json").write_text(json.dumps(cur))
    return cur


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
    srv = load_json("embed-health.json", {}).get("state")
    if srv in SERVER_DOWN:  # DEC-1015: the last known state (the check itself runs after the decisions)
        why = "embedding server hung: starts held (DEC-1015)"
        return None, {" ".join(e[:2]): why for e in read_list(D / "ready.txt")} or {"held": why}
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


def clock_today(text, default):
    """Today's local time HH:MM as a timestamp (a malformed value: the default)."""
    for v in (text, default):
        try:
            h, m = (int(x) for x in str(v).split(":"))
            return datetime.fromtimestamp(now()).replace(hour=h, minute=m, second=0, microsecond=0).timestamp()
        except (ValueError, TypeError):
            continue


NIGHTLY_HELD = "held for the nightly (DEC-1018) until it starts"


def nightly_hold(c):
    """DEC-1018 item 1: the nightly (cron 04:00) starts only after 5 quiet minutes in a clean main tree, and a landing
    run takes about 45 minutes; so from `nightly_hold_from` no new landing is claimed until the nightly has started
    (ORCH/NIGHTLY-RUNNING newer than today's hold start, or a line for today in log/nightly/status.txt), and never
    after `nightly_hold_until`. Returns the hold's reason, or None."""
    start = clock_today(c.get("nightly_hold_from"), "03:15")
    until = clock_today(c.get("nightly_hold_until"), "05:30")
    if not start <= now() < until:
        return None
    try:
        if (ORCH / "NIGHTLY-RUNNING").stat().st_mtime >= start:
            return None
    except OSError:
        pass
    today = datetime.fromtimestamp(now()).strftime("%Y-%m-%d")
    try:
        if any(l.startswith(today) for l in (LOG / "nightly" / "status.txt").read_text().splitlines()):
            return None
    except OSError:
        pass
    return NIGHTLY_HELD


def land_step(t, dry):
    if (D / "land-inflight.txt").exists():
        return finalise_land(t, dry)  # a landing in flight is never stopped by the nightly hold
    held = nightly_hold(t.get("_c") or {})
    if held:
        return held
    if not read_list(D / "land.txt"):
        return "nothing to land"
    if t["queue_busy"]:
        return "queue busy"
    # DEC-1014 item 1: a running close holds a landing only if it closes one of the landing's tickets, or while it
    # commits (its ticket or close-record files modified in the main tree: one pass); any other close does not
    want = {" ".join(e).split("=")[0] for e in read_list(D / "land.txt")}
    clash = sorted(want & set(t.get("closing_w2s", [])))
    if clash:
        return f"a close of {', '.join(clash)} is running (the same ticket): waits"
    committing = t["close_running"] and t.get("main_dirty") and all(
        p.startswith(".tickets/") or p.startswith("governance/project/orchestration/closes/") for p in t["main_dirty"])
    if committing:
        return "a close is committing its records: next pass"
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

def balance(t, emb, c):
    """DEC-1032: the machine's balance in one line and its record: the CPU against its band (`cpu_band`, 14-18 of 20),
    memory available against the floor, the GPU used/total and the budget's holders (the embedders by their layers,
    nvidia-smi's holders by kind; read this pass), the embedders' states, the heavy slots by the shared embedder's
    device, the lead cap from memory, the rerankers."""
    gb = lambda kb: f"{kb / 1048576:.1f}"
    lo, hi = (c.get("cpu_band") or [14, 18])[:2]
    busy = t.get("busy_cores")
    band = None if busy is None else ("below" if busy < lo else "above" if busy > hi else "within")
    cpu = (f"CPU {busy}/{t.get('nproc')} busy (band {lo}-{hi}: {band})" if busy is not None
           else f"CPU ?/{t.get('nproc')} (measuring)")
    try:
        floor_kb = json.loads(GATE_CONFIG.read_text())["floor_kb"]
    except (OSError, ValueError, KeyError):
        floor_kb = None
    avail = t.get("mem_available_mb")
    ram = (f"RAM {'?' if avail is None else gb(avail * 1024)} GB available (floor "
           f"{'?' if floor_kb is None else gb(floor_kb)} GB)")
    g = gpu_last(c)
    layers = load_json("gpu-health.json", {}).get("layers") or {}
    lay = ", ".join(f"{n} {v['x']}/{v['y']}" for n, v in sorted(layers.items()))
    if g:
        held = ", ".join(f"{k} {n}" for k, n in sorted(g["holders"].items())) or "none listed"
        gpu = (f"GPU {g['used_mib'] / 1024:.1f}/{g['total_mib'] / 1024:.1f} GB used, {g['free_mib'] / 1024:.1f} free "
               f"(headroom {int(c.get('gpu_headroom_mib', 2048)) / 1024:.1f} GB; embedders' layers: {lay or '?'}; "
               f"holders: {held})")
    else:
        gpu = f"GPU unread (embedders' layers: {lay or '?'})"
    target, device = slots_by_device(c)
    cap = t.get("lead_cap")
    caps = (f"lead cap {cap['cap']} from memory ({gb(cap['room_kb'])} GB room / {gb(cap['p95_kb'])} GB a lead)"
            if cap else "lead cap ? (no peaks or no memory rule)")
    rr = t.get("rerankers") or {}
    res = t.get("reranker_reserve")
    rer = (f"rerankers {rr.get('n', 0)} ({gb(rr.get('rss_kb', 0))} GB RSS; "
           f"{'?' if rr.get('gpu_held') is None else rr['gpu_held']} of {rr.get('gpu_slots', '?')} GPU slots held; "
           + (f"reserve {gb(res['kb'])} GB: {res['how']}" if res else "reserve ?") + ")")
    rec = {"busy_cores": busy, "nproc": t.get("nproc"), "cpu_band": [lo, hi], "cpu_in_band": band,
           "mem_available_mb": avail, "floor_kb": floor_kb, "gpu": g, "layers": layers,
           "embedders": {n: {k: sv.get(k) for k in ("state", "judged", "tasks_per_min", "waiting", "quiet_s")}
                         for n, sv in (emb.get("servers") or {}).items()},
           "embedder_state": emb.get("state"), "slots_target": target, "slots_device": device, "lead_cap": cap,
           "rerankers": rr, "reranker_reserve": res}
    line = (f"Balance: {cpu}; {ram}; {gpu}; embedders: {embed_line(emb, short=True)}; slots {target} by device "
            f"({device}); {caps}; {rer}")
    return rec, line


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
    try:
        bal, bal_line = balance(t, load_json("embed-health.json", {}), t.get("_c") or {})
    except Exception as exc:  # noqa: BLE001 - the status line says so; the rest of the status is written
        bal, bal_line = None, f"Balance: unreadable ({exc!r})"[:200]
    s["balance"] = bal
    txt = ([f"TICK FAILED in part: {'; '.join(failures)} at {s['time']}"] if failures else []) + [
        f"dispatcher {s['time']}",
        f"leads running ({t['lead_count']}, from the processes): {', '.join(t['leads']) or 'none'}",
        f"load {load}; real busy cores {t.get('busy_cores')} of {t.get('nproc')} (the embedding server "
        f"{t.get('embedding_cores')}); memory available {t.get('mem_available_mb')} MB; gate_check (for comparison) {'open' if t['gate_open'] else 'SHUT'}"
        f" ({t['gate'][:120]}); disk {'open' if t['disk_open'] else 'SHUT'}",
        bal_line,
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
    silent = sentinel_silent()
    want = {}  # F4 (v4 review): one line per cause, keyed; the sentinel's first (deadman.py keys on 150 characters)
    if silent:
        want["sentinel"] = "sentinel: " + silent.split(" (")[0]  # stable for one silence: no minutes in it
    emb, slots = load_json("embed-health.json", {}), load_json("slot-progress.json", {})
    if emb.get("hung_since"):
        want["server"] = f"server: the embedding server {emb.get('state')} since {stamp(emb['hung_since'])}"
    for name, sv in sorted((emb.get("servers") or {}).items()):  # DEC-1032: the other servers' incidents
        if name != "shared" and sv.get("hung_since"):
            want[f"server {name}"] = (f"server {name}: the {name} embedding server {sv.get('state')} since "
                                      f"{stamp(sv['hung_since'])}")
    gpu = load_json("gpu-health.json", {})
    if gpu_stale_line(gpu):
        want["gpu"] = gpu_stale_line(gpu)
    for e in sorted(slots.values(), key=lambda e: (str(e.get("slot")), e.get("pid", 0))):
        if e.get("reported"):
            k = f"slot {e['slot']} pid {e['pid']}"
            want[k] = f"{k}: IDLE since {stamp(e['since'])}"
    if age is not None and age >= STALE_S:
        want["inbox"] = f"inbox: {len(items)} item(s) unread; the oldest {oldest_item.name}"
    if silent:
        if not (D / "sentinel-silence-reported.txt").exists():
            inbox_item("sentinel-silent", f"log: deadman.log\nSentinel: silent\nstatus: {silent}; restart the sentinel "
                                          "(ACT-SENTINEL-1) or remove dispatch/sentinel-expected\n")
            (D / "sentinel-silence-reported.txt").write_text(silent + "\n")
    elif (D / "sentinel-silence-reported.txt").exists():
        os.unlink(D / "sentinel-silence-reported.txt")
    s["sentinel"] = silent or ("watched" if (D / "sentinel-expected").exists() else "not expected")
    have = {}
    try:
        for line in stale.read_text().splitlines():
            if line.strip():  # a line without a known key (the v4 form) is the inbox's
                k = line.split(":", 1)[0]
                have.setdefault(k if k in ("sentinel", "server", "gpu", "inbox") or k.startswith(("slot ", "server "))
                                else "inbox", line)
    except OSError:
        pass
    order = ["sentinel", "server"] + sorted(k for k in want if k.startswith("server ")) + ["gpu"] \
        + sorted(k for k in want if k.startswith("slot ")) + ["inbox"]
    keep = [have.get(k) or want[k] for k in order if k in want]  # a cause's line kept as first written
    if keep:
        text = "\n".join(keep) + "\n"
        if not stale.exists() or stale.read_text() != text:
            stale.write_text(text)
    elif stale.exists():
        os.unlink(stale)
    rec, _ = harvest_result()
    s["guard_harvest"] = rec
    s["embedding_server"], s["slot_holders"] = emb or None, list(slots.values())
    c = t.get("_c") or {}
    s["gpu"] = {"line": gpu_status_line(gpu, c), "state": gpu.get("gpu"), "layers": gpu.get("layers"),
                "alerts_24h": [a for a in gpu.get("alerts", []) if now() - a.get("at", 0) < 86400]} if gpu else None
    (D / "status.json").write_text(json.dumps(s, indent=1))  # again, with the sentinel's state
    with open(D / "status.txt", "a") as f:
        f.write(f"sentinel: {s['sentinel']}\n")
        f.write("guard harvest: " + (f"last {rec.get('at')}, rc {rec.get('rc')}, {rec.get('secs')} s of "
                                     f"{rec.get('limit_s')} s" if rec else "no record yet") + "\n")
        f.write(f"embedding server: {embed_line(emb)}\n")
        f.write((s["gpu"]["line"] if gpu else "GPU: not checked yet") + "\n")
        f.write("heavy slot holders: " + ("; ".join(
            f"slot {e['slot']} pid {e['pid']} ({e['cmd'][:60]}) {'IDLE' if e.get('reported') else 'idle'} "
            f"{int((now() - e['since']) // 60)} min" for e in slots.values()) or "none") + "\n")


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
    for name, fn in (("interim", lambda: watch_interim(dry)), ("guard", lambda: watch_guard(dry)),
                     ("nightly", lambda: watch_nightly(dry))):
        try:
            fn()
        except Exception as exc:
            failures.append(f"{name} watch: {exc!r}"[:200])
            log(f"{name} watch failed: {exc!r}")
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
    try:  # F2 (v4 review): after the start and land decisions, detached; its failure is the pass's, never silent
        guard_harvest(dry, t.get("_c") or {})
        _, hf = harvest_result()
        if hf:
            failures.append(hf[:200])
    except Exception as exc:
        failures.append(f"guard harvest: {exc!r}"[:200])
        log(f"guard harvest failed: {exc!r}")
    embed = None  # DEC-1015 item 2: after the decisions too (a hung server costs up to embed_timeout_s here)
    try:
        embed = watch_embedding(dry, t.get("_c") or {})
    except Exception as exc:
        failures.append(f"embedding check: {exc!r}"[:200])
        log(f"embedding check failed: {exc!r}")
    try:  # DEC-1030: the GPU, its holders and the embedding models' layers (an unreadable GPU is a status, not this)
        watch_gpu(dry, t.get("_c") or {})
    except Exception as exc:
        failures.append(f"gpu watch: {exc!r}"[:200])
        log(f"gpu watch failed: {exc!r}")
    try:
        watch_slots(dry, t.get("_c") or {}, embed)
    except Exception as exc:
        failures.append(f"slot progress: {exc!r}"[:200])
        log(f"slot progress failed: {exc!r}")
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
    if not argv or argv[0] not in ("tick", "status", "harvest"):
        sys.exit("usage: dispatcher.py tick [--dry] | status | harvest")
    if state_is_code() and E("DISPATCH_TEST") != "1":
        sys.exit(f"dispatcher: refused: the state folder {STATE} is the code folder or inside it (a stray "
                 "DISPATCH_STATE or DISPATCH_DIR?); nothing done")
    if argv[0] == "status":
        p = D / "status.txt"
        print(p.read_text() if p.exists() else "no status yet")
        return 0
    if argv[0] == "harvest":
        return harvest()
    if "--dry" in argv:
        os.environ["DISPATCH_DRY_FLAG"] = "1"
    return tick("--dry" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
