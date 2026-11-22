"""The dead-man's switch on the CTO's session (owner, DEC-988 item 4, DEC-991): run by cron every 15 minutes.

    python3 deadman.py [--dry] [--now "YYYY-MM-DD HH:MM"] [--channel push] [--projects <dir>] [--state <file>]
    python3 deadman.py --test "<label>" [--channel push]     # a forced test alert through the channel (ACT-DEADMAN-1)
    python3 deadman.py --watch [--every 120] [--max 6600]     # the sentinel's wait (DEC-998): exits 10 with the
        # alert line on a stall (sending nothing itself), or 0 with a HEARTBEAT line after --max seconds

The session watched is the one named in log/cto-session.txt (each CTO session writes its id there at its start,
DEC-998), so a sentinel or a throwaway session in the same folder is never mistaken for it; without the file, the
newest transcript.

Reads the newest session transcript in the main repository's Claude Code project folder (never the file's mtime:
queued notifications keep writing it during a freeze) and finds its last `assistant` entry. It alerts when that is
older than 60 minutes (inside the quiet hours, 02:00 to 07:30, only past 2 hours), saying "waiting on a tool (likely
a permission prompt) since HH:MM" when the last entry is a tool call with no result, else "idle since HH:MM". One
alert per stall, then a reminder every 2 hours while it lasts (state in log/deadman-state.json). Channels: `toast`
(a Windows notification on the PC, no install), `push` (a headless `claude -p` call to PushNotification, which reaches
the phone through Remote Control when the PC is not in use), `log` (~/.config/gov-os-notify/pings.log). Every
decision is appended to log/deadman.log. It never reads or prints a transcript's text beyond entry types and times.

The wake (DAEO-sdxk, 2026-11-10; DEC-1112 (3)): once the watched session's last `assistant` entry is 60 minutes old,
at any hour (quiet hours included), it writes one inbox item, dispatch/inbox/<stamp>-deadman-wake.txt (the stall line
and "check the helpers and resume them"), once per stall (state in log/deadman-wake-state.json), so the CTO's own inbox
waiter wakes the CTO. The wake writes only into the CTO's inbox: it pushes nothing, and the ALERT, its limits (60
minutes by day, 2 hours in the quiet hours) and its reminders are unchanged. Not in a stand-by, not with --dry. The
inbox is ORCH/dispatch/inbox when the state is the live one, else a folder `inbox` beside --state (a replay or a test
never writes the live inbox), or --inbox. Because an item unread 30 minutes makes the dispatcher's inbox-stale line,
the watch re-reads the inbox folder (the stale file's sibling `inbox/`) before it uses the dispatcher's `inbox:` line:
  - no item there unread past 30 minutes (--stale-s, kept equal to the dispatcher's STALE_S, 1800 s): the line is
    from before a read and is left out (review F1); a missing or unreadable folder keeps it (fail toward the push);
  - outside a CTO stand-by: left out when every stale item is one of the CTO's own wake items (a name ending
    -deadman-wake, -helper-watch or -spend-brake, with an optional -<n>), whose staleness the stall's own ALERT
    already covers (it is silent only in a stand-by);
  - in a stand-by, when the ALERT is silent by design: left out only when every stale item is a -spend-brake item
    (DEC-1089 (3): usage never alarms the owner); a stale -helper-watch or -deadman-wake item pushes (review F2);
  - any other stale item pushes exactly as before.
The stall's key is written before the item, so a key that cannot be written gives no item rather than one on every
pass; a key that is not an object is read as no key (review F3).
A stand-by note expires (owner, 2026-11-10: "a stale one can never mute the dead-man for hours again"). The note mutes
the ALERT, the wake and the inbox exemptions only while it is younger than --standby-max-s (default 7200, 2 hours).
Its age is read from the UTC time that leads the note ("2026-11-10 15:49:50 ..."), else from the file's mtime; a time
more than 5 minutes ahead of the clock is not believed (the mtime is read instead, and failing that the note is
expired), so a note can never mute for good. Once it is expired the normal logic applies: the log's note carries
`"standby": "expired (written <time> UTC, <n> min ago)"` and an ALERT line ends with the same words. A CTO that is still
waiting renews the note by writing a new time into it.
The inbox wake (ACT-DEADMAN-INBOX-1; DEC-1191 (3), P-SESSIONS-1 item 4b; review round 1's F1-F8 fixed): on each
pass (each --watch tick and each plain run), when an item in the wake's inbox (the folder `inbox_dir` names) is unread
past --wake-unread-s (600 s), or no process whose arguments hold the waiter guard's path has been seen for
--guard-grace-s (300 s; the guard exits on purpose to wake the CTO; read from `ps -eo args=`, never signalled; a ps that
cannot run reads as alive and is logged once, "ps unreadable"), it sends ONE cross-session wake to the CTO session:
  - only when the state is the live one (a replay or test, with --state or --inbox elsewhere, never sends);
  - to the name in log/cto-name.txt, which must match ^[a-z0-9][a-z0-9-]{0,63}$, else it is treated as missing;
  - through a headless `claude -p` limited to the message's tools (`--tools ToolSearch,SendMessage`, the rest
    disallowed, `--permission-mode default`, `--strict-mcp-config`, `--setting-sources user`), from a fresh 0700
    folder in a 0700 `xwake-cwd/` beside the state (never /tmp), 60 s at most;
  - with fixed words and numbers only, never a file name or any other inbox-derived text: "INBOX WAKE: <n> items
    unread, oldest <m> min" and/or "no waiter guard alive for <k> min", then "re-arm the inbox waiter and the waiter
    guard".
A new cause while the incident lasts (another oldest item, the guard going) wakes again; the incident's first wake time
is kept. If the incident still holds --push-after-s (600 s) after its first wake, an `INBOX-WAKE` ALERT (at most 200
characters, numbers only) goes once to the owner: the watch exits 10 with it (the sentinel pushes it, as every ALERT), a
plain run sends it on its channels. The CTO's own items (-spend-brake, -deadman-wake, -helper-watch; DEC-1089 (3))
may wake the CTO but never cause the push. No valid CTO name: no cross-session wake, the ALERT at once (fail toward the
owner). Any error in this code is caught: it is logged, and the ALERT goes once per error kind. Muted while a stand-by
note is active; --dry sends nothing (and never writes the live key). The incident over, its key is cleared.
ORCH (environment) moves the whole scratch root; --log, --state, --inbox, --session-file, --standby and --inbox-stale
move each file, so a test or rehearsal never touches the live ones.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECTS = Path.home() / ".claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS"
ORCH = Path(os.environ.get("ORCH") or "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
TOOLS_DIR = Path(__file__).resolve().parent
STATE = ORCH / "log/deadman-state.json"
SESSION_FILE = ORCH / "log/cto-session.txt"
STANDBY = ORCH / "log/cto-standby.txt"  # while it is younger than --standby-max-s, the CTO stands by on purpose: no alert (DEC-998)
# The dispatcher writes this file while an inbox item has been unread 30 minutes (the owner, 2026-11-01); its
# content is stable for one stall, so the watch alerts once per stall. It also alerts during a CTO stand-by (intended);
# the CTO's own wake items are left out outside a stand-by, and -spend-brake items always (ACT-DEADMAN-WAKE-1).
INBOX_STALE = ORCH / "dispatch/inbox-stale.txt"
LOG = ORCH / "log/deadman.log"
PINGS = Path.home() / ".config/gov-os-notify/pings.log"
TOAST = TOOLS_DIR / "win_toast.ps1"
PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
DAY_LIMIT, NIGHT_LIMIT, REMIND = timedelta(minutes=60), timedelta(hours=2), timedelta(hours=2)
WAKE_LIMIT = timedelta(minutes=60)  # the wake, at any hour (DEC-1112 (3)); the push keeps the owner's limits above
WAKE_ITEM = re.compile(r"-(?:deadman-wake|helper-watch|spend-brake)(?:-\d+)?\.txt$")  # the CTO's own wake items
BRAKE_ITEM = re.compile(r"-spend-brake(?:-\d+)?\.txt$")  # never an alarm to the owner, stand-by or not (DEC-1089 (3))
CTO_NAME_FILE = ORCH / "log/cto-name.txt"  # the CTO session's name for a cross-session message (ACT-DEADMAN-INBOX-1)
WAITER_GUARD = ".gov-runtime/scratch/orchestrator/tools/waiter_guard.sh"  # the CTO's watch on its own watches
STANDBY_MAX_S = 7200  # a stand-by note older than this no longer mutes (owner, 2026-11-10)
STANDBY_SLACK = timedelta(minutes=5)  # a time this far ahead of the clock is clock skew, any more is not believed
STANDBY_STAMP = re.compile(r"\s*(\d{4}-\d\d-\d\d)[ T](\d\d:\d\d:\d\d)Z?(?!\S)")  # the note's leading UTC time


def quiet(t):
    hm = t.hour * 60 + t.minute
    return 2 * 60 <= hm < 7 * 60 + 30


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone()


def last_state(path, tail=4_000_000):
    """(last assistant time, whether it is a tool call with no result after it, the tool name)."""
    with open(path, "rb") as f:
        f.seek(0, 2)
        start = max(0, f.tell() - tail)
        f.seek(start)
        lines = f.read().decode("utf-8", "replace").splitlines()[1 if start else 0:]  # a cut first line is dropped
    last_a, pending, tool = None, False, None
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("isSidechain"):
            continue
        content = (e.get("message") or {}).get("content")
        if e.get("type") == "assistant" and e.get("timestamp"):
            last_a = parse_ts(e["timestamp"])
            uses = [c for c in content or [] if isinstance(c, dict) and c.get("type") == "tool_use"]
            pending, tool = (True, uses[-1].get("name")) if uses else (False, None)
        elif e.get("type") == "user" and isinstance(content, list) and \
                any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content):
            pending = False
    return last_a, pending, tool


def send(channels, line, dry):
    out = []
    for ch in channels:
        if dry:
            out.append(f"{ch}: dry")
            continue
        try:
            if ch == "log":
                PINGS.parent.mkdir(parents=True, exist_ok=True)
                with open(PINGS, "a") as f:
                    f.write(time.strftime("%Y-%m-%dT%H:%M:%S%z ") + line + "\n")
                out.append("log: written")
            elif ch == "toast":
                win = subprocess.run(["wslpath", "-w", str(TOAST)], capture_output=True, text=True).stdout.strip()
                r = subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", win, "-Title",
                                    "Gov OS: CTO session stalled", "-Body", line], capture_output=True, text=True,
                                   timeout=60)
                out.append(f"toast: rc {r.returncode}")
            elif ch == "push":
                r = subprocess.run([str(Path.home() / ".local/bin/claude"), "-p", "--model", "claude-sonnet-5-5",
                                    "--output-format", "json",
                                    "Load the PushNotification tool (ToolSearch select:PushNotification if deferred) "
                                    "and call it once, status proactive, with exactly this message: " + line[:190]
                                    + " . Then reply with only the tool's result text."],
                                   capture_output=True, text=True, timeout=300, cwd="/tmp")
                res = ""
                for chunk in r.stdout.splitlines():
                    if chunk.startswith("{"):
                        try:
                            res = json.loads(chunk).get("result", "")
                        except ValueError:
                            pass
                out.append(f"push: rc {r.returncode} {res[:120]}")
        except (OSError, subprocess.SubprocessError) as exc:
            out.append(f"{ch}: failed {exc.__class__.__name__}")
    return out


def inbox_dir(a):
    """The wake's inbox: --inbox, else the live inbox for the live state, else `inbox` beside the state."""
    if getattr(a, "inbox", None):
        return Path(a.inbox)
    return ORCH / "dispatch/inbox" if Path(a.state).resolve() == STATE.resolve() else Path(a.state).parent / "inbox"


