"""The operator agent's shared parts (OPERATOR-AGENT-1, DEC-1104 (2)): settings, the clock, the APPROVED check, the log,
the notices, the owner's lines read from the CTO session's transcript, the holds, and safe subprocess calls.

Standalone: the standard library only (PyYAML is used by act_class.py). Every location comes from a setting with
today's default (S24), so every test runs on planted folders. Nothing here waits on or stops a process by a name match
(L-0075): a child is waited on by its own pid, and a group is stopped by its own pgid.
"""
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ACT_RE = re.compile(r"^ACT-[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
CLASSES = ("a", "b", "O")
RANK = {"a": 0, "b": 1, "O": 2}
LIVE_REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
QUIET = ((2, 0), (7, 30))           # the quiet hours, 02:00 to 07:30 (DEC-1104 (2), G9)
DEFAULT_NIGHTLY = "03:50-08:00"     # the nightly (04:00 to about 07:00) and its wake (03:50): ACT-NIGHTLY-0400
AFTER_G7 = ("G7", "G8", "G9", "recompute", "apply", "checks", "unlisted", "staged", "commit", "after-check")


class Refused(Exception):
    """A gate refused: (gate, reason). Every gate fails closed by raising it."""

    def __init__(self, gate, reason):
        super().__init__(f"{gate}: {reason}")
        self.gate, self.reason = gate, reason


# ---------------------------------------------------------------------------------------------------------- settings
def install_dir():
    return HERE


def load_settings(config_path=None):
    """The settings: the --config file's keys over today's defaults (S24). A key left out takes its default."""
    conf = {}
    if config_path is None:
        own = os.path.join(HERE, "operator-settings.json")   # the install's own, hashed in APPROVED like the code
        if os.path.isfile(own):
            config_path = own
    if config_path is not None:
        with open(config_path, encoding="utf-8") as f:
            conf = json.load(f)
        if not isinstance(conf, dict):
            raise ValueError("the settings file is not a JSON object")
    s = {}
    s["install"] = HERE
    s["operator_root"] = os.path.abspath(os.path.expanduser(conf.get("operator_root") or os.path.dirname(HERE)))
    s["repo"] = os.path.abspath(os.path.expanduser(conf.get("repo") or LIVE_REPO))
    s["home"] = os.path.abspath(os.path.expanduser(conf.get("home") or os.path.expanduser("~")))
    s["scratch"] = os.path.abspath(os.path.expanduser(
        conf.get("scratch") or os.path.join(s["repo"], ".gov-runtime/scratch/orchestrator")))
    s["transcripts"] = os.path.abspath(os.path.expanduser(
        conf.get("transcripts") or os.path.join(s["home"], ".claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS")))
    s["clock"] = conf.get("clock")
    s["pings_log"] = os.path.abspath(os.path.expanduser(
        conf.get("pings_log") or os.path.join(s["home"], ".config/gov-os-notify/pings.log")))
    push = conf.get("push_cmd")
    if push is None:
        push = ["python3", os.path.join(s["repo"], "governance/project/orchestration/tools/deadman.py"),
                "--channel", "push", "--test"]
    s["push_cmd"] = shlex.split(push) if isinstance(push, str) else [str(x) for x in push]
    log = os.path.join(s["operator_root"], "log")
    s["log_dir"] = log
    s["calls"] = os.path.abspath(os.path.expanduser(conf.get("calls") or os.path.join(log, "calls.jsonl")))
    s["close_flag"] = os.path.abspath(os.path.expanduser(
        conf.get("close_flag") or os.path.join(s["scratch"], "CLOSE-RUNNING")))
    s["nightly_window"] = conf.get("nightly_window") or DEFAULT_NIGHTLY
    s["poll_s"] = float(conf.get("poll_s") if conf.get("poll_s") is not None else 60)
    s["freeze"] = os.path.abspath(os.path.expanduser(conf.get("freeze") or os.path.join(log, "act-in-progress.txt")))
    s["approvals"] = os.path.abspath(os.path.expanduser(
        conf.get("approvals") or os.path.join(log, "act-approvals.jsonl")))
    s["cto_freeze"] = os.path.join(s["scratch"], "log/act-in-progress.txt")
    s["claude"] = conf.get("claude") or "claude"
    s["model"] = conf.get("model") or "claude-sonnet-5-5"
    s["canary_model"] = conf.get("canary_model") or "claude-haiku-5-5"
    s["budget_usd"] = str(conf.get("budget_usd") or "1")
    s["canary_budget_usd"] = str(conf.get("canary_budget_usd") or "0.05")
    s["session_timeout_s"] = float(conf.get("session_timeout_s") or 2700)
    s["canary_timeout_s"] = float(conf.get("canary_timeout_s") or 300)
    s["check_timeout_s"] = float(conf.get("check_timeout_s") or 3600)
    s["hold_max_s"] = float(conf.get("hold_max_s") or 0)     # 0: a hold waits as long as it lasts (G9 never refuses)
    for k in ("operator_root", "repo", "home"):
        if s[k] in ("/", ""):
            raise ValueError(f"the setting {k} is the file system's root")
    return s


# ------------------------------------------------------------------------------------------------------------- clock
def parse_iso(text):
    """An ISO-8601 time with its offset (a trailing Z is UTC); None when it has no offset or does not parse."""
    if not isinstance(text, str) or not text.strip():
        return None
    t = text.strip()
    if t.endswith("Z") or t.endswith("z"):
        t = t[:-1] + "+00:00"
    try:
        d = datetime.fromisoformat(t)
    except ValueError:
        return None
    return d if d.tzinfo is not None else None


def now(s):
    """The time, read afresh each call: the clock file's one line when set, else the system clock (with its offset)."""
    if s.get("clock"):
        with open(os.path.expanduser(s["clock"]), encoding="utf-8") as f:
            lines = f.read().strip().splitlines()
        d = parse_iso(lines[0]) if lines else None
        if d is None:
            raise ValueError("the clock file holds no ISO-8601 time with an offset")
        return d
    return datetime.now(timezone.utc).astimezone()


def iso(d):
    return d.isoformat()


def in_window(d, window):
    """True when d's own wall clock lies inside 'HH:MM-HH:MM' (a window past midnight wraps)."""
    m = re.match(r"^\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*$", str(window or ""))
    if not m:
        raise ValueError(f"the window {window!r} is not HH:MM-HH:MM")
    a = int(m.group(1)) * 60 + int(m.group(2))
    b = int(m.group(3)) * 60 + int(m.group(4))
    t = d.hour * 60 + d.minute
    return a <= t < b if a <= b else (t >= a or t < b)


def holds(s):
    """G9's holds now, as a list of reasons (empty: no hold). Fails closed: a clock it cannot read is a hold."""
    out = []
    try:
        d = now(s)
    except (OSError, ValueError, IndexError) as exc:
        return [f"the clock cannot be read ({exc})"]
    (qa, qb) = QUIET
    if in_window(d, f"{qa[0]:02d}:{qa[1]:02d}-{qb[0]:02d}:{qb[1]:02d}"):
        out.append("the quiet hours (02:00 to 07:30)")
    try:
        if in_window(d, s["nightly_window"]):
            out.append(f"the nightly's window ({s['nightly_window']})")
    except ValueError as exc:
        out.append(str(exc))
    if os.path.lexists(s["close_flag"]):
        out.append("a close queue runs")
    if os.path.lexists(s["cto_freeze"]):
        out.append("the CTO's log/act-in-progress.txt exists")
    if os.path.lexists(s["freeze"]):
        out.append("the operator's log/act-in-progress.txt exists (another ACT)")
    return out


# ------------------------------------------------------------------------------------------------------------ hashes
def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_rel(path):
    """A relative path with no '..', no absolute start, no empty or NUL part; else None."""
    if not isinstance(path, str) or not path or "\x00" in path or path.startswith("/") or "\\" in path:
        return None
    parts = path.split("/")
    if any(p in ("", ".", "..") for p in parts):
        return None
    return path


# ---------------------------------------------------------------------------------------------------------- APPROVED
def approved_state(install=None):
    """(ok, approved_sha256, reason, lines {rel path: sha256}). Every file under install/ but APPROVED and __pycache__
    must match its line, and every line must name a file: one byte off, one file more or less refuses (S17)."""
    install = install or HERE
    ap = os.path.join(install, "APPROVED")
    if not os.path.isfile(ap) or os.path.islink(ap):
        return False, None, "install/APPROVED is missing", {}
    try:
        raw = open(ap, "rb").read()
    except OSError as exc:
        return False, None, f"install/APPROVED cannot be read ({exc})", {}
    asha = sha256_bytes(raw)
    lines = {}
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False, asha, "install/APPROVED is not text", {}
    for ln in text.splitlines():
        if not ln.strip():
            continue
        m = re.match(r"^([0-9a-f]{64}) [ *](.+)$", ln)
        rel = safe_rel(m.group(2)) if m else None
        if not m or rel is None or rel in lines:
            return False, asha, f"install/APPROVED has a malformed line: {ln[:80]!r}", {}
        lines[rel] = m.group(1)
    found = {}
    for top, dirs, files in os.walk(install):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for d in dirs:
            if os.path.islink(os.path.join(top, d)):
                return False, asha, f"install/ holds a link ({d})", lines
        for fn in files:
            full = os.path.join(top, fn)
            rel = os.path.relpath(full, install).replace(os.sep, "/")
            if rel == "APPROVED":
                continue
            if os.path.islink(full) or not os.path.isfile(full):
                return False, asha, f"install/ holds a link or a special file ({rel})", lines
            found[rel] = sha256_file(full)
    for rel in sorted(set(found) | set(lines)):
        if rel not in lines:
            return False, asha, f"install/{rel} has no line in APPROVED", lines
        if rel not in found:
            return False, asha, f"install/{rel} is named in APPROVED but missing", lines
        if found[rel] != lines[rel]:
            return False, asha, f"install/{rel} does not match its APPROVED line", lines
    return True, asha, "", lines


# --------------------------------------------------------------------------------------------------------- the output
def finish(result, code):
    """The result: the last line of stdout, one JSON object; then the exit code."""
    sys.stdout.flush()
    sys.stdout.write(json.dumps(result, sort_keys=False) + "\n")
    sys.stdout.flush()
    sys.exit(code)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def append_jsonl(path, obj):
    ensure_dir(os.path.dirname(path))
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path):
    """The JSON lines of a file, skipping lines that are not JSON objects; [] when the file is missing."""
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    e = json.loads(ln)
                except ValueError:
                    continue
                if isinstance(e, dict):
                    out.append(e)
    except FileNotFoundError:
        return []
    return out


