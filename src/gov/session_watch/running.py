"""What is running: processes, the session's background agents and tasks, and launched work named by pid files (S2).

``/proc`` is read here only; ``GOV_SESSION_WATCH_PS`` replaces it with a planted list. Work past the 3-hour bound is
named as stale and never counted: a loop that never ends cannot keep idle turns passing silently.
"""

from __future__ import annotations

import glob
import json
import os
import re
import time
from pathlib import Path

from gov.session_watch.state import now

RUN_BOUND_S = 3 * 3600
AGENT_STALE_S = 1800
START_SLACK_S = 900  # a pid file's process counts only if it started no later than this after the file was written
BARE_SLEEP = re.compile(r"^\s*sleep\s+[0-9.]+[smhd]?\s*$")


def processes() -> dict:
    """``{pid: {cmdline, start (epoch), state, fds (set of paths)}}`` for every readable process."""
    fake = os.environ.get("GOV_SESSION_WATCH_PS")
    if fake is not None:
        text = fake if fake.lstrip().startswith("[") else Path(fake).read_text(encoding="utf-8")
        return {int(p["pid"]): {"cmdline": p.get("cmdline", ""), "start": float(p.get("start", 0)),
                                "state": p.get("state", "S"), "fds": set(p.get("fds", []))} for p in json.loads(text)}
    wall, up = time.time(), float(Path("/proc/uptime").read_text().split()[0])  # start: now less the age on the boot clock
    tick, out = os.sysconf("SC_CLK_TCK"), {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        base = f"/proc/{entry}"
        try:
            stat = Path(base, "stat").read_text()
            fields = stat[stat.rindex(")") + 2:].split()
            command = Path(base, "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
        except (OSError, ValueError):
            continue
        fds = set()
        try:
            for fd in os.listdir(base + "/fd"):
                try:
                    fds.add(os.readlink(f"{base}/fd/{fd}"))
                except OSError:
                    continue
        except OSError:
            pass
        out[int(entry)] = {"cmdline": command, "start": wall - (up - int(fields[19]) / tick), "state": fields[0], "fds": fds}
    return out


def alive(procs: dict, pid: int) -> bool:
    found = procs.get(pid)
    return found is not None and found["state"] not in ("Z", "X")


def waiter_alive(procs: dict, commands) -> bool:
    return any(any(c in p["cmdline"] for c in commands) for pid, p in procs.items()
               if alive(procs, pid) and pid != os.getpid())


def folders(data: dict) -> tuple[Path | None, Path | None]:
    """The session's background agents' and tasks' folders: from the environment, else Claude Code's own paths."""
    path, sid = data.get("transcript_path") or "", data.get("session_id") or ""
    agents = os.environ.get("GOV_SESSION_WATCH_SUBAGENTS") or (path[:-6] + "/subagents" if path.endswith(".jsonl") else "")
    tasks = os.environ.get("GOV_SESSION_WATCH_TASKS") or (
        f"/tmp/claude-{os.getuid()}/{Path(path).parent.name}/{sid}/tasks" if path and sid else "")
    return (Path(agents) if agents else None), (Path(tasks) if tasks else None)


def _hours(age: float) -> str:
    return f"{int(age // 3600)} h"


def agents(folder: Path | None, notes: list) -> list:
    """``agent-*.meta.json`` without ``"finished": true`` whose transcript was written in the last 30 minutes."""
    found = []
    for meta in sorted(folder.glob("agent-*.meta.json")) if folder and folder.is_dir() else ():
        try:
            info = json.loads(meta.read_text())
        except (OSError, ValueError) as error:
            notes.append(f"agent meta unreadable {meta.name}: {error}")
            continue
        if not isinstance(info, dict) or info.get("finished"):
            continue
        written = meta.with_name(meta.name[:-len(".meta.json")] + ".jsonl")
        try:
            age = now() - written.stat().st_mtime
        except OSError:
            age = now() - meta.stat().st_mtime
        name = f"agent {info.get('description') or meta.name}"
        if age <= AGENT_STALE_S:
            found.append(name)
        else:
            notes.append(f"{name}: unfinished but silent {int(age // 60)} min (stale, not counted)")
    return found


def tasks(folder: Path | None, procs: dict, standing: tuple, stale: list) -> list:
    """Task output files held open by a live process; a bare ``sleep`` and the standing watchers are not work."""
    held: dict = {}
    for pid, proc in procs.items():
        for fd in proc["fds"] if folder and alive(procs, pid) else ():
            if fd.startswith(f"{folder}/") and not os.path.islink(fd):
                held.setdefault(fd, []).append(pid)
    found = []
    for path, pids in sorted(held.items()):
        command = " ; ".join(procs[p]["cmdline"] for p in sorted(pids))
        inner = re.search(r"eval '(.*?)' < /dev/null", command, re.S)
        command = inner.group(1) if inner else command
        if any(w in command for w in standing) or BARE_SLEEP.match(command):
            continue
        age = now() - min(procs[p]["start"] for p in pids)
        name = f"task {Path(path).stem}: {' '.join(command.split())[:80]}"
        if age > RUN_BOUND_S:
            stale.append(f"{name} {_hours(age)}")
        else:
            found.append(name)
    return found


def pid_files(root: Path, globs, procs: dict, stale: list) -> list:
    """Pid files under ``globs`` whose process is alive, started under 3 hours ago, with no ``<name>.exit`` beside.

    A process that started more than ``START_SLACK_S`` after the file's mtime is a reused pid, not the work the file
    named: it is neither counted nor named (as a dead pid is not); the slack absorbs clock steps."""
    found = []
    for pattern in globs:
        for file in sorted(glob.glob(str(Path(root) / pattern), recursive=True, include_hidden=True)):
            try:
                pid = int(Path(file).read_text().split()[0])
            except (OSError, ValueError, IndexError):
                continue
            if not alive(procs, pid) or os.path.exists(os.path.splitext(file)[0] + ".exit"):
                continue
            try:
                written = os.stat(file).st_mtime
            except OSError:
                continue
            if procs[pid]["start"] > written + START_SLACK_S:  # a reused pid: the process the file named is gone
                continue
            name = f"pid {pid} ({os.path.relpath(file, root)})"
            age = now() - procs[pid]["start"]
            if age > RUN_BOUND_S:
                stale.append(f"{name} {_hours(age)}")
            else:
                found.append(name)
    return found