def wake(a, stall, line, now):
    """One inbox item per stall (key: the stall); returns the item's path, or a note why none was written."""
    key_f = Path(a.state).with_name("deadman-wake-state.json")
    try:
        if json.loads(key_f.read_text()).get("stall") == stall:
            return "woken already"
    except (OSError, ValueError, AttributeError, TypeError):  # missing, unreadable or not an object: no key (F3)
        pass
    box = inbox_dir(a)
    try:
        tmp = key_f.with_name(key_f.name + ".tmp")  # the key first: a key that cannot be written gives no item
        tmp.write_text(json.dumps({"stall": stall, "woken": now.isoformat()}))
        os.replace(tmp, key_f)
        box.mkdir(parents=True, exist_ok=True)
        stamp, n = now.strftime("%Y%m%d-%H%M%S"), 1
        item = box / f"{stamp}-deadman-wake.txt"
        while True:  # never overwrite an item (the dispatcher's rule)
            try:
                with open(item, "x") as f:
                    f.write(f"log: deadman.log\nDeadman: wake\nstatus: {line}\n\ncheck the helpers and resume them "
                            "(their transcripts: subagents/agent-*.jsonl; tools/helper_watch.py)\n")
                break
            except FileExistsError:
                n += 1
                item = box / f"{stamp}-deadman-wake-{n}.txt"
        return str(item)
    except OSError as exc:
        return f"wake failed {exc.__class__.__name__}"


