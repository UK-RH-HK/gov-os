"""THROWAWAY MODEL of gov dispatch, written only to exercise the acceptance tests' plumbing. Not the engineer's."""
import datetime, fcntl, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path
import yaml

CHILD_EXIT_CODE = True
HELP = "model"
GIB = 1024 ** 3

def add_arguments(parser):
    parser.add_argument("action", choices=("tick", "status"))

class Cfg(Exception):
    pass

def now():
    return datetime.datetime.now(datetime.timezone.utc)

def iso(t=None):
    return (t or now()).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_cfg(root):
    f = root / "governance/project/dispatch.yaml"
    try:
        doc = yaml.safe_load(f.read_text())
    except FileNotFoundError:
        raise Cfg("dispatch.yaml is missing")
    except yaml.YAMLError:
        raise Cfg("dispatch.yaml is not YAML")
    d = doc.get("dispatch") if isinstance(doc, dict) else None
    if not isinstance(d, dict):
        raise Cfg("dispatch.yaml: no dispatch mapping")
    for k in ("integration_branch", "worktrees_root"):
        if not isinstance(d.get(k), str):
            raise Cfg(f"{k} is needed")
    for k in ("max_leads", "stagger_s"):
        if type(d.get(k)) is not int or d[k] < 0:
            raise Cfg(f"{k} must be a whole number")
    if isinstance(d.get("cpu_band"), bool) or not isinstance(d.get("cpu_band"), (int, float)) or d["cpu_band"] < 0:
        raise Cfg("cpu_band must be a number")
    d.setdefault("launch_command", ["gov", "launch", "lead", "{ticket}"])
    for k in ("launch_command", "notifier_command"):
        if k in d and not (isinstance(d[k], list) and all(isinstance(x, str) for x in d[k])):
            raise Cfg(f"{k} must be an argv list")
    d.setdefault("briefs_dir", ".gov-runtime/dispatch/briefs")
    d.setdefault("never_ran_after_s", 300)
    d.setdefault("unread_escalate_s", 3600)
    d.setdefault("command_timeout_s", 60)
    d.setdefault("history", ".gov-runtime/dispatch/history.jsonl")
    d.setdefault("probes_dir", "docs/probes")
    d.setdefault("job_markers", {})
    return d

class Timeout(Exception):
    pass

def sh(argv, cfg, cwd=None, stdin=None):
    try:
        done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=cfg["command_timeout_s"], input=stdin)
    except subprocess.TimeoutExpired:
        raise Timeout(f"command timed out after {cfg['command_timeout_s']}s: {' '.join(argv[:3])}")
    return done

def git(cfg, cwd, *args):
    return sh(["git", *args], cfg, cwd=cwd)

def write_whole(path, text):
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".w-")
    with os.fdopen(fd, "w") as h:
        h.write(text)
    os.replace(tmp, path)

