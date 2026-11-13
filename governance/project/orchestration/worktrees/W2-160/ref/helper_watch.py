#!/usr/bin/env python3
"""The helper watch (DAEO-sdxk, 2026-11-10; DEC-1112 (3)): the CTO arms it in the background beside its inbox waiter.

    python3 helper_watch.py [--every 300] [--max 86400] [--stale-min 30] [--window-h 24]
                            [--projects <dir>] [--session <id>] [--workers-glob <glob> ...] [--once] [--now <ISO>]

Why: on 2026-11-10 a short network fault (EAI_AGAIN, 02:19 to 02:26 UTC) killed two of the CTO's in-session helpers;
their failure notices did not wake the CTO, which sat idle for 7 hours. Every --every seconds this looks at:
  - each in-session helper of the CTO session (the id in log/cto-session.txt):
    ~/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS/<id>/subagents/agent-*.jsonl, with its .meta.json.
    A helper whose last entry is an API or network error (isApiErrorMessage / apiError), or which is not finished
    (no "finished": true in its meta) and whose transcript has had no new entry for --stale-min minutes;
  - each launched worker it can find by pid file (launch_worker.sh's <base>.pid, default under
    ~/gov-os-worktrees/*/.gov-runtime/scratch/lead/log/): one gone without its <base>.exit (asked of tools/proc.sh by
    that pid only), or one whose exit file appeared since the watch started with a non-zero code or an error in its
    JSON result (is_error, api_error_status).
Each such condition gives one inbox item, dispatch/inbox/<stamp>-helper-watch.txt, naming the agent id (or the worker's
log) and its last line, once per condition (state in log/helper-watch-state.json); the CTO's inbox waiter wakes the CTO.
Only transcripts whose last entry is within --window-h hours are looked at.

It reads names and timestamps only: entry types, times, tool names, the error codes and the fixed text of a synthetic
API-error entry; never a message's own text. It never matches a process by name (L-0075, DEC-1073 (4)) and is no
Monitor: it runs as a Bash background run and writes only into the CTO's inbox and its own state and log. It keeps
running after an item (the inbox waiter does the waking) and ends after --max seconds with one line, HELPER_WATCH
ended ..., so the CTO re-arms it. ORCH (environment) moves the scratch root, for tests and rehearsals.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ORCH = Path(os.environ.get("ORCH") or "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
PROJECTS = Path.home() / ".claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS"
WORKERS = "/home/usain/gov-os-worktrees/*/.gov-runtime/scratch/lead/log/*.pid"
PROC = Path(os.environ.get("HELPER_PROC") or Path(__file__).resolve().parent / "proc.sh")
TAIL = 1_000_000


def ts(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def tail_entries(path):
    with open(path, "rb") as f:
        f.seek(0, 2)
        start = max(0, f.tell() - TAIL)
        f.seek(start)
        lines = f.read().decode("utf-8", "replace").splitlines()[1 if start else 0:]
    out = []
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if isinstance(e, dict):
            out.append(e)
    return out


def describe(e):
    """The last line, from names and timestamps only."""
    if e is None:
        return "no entry"
    m = e.get("message") if isinstance(e.get("message"), dict) else {}
    c = m.get("content")
    head = f"{e.get('type')} at {e.get('timestamp')}"
    if e.get("isApiErrorMessage") or e.get("apiError"):
        text = ""
        if m.get("model") == "<synthetic>" and isinstance(c, list):  # the client's own fixed error text
            text = " ".join(x.get("text", "") for x in c if isinstance(x, dict))[:120]
        return f"{head} (API error {e.get('apiError')}/{e.get('error')}: {text})"
    if isinstance(c, list):
        kinds = [x.get("type") + (f" {x.get('name')}" if x.get("type") == "tool_use" else "")
                 for x in c if isinstance(x, dict) and x.get("type")]
        return f"{head} ({', '.join(kinds)})" if kinds else head
    return head


def helpers(a, now, state):
    found = []
    sid = a.session or ((ORCH / "log/cto-session.txt").read_text().strip()
                        if (ORCH / "log/cto-session.txt").is_file() else "")
    folder = Path(a.projects) / sid / "subagents"
    if not sid or not folder.is_dir():
        return found
    for path in sorted(folder.glob("agent-*.jsonl")):
        aid = path.stem[len("agent-"):]
        try:
            meta = json.loads(path.with_name(f"agent-{aid}.meta.json").read_text())
        except (OSError, ValueError):
            meta = {}
        entries = tail_entries(path)
        times = [t for t in (ts(e.get("timestamp")) for e in entries if e.get("timestamp")) if t]
        last_t = max(times) if times else datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        if now - last_t > timedelta(hours=a.window_h):
            continue
        last = next((e for e in reversed(entries) if e.get("type") in ("assistant", "user", "system")), None)
        name = f"helper {aid} ({meta.get('description', '?')}, {meta.get('agentType', '?')})"
        if last is not None and (last.get("isApiErrorMessage") or last.get("apiError")):
            found.append((f"h:{aid}", f"api-error@{last.get('timestamp')}", "api-error",
                          f"{name} stopped on an API or network error", describe(last), str(path)))
        elif not meta.get("finished") and now - last_t >= timedelta(minutes=a.stale_min):
            mins = int((now - last_t).total_seconds() // 60)
            found.append((f"h:{aid}", f"stalled@{last_t.isoformat()}", "stalled",
                          f"{name} is not finished and has had no new entry for {mins} min", describe(last),
                          str(path)))
    return found


def gone(pid):
    """True when the pid has exited: asked of proc.sh by pid only (exit 0 gone, 124 running)."""
    r = subprocess.run(["bash", str(PROC), "wait", "--max", "0", "--every", "1", str(pid)], capture_output=True,
                       timeout=30)
    return r.returncode == 0


def json_result(path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    for raw in reversed(text.splitlines()):
        if raw.strip().startswith("{"):
            try:
                d = json.loads(raw)
                return d if isinstance(d, dict) else {}
            except ValueError:
                continue
    return {}


def workers(a, now, since):
    import glob
    found = []
    for g in a.workers_glob or [WORKERS]:
        for p in sorted(glob.glob(g)):
            pid_f = Path(p)
            try:
                mt = datetime.fromtimestamp(pid_f.stat().st_mtime, timezone.utc)
                pid = "".join(ch for ch in pid_f.read_text()[:20] if ch.isdigit())
            except OSError:
                continue
            if now - mt > timedelta(hours=a.window_h) or not pid:
                continue
            base = Path(str(pid_f)[:-len(".pid")])
            ex = base.with_name(base.name + ".exit")
            name = f"launched worker {base.name} (pid {pid}, {base.parent})"
            if not ex.exists():
                if gone(pid):
                    found.append((f"w:{pid_f}", f"gone@{pid}", "worker gone", f"{name} is gone without its exit file",
                                  "no exit file; its log: " + str(base) + ".json", str(pid_f)))
                continue
            try:
                code, emt = ex.read_text().strip(), datetime.fromtimestamp(ex.stat().st_mtime, timezone.utc)
            except OSError:
                continue
            if emt < since:
                continue
            r = json_result(base.with_name(base.name + ".json"))
            bad = [f"{k} {r[k]}" for k in ("is_error", "api_error_status") if r.get(k)]
            if code != "0" or bad:
                found.append((f"w:{pid_f}", f"exit@{emt.isoformat()}", "worker ended with an error",
                              f"{name} ended with exit {code}", ", ".join(bad) or "no error in its JSON result",
                              str(base) + ".json"))
    return found


def item(kind, status, last, where):
    box = ORCH / "dispatch/inbox"
    box.mkdir(parents=True, exist_ok=True)
    stamp, n = time.strftime("%Y%m%d-%H%M%S"), 1
    path = box / f"{stamp}-helper-watch.txt"
    while True:
        try:
            with open(path, "x") as f:
                f.write(f"log: helper-watch.log\nHelper: {kind}\nstatus: {status}\nlast: {last}\n\nfile: {where}\n"
                        "Check it and resume it (SendMessage to the agent id, or a fresh session from its brief).\n")
            return path
        except FileExistsError:
            n += 1
            path = box / f"{stamp}-helper-watch-{n}.txt"


def once(a, now, since):
    sf = ORCH / "log/helper-watch-state.json"
    try:
        state = json.loads(sf.read_text())
    except (OSError, ValueError):
        state = {}
    found = helpers(a, now, state) + workers(a, now, since)
    # DEC-1140 (1)(a): a reported condition is never forgotten (each condition string carries its own event time), so a
    # second instance or a condition that drops out of one pass cannot re-send the same item; the state only grows
    new, written = dict(state), []
    for key, cond, kind, status, last, where in found:
        new[key] = cond
        if state.get(key) != cond:
            written.append(item(kind, status, last, where))
    sf.parent.mkdir(parents=True, exist_ok=True)
    sf.write_text(json.dumps(new))
    with open(ORCH / "log/helper-watch.log", "a") as f:
        f.write(json.dumps({"at": now.isoformat(), "conditions": len(found), "items": [p.name for p in written]})
                + "\n")
    for p in written:
        print(f"HELPER_WATCH item {p}", flush=True)
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--every", type=int, default=300)
    ap.add_argument("--max", type=int, default=86400)
    ap.add_argument("--stale-min", type=int, default=30)
    ap.add_argument("--window-h", type=float, default=24)
    ap.add_argument("--projects", default=str(PROJECTS))
    ap.add_argument("--session")
    ap.add_argument("--workers-glob", action="append")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--now", help="ISO time (tests); default the clock")
    a = ap.parse_args()
    start = time.time()
    clock = (lambda: ts(a.now)) if a.now else (lambda: datetime.now(timezone.utc))
    since = clock() - timedelta(seconds=a.every)
    total = 0
    while True:
        total += len(once(a, clock(), since))
        if a.once:
            return
        if time.time() - start >= a.max:
            print(f"HELPER_WATCH ended after {int(time.time() - start)} s; {total} item(s) written; re-arm it",
                  flush=True)
            return
        time.sleep(a.every)


if __name__ == "__main__":
    main()
