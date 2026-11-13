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
# G9 has no time hold (DEC-1157 (2), ACT-OPERATOR-HOURS-3: the night hold is removed, so the hours 02:10 to 07:59 that
# ACT-OPERATOR-HOURS-2 held for it, and the night hold's state file it read, are gone; it had replaced the fixed quiet hours
# of DEC-1104 (2)). G9 holds at any hour only for what runs now: the NIGHTLY-RUNNING flag, an explicit nightly_window, a close
# queue, the CTO's log/act-in-progress.txt, the operator's commit freeze, and a clock it cannot read.
DEFAULT_NIGHTLY = None              # no fixed nightly window by default; the NIGHTLY-RUNNING flag says when the nightly runs
AFTER_G7 = ("G7", "G8", "G9", "recompute", "apply", "checks", "unlisted", "staged", "commit", "after-check")
FREEZE_NAME = "act-in-progress.txt"  # the commit freeze, <operator root>/install/act-in-progress.txt (DEC-1106 (3))


class Refused(Exception):
    """A gate refused: (gate, reason). Every gate fails closed by raising it."""

    def __init__(self, gate, reason, **extra):
        super().__init__(f"{gate}: {reason}")
        self.gate, self.reason, self.extra = gate, reason, extra


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
    # push_cmd overrides the default channels: `<push_cmd> <notice JSON>`. Without it (today's default), a notice goes
    # through the dead-man's three channels from the install's own code (F4): pings_log, the Windows toast and a
    # headless `claude -p` PushNotification, as one line of at most 190 characters.
    s["push_cmd"] = None if push is None else (shlex.split(push) if isinstance(push, str) else [str(x) for x in push])
    chans = conf.get("channels")
    s["channels"] = [str(c) for c in chans] if isinstance(chans, list) else ["log", "toast", "push"]
    s["push_claude"] = os.path.expanduser(conf.get("push_claude") or os.path.join(s["home"], ".local/bin/claude"))
    s["push_model"] = conf.get("push_model") or "claude-haiku-5-5"
    s["powershell"] = conf.get("powershell") or "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    s["wslpath"] = conf.get("wslpath") or "wslpath"
    log = os.path.join(s["operator_root"], "log")
    s["log_dir"] = log
    # S15's replay (DEC-1108 (2)): the CTO's call set (header line, then calls and dropped calls), checked against the
    # guard's own call log (one file per UTC day) both ways before anything is re-judged; the set's `until` may be at
    # most replay_stale_h hours old
    s["calls"] = os.path.abspath(os.path.expanduser(conf.get("calls") or os.path.join(log, "calls.jsonl")))
    s["guard_calls"] = os.path.abspath(os.path.expanduser(
        conf.get("guard_calls") or os.path.join(s["home"], ".gov-os", "guard-calls")))
    s["replay_stale_h"] = float(conf.get("replay_stale_h") if conf.get("replay_stale_h") is not None else 12)
    s["close_flag"] = os.path.abspath(os.path.expanduser(
        conf.get("close_flag") or os.path.join(s["scratch"], "CLOSE-RUNNING")))
    s["nightly_window"] = conf.get("nightly_window") or DEFAULT_NIGHTLY       # an explicit window still holds
    # F12: the flag the nightly writes while it runs (nightly.sh: $ORCH/NIGHTLY-RUNNING, ORCH the CTO's scratch), so a
    # nightly that overruns its window still holds; older than nightly.sh's own 6 hours it is a dead run's leftover
    s["nightly_flag"] = os.path.abspath(os.path.expanduser(
        conf.get("nightly_flag") or os.path.join(s["scratch"], "NIGHTLY-RUNNING")))
    s["nightly_flag_max_age_s"] = float(conf.get("nightly_flag_max_age_s") or 6 * 3600)
    s["poll_s"] = float(conf.get("poll_s") if conf.get("poll_s") is not None else 60)
    # DEC-1106 (3): the commit freeze lives in the install folder, never in a log/ (the CTO's tools and the landing
    # hook read it; the APPROVED check and the install's control-file hash leave it out)
    s["freeze"] = os.path.abspath(os.path.expanduser(
        conf.get("freeze") or os.path.join(s["operator_root"], "install", FREEZE_NAME)))
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
    """G9's holds now, as a list of reasons (empty: no hold). No time hold (DEC-1157 (2)). Fails closed: a clock it
    cannot read is a hold."""
    out = []
    try:
        d = now(s)
    except (OSError, ValueError, IndexError) as exc:
        return [f"the clock cannot be read ({exc})"]
    try:
        if s["nightly_window"] and in_window(d, s["nightly_window"]):
            out.append(f"the nightly's window ({s['nightly_window']})")
    except ValueError as exc:
        out.append(str(exc))
    try:
        age = time.time() - os.lstat(s["nightly_flag"]).st_mtime
        if age < s["nightly_flag_max_age_s"]:
            out.append("the nightly runs (NIGHTLY-RUNNING)")
    except FileNotFoundError:
        pass
    except OSError as exc:
        out.append(f"NIGHTLY-RUNNING cannot be read ({exc.__class__.__name__})")
    if os.path.lexists(s["close_flag"]):
        out.append("a close queue runs")
    if os.path.lexists(s["cto_freeze"]):
        out.append("the CTO's log/act-in-progress.txt exists")
    if os.path.lexists(s["freeze"]):
        out.append("the commit freeze install/act-in-progress.txt exists (another run's, or a stale one: "
                   "only the run that wrote it removes it)")
    return out


