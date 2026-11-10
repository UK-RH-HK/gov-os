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
the watch leaves out an `inbox:` line whose oldest item is one of the CTO's own wake items (-deadman-wake,
-helper-watch, -spend-brake): their staleness never brings a push forward; the stall's own ALERT stays the backstop.
ORCH (environment) moves the whole scratch root, for rehearsals.
"""
import argparse
import json
import os
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
STANDBY = ORCH / "log/cto-standby.txt"  # while it exists, the CTO stands by on purpose: no alert (DEC-998)
# The dispatcher writes this file while an inbox item has been unread 30 minutes (the owner, 2026-11-01); its
# content is stable for one stall, so the watch alerts once per stall. It also alerts during a CTO stand-by (intended).
INBOX_STALE = ORCH / "dispatch/inbox-stale.txt"
LOG = ORCH / "log/deadman.log"
PINGS = Path.home() / ".config/gov-os-notify/pings.log"
TOAST = TOOLS_DIR / "win_toast.ps1"
PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
DAY_LIMIT, NIGHT_LIMIT, REMIND = timedelta(minutes=60), timedelta(hours=2), timedelta(hours=2)
WAKE_LIMIT = timedelta(minutes=60)  # the wake, at any hour (DEC-1112 (3)); the push keeps the owner's limits above
WAKE_ONLY = ("-deadman-wake", "-helper-watch", "-spend-brake")  # the CTO's own wake items: no push on their staleness


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
                r = subprocess.run([str(Path.home() / ".local/bin/claude"), "-p", "--model", "claude-haiku-5-5",
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
    except (OSError, ValueError):
        pass
    box = inbox_dir(a)
    try:
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
        key_f.write_text(json.dumps({"stall": stall, "woken": now.isoformat(), "item": item.name}))
        return str(item)
    except OSError as exc:
        return f"wake failed {exc.__class__.__name__}"


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
    if Path(a.standby).is_file():
        note["verdict"] = "standby: " + Path(a.standby).read_text().strip()[:120]
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
            note["verdict"], note["line"], note["sent"] = "ALERT", line, send(channels, line, a.dry)
            if not a.dry:
                state_path.write_text(json.dumps({"stall": stall, "alerted": now.isoformat()}))
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
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
    ap.add_argument("--daily", default="09:05", help="the watch exits with a DAILY line once a day at this time")
    ap.add_argument("--inbox-stale", default=str(INBOX_STALE))
    ap.add_argument("--inbox", help="the wake's inbox (default: the live one for the live state, else beside --state)")
    a = ap.parse_args()
    if a.watch:
        start, day0 = time.time(), datetime.now()
        dh, dm = (int(x) for x in a.daily.split(":"))
        while True:
            stale, seen_f = Path(a.inbox_stale), Path(a.state).with_name("deadman-inbox-stale-seen.txt")
            try:  # the dispatcher may remove it between the check and the read (review of 2026-11-01, L3)
                text = stale.read_text() if stale.is_file() else ""
                kept = [x for x in text.splitlines()  # the CTO's own wake items never push on staleness
                        if not (x.startswith("inbox:") and any(w in x for w in WAKE_ONLY))]
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
        with open(LOG, "a") as f:
            f.write(json.dumps(note) + "\n")
        print(json.dumps(note))
        return
    note = check(a, a.now, a.channel.split(','))
    print(json.dumps(note))



if __name__ == "__main__":
    main()
