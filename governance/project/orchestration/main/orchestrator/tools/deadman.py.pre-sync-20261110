"""The dead-man's switch on the CTO's session (owner, DEC-988 item 4, DEC-991): run by cron every 15 minutes.

    python3 deadman.py [--dry] [--now "YYYY-MM-DD HH:MM"] [--channel toast,push,log] [--projects <dir>]

Reads the newest session transcript in the main repository's Claude Code project folder (never the file's mtime:
queued notifications keep writing it during a freeze) and finds its last `assistant` entry. It alerts when that is
older than 60 minutes (inside the quiet hours, 02:00 to 07:30, only past 2 hours), saying "waiting on a tool (likely
a permission prompt) since HH:MM" when the last entry is a tool call with no result, else "idle since HH:MM". One
alert per stall, then a reminder every 2 hours while it lasts (state in log/deadman-state.json). Channels: `toast`
(a Windows notification on the PC, no install), `push` (a headless `claude -p` call to PushNotification, which reaches
the phone through Remote Control when the PC is not in use), `log` (~/.config/gov-os-notify/pings.log). Every
decision is appended to log/deadman.log. It never reads or prints a transcript's text beyond entry types and times.
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECTS = Path.home() / ".claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS"
ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
STATE = ORCH / "log/deadman-state.json"
LOG = ORCH / "log/deadman.log"
PINGS = Path.home() / ".config/gov-os-notify/pings.log"
TOAST = ORCH / "tools/win_toast.ps1"
PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
DAY_LIMIT, NIGHT_LIMIT, REMIND = timedelta(minutes=60), timedelta(hours=2), timedelta(hours=2)


def quiet(t):
    hm = t.hour * 60 + t.minute
    return 2 * 60 <= hm < 7 * 60 + 30


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone()


def last_state(path, tail=4_000_000):
    """(last assistant time, whether it is a tool call with no result after it, the tool name)."""
    with open(path, "rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - tail))
        lines = f.read().decode("utf-8", "replace").splitlines()[1:]
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--now")
    ap.add_argument("--channel", default="toast,push,log")
    ap.add_argument("--projects", default=str(PROJECTS))
    a = ap.parse_args()
    now = datetime.strptime(a.now, "%Y-%m-%d %H:%M").astimezone() if a.now else datetime.now().astimezone()
    files = sorted(Path(a.projects).glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not files:
        sys.exit("no transcript")
    path = files[-1]
    last_a, pending, tool = last_state(path)
    note = {"at": now.strftime("%F %T"), "transcript": path.name, "last_assistant": last_a and last_a.strftime("%F %T"),
            "pending_tool": tool if pending else None}
    if last_a is None:
        note["verdict"] = "no assistant entry"
    else:
        age, limit = now - last_a, NIGHT_LIMIT if quiet(now) else DAY_LIMIT
        note["age_min"] = int(age.total_seconds() // 60)
        try:
            state = json.loads(STATE.read_text())
        except (OSError, ValueError):
            state = {}
        stall = f"{path.name}@{last_a.isoformat()}"
        if age < limit:
            note["verdict"] = "alive"
        elif state.get("stall") == stall and now - datetime.fromisoformat(state["alerted"]) < REMIND:
            note["verdict"] = "stalled, alerted already"
        else:
            what = (f"waiting on a tool ({tool}; likely a permission prompt) since {last_a:%H:%M}" if pending
                    else f"idle since {last_a:%H:%M} (its turn ended and nothing woke it)")
            line = f"P1 DEADMAN | the CTO session is {what}, {note['age_min']} min | approve or restart it"
            note["verdict"], note["sent"] = "ALERT", send(a.channel.split(","), line, a.dry)
            if not a.dry:
                STATE.write_text(json.dumps({"stall": stall, "alerted": now.isoformat()}))
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps(note) + "\n")
    print(json.dumps(note))


if __name__ == "__main__":
    main()