def claim_freeze(s, act, sha, what="operator"):
    """Write the commit freeze if no one holds it (O_EXCL): returns the exact text written (the run's token), or None
    when the file already exists. Only the run holding the token removes it (release_freeze)."""
    path = s["freeze"]
    ensure_dir(os.path.dirname(path))
    try:
        t = iso(now(s))
    except (OSError, ValueError, IndexError):
        t = iso(datetime.now(timezone.utc).astimezone())
    token = f"{act} {sha} {t} {what} {os.getpid()}-{uuid.uuid4().hex}\n"
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return None
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(token)
        f.flush()
        os.fsync(f.fileno())
    return token


def release_freeze(s, token):
    """Remove the commit freeze only when it still holds this run's own token: a freeze another run wrote, or a stale
    one, is never removed (DEC-1106 (3))."""
    if not token:
        return False
    path = s["freeze"]
    try:
        if os.path.islink(path):
            return False
        with open(path, encoding="utf-8", errors="replace") as f:
            if f.read() != token:
                return False
        os.unlink(path)
        return True
    except OSError:
        return False


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
    """(ok, approved_sha256, reason, lines {rel path: sha256}). Every file under install/ but APPROVED, __pycache__ and
    the commit freeze act-in-progress.txt (DEC-1106 (3)) must match its line, and every line must name a file: one
    byte off, one file more or less refuses (S17)."""
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
            if rel in ("APPROVED", FREEZE_NAME):
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
LINE_MAX = 190      # the phone's PushNotification keeps 190 characters (deadman.py's send())
TOAST_TITLE = "Gov OS operator"
PUSH_PROMPT = ("Load the PushNotification tool (ToolSearch select:PushNotification if deferred) and call it once, status "
               "proactive, with exactly this message: {line} . Then reply with only the tool's result text.")


def notice_line(priority, act, short, undo=None):
    """One notice line of at most 190 characters: the priority and the ACT first, then the gate or the result, then
    the undo line; the middle is cut when it is too long, never the head or the undo line."""
    head = f"{priority} {act or 'operator'}"
    tail = f" | {' '.join(str(undo).split())}" if undo else ""
    body = " ".join(str(short or "").split())
    room = LINE_MAX - len(head) - len(" | ") - len(tail)
    if room < 8:
        tail, room = "", LINE_MAX - len(head) - len(" | ")
    if len(body) > room:
        body = body[:max(0, room - 1)].rstrip() + "…"
    return f"{head} | {body}{tail}"[:LINE_MAX]


def send_channels(s, line):
    """The dead-man's channels, copied in form (deadman.py's send(); the install never imports the repository): the
    Windows toast through the install's own win_toast.ps1, and a headless `claude -p` asked to call PushNotification
    with the line. The log channel is the pings_log line notify() writes. Returns {channel: result}."""
    out = {}
    env = clean_env(s, s["home"])
    for ch in s.get("channels") or []:
        try:
            if ch == "toast":
                rc, win, _ = run([s["wslpath"], "-w", os.path.join(HERE, "win_toast.ps1")], env=env, timeout=30)
                rc, _, _ = run([s["powershell"], "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                win.decode("utf-8", "replace").strip(), "-Title", TOAST_TITLE, "-Body", line],
                               env=env, timeout=60)
                out["toast"] = rc
            elif ch == "push":
                rc, _, _ = run([s["push_claude"], "-p", "--model", s["push_model"], "--output-format", "json",
                                PUSH_PROMPT.format(line=line)], cwd=env.get("TMPDIR") or "/tmp", env=env, timeout=300)
                out["push"] = rc
        except (OSError, ValueError) as exc:
            out[ch] = f"failed {exc.__class__.__name__}"
    return out


def notify(s, act, priority, kind, text, short=None, undo=None, **extra):
    """A notice: with push_cmd set, `<push_cmd> <notice JSON>`; otherwise the dead-man's channels (the toast and the
    headless push) with the notice's one line. Always one JSON line in pings_log, the log channel. A push that fails
    still leaves the pings line (the digest compares the log with the notices sent)."""
    try:
        t = iso(now(s))
    except (OSError, ValueError, IndexError):
        t = iso(datetime.now(timezone.utc).astimezone())
    if short is None:
        short = text[len(f"{act}: "):] if act and text.startswith(f"{act}: ") else text
    notice = {"time": t, "act": act, "priority": priority, "kind": kind, "text": text,
              "line": notice_line(priority, act, short, undo)}
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
    else:
        rc = send_channels(s, notice["line"])
    try:
        append_jsonl(s["pings_log"], notice)
    except OSError:
        pass
    return notice, rc


# --------------------------------------------------------------------------------------------- the owner's lines (S10)
def owner_text(entry):
    """The text of a transcript line typed by the owner, or None. Counts only a `type: user` line marked human
    (origin.kind human), not isMeta, not isCompactSummary, not a sidechain, its content a string or text blocks; never a tool result, a task
    notification or an assistant line (the CTO's settled reading, 2026-11-09). A line without the mark never counts."""
    if not isinstance(entry, dict) or entry.get("type") != "user":
        return None
    origin = entry.get("origin")
    if not isinstance(origin, dict) or origin.get("kind") != "human":
        return None
    if entry.get("isMeta") or entry.get("isSidechain") or entry.get("isCompactSummary") or "toolUseResult" in entry:
        return None                        # a compact summary quotes old turns afresh (F13): never the owner's
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
