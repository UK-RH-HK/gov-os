#!/usr/bin/env python3
"""The 48-hour call set for W2-148's after-check replay (DEC-1108 (2); ACT-GUARD-CALLLOG-1 §3 (a), option 1).

Builds, from the transcripts of the main tree's and the worktrees' sessions (subagents included), the calls of the
window in the form `replay()` in governance/project/operator/operator_run.py reads, for the operator agent to check
against the guard's call log by sha256 both ways before it re-judges any of them:

  line 1   {"v": 1, "window": {"since": ISO, "until": ISO}, "built_by": "build_replay_calls.py"}
  a call   {"id": <tool_use id>, "time": ISO, "session": <session id>, "role", "ticket", "agent",
            "sha256": <the guard's hash>, "event": {"tool_name", "tool_input", "cwd"}}
  dropped  {"id", "time", "session", "agent", "sha256", "dropped": "names the sets root"}   (no event: nothing copied)

Reads only the tool calls' inputs (tool name, input, cwd, time, tool_use id) of assistant records, and the first user
message's first 300 characters to guess a role when the log has none (as G-14's and the sets replays do); never a tool
result. Only the main tree's project folder and the worktrees' are read: the writer's, the checker's, the walls', the
run clones' and every other folder are never opened (a worktree folder whose name holds writer, checker, labeller,
indep-walls or the sets root's name is skipped too). A call whose input or folder names the sets root, in any
spelling, is never copied: it is written as its hash only, marked dropped.

Each call's sha256 is the guard's own: `action_bytes(tool, input)` imported from the live hook (--hook), so the
normalisation is exactly the one the guard logs. With the log (default ~/.gov-os/guard-calls), each call is matched
to a logged line of the same session by that hash; a call the log does not hold is first tried with its string
booleans ("true"/"false") as the hook was given them (removed, or as booleans: Claude Code passed the Agent tool's
`run_in_background: "true"` to the hook without it on 2026-11-09), then left out and counted (the guard never judged
it as written, so there is nothing to replay); the log's role and ticket are written on the line. The operator agent
recomputes every hash itself and trusts none of this file's fields but the event.

  python3 build_replay_calls.py --out <file> [--hours 48] [--until ISO] [--log DIR | --no-log]
        [--projects ~/.claude/projects] [--main <main tree>] [--worktrees ~/gov-os-worktrees] [--hook <pretooluse.py>]

Writes the file (mode 0600: it holds the actions' inputs) and prints counts and hash prefixes only, never an input.
"""
import argparse
import collections
import datetime as dt
import glob
import hashlib
import importlib.util
import json
import os
import re
import sys

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
SETS_ROOT_NAME = "gov-os-" + "eval"          # never written on a command line (the CTO's rule)
SKIP_WORDS = ("writer", "checker", "labeller", "indep-walls", SETS_ROOT_NAME)
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
LIVE_TREES = ("main", "worktree")
SLACK_S = 120          # a call's transcript time and its log time differ by milliseconds; the edges get two minutes
KNOWN = ("orchestrator", "product-spec", "engineer", "independent-test-designer", "independent-auditor", "research")


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (t.microsecond // 1000)


def parse_iso(s):
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t.astimezone(dt.timezone.utc) if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def folder_name(path):
    """Claude Code's project folder for a path: every character but a letter or a digit becomes '-'."""
    return "".join(c if c.isalnum() else "-" for c in path)


def load_action_bytes(hook):
    spec = importlib.util.spec_from_file_location("gov_live_hook_for_replay_calls", hook)
    if spec is None or spec.loader is None:
        raise SystemExit(f"build_replay_calls: cannot load the guard hook {hook}; nothing written")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = getattr(mod, "action_bytes", None)
    if not callable(fn):
        raise SystemExit(f"build_replay_calls: the hook {hook} has no action_bytes(); nothing written")
    return fn


def role_of_text(text, main):  # G-14's replay.py rule, as the sets replay and the corpus extractor use it
    t = text[:300].lower()
    if t.startswith("<local-command-caveat>") or t.startswith("<command-"):
        return "orchestrator"
    for key, role in (("ticket lead", "orchestrator"), ("test designer", "independent-test-designer"),
                      ("test-designer", "independent-test-designer"), ("reviewer", "independent-auditor"),
                      ("auditor", "independent-auditor"), ("product-spec", "product-spec"), ("engineer", "engineer"),
                      ("research", "research"), ("sentinel", "orchestrator"), ("cto", "orchestrator")):
        if key in t:
            return role
    return "orchestrator" if main else "unknown"


def first_text(path):
    try:
        f = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return ""
    with f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if not isinstance(d, dict) or d.get("type") != "user" or d.get("isMeta"):
                continue
            c = (d.get("message") or {}).get("content")
            t = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c or []
                                                      if isinstance(x, dict) and x.get("type") == "text")
            if t.strip():
                return t.strip()[:300]
    return ""


