"""The CTO's idle check, a Stop hook (owner, DEC-1110 (1); DEC-1109 (3), DEC-936 item 2): a turn does not end idle.

Claude Code runs it when a session is about to end a turn. For the CTO's registered session (`log/cto-session.txt`)
it answers "block" when nothing of the CTO's is running while DECIDED-NOT-DONE shows unblocked items, naming them;
it lets a legitimate wait through and names which. In order:

1. The bound. It blocks at most once per turn: never when `stop_hook_active` is set (the turn already continued
   for a Stop hook), never twice for the same turn (kept in `log/stop-idle-state.json`). A turn starts at a user
   entry that is not a tool result and not meta, or at any user entry carrying `turnOrigin` or `wakeupSource` (a
   scheduled wakeup is meta but starts a turn). A line `IDLE-REASON: <why>` in the CTO's messages of this turn lets
   it end; the line is recorded in `log/stop-idle.log` and shown to the owner. Neither a block nor a reason carries
   into the next turn.
2. Running, any of (each named in the log):
   - the session's background agents: `<transcript>/subagents/agent-*.meta.json` without `"finished": true`
     whose transcript was written in the last 30 minutes (Claude Code's own flag; an older unfinished one is named
     as stale and not counted);
   - the session's background Bash tasks: `/tmp/claude-<uid>/<project>/<session>/tasks/*.output` held open by a
     live process started less than 3 hours ago, except the standing watchers (the inbox waiter, the sentinel
     check, the usage log, the daily store refresh, the bare-repository watch, a bare `sleep N` timer);
   - the launched workers, verifications, landing selections and runs: a pid file (launch_worker.sh's
     `<tree>/.gov-runtime/scratch/lead/log/*.pid`, lead_verify.sh's `verify.pid`, landing_select.sh's `run.pid`,
     `~/gov-os-runs/**.pid`) whose process is alive, started less than 3 hours ago, and started no later than the
     file was written (a reused pid is not counted), and whose `<name>.exit` is absent;
   - a task or pid file past the 3-hour bound is not counted and is named, in the block and in any let-through
     message (a loop that never ends cannot keep idle turns passing silently; launched workers took at most 1.75 h
     over 84 runs);
   - the dispatcher (`dispatch/status.json`, the same tick as `status.txt`, at most 5 minutes old): leads,
     launches pending, jobs by phase, a close or a landing running.
3. A legitimate wait, from the same dispatcher tick: the gate shut (the gate or the disk gate) or the machine full
   (admission refused or the lead forecast refusing).
4. DECIDED-NOT-DONE's tracking tables (every `## 0<letter>.` section). The state is split at its first WAIT word
   into a head and the wait. Open (unblocked; nothing runs, so nothing runs for it): the head holds NOT STARTED, IN
   PROGRESS, DUE NOW or a pending step (`next`, or `; then` / `: then`). Else a wait, when there is a WAIT word (on
   the owner, a running job, or a trigger). Else closed only when the state begins DONE, MERGED, APPLIED, STANDING,
   SUPERSEDED or CLOSED. Anything else (READY, APPROVED, FILED, ANSWERED, an unknown word) is open: a block is
   bounded, so the check errs toward the reminder. No unblocked item: every open item waits, named with its counts.
   Otherwise: block, naming the unblocked items.

A cto-standby.txt does not let a turn end idle here (DEC-1109 (3): unblocked work moves while the owner decides).
It never fails open silently: an error is named to the owner (`systemMessage`) and in the log, and the turn ends.
It always exits 0 and prints at most one JSON object. Standard library only.
Overrides for tests: GOV_STOPIDLE_ORCH, GOV_STOPIDLE_DND, GOV_STOPIDLE_TASKS, GOV_STOPIDLE_SUBAGENTS,
GOV_STOPIDLE_PROC (a JSON list of {pid, cmdline, start, state, fds} instead of /proc), GOV_STOPIDLE_PIDGLOBS
(globs joined by ':'), GOV_STOPIDLE_NOW (epoch seconds).
"""
import glob
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # <repo>/governance/project/orchestration/tools/stop_idle_check.py
HOME = Path.home()
ORCH = Path(os.environ.get("GOV_STOPIDLE_ORCH") or ROOT / ".gov-runtime/scratch/orchestrator")
DND = Path(os.environ.get("GOV_STOPIDLE_DND")
           or ROOT / "governance/project/orchestration/packages/DECIDED-NOT-DONE.md")