def write_atomic(path, data, mode=0o644):
    ensure_dir(os.path.dirname(path))
    tmp = f"{path}.tmp-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    with open(tmp, "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode("utf-8"))
        f.flush()
        os.fsync(f.fileno())
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def log_path(s):
    return os.path.join(s["log_dir"], "operator.jsonl")


def log_event(s, act, sha, gate, result, votes=None, commit=None, checks=None, undo=None, **extra):
    """One line of log/operator.jsonl per gate reached per ACT (S20): every key present."""
    try:
        t = iso(now(s))
    except (OSError, ValueError, IndexError):
        t = iso(datetime.now(timezone.utc).astimezone())
    line = {"time": t, "act": act, "manifest_sha256": sha, "votes": votes, "gate": gate, "result": result,
            "commit": commit, "checks": checks, "undo": undo}
    line.update(extra)
    append_jsonl(log_path(s), line)
    return line


# ---------------------------------------------------------------------------------------------------------- notices
def notify(s, act, priority, kind, text, **extra):
    """A notice through the dead-man's channels: `<push_cmd> <notice JSON>`, and one JSON line in pings_log. A push
    that fails still leaves the pings line (the digest compares the log with the notices sent)."""
    try:
        t = iso(now(s))
    except (OSError, ValueError, IndexError):
        t = iso(datetime.now(timezone.utc).astimezone())
    notice = {"time": t, "act": act, "priority": priority, "kind": kind, "text": text}
    notice.update(extra)
    payload = json.dumps(notice, sort_keys=False)
    rc = None
    if s.get("push_cmd"):
        try:
            r = subprocess.run(list(s["push_cmd"]) + [payload], stdin=subprocess.DEVNULL, capture_output=True,
                               timeout=300, env=clean_env(s, s["home"]))
            rc = r.returncode
        except (OSError, subprocess.SubprocessError):
            rc = -1
    try:
        append_jsonl(s["pings_log"], notice)
    except OSError:
        pass
    return notice, rc