def project_folders(projects, main, worktrees, counts):
    """(folder, is_main): the main tree's folder and each worktree's; nothing else is opened."""
    out = []
    mf = os.path.join(projects, folder_name(main))
    if os.path.isdir(mf):
        out.append((mf, True))
    prefix = folder_name(worktrees.rstrip("/")) + "-"
    for f in sorted(glob.glob(os.path.join(glob.escape(projects), glob.escape(prefix) + "*"))):
        if not os.path.isdir(f):
            continue
        if any(w in os.path.basename(f)[len(prefix):].lower() for w in SKIP_WORDS):
            counts["folders skipped (writer, checker, walls)"] += 1
            continue
        out.append((f, False))
    return out


def session_files(folder):
    """(transcript, session id, agent type or None, the session's top transcript)."""
    for f in sorted(glob.glob(os.path.join(glob.escape(folder), "*.jsonl"))):
        sid = os.path.basename(f)[:-6]
        yield f, sid, None, f
        for s in sorted(glob.glob(os.path.join(glob.escape(f[:-6]), "subagents", "*.jsonl"))):
            try:
                with open(s[:-6] + ".meta.json", encoding="utf-8") as m:
                    agent = json.load(m).get("agentType")
            except (OSError, ValueError, AttributeError):
                agent = None
            yield s, sid, agent or "subagent", f


def tool_calls(path):
    """(name, input, cwd, time, tool_use id) of the assistant records' tool_use blocks; never a tool result."""
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"tool_use"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if not isinstance(d, dict) or d.get("type") != "assistant":
                continue
            for x in (d.get("message") or {}).get("content") or []:
                if isinstance(x, dict) and x.get("type") == "tool_use" and isinstance(x.get("name"), str):
                    yield x["name"], x.get("input"), d.get("cwd"), d.get("timestamp") or "", x.get("id")


def variants(tin):
    """The input as written, then as the hook may have been given it: string booleans removed, or made booleans."""
    yield tin
    if isinstance(tin, dict):
        sb = [k for k, v in tin.items() if v in ("true", "false")]
        if sb:
            yield {k: v for k, v in tin.items() if k not in sb}
            yield {k: (v == "true" if k in sb else v) for k, v in tin.items()}


def load_log(folder, since, until, counts):
    """{(session, sha256): log row} of the window's lines (edges widened by SLACK_S), and the replayable rows."""
    if not os.path.isdir(folder):
        raise SystemExit(f"build_replay_calls: no guard call log at {folder} (use --no-log to build without it)")
    lo, hi = since - dt.timedelta(seconds=SLACK_S), until + dt.timedelta(seconds=SLACK_S)
    day, index, live = lo.date(), {}, []
    while day <= hi.date():
        p = os.path.join(folder, day.isoformat() + ".jsonl")
        if os.path.exists(p + ".capped"):
            counts["log days capped (the replay will refuse)"] += 1
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                for ln in f:
                    try:
                        r = json.loads(ln)
                    except ValueError:
                        counts["log lines malformed (the replay will refuse)"] += 1
                        continue
                    t = parse_iso(r.get("time")) if isinstance(r, dict) else None
                    if t is None or not (lo <= t <= hi):
                        continue
                    index.setdefault((r.get("session"), r.get("sha256")), r)
                    if (UUID.match(str(r.get("session") or "")) and r.get("tree") in LIVE_TREES
                            and since + dt.timedelta(seconds=SLACK_S) <= t <= until - dt.timedelta(seconds=SLACK_S)):
                        live.append(r)
        day += dt.timedelta(days=1)
    return index, live