def leave_out_inbox_line(box, stale_s, standby):
    """Whether the dispatcher's `inbox:` line is left out: the folder holds no item unread past stale_s (the line is
    from before a read), or every stale item is exempt (outside a stand-by the CTO's wake items, in a stand-by only
    -spend-brake items). A missing or unreadable folder keeps the line (fail toward the push)."""
    try:
        if not box.is_dir():
            return False
        cut = time.time() - stale_s
        old = [p.name for p in box.glob("*.txt") if p.stat().st_mtime <= cut]
    except OSError:
        return False
    exempt = BRAKE_ITEM if standby else WAKE_ITEM
    return all(exempt.search(n) for n in old)


def standby_state(path, max_s, now):
    """None without a note; else {active, text, written, expired}. The note mutes only while its age is under max_s.
    The age is from the UTC time leading the note, else the file's mtime; a time more than STANDBY_SLACK ahead of
    `now` is not believed (the mtime is read instead), and no usable time at all is expired: fail toward the alert."""
    p = Path(path)
    if not p.is_file():
        return None
    try:
        text = p.read_text(errors="replace").strip()
    except OSError:
        text = ""
    written, m = None, STANDBY_STAMP.match(text)
    if m:
        try:
            written = datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}+00:00")
        except ValueError:
            pass
    if written is None or written - now > STANDBY_SLACK:
        try:
            written = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc)
        except (OSError, OverflowError, ValueError):
            written = None
    age = None if written is None else now - written
    active = age is not None and -STANDBY_SLACK <= age < timedelta(seconds=max_s)
    if active:
        return {"active": True, "text": text}
    if age is None:
        why = "expired (no usable time on the note or the file)"
    elif age < timedelta(0):
        why = f"expired (dated {written:%F %H:%M} UTC, ahead of the clock)"
    else:
        why = f"expired (written {written:%F %H:%M} UTC, {int(age.total_seconds() // 60)} min ago)"
    return {"active": False, "text": text, "expired": why}


NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")  # a CTO session name as the message tools list it
PREFIX_RE = re.compile(r"^[A-Za-z0-9 :._-]{0,40}$")
XWAKE_TOOLS = ["--tools", "ToolSearch,SendMessage", "--disallowedTools", "Bash", "Edit", "Write", "Read", "Glob", "Grep",
               "WebFetch", "WebSearch", "NotebookEdit", "Task", "--permission-mode", "default", "--strict-mcp-config",
               "--setting-sources", "user"]  # review F9: no project or local settings, hooks or CLAUDE.md of a folder


def private_dir(parent):
    """A fresh 0700 folder inside `parent`, which is created 0700 and must be this user's and not reachable by others
    (review F9: the headless call must not start in a folder another session can write, such as /tmp). None if not."""
    import tempfile
    try:
        parent = Path(parent)
        parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        st = parent.stat()
        if st.st_uid != os.getuid() or st.st_mode & 0o077:
            os.chmod(parent, 0o700)
            st = parent.stat()
            if st.st_uid != os.getuid() or st.st_mode & 0o077:
                return None
        return Path(tempfile.mkdtemp(prefix="xwake-", dir=parent))
    except OSError:
        return None


def xwake(name, text, cwd_parent):
    """One cross-session message to the session `name`, through a headless `claude -p` limited to the message's tools,
    with no project or local settings (`--setting-sources user`), from a fresh private folder in `cwd_parent`, 60 s at
    most; returns a short result note. Refuses a name outside NAME_RE. `text` is built by inbox_wake from fixed words
    and numbers only."""
    import shutil
    if not NAME_RE.match(name or ""):
        return "xwake: refused (no valid name)"
    cwd = private_dir(cwd_parent)
    if cwd is None:
        return "xwake: refused (no private working folder)"
    try:
        r = subprocess.run([str(Path.home() / ".local/bin/claude"), "-p", "--model", "claude-sonnet-5-5",
                            "--output-format", "json", *XWAKE_TOOLS, "--",
                            "Load the SendMessage tool (ToolSearch select:SendMessage if deferred) and send ONE "
                            f"cross-session message to the session named {name} with exactly this text: {text} . "
                            "Then reply with only SENT or FAILED and the reason."],
                           capture_output=True, text=True, timeout=60, cwd=str(cwd))
    except (OSError, subprocess.SubprocessError) as exc:
        return f"xwake: failed {exc.__class__.__name__}"
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    res = ""
    for chunk in r.stdout.splitlines():
        if chunk.startswith("{"):
            try:
                res = json.loads(chunk).get("result", "")
            except ValueError:
                pass
    return f"xwake: rc {r.returncode} {res[:120]}"