# --------------------------------------------------------------------------------------------- the owner's lines (S10)
def owner_text(entry):
    """The text of a transcript line typed by the owner, or None. Counts only a `type: user` line marked human
    (origin.kind human), not isMeta, not a sidechain, its content a string or text blocks; never a tool result, a task
    notification or an assistant line (the CTO's settled reading, 2026-11-09). A line without the mark never counts."""
    if not isinstance(entry, dict) or entry.get("type") != "user":
        return None
    origin = entry.get("origin")
    if not isinstance(origin, dict) or origin.get("kind") != "human":
        return None
    if entry.get("isMeta") or entry.get("isSidechain") or "toolUseResult" in entry:
        return None
    msg = entry.get("message")
    if not isinstance(msg, dict) or msg.get("role", "user") != "user":
        return None
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list) and content:
        texts = []
        for block in content:
            if not isinstance(block, dict):
                return None
            if block.get("type") == "tool_result":
                return None
            if block.get("type") == "text" and isinstance(block.get("text"), str):
                texts.append(block["text"])
        return "\n".join(texts) if texts else None
    return None


def cto_session(s):
    """The CTO session's id from <scratch>/log/cto-session.txt; None when missing or not a plain id."""
    path = os.path.join(s["scratch"], "log/cto-session.txt")
    try:
        with open(path, encoding="utf-8") as f:
            words = f.read().split()
    except OSError:
        return None
    sid = words[0] if words else ""
    return sid if re.match(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$", sid) else None


def transcript_path(s):
    sid = cto_session(s)
    return (sid, os.path.join(s["transcripts"], sid + ".jsonl")) if sid else (None, None)


def find_owner_line(s, wanted, after):
    """The first owner line in the CTO session's transcript whose text holds the line `wanted` exactly, typed after
    `after` (aware datetime). Returns (raw line, entry, timestamp) or None. Fails closed: anything unreadable counts
    as no line."""
    sid, path = transcript_path(s)
    if not path:
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            raw_lines = f.readlines()
    except OSError:
        return None
    for raw in raw_lines:
        raw = raw.rstrip("\n")
        if wanted not in raw:
            continue
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        text = owner_text(entry)
        if text is None:
            continue
        if not any(ln.strip() == wanted for ln in text.splitlines()):
            continue
        ts = parse_iso(entry.get("timestamp"))
        if ts is None or after is None or not ts > after:
            continue
        return raw, entry, ts
    return None


# ------------------------------------------------------------------------------------------------------- subprocesses
def clean_env(s, home, extra=None, path_prefix=None):
    """A clean environment: PATH, HOME, LANG, USER, LOGNAME, TMPDIR; never GOV_* or CLAUDE_PROJECT_DIR."""
    env = {}
    for k in ("PATH", "LANG", "LC_ALL", "USER", "LOGNAME", "TMPDIR", "TZ"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    env.setdefault("PATH", "/usr/local/bin:/usr/bin:/bin")
    env.setdefault("LANG", "C.UTF-8")
    env["HOME"] = home
    if path_prefix:
        env["PATH"] = path_prefix + os.pathsep + env["PATH"]
    for k, v in (extra or {}).items():
        env[k] = v
    for k in list(env):
        if k.startswith("GOV_") or k == "CLAUDE_PROJECT_DIR":
            del env[k]
    return env


def run(cmd, cwd=None, env=None, timeout=600, input_bytes=None):
    """Run a command in its own process group; wait by its pid; on a timeout stop its group by its pgid (L-0075).
    Returns (exit code, stdout bytes, stderr bytes); exit 124 on a timeout."""
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        out, err = p.communicate(input=input_bytes, timeout=timeout)
        return p.returncode, out, err
    except subprocess.TimeoutExpired:
        stop_group(p.pid)
        try:
            out, err = p.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            out, err = b"", b""
        return 124, out, err


def stop_group(pid, grace=10):
    """Stop the process group led by pid, by its pgid only: TERM, then KILL after a grace period."""
    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        return
    if pgid <= 1 or pgid == os.getpgid(0):
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline:
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.2)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def git(repo, *args, env=None, timeout=600):
    return run(["git", "-C", repo] + list(args), env=env, timeout=timeout)


def crontab_bytes(env=None):
    """`crontab -l`'s output, or None when it has none (any non-zero exit)."""
    try:
        rc, out, _ = run(["crontab", "-l"], env=env, timeout=60)
    except OSError:
        return None
    return out if rc == 0 else None


def live_file(s, root, path, env=None):
    """The bytes of a touched file as it is live: repo or home file, or `crontab -l`; None when it does not exist."""
    if root == "crontab":
        return crontab_bytes(env)
    base = s["repo"] if root == "repo" else s["home"]
    full = os.path.join(base, path)
    if os.path.islink(full):
        return ("link:" + os.readlink(full)).encode()
    if not os.path.isfile(full):
        return None
    with open(full, "rb") as f:
        return f.read()


def live_hash(s, root, path, env=None):
    b = live_file(s, root, path, env)
    return None if b is None else sha256_bytes(b)


def make_writable(path):
    """Give the owner write access again under path (to remove a read-only tree the agent made itself)."""
    if not os.path.lexists(path):
        return
    if os.path.isdir(path) and not os.path.islink(path):
        for top, dirs, files in os.walk(path):
            try:
                os.chmod(top, stat.S_IRWXU)
            except OSError:
                pass
            for d in dirs:
                p = os.path.join(top, d)
                if not os.path.islink(p):
                    try:
                        os.chmod(p, stat.S_IRWXU)
                    except OSError:
                        pass
            for fn in files:
                p = os.path.join(top, fn)
                if not os.path.islink(p):
                    try:
                        os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)
                    except OSError:
                        pass