def build(a):
    counts = collections.Counter()
    until = parse_iso(a.until) if a.until else dt.datetime.now(dt.timezone.utc)
    if until is None:
        raise SystemExit("build_replay_calls: --until is not an ISO time")
    since = until - dt.timedelta(hours=a.hours)
    s_iso, u_iso = iso(since), iso(until)
    action_bytes = load_action_bytes(a.hook)

    def digest(tool, tin):
        return hashlib.sha256(action_bytes(tool, tin)).hexdigest()

    index, live = load_log(a.log, since, until, counts) if a.log else ({}, [])
    rows = []
    for folder, is_main in project_folders(a.projects, a.main, a.worktrees, counts):
        for path, sid, agent, top in session_files(folder):
            guess = None
            for tool, tin, cwd, ts, tid in tool_calls(path):
                t = parse_iso(ts)
                if t is None or not (since <= t <= until):
                    continue
                counts["calls in the window"] += 1
                cwd = cwd if isinstance(cwd, str) and cwd else a.main
                base = {"id": tid, "time": ts, "session": sid, "agent": agent}
                names_root = SETS_ROOT_NAME in action_bytes(tool, tin).decode("utf-8", "replace") or \
                    SETS_ROOT_NAME in cwd
                h, logged = digest(tool, tin), None
                if a.log:
                    for v in variants(tin):
                        hv = digest(tool, v)
                        if (sid, hv) in index:
                            logged = index[(sid, hv)]
                            if v is not tin:
                                counts["reconciled with the log"] += 1
                            tin, h = v, hv
                            break
                    if logged is None:
                        counts["left out: no log line"] += 1
                        continue
                if names_root:
                    rows.append(dict(base, sha256=h, dropped="names the sets root"))
                    counts["dropped: names the sets root"] += 1
                    continue
                if logged is not None and logged.get("role"):
                    role, ticket = logged.get("role"), logged.get("ticket") or None
                else:
                    if guess is None:
                        guess = role_of_text(first_text(top), is_main)
                    role, ticket = guess, None
                rows.append(dict(base, role=role, ticket=ticket, sha256=h,
                                 event={"tool_name": tool, "tool_input": tin, "cwd": cwd}))
                counts["calls written"] += 1
    rows.sort(key=lambda r: (r["time"], str(r["id"])))
    have = {(r["session"], r["sha256"]) for r in rows}
    missing = [r for r in live if (r.get("session"), r.get("sha256")) not in have]
    counts["logged replayable calls in the window"] = len(live)
    counts["logged replayable calls with no set line"] = len(missing)
    head = {"v": 1, "window": {"since": s_iso, "until": u_iso}, "built_by": "build_replay_calls.py"}
    tmp = a.out + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for r in [head] + rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    os.chmod(tmp, 0o600)
    os.replace(tmp, a.out)
    with open(a.out, "rb") as f:
        file_sha = hashlib.sha256(f.read()).hexdigest()
    for r in missing[:20]:   # hashes, tools, times and rules only: never an input
        print(f"no set line: session {str(r.get('session'))[:8]} {r.get('tool')} {r.get('time')} "
              f"rule {r.get('rule')} sha256 {str(r.get('sha256'))[:12]}")
    out = dict(sorted(counts.items()))
    out.update(window=head["window"], file=a.out, sha256=file_sha)
    print(json.dumps(out))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--out", required=True)
    p.add_argument("--hours", type=float, default=48)
    p.add_argument("--until", default=None, help="the window's end (ISO, UTC); default now")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--log", default=os.path.expanduser("~/.gov-os/guard-calls"))
    g.add_argument("--no-log", dest="log", action="store_const", const=None)
    p.add_argument("--projects", default=os.path.expanduser("~/.claude/projects"))
    p.add_argument("--main", default=MAIN)
    p.add_argument("--worktrees", default=os.path.expanduser("~/gov-os-worktrees"))
    p.add_argument("--hook", default=os.path.join(MAIN, ".claude/hooks/pretooluse.py"))
    return build(p.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