LOG = ORCH / "log/stop-idle.log"
STATE = ORCH / "log/stop-idle-state.json"
AGENT_STALE_S = 1800
STATUS_MAX_AGE_S = 300
WATCHERS = ("inbox_wait.sh", "inbox_wait_quiet.sh", "sentinel_check.sh", "usage_log.sh", "store_refresh_daily.sh",
            "bare_watch.sh")
LAUNCHERS = ("launch_worker.sh --run", "lead_verify.sh", "landing_select.sh")
START_SLACK_S = 900
RUN_BOUND_S = 3 * 3600
BARE_SLEEP = re.compile(r"^\s*sleep\s+[0-9.]+[smhd]?\s*$")
REASON_LINE = re.compile(r"^\s*IDLE-REASON:\s*(\S.*?)\s*$", re.M)
OPEN_WORDS = re.compile(r"\b(NOT STARTED|IN PROGRESS|DUE NOW)\b")  # the states, in capitals; not prose
NEXT_STEP = re.compile(r"\bnext\b|[;:]\s*then\b", re.I)
WAIT_WORD = re.compile(r"\bWAITS?\b", re.I)
FINAL_WORDS = re.compile(r"^(DONE|MERGED|APPLIED|STANDING|SUPERSEDED|CLOSED)\b", re.I)
SECTION = re.compile(r"^## 0[a-z]?\.\s")
SHOW_MAX = 15


class CheckError(Exception):
    """A reading the check depends on failed: named, logged, and the turn ends."""


def now():
    return float(os.environ.get("GOV_STOPIDLE_NOW") or time.time())


