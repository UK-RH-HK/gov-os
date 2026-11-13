"""``gov session-watch helper-watch``: an inbox item when a helper of the registered session, or a launched worker, dies or
goes silent (DEC-1112 (3), DEC-1073 (4)).

KPI map
-------
- S3 the conditions, once each: ``_helpers`` (a helper whose last entry is an API or network error, or which is not
  finished and wrote nothing for ``--stale-min`` minutes), ``_workers`` (a pid file whose job is gone without its exit
  file, or whose exit file holds a non-zero code or an error in its result), ``_pass`` (the state file that only grows,
  one item per new condition, ``_item`` opened with ``x``), ``run`` (the loop and the one "ended" line).
- S4 names, times and error codes only: ``_describe`` takes entry types, tool names and error codes (a name that is not
  a plain word is shown as ``?``) and the client's fixed synthetic error text, never a message's own text; the pid is
  asked of ``gov.wait.liveness`` alone; only the inbox, ``helper-watch-state.json`` and ``helper-watch.log`` are
  written, each by a plain open (no temporary or lock file); a transcript or pid file older than ``--window-h`` is skipped.

Environment: ``GOV_SESSION_WATCH_NOW`` (epoch seconds, the clock) and ``GOV_SESSION_WATCH_SUBAGENTS`` (the helpers'
folder), as for the Stop checks.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TAIL = 1_000_000
NAMES = re.compile(r"[\w.:+\-]{1,60}")
FOLDER = Path(".gov-runtime") / "session-watch"
INBOX = Path(".gov-runtime") / "dispatch" / "inbox"


def _name(value) -> str:
    """A plain word (a type, a tool, a code, a time) as it is; anything else, which could be text, as ``?``."""
    text = str(value)
    return text if isinstance(value, (str, int, float)) and NAMES.fullmatch(text) else "?"


def _epoch(value) -> float | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc).timestamp()
    except ValueError:
        return None


def _entries(path: Path) -> list[dict]:
    with open(path, "rb") as stream:
        stream.seek(0, 2)
        start = max(0, stream.tell() - TAIL)
        stream.seek(start)
        lines = stream.read().decode("utf-8", "replace").splitlines()[1 if start else 0:]
    found = []
    for line in lines:
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict):
            found.append(entry)
    return found


def _describe(entry: dict | None) -> str:
    """The last line, from names and times only (and the client's fixed text of a synthetic API-error entry)."""
    if entry is None:
        return "no entry"
    message = entry.get("message") if isinstance(entry.get("message"), dict) else {}
    content = message.get("content")
    head = f"{_name(entry.get('type'))} at {_name(entry.get('timestamp'))}"
    if entry.get("isApiErrorMessage") or entry.get("apiError"):
        fixed = ""
        if message.get("model") == "<synthetic>" and isinstance(content, list):
            fixed = " ".join(" ".join(str(p.get("text", "")).split()) for p in content if isinstance(p, dict))[:120]
        return f"{head} (API error {_name(entry.get('apiError'))}/{_name(entry.get('error'))}: {fixed})"
    if isinstance(content, list):
        kinds = [_name(p.get("type")) + (f" {_name(p.get('name'))}" if p.get("type") == "tool_use" else "")
                 for p in content if isinstance(p, dict) and p.get("type")]
        return f"{head} ({', '.join(kinds)})" if kinds else head
    return head


def _session(root: Path) -> str:
    try:
        return (root / FOLDER / "session.txt").read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return ""


def _helpers_folder(root: Path, session: str) -> Path:
    given = os.environ.get("GOV_SESSION_WATCH_SUBAGENTS")
    if given:
        return Path(given)
    mangled = re.sub(r"[^A-Za-z0-9\-]", "-", os.path.abspath(root))
    return Path.home() / ".claude" / "projects" / mangled / session / "subagents"


def _helpers(root: Path, now: float, args) -> list[tuple]:
    session = _session(root)
    folder = _helpers_folder(root, session) if session else None
    if folder is None or not folder.is_dir():
        return []
    found = []
    for path in sorted(folder.glob("agent-*.jsonl")):
        ident = path.stem[len("agent-"):]
        try:
            meta = json.loads(path.with_name(f"agent-{ident}.meta.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            meta = {}
        meta = meta if isinstance(meta, dict) else {}
        try:
            entries = _entries(path)
            fallback = path.stat().st_mtime
        except OSError:
            continue
        times = [t for t in (_epoch(e.get("timestamp")) for e in entries if e.get("timestamp")) if t is not None]
        last_time = max(times) if times else fallback
        if now - last_time > args.window_h * 3600:
            continue
        last = next((e for e in reversed(entries) if e.get("type") in ("assistant", "user", "system")), None)
        label = " ".join(f"{meta.get('description', '?')}".split())[:80]
        name = f"helper {ident} ({label}, {_name(meta.get('agentType', '?'))})"
        if last is not None and (last.get("isApiErrorMessage") or last.get("apiError")):
            found.append((f"h:{ident}:api-error", f"api-error@{_name(last.get('timestamp'))}", "api-error",
                          f"{name} stopped on an API or network error", _describe(last), str(path)))
        elif not meta.get("finished") and now - last_time >= args.stale_min * 60:
            minutes = int((now - last_time) // 60)
            found.append((f"h:{ident}:stalled", f"stalled@{int(last_time)}", "stalled",
                          f"{name} is not finished and has had no new entry for {minutes} min", _describe(last),
                          str(path)))
    return found


def _result(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    for line in reversed(text.splitlines()):
        if line.strip().startswith("{"):
            try:
                found = json.loads(line)
            except ValueError:
                continue
            return found if isinstance(found, dict) else {}
    return {}


def _workers(root: Path, now: float, since: float, args, patterns: tuple) -> list[tuple]:
    from gov.wait import liveness

    found = []
    for pattern in patterns:
        for name in sorted(glob.glob(str(root / pattern), recursive=True)):
            pid_file = Path(name)
            try:
                modified = pid_file.stat().st_mtime
            except OSError:
                continue
            pid = liveness.read_pid(pid_file)
            if now - modified > args.window_h * 3600 or pid is None:
                continue
            base = str(pid_file)[:-len(".pid")]
            exit_file, log = Path(base + ".exit"), base + ".json"
            who = f"launched worker {Path(base).name} (pid {pid}, {pid_file.parent})"
            try:
                code = exit_file.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0].strip()
                ended = exit_file.stat().st_mtime
            except OSError:
                code, ended = "", 0.0
            if not code:  # no exit file yet, or an empty one: the job has not ended by its own account
                if liveness.gone(pid):
                    found.append((f"w:{pid_file}:gone", f"gone@{pid}", "worker gone",
                                  f"{who} is gone without its exit file", f"no exit file; its log: {log}",
                                  str(pid_file)))
                continue
            if ended < since:
                continue
            result = _result(Path(log))
            bad = [f"{k} {result[k] if isinstance(result[k], (bool, int)) else 'set'}"
                   for k in ("is_error", "api_error_status") if result.get(k)]
            if not (code.isascii() and code.isdigit() and int(code) == 0) or bad:
                found.append((f"w:{pid_file}:error", f"exit@{int(ended)}", "worker ended with an error",
                              f"{who} ended with exit {_name(code)}", ", ".join(bad) or "no error in its JSON result",
                              log))
    return found


def _item(inbox: Path, stamp: str, kind: str, status: str, last: str, where: str) -> Path:
    inbox.mkdir(parents=True, exist_ok=True)
    number, path = 1, inbox / f"{stamp}-helper-watch.txt"
    while True:
        try:
            with open(path, "x", encoding="utf-8") as stream:
                stream.write(f"log: helper-watch.log\nHelper: {kind}\nstatus: {status}\nlast: {last}\n\nfile: {where}\n"
                             "Check it and resume it (SendMessage to the agent id, or a fresh session from its brief).\n")
            return path
        except FileExistsError:
            number += 1
            path = inbox / f"{stamp}-helper-watch-{number}.txt"


def _pass(root: Path, now: float, since: float, args, patterns: tuple) -> list[Path]:
    """One look: write an item for each condition the state file has not got, then grow the state and the log."""
    state_file = root / FOLDER / "helper-watch-state.json"
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    state = state if isinstance(state, dict) else {}
    found = _helpers(root, now, args) + _workers(root, now, since, args, patterns)
    grown, written = dict(state), []
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime(now))
    for key, event, kind, status, last, where in found:
        grown[key] = event  # a condition is never forgotten: its key stays, so no item is sent twice
        if state.get(key) != event:
            written.append(_item(root / INBOX, stamp, kind, status, last, where))
    (root / FOLDER).mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(grown), encoding="utf-8")
    at = datetime.fromtimestamp(now, timezone.utc).isoformat()
    with open(root / FOLDER / "helper-watch.log", "a", encoding="utf-8") as stream:
        stream.write(json.dumps({"at": at, "conditions": len(found), "items": [p.name for p in written]}) + "\n")
    return written


def run(root: Path, args) -> int:
    from gov.session_watch import config, state

    root = Path(root)
    try:
        patterns = config.load(root).pid_globs
    except config.ConfigError as error:
        print(f"gov session-watch helper-watch: {error}", file=sys.stderr)
        return 1
    began = time.time()
    since = state.now() - args.every
    total = 0
    while True:
        written = _pass(root, state.now(), since, args, patterns)
        total += len(written)
        for path in written:
            print(f"HELPER_WATCH item {path}", flush=True)
        if args.once:
            return 0
        if time.time() - began >= args.max:
            print(f"HELPER_WATCH ended after {int(time.time() - began)} s; {total} item(s) written; re-arm it", flush=True)
            return 0
        time.sleep(min(args.every, max(0.0, args.max - (time.time() - began))))