def processes():
    proc = Path(os.environ.get("GOV_RESOURCES_PROC", "/proc"))
    out = []
    for d in proc.iterdir():
        if d.name.isdigit():
            try:
                cmd = (d / "cmdline").read_bytes().split(b"\0")
                cmd = [c.decode() for c in cmd if c]
                rss = int((d / "statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")
            except OSError:
                continue
            out.append((int(d.name), cmd, rss))
    return out

def leads(procs):
    out = {}
    for pid, cmd, rss in procs:
        if "--settings" in cmd:
            try:
                env = json.loads(cmd[cmd.index("--settings") + 1])["env"]
            except (ValueError, KeyError, IndexError):
                continue
            if env.get("GOV_ROLE") == "orchestrator" and env.get("GOV_TICKET"):
                out[env["GOV_TICKET"]] = rss
    return out

def run(root, args, config):
    root = Path(root)
    state = root / ".gov-runtime/dispatch"
    if args.action == "status":
        f = state / "status.txt"
        if not f.is_file():
            print("no pass has run")
            return 0
        if getattr(args, "json", False):
            print(json.dumps({"ok": True, "command": "dispatch", "result": json.loads((state / "status.json").read_text()), "session": ""}))
            return 0
        print(f.read_text(), end="")
        j = json.loads((state / "status.json").read_text())
        if (now() - datetime.datetime.strptime(j["time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)).total_seconds() > 180:
            print("the last pass is older than three minutes (stale)")
        return 0
    try:
        cfg = load_cfg(root)
    except Cfg as e:
        print(f"gov dispatch: CONFIG: {e}", file=sys.stderr)
        return 2
    state.mkdir(parents=True, exist_ok=True)
    fd = os.open(state / "tick.lock", os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return 4
    try:
        if (state / "OFF").exists():
            write_whole(state / "status.txt", "OFF\n")
            write_whole(state / "status.json", json.dumps({"ok": True, "off": True, "time": iso()}))
            return 0
        st = {"ok": True, "time": iso(), "skipped": [], "started": None}
        code = 0
        try:
            code = one_pass(root, state, cfg, st)
        except Exception as e:
            st = {"ok": False, "time": iso(), "reason": f"{type(e).__name__}: {e}"}
            write_whole(state / "status.json", json.dumps(st))
            write_whole(state / "status.txt", f"PASS FAILED {st['time']}: {st['reason']}\n")
            print(st["reason"], file=sys.stderr)
            return 1
        write_status(state, st)
        return code
    finally:
        os.close(fd)

def write_status(state, st):
    lines = [f"pass {st['time']} ok={st['ok']}"]
    for s in st["skipped"]:
        lines.append(f"skipped {s['entry']}: {s['reason']}")
    for k in ("notes",):
        lines += st.get(k, [])
    lines.append("kinds: " + ", ".join(f"{k} {v}" for k, v in st["peaks"].items()))
    lines.append("queue: " + json.dumps(st["queue"]))
    lines.append("inbox: " + json.dumps(st["inbox"]))
    write_whole(state / "status.json", json.dumps(st))
    write_whole(state / "status.txt", "\n".join(lines) + "\n")

WRAP = r'''
import subprocess, sys
log, exitf, brief = sys.argv[1:4]
argv = sys.argv[4:]
with open(brief) as i, open(log, "w") as o:
    code = subprocess.call(argv, stdin=i, stdout=o, stderr=subprocess.STDOUT)
open(exitf, "w").write(str(code))
'''

def one_pass(root, state, cfg, st):
    procs = processes()
    run_leads = leads(procs)
    notes = st.setdefault("notes", [])
    (state / "logs").mkdir(exist_ok=True)
    (state / "inbox" / "read").mkdir(parents=True, exist_ok=True)
    started_f = state / "started.txt"
    started = []
    if started_f.exists():
        started = [l.split() for l in started_f.read_text().splitlines() if l.strip()]
    wt_root = Path(cfg["worktrees_root"])
    if not wt_root.is_absolute():
        wt_root = root / wt_root
    seen_f = state / "returns-seen.txt"
    seen = set(seen_f.read_text().split()) if seen_f.exists() else set()
    esc_f = state / "escalated.txt"
    esc = set(esc_f.read_text().split()) if esc_f.exists() else set()
    def item(name, log, w2, status, extra=""):
        write_whole(state / "inbox" / name, f"log: {log}\nW2: {w2}\nstatus: {status}\n{extra}\n")
    # returns and never-ran
    for log, at, w2, ticket in [(s + [None] * 4)[:4] for s in started]:
        ex = state / "logs" / f"{log}.exit"
        if ex.exists() and log not in seen:
            text = (state / "logs" / log).read_text() if (state / "logs" / log).exists() else ""
            m = re.search(r"^status:\s*(.+)$", text, re.M)
            status = m.group(1).strip() if m else f"exit {ex.read_text().strip()}"
            bad = []
            wt = wt_root / w2
            for key, kind in (("commits", "c"), ("files_changed", "p")):
                mm = re.search(rf"^{key}:(.*)$", text, re.M)
                toks = [t for t in re.split(r"[,\s]+", mm.group(1)) if t] if mm else []
                for t in toks:
                    if kind == "c" and re.fullmatch(r"[0-9a-f]{7,40}", t):
                        if git(cfg, wt, "cat-file", "-e", f"{t}^{{commit}}").returncode:
                            bad.append(t)
                    elif kind == "p" and "/" in t or (kind == "p" and "." in t):
                        if git(cfg, wt, "cat-file", "-e", f"HEAD:{t}").returncode:
                            bad.append(t)
            extra = ("unresolved: " + ", ".join(bad) + "\n") if bad else ""
            item(f"{int(time.time()*1000)}-{log}.txt", log, w2, status, extra)
            seen.add(log)
            seen_f.write_text("\n".join(sorted(seen)) + "\n")
        elif not ex.exists() and log not in seen and ticket not in run_leads:
            age = time.time() - datetime.datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
            if age > cfg["never_ran_after_s"]:
                nr = state / "never-ran.txt"
                done = nr.read_text().split() if nr.exists() else []
                if log not in done:
                    item(f"{int(time.time()*1000)}-never-{log}.txt", log, w2, "never ran")
                    nr.write_text("\n".join(done + [log]) + "\n")
    # escalation
    for f in sorted((state / "inbox").iterdir()):
        if f.is_file() and f.name not in esc and time.time() - f.stat().st_mtime > cfg["unread_escalate_s"] and cfg.get("notifier_command"):
            esc.add(f.name)
            esc_f.write_text("\n".join(sorted(esc)) + "\n")
            try:
                sh([*cfg["notifier_command"], str(f)], cfg)
            except Timeout as e:
                notes.append(str(e))
    unread = [f for f in sorted((state / "inbox").iterdir()) if f.is_file()]
    unread_w2 = {re.search(r"^W2:\s*(\S+)", f.read_text(), re.M).group(1) for f in unread if re.search(r"^W2:", f.read_text(), re.M)}
    # history and peaks
    hist = {}
    hf = root / cfg["history"]
    if hf.exists():
        for l in hf.read_text().splitlines():
            try:
                h = json.loads(l)
            except ValueError:
                continue
            k = hist.setdefault(h["kind"], {"cpu": 0, "mem_bytes": 0})
            k["cpu"] = max(k["cpu"], h["cpu"]); k["mem_bytes"] = max(k["mem_bytes"], h["mem_bytes"])
    from gov.resources import gate, config as rc
    values = rc.load()["values"]
    W, F = values["working_size_bytes"], values["memory_floor_bytes"]
    pk = state / "peaks.json"
    old = (not pk.exists()) or time.time() - pk.stat().st_mtime > 86400
    if old:
        write_whole(pk, json.dumps({k: {**v, "date": iso()[:10]} for k, v in hist.items()}))
    peaks = json.loads(pk.read_text())
    st["peaks"] = peaks
    st["running"] = sorted(run_leads)
    st["load"] = open(os.environ["GOV_RESOURCES_LOADAVG"]).read().split()[0]
    st["memory"] = {"available": int(re.search(r"MemAvailable:\s+(\d+)", open(os.environ["GOV_RESOURCES_MEMINFO"]).read()).group(1)) * 1024}
    reading = gate.read(check=True)
    st["gate"] = {"open": reading["gate"]["open"], "reasons": [gate.describe(r) for r in reading["gate"]["reasons"]]}
    st["slots"] = reading["slots"]
    ahead_mem = 0
    for kind, marker in cfg["job_markers"].items():
        for pid, cmd, rss in procs:
            if marker in " ".join(cmd):
                ahead_mem += max(0, peaks.get(kind, {}).get("mem_bytes", W) - rss)
    lead_peak = peaks.get("lead", {}).get("mem_bytes", W)
    for t, rss in run_leads.items():
        ahead_mem += max(0, lead_peak - rss)
    st["ahead"] = {"mem_bytes": ahead_mem}
    land = state / "land.txt"
    st["queue"] = [l for l in land.read_text().splitlines() if l.strip()] if land.exists() else []
    st["inbox"] = [{"file": f.name, "text": f.read_text()} for f in unread]
    ready = state / "ready.txt"
    if not ready.exists():
        return 0
    code = 0
    started_logs = [s[0] for s in started]
    room_refused = False
    for raw in ready.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        f = line.split()
        if len(f) != 4:
            st["skipped"].append({"entry": line, "reason": "malformed line"}); continue
        w2, ticket, brief, log = f
        def skip(reason):
            st["skipped"].append({"entry": f"{log} {w2} {ticket}", "reason": reason})
        if log in started_logs:
            skip("already started"); continue
        wt = wt_root / w2
        ok = True
        tip = git(cfg, root, "show", f"{cfg['integration_branch']}:.tickets/{ticket}.md")
        head = git(cfg, wt, "show", f"HEAD:.tickets/{ticket}.md")
        if tip.returncode or head.returncode or "status: in_progress" not in tip.stdout or "status: in_progress" not in head.stdout:
            skip("claim not committed on the integration branch and in the worktree"); continue
        if git(cfg, wt, "status", "--porcelain", "--untracked-files=no").stdout.strip():
            skip("worktree not clean (tracked change)"); continue
        bp = Path(brief)
        if not bp.is_absolute():
            bd = Path(cfg["briefs_dir"])
            bp = (bd if bd.is_absolute() else root / bd) / brief
        text = bp.read_text() if bp.is_file() else ""
        if not text.strip() or "@@" in text or re.search(r"\{[A-Z][A-Z0-9_]*\}", text):
            skip("brief missing, empty or incomplete"); continue
        if ticket in run_leads:
            skip("ticket already running"); continue
        if w2 in unread_w2:
            skip("unread return"); continue
        if re.search(r"^run: review$", text, re.M):
            pd = wt / cfg["probes_dir"] / ticket
            if len(list(pd.glob("*.md"))) >= 2:
                skip("a third review round: owner item")
                if not any(f"-owner-{log}" in x.name for x in (state / "inbox").iterdir()) and not any(f"-owner-{log}" in x.name for x in (state / "inbox/read").iterdir()):
                    item(f"{int(time.time()*1000)}-owner-{log}.txt", log, w2, "owner")
                continue
        if not st["gate"]["open"]:
            skip("gate shut: " + "; ".join(st["gate"]["reasons"])); code = 3; continue
        pend = [s for s in started if s[0] not in seen and not (state / "logs" / f"{s[0]}.exit").exists()]
        launching = [s for s in pend if s[3] not in run_leads]
        if len(run_leads) + len(launching) >= cfg["max_leads"]:
            skip("max_leads reached"); continue
        if started and cfg["stagger_s"]:
            last = max(datetime.datetime.strptime(s[1], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp() for s in started)
            if time.time() - last < cfg["stagger_s"]:
                skip("staggered"); continue
        avail = st["memory"]["available"]
        nproc = int(os.environ["GOV_RESOURCES_NPROC"]); busy = float(os.environ["GOV_RESOURCES_BUSY_CORES"])
        lp = peaks.get("lead", {"cpu": 0, "mem_bytes": W})
        if avail - F - ahead_mem < lp["mem_bytes"] or nproc - busy - cfg["cpu_band"] < lp["cpu"]:
            skip(f"no room for its peak: available {avail} floor {F} ahead {ahead_mem} peak {lp['mem_bytes']}"); code = 3; continue
        with open(started_f, "a") as h:
            h.write(f"{log} {iso()} {w2} {ticket}\n")
        argv = [a.format(ticket=ticket, w2=w2, brief=str(bp), log=log) for a in cfg["launch_command"]]
        subprocess.Popen([sys.executable, "-c", WRAP, str(state / "logs" / log), str(state / "logs" / f"{log}.exit"), str(bp), *argv],
                         start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        st["started"] = log
        break
    return code