def guard_alive(needle):
    """(alive, readable): whether a process whose arguments hold `needle` runs (ps output only; nothing is signalled).
    A ps that cannot run reads as alive (readable False): no guard wake from a broken ps; the inbox half still wakes."""
    try:
        out = subprocess.run(["ps", "-eo", "args="], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return True, False
    return any(needle in line and "deadman.py" not in line for line in out.splitlines()), True


def _once(path, value):
    """True the first time `value` is written to `path` (a marker); False when it is there already or cannot be written."""
    try:
        if path.is_file() and path.read_text(errors="replace") == value:
            return False
        path.write_text(value)
        return True
    except OSError:
        return False


def inbox_wake(a, sb):
    """The inbox wake's pass, guarded (F5): any error becomes a note, and the ALERT once per error kind."""
    try:
        return _inbox_wake(a, sb)
    except Exception as exc:  # noqa: BLE001 - the watch must never die of this code (review F5)
        kind = exc.__class__.__name__
        mark = Path(a.state).with_name("deadman-inbox-error-seen.txt")
        line = f"P1 INBOX-WAKE | the inbox wake failed ({kind}) | check deadman.log and the inbox"
        if not a.dry and _once(mark, kind):
            return f"error {kind}", line[:200]
        return f"error {kind}", None


def _inbox_wake(a, sb):
    """(note, alert line or None). The incident: the condition held without a break; its first wake time is kept."""
    now = datetime.now(timezone.utc)
    live = Path(a.state).resolve() == STATE.resolve() and not getattr(a, "inbox", None)
    record = not (a.dry and live)  # a dry run never writes the live key
    key_f = Path(a.state).with_name("deadman-inbox-wake-state.json")
    box = inbox_dir(a)
    old = []
    if box.is_dir():
        for p in box.glob("*.txt"):
            try:
                m = p.stat().st_mtime
            except OSError:
                continue
            if time.time() - m > a.wake_unread_s:
                old.append((m, p.name))
    old.sort()
    notes = []
    gone_f = key_f.with_name("deadman-noguard-since.txt")
    alive, readable = guard_alive(a.waiter_guard_needle)
    if not readable and _once(key_f.with_name("deadman-ps-unreadable.txt"), "ps unreadable"):
        notes.append("ps unreadable")
    noguard_min = None
    if alive:
        if gone_f.is_file() and record:
            gone_f.unlink(missing_ok=True)
    else:
        try:
            since = float(gone_f.read_text().strip())
        except (OSError, ValueError):
            since = time.time()
            if record:
                gone_f.write_text(str(since))
        if time.time() - since >= a.guard_grace_s:
            noguard_min = int((time.time() - since) // 60)
    if not old and noguard_min is None:
        if key_f.is_file() and record:
            key_f.unlink(missing_ok=True)  # the incident is over: the next one wakes again
        return "; ".join(["none", *notes]), None
    if sb and sb["active"]:
        return "standby", None
    parts = []
    if old:
        parts.append(f"{len(old)} items unread, oldest {int((time.time() - old[0][0]) // 60)} min")
    if noguard_min is not None:
        parts.append(f"no waiter guard alive for {noguard_min} min")
    what = "; ".join(parts)
    pushable = noguard_min is not None or any(not WAKE_ITEM.search(n) for _, n in old)  # DEC-1089 (3), the stale rule
    key = ("items:" + old[0][1] if old else "") + ("|noguard" if noguard_min is not None else "")
    try:
        state = json.loads(key_f.read_text())
        state = state if isinstance(state, dict) else {}
    except (OSError, ValueError):
        state = {}
    try:
        first = datetime.fromisoformat(state["woken"]) if state.get("woken") else None
    except (TypeError, ValueError):
        first = None
    try:
        raw = Path(a.cto_name_file).read_bytes().decode("utf-8", "replace").strip()
    except OSError:
        raw = ""
    name = raw if NAME_RE.match(raw) else ""
    if first is not None and state.get("key") == key:  # the same incident, the same cause
        if not state.get("pushed") and not name and pushable:  # no name to wake: the owner at once (review F10)
            first = now - timedelta(seconds=a.push_after_s)
        if state.get("pushed") or now - first < timedelta(seconds=a.push_after_s):
            return "; ".join(["woken already", *notes]), None
        if not pushable:
            return "; ".join(["woken already (own items only: no push, DEC-1089 (3))", *notes]), None
        if record:
            key_f.write_text(json.dumps({**state, "pushed": now.isoformat()}))
        if not name:
            line = f"P1 INBOX-WAKE | no valid CTO session name to wake: {what} | read it or restart the CTO"
            return ("would push (no name)" if a.dry else "push (no name)"), line[:200]
        line = f"P1 INBOX-WAKE | the CTO did not answer an inbox wake: {what} | read it or restart the CTO"
        return ("would push" if a.dry else "push"), line[:200]
    # a new incident, or a new cause in the same incident: wake again, keep the incident's first wake time
    keep = first if first is not None and state.get("key") else None
    if not name:
        if record:  # `pushed` only when this branch pushes (review F10)
            kept = {"pushed": state["pushed"]} if keep is not None and state.get("pushed") else {}
            mark = {"pushed": now.isoformat()} if pushable else {}
            key_f.write_text(json.dumps({"key": key, "woken": (keep or now).isoformat(), **kept, **mark}))
        if not pushable:
            return "; ".join(["no valid CTO name (own items only: no push, DEC-1089 (3))", *notes]), None
        line = f"P1 INBOX-WAKE | no valid CTO session name to wake: {what} | read it or restart the CTO"
        return ("would push (no name)" if a.dry else "push (no name)"), line[:200]
    prefix = a.wake_prefix if PREFIX_RE.match(a.wake_prefix or "") else ""
    text = f"{prefix}INBOX WAKE: {what} | re-arm the inbox waiter and the waiter guard"
    if record:
        kept = {"pushed": state["pushed"]} if keep is not None and state.get("pushed") else {}
        key_f.write_text(json.dumps({"key": key, "woken": (keep or now).isoformat(), **kept}))
    if a.dry:
        return "; ".join([f"would wake {name}: {text}", *notes]), None
    if not live:
        return "; ".join([f"would wake {name} (not the live state: no send): {text}", *notes]), None
    return "; ".join([f"woke {name}: {xwake(name, text, key_f.with_name('xwake-cwd'))}", *notes]), None


def check(a, now_s, channels):
    """One look at the watched session; logs and returns the note (ALERT notes carry `line`)."""
    state_path = Path(a.state)
    now = datetime.strptime(now_s, "%Y-%m-%d %H:%M").astimezone() if now_s else datetime.now().astimezone()
    sid = Path(a.session_file).read_text().strip() if Path(a.session_file).is_file() else ""
    if sid and (Path(a.projects) / f"{sid}.jsonl").is_file():
        path = Path(a.projects) / f"{sid}.jsonl"
    else:
        files = sorted(Path(a.projects).glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        if not files:
            sys.exit("no transcript")
        path = files[-1]
    last_a, pending, tool = last_state(path)
    note = {"at": now.strftime("%F %T"), "transcript": path.name, "last_assistant": last_a and last_a.strftime("%F %T"),
            "pending_tool": tool if pending else None}
    sb = standby_state(a.standby, a.standby_max_s, now)
    if sb and not sb["active"]:
        note["standby"] = sb["expired"]  # the note no longer mutes: the normal logic below applies
    if sb and sb["active"]:
        note["verdict"] = "standby: " + sb["text"][:120]
    elif last_a is None:
        note["verdict"] = "no assistant entry"
    else:
        age, limit = now - last_a, NIGHT_LIMIT if quiet(now) else DAY_LIMIT
        note["age_min"] = int(age.total_seconds() // 60)
        try:
            state = json.loads(state_path.read_text())
        except (OSError, ValueError):
            state = {}
        stall = f"{path.name}@{last_a.isoformat()}"
        if age >= WAKE_LIMIT and not a.dry:
            what = (f"waiting on a tool ({tool}) since {last_a:%H:%M}" if pending else f"idle since {last_a:%H:%M}")
            note["wake"] = wake(a, stall, f"DEADMAN WAKE | the CTO session is {what}, {note['age_min']} min", now)
        if age < limit:
            note["verdict"] = "alive"
        elif state.get("stall") == stall and now - datetime.fromisoformat(state["alerted"]) < REMIND:
            note["verdict"] = "stalled, alerted already"
        else:
            what = (f"waiting on a tool ({tool}; likely a permission prompt) since {last_a:%H:%M}" if pending
                    else f"idle since {last_a:%H:%M} (its turn ended and nothing woke it)")
            line = f"P1 DEADMAN | the CTO session is {what}, {note['age_min']} min | approve or restart it"
            if sb:
                line += f" | its stand-by note had {sb['expired']}"
            note["verdict"], note["line"], note["sent"] = "ALERT", line, send(channels, line, a.dry)
            if not a.dry:
                state_path.write_text(json.dumps({"stall": stall, "alerted": now.isoformat()}))
    note["inbox_wake"], inbox_line = inbox_wake(a, sb)
    if inbox_line:
        note["inbox_alert"] = inbox_line
    log = Path(a.log)
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a") as f:
        f.write(json.dumps(note) + "\n")
    return note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--now")
    ap.add_argument("--channel", default="log")  # the push comes from the sentinel session (DEC-998)
    ap.add_argument("--projects", default=str(PROJECTS))
    ap.add_argument("--state", default=str(STATE), help="the stall memory (a replay test uses its own)")
    ap.add_argument("--test", help="send one forced test alert with this label and exit")
    ap.add_argument("--session-file", default=str(SESSION_FILE))
    ap.add_argument("--watch", action="store_true", help="loop until a stall (exit 10) or --max seconds (exit 0)")
    ap.add_argument("--every", type=int, default=120)
    ap.add_argument("--max", type=int, default=6600)
    ap.add_argument("--standby", default=str(STANDBY))
    ap.add_argument("--standby-max-s", type=int, default=STANDBY_MAX_S,
                    help="a stand-by note older than this (its leading UTC time, else its mtime) no longer mutes")
    ap.add_argument("--daily", default="09:05", help="the watch exits with a DAILY line once a day at this time")
    ap.add_argument("--inbox-stale", default=str(INBOX_STALE))
    ap.add_argument("--inbox", help="the wake's inbox (default: the live one for the live state, else beside --state)")
    ap.add_argument("--log", default=str(LOG), help="the decision log (a test or rehearsal names its own)")
    ap.add_argument("--stale-s", type=int, default=1800, help="the dispatcher's stale age for an unread item")
    ap.add_argument("--wake-unread-s", type=int, default=600, help="the inbox wake: an item unread past this wakes the CTO")
    ap.add_argument("--push-after-s", type=int, default=600, help="the inbox wake: still unread this long after it, the owner is pushed")
    ap.add_argument("--cto-name-file", default=str(CTO_NAME_FILE), help="the CTO session's name for the cross-session wake")
    ap.add_argument("--waiter-guard-needle", default=WAITER_GUARD, help="the waiter guard's path as ps shows it")
    ap.add_argument("--guard-grace-s", type=int, default=300, help="the waiter guard missing this long counts (it exits on purpose to wake the CTO)")
    ap.add_argument("--wake-prefix", default="", help="a prefix for the wake's text (a rehearsal names itself)")
    a = ap.parse_args()
    if a.watch:
        start, day0 = time.time(), datetime.now()
        dh, dm = (int(x) for x in a.daily.split(":"))
        while True:
            stale, seen_f = Path(a.inbox_stale), Path(a.state).with_name("deadman-inbox-stale-seen.txt")
            try:  # the dispatcher may remove it between the check and the read (review of 2026-11-01, L3)
                text = stale.read_text() if stale.is_file() else ""
                sb = standby_state(a.standby, a.standby_max_s, datetime.now().astimezone())
                drop = leave_out_inbox_line(stale.parent / "inbox", a.stale_s, bool(sb and sb["active"]))
                kept = [x for x in text.splitlines() if not (x.startswith("inbox:") and drop)]
                line = "\n".join(kept).strip()[:150] or None
            except OSError:
                line = None
            if line:
                if not seen_f.is_file() or seen_f.read_text() != line:
                    seen_f.write_text(line)  # one alert per stall: the file's stable content is the key
                    print(f"ALERT P1 INBOX | the dispatcher's inbox: {line} | read it or restart the CTO", flush=True)
                    sys.exit(10)
            elif seen_f.is_file():
                seen_f.unlink(missing_ok=True)  # the stall is over: the next one alerts again
            note = check(a, None, [])
            if note.get("verdict") == "ALERT":
                print("ALERT " + note["line"], flush=True)
                sys.exit(10)
            if note.get("inbox_alert"):
                print("ALERT " + note["inbox_alert"], flush=True)
                sys.exit(10)
            due = datetime.now().replace(hour=dh, minute=dm, second=0, microsecond=0)
            if day0 < due <= datetime.now():
                print(f"DAILY CTO sentinel alive; the CTO session: {note.get('verdict')}", flush=True)
                sys.exit(0)
            if time.time() - start >= a.max:
                print(f"HEARTBEAT {note.get('verdict')} age {note.get('age_min')} min", flush=True)
                sys.exit(0)
            time.sleep(a.every)
    state_path = Path(a.state)
    if a.test:
        line = f"TEST DEADMAN | {a.test} | no action needed: confirm on your phone that this arrived"
        note = {"at": time.strftime("%F %T"), "verdict": "TEST", "sent": send(a.channel.split(","), line, a.dry)}
        with open(a.log, "a") as f:
            f.write(json.dumps(note) + "\n")
        print(json.dumps(note))
        return
    note = check(a, a.now, a.channel.split(','))
    if note.get("inbox_alert"):
        note["inbox_sent"] = send(a.channel.split(","), note["inbox_alert"], a.dry)
    print(json.dumps(note))



if __name__ == "__main__":
    main()