# ------------------------------------------------------------------------------------------------------- processes
def processes():
    """Every readable process: {pid: {"cmdline", "start" (epoch), "state", "fds" (set of paths)}}."""
    fake = os.environ.get("GOV_STOPIDLE_PROC")
    if fake:
        return {int(p["pid"]): {"cmdline": p.get("cmdline", ""), "start": float(p.get("start", 0)),
                                "state": p.get("state", "S"), "fds": set(p.get("fds", []))}
                for p in json.loads(Path(fake).read_text())}
    # A process's start on the wall clock: now less its age on the boot clock (WSL's btime drifts by minutes).
    wall, up = time.time(), float(Path("/proc/uptime").read_text().split()[0])
    tick = os.sysconf("SC_CLK_TCK")
    out = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        base = f"/proc/{entry}"
        try:
            stat = Path(base, "stat").read_text()
            fields = stat[stat.rindex(")") + 2:].split()
            cmd = Path(base, "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
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
        out[int(entry)] = {"cmdline": cmd, "start": wall - (up - int(fields[19]) / tick), "state": fields[0], "fds": fds}
    return out


def alive(procs, pid):
    p = procs.get(pid)
    return p is not None and p["state"] not in ("Z", "X")


# --------------------------------------------------------------------------------------------------------- running
def session_dirs(data):
    tp = data.get("transcript_path") or ""
    sid = data.get("session_id") or ""
    sub = os.environ.get("GOV_STOPIDLE_SUBAGENTS") or (tp[:-6] + "/subagents" if tp.endswith(".jsonl") else "")
    tasks = os.environ.get("GOV_STOPIDLE_TASKS")
    if not tasks and tp:
        tasks = f"/tmp/claude-{os.getuid()}/{Path(tp).parent.name}/{sid}/tasks"
    return Path(sub) if sub else None, Path(tasks) if tasks else None


def running_agents(sub, notes):
    found = []
    if sub is None or not sub.is_dir():
        return found
    for meta in sorted(sub.glob("agent-*.meta.json")):
        try:
            m = json.loads(meta.read_text())
        except (OSError, ValueError) as exc:
            notes.append(f"agent meta unreadable {meta.name}: {exc}")
            continue
        if m.get("finished"):
            continue
        tr = meta.with_name(meta.name[:-len(".meta.json")] + ".jsonl")
        try:
            age = now() - tr.stat().st_mtime
        except OSError:
            age = now() - meta.stat().st_mtime
        name = f"agent {m.get('description') or meta.name}"
        if age <= AGENT_STALE_S:
            found.append(name)
        else:
            notes.append(f"{name}: unfinished but silent {int(age // 60)} min (stale, not counted)")
    return found


def task_command(pids, procs):
    for pid in pids:
        cmd = procs[pid]["cmdline"]
        m = re.search(r"eval '(.*?)' < /dev/null", cmd, re.S)
        if m:
            return m.group(1)
    return " ; ".join(procs[p]["cmdline"] for p in pids)


def over(age):
    return f"{int(age // 3600)} h"


def running_tasks(tasks, procs, past):
    found = []
    if tasks is None or not tasks.is_dir():
        return found
    holders = {}
    for pid, p in procs.items():
        if not alive(procs, pid):
            continue
        for fd in p["fds"]:
            if fd.startswith(str(tasks) + "/"):
                holders.setdefault(fd, []).append(pid)
    for path, pids in sorted(holders.items()):
        if os.path.islink(path):
            continue
        cmd = task_command(sorted(pids), procs)
        if any(w in cmd for w in WATCHERS) or BARE_SLEEP.match(cmd):
            continue
        short = re.sub(r"(?<![\w.-])/(?:[^\s/'\"]+/)+", "", " ".join(cmd.split()))
        age = now() - min(procs[p]["start"] for p in pids)
        if age > RUN_BOUND_S:
            past.append(f"task {Path(path).stem} {over(age)}: {short[:60]}")
            continue
        found.append(f"task {Path(path).stem}: {short[:80]}")
    return found


def pid_globs():
    env = os.environ.get("GOV_STOPIDLE_PIDGLOBS")
    if env is not None:
        return [g for g in env.split(":") if g]
    wt = HOME / "gov-os-worktrees"
    return [str(wt / "*/.gov-runtime/scratch/lead/log/*.pid"), str(wt / "*/.gov-runtime/scratch/lead/log/*/*.pid"),
            str(ROOT / ".gov-runtime/scratch/lead/log/*.pid"), str(ORCH / "log/landing-select/*/run.pid"),
            str(HOME / "gov-os-runs/*/*.pid"), str(HOME / "gov-os-runs/*/*/*.pid")]


def running_pidfiles(procs, past):
    found = []
    for pattern in pid_globs():
        for f in sorted(glob.glob(pattern)):
            try:
                pid = int(Path(f).read_text().split()[0])
                written = os.stat(f).st_mtime
            except (OSError, ValueError, IndexError):
                continue
            if not alive(procs, pid):
                continue
            # A reused pid (pid_max wraps here in days) started long after the file was written, unless it is one of
            # the launchers, which is running work whichever file named it; the slack absorbs WSL's clock steps.
            if procs[pid]["start"] > written + START_SLACK_S and not any(m in procs[pid]["cmdline"] for m in LAUNCHERS):
                continue
            if os.path.exists(f[:-4] + ".exit"):  # launch_worker's <name>.exit, lead_verify's verify.exit
                continue
            tree, sep, rest = f.partition("/.gov-runtime/scratch/lead/log/")
            name = f"pid {pid} ({Path(tree).name}: {rest})" if sep else f"pid {pid} ({f})"
            age = now() - procs[pid]["start"]
            if age > RUN_BOUND_S:
                past.append(f"{name} {over(age)}")
                continue
            found.append(name)
    return found


def dispatcher(notes):
    """(status or None, running list). An unusable status is named, never relied on."""
    p = ORCH / "dispatch/status.json"
    try:
        st = json.loads(p.read_text())
        if not isinstance(st, dict):
            raise ValueError("not an object")
        age = now() - p.stat().st_mtime
    except (OSError, ValueError) as exc:
        notes.append(f"dispatcher status unusable ({p.name}: {exc})")
        return None, []
    if age > STATUS_MAX_AGE_S:
        notes.append(f"dispatcher status unusable (written {int(age)} s ago, over {STATUS_MAX_AGE_S} s)")
        return None, []
    run = []
    if st.get("lead_count"):
        run.append(f"dispatcher: {st['lead_count']} lead(s) {', '.join(map(str, st.get('leads') or []))}".rstrip())
    if st.get("pending_launches"):
        run.append(f"dispatcher: {len(st['pending_launches'])} launch(es) pending")
    for j in st.get("jobs") or []:
        run.append("dispatcher job: " + (f"{j.get('kind', '?')} {j.get('name', '?')} ({j.get('phase', '?')})"
                                         if isinstance(j, dict) else str(j)[:80]))
    if st.get("close_running"):
        run.append("dispatcher: a close running")
    if st.get("land_running"):
        run.append("dispatcher: a landing running")
    return st, run


def legit_wait(st):
    if st is None:
        return None
    if st.get("gate_open") is False or st.get("disk_open") is False:
        what = st.get("gate") if st.get("gate_open") is False else st.get("disk")
        return f"the gate shut ({str(what)[:120]})"
    lead = ((st.get("forecast") or {}).get("lead") or {})
    if st.get("admit") is False or lead.get("ok") is False:
        why = lead.get("reason") if lead.get("ok") is False else st.get("admit_reason")
        return f"the machine full ({str(why)[:160]})"
    return None


# ----------------------------------------------------------------------------------------------- DECIDED-NOT-DONE
def cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def plain(text):
    return re.sub(r"[*`]", "", text).strip()


def classify(state):
    s = plain(state)
    m = WAIT_WORD.search(s)
    head, on = (s[:m.start()], s[m.end():].lower()) if m else (s, "")
    if OPEN_WORDS.search(head) or NEXT_STEP.search(head):
        return "open", ""
    if m:
        return "wait", "owner" if "owner" in on else "running job" if "running" in on else "trigger"
    if FINAL_WORDS.match(s):
        return "closed", ""
    return "open", ""


def read_items():
    """Every row of every `## 0<letter>.` table: [(#, item, state, kind, on)]. A malformed table is a CheckError."""
    try:
        lines = DND.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CheckError(f"DECIDED-NOT-DONE unreadable: {exc}") from exc
    items, sections, i = [], 0, 0
    while i < len(lines):
        if not SECTION.match(lines[i]):
            i += 1
            continue
        title, sections, i = lines[i], sections + 1, i + 1
        header = None
        while i < len(lines) and not lines[i].startswith("## "):
            line = lines[i]
            if line.lstrip().startswith("|"):
                c = cells(line)
                if header is None:
                    header = [h.lower() for h in c]
                    if "state" not in header or "#" not in header:
                        raise CheckError(f"DECIDED-NOT-DONE line {i + 1} ({title[:30]}): a table with no '#' or "
                                         f"'state' column")
                elif not all(re.fullmatch(r":?-+:?", x) for x in c if x):
                    si, ni = header.index("state"), header.index("#")
                    if len(c) < len(header):
                        raise CheckError(f"DECIDED-NOT-DONE line {i + 1}: {len(c)} cells, the header has "
                                         f"{len(header)}")
                    state = " | ".join(c[si:]) if si == len(header) - 1 else c[si]
                    item = c[header.index("item")] if "item" in header else c[ni + 1]
                    kind, on = classify(state)
                    items.append((plain(c[ni]), plain(item), plain(state), kind, on))
            i += 1
        if header is None:
            raise CheckError(f"DECIDED-NOT-DONE: section '{title[:40]}' has no table")
    if not sections:
        raise CheckError("DECIDED-NOT-DONE: no '## 0.' tracking section found")
    return items


# ------------------------------------------------------------------------------------------------------- transcript
def turn_and_reason(data):
    """(the turn's id: the last user entry that is not a tool result, or None; the IDLE-REASON line, or None)."""
    last = data.get("last_assistant_message")
    texts, turn = [], None
    tp = data.get("transcript_path")
    if tp and os.path.isfile(tp):
        with open(tp, "rb") as f:
            size = f.seek(0, 2)
            f.seek(max(0, size - 8 * 1024 * 1024))
            tail = f.read().decode("utf-8", errors="replace").splitlines()
        for line in reversed(tail):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            content = (d.get("message") or {}).get("content")
            if d.get("type") == "user":
                scheduled = d.get("turnOrigin") or d.get("wakeupSource")  # a scheduled wakeup: meta, a new turn
                prompt = not d.get("isMeta") and (isinstance(content, str) or (
                    isinstance(content, list) and any(c.get("type") != "tool_result" for c in content
                                                      if isinstance(c, dict))))
                if scheduled or prompt:
                    turn = d.get("uuid") or d.get("timestamp")
                    break
            elif d.get("type") == "assistant" and isinstance(content, list):
                texts += [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
    if isinstance(last, str):
        texts.append(last)
    for t in texts:
        m = REASON_LINE.search(t or "")
        if m:
            return turn, m.group(1)[:300]
    return turn, None


# ------------------------------------------------------------------------------------------------------------- main
def log(sid, decision, case, detail=""):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{sid[:8]}\t{decision}\t{case}\t{detail}"[:2000] + "\n")


def decide(data):
    """(decision, case, detail, output dict or None)."""
    sid = data.get("session_id") or ""
    try:
        cto = (ORCH / "log/cto-session.txt").read_text().strip()
    except OSError:
        return "skip", "no registered CTO session", "", None
    if not cto or sid != cto:
        return "skip", "another session", "", None
    turn, reason = turn_and_reason(data)
    if reason:
        return "through", "the CTO's stated reason", reason, {
            "systemMessage": f"Idle check (DEC-1110): let through on the CTO's stated reason, recorded: {reason}"}
    try:
        state = json.loads(STATE.read_text())
    except (OSError, ValueError):
        state = {}
    if data.get("stop_hook_active") or (turn and state.get("session") == sid and state.get("turn") == turn):
        return "through", "bound: blocked once this turn", "no IDLE-REASON stated", {
            "systemMessage": "Idle check (DEC-1110): a second stop this turn, let through (no IDLE-REASON line stated)"}
    notes = []
    procs = processes()
    sub, tasks = session_dirs(data)
    st, disp = dispatcher(notes)
    past = []
    running = running_agents(sub, notes) + running_tasks(tasks, procs, past) + running_pidfiles(procs, past) + disp
    pasts = f"over the {RUN_BOUND_S // 3600} h bound, not counted: {', '.join(past)}" if past else ""
    if running:
        return "through", f"running: {len(running)}", "; ".join(running + notes + ([pasts] if past else [])), None
    tail = f" ({pasts[0].upper()}{pasts[1:]}; check it is work.)" if past else ""
    wait = legit_wait(st)
    if wait:
        return "through", wait, "; ".join(notes + ([pasts] if past else [])), {
            "systemMessage": f"Idle check (DEC-1110): nothing running; let through: {wait}.{tail}"}
    items = read_items()
    unblocked = [x for x in items if x[3] == "open"]
    if not unblocked:
        waits = [x for x in items if x[3] == "wait"]
        count = {k: sum(1 for x in waits if x[4] == k) for k in ("owner", "running job", "trigger")}
        case = (f"every open item waits ({count['owner']} on the owner, {count['running job']} on a running job, "
                f"{count['trigger']} on a trigger)")
        return "through", case, "; ".join(notes + ([pasts] if past else [])), {
            "systemMessage": f"Idle check (DEC-1110): nothing running; let through: {case}.{tail}"}
    shown = "; ".join(f"#{n} {it[:60]} ({s[:40]})" for n, it, s, _, _ in unblocked[:SHOW_MAX])
    more = f"; and {len(unblocked) - SHOW_MAX} more" if len(unblocked) > SHOW_MAX else ""
    disp_note = next((n for n in notes if n.startswith("dispatcher status unusable")), "dispatcher status unusable")
    seen = "none of the session's agents or tasks, no launched worker" + (
        "; dispatcher: no lead or job, the gate open, the machine not full" if st is not None else f"; {disp_note}") \
        + (f"; {pasts}" if past else "")
    reason = (f"Idle check (DEC-1110 (1), DEC-1109 (3)): nothing of yours is running ({seen}) while DECIDED-NOT-DONE "
              f"shows {len(unblocked)} unblocked item(s): {shown}{more}. Start them now within the machine's "
              f"limits (or move each to its true state in DECIDED-NOT-DONE), then end the turn. If none can move, "
              f"write one line `IDLE-REASON: <why>` (recorded in log/stop-idle.log, shown to the owner) and end the "
              f"turn.")
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"session": sid, "turn": turn, "at": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n")
    return "block", f"{len(unblocked)} unblocked", "; ".join([shown + more] + notes), {"decision": "block",
                                                                                  "reason": reason}


def main():
    sid = ""
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise CheckError("the hook's input is not a JSON object")
        sid = data.get("session_id") or ""
        decision, case, detail, out = decide(data)
    except Exception as exc:  # noqa: BLE001 - named to the owner and logged; never traps the session
        decision, case, detail = "error", f"{type(exc).__name__}: {exc}"[:300], ""
        out = {"systemMessage": f"Idle check (DEC-1110) could not run: {case}. The turn ends unchecked "
                                f"(logged in log/stop-idle.log)."}
    if decision != "skip":
        try:
            log(sid, decision, case, detail)
        except Exception as exc:  # noqa: BLE001
            out = dict(out or {})
            out["systemMessage"] = (out.get("systemMessage", "Idle check (DEC-1110)") +
                                    f" [the log could not be written: {exc}]")
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