def remove_tree(path):
    if os.path.lexists(path):
        make_writable(path)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.unlink(path)


def make_read_only(path):
    for top, dirs, files in os.walk(path, topdown=False):
        for fn in files:
            p = os.path.join(top, fn)
            if not os.path.islink(p):
                os.chmod(p, 0o444)
        for d in dirs:
            p = os.path.join(top, d)
            if not os.path.islink(p):
                os.chmod(p, 0o555)
    os.chmod(path, 0o555)


def first_a_time(s):
    """The time of the first live (a) ACT applied, from the log; None before it."""
    first = None
    for e in read_jsonl(log_path(s)):
        if e.get("result") != "applied":
            continue
        cls = e.get("class")
        if cls is None and isinstance(e.get("votes"), dict):
            vs = [v for v in e["votes"].values() if v in RANK]
            cls = max(vs, key=RANK.get) if vs else None
        if cls != "a":
            continue
        t = parse_iso(e.get("time"))
        if t is not None and (first is None or t < first):
            first = t
    return first


def within_first_14_days(s, when):
    first = first_a_time(s)
    if first is None:
        return True
    return (when.date() - first.astimezone(when.tzinfo).date()).days < 14


def highest(*classes):
    vs = [c if c in RANK else "O" for c in classes]
    return max(vs, key=RANK.get)


def plus_days(d, n):
    return d + timedelta(days=n)
