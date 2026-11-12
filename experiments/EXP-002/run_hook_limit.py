#!/usr/bin/env python3
"""EXP-002 (hook-limit round, ticket DAEO-6ox0): what Claude Code does with a hook that runs past its time limit.

One case per call. A case builds one throwaway project under --base whose .claude/settings.json registers one
hook and nothing else, starts one headless `claude -p` session in it, and writes what happened as one JSON line
to <out>/<case>-<run>.json and to stdout. Standard library only. Run: python3 run_hook_limit.py --help

The script writes nothing outside --base and --out. It reads no settings file but the throwaway one it wrote
(`claude --help` is run once to see whether --setting-sources exists; that starts no session). It never keeps the
raw stream, the environment or any key: only the extracted fields below.
"""
import argparse
import json
import os
import shlex
import signal
import subprocess
import sys
import threading
import time

DEFAULT_CLAUDE = "/home/usain/.local/bin/claude"
HEAD = 300            # characters kept of a tool result and of the final result
EVENT_HEAD = 200      # characters kept of a field of a hook lifecycle event
SETTLE_S = 3          # extra seconds waited after started + the hook's sleep before the log is read
WALL_EXTRA_S = 60     # the session's wall limit is the hook's sleep plus this
HOOK_EVENT_KEYS = ("subtype", "hook_event", "hook_name", "outcome", "exit_code", "timeout", "stdout", "stderr")

# id: (hook event, configured limit in seconds or None for "no timeout key", the hook's sleep in seconds,
#      the exit code it would end with, mandatory)
CASES = {
    "pre-control-5": ("PreToolUse", 5, 0, 2, True),
    "pre-allow-5": ("PreToolUse", 5, 25, 0, True),
    "pre-deny-5": ("PreToolUse", 5, 25, 2, True),
    "pre-allow-60": ("PreToolUse", 60, 90, 0, True),
    "pre-deny-60": ("PreToolUse", 60, 90, 2, True),
    "pre-nolimit": ("PreToolUse", None, 130, 0, False),
    "post-5": ("PostToolUse", 5, 25, 0, False),
    "stop-5": ("Stop", 5, 25, 0, False),
}
TOOL_EVENTS = ("PreToolUse", "PostToolUse")  # these take a matcher; Stop does not


def clean_env():
    """The environment of the session: every CLAUDE* and GOV_* variable removed (DEC-784's way)."""
    return {k: v for k, v in os.environ.items() if not (k.startswith("CLAUDE") or k.startswith("GOV_"))}


def removed_env_count():
    return sum(1 for k in os.environ if k.startswith("CLAUDE") or k.startswith("GOV_"))


def hook_command(project, sleep_s, code):
    """The hook: `started`, then one `tick` a second for sleep_s seconds, then `finished`, then exit with code.
    Every line is `<word> <epoch seconds with fractions>`, appended to <project>/hook.log."""
    log = shlex.quote(os.path.join(project, "hook.log"))
    parts = [f'echo "started $(date +%s.%N)" >> {log}']
    if sleep_s:
        parts.append(f'i=0; while [ "$i" -lt {sleep_s} ]; do sleep 1; echo "tick $(date +%s.%N)" >> {log}; '
                     f'i=$((i+1)); done')
    parts.append(f'echo "finished $(date +%s.%N)" >> {log}')
    if code == 2:
        parts.append("echo 'refused by the experiment hook' >&2")
    parts.append(f"exit {code}")
    return "; ".join(parts)


def settings_for(case, project):
    event, limit, sleep_s, code, _ = CASES[case]
    entry = {"type": "command", "command": hook_command(project, sleep_s, code)}
    if limit is not None:
        entry["timeout"] = limit
    group = {"hooks": [entry]}
    if event in TOOL_EVENTS:
        group = {"matcher": "Bash", "hooks": [entry]}
    return {"hooks": {event: [group]}}


def has_setting_sources(claude):
    """Whether `claude --help` names --setting-sources (no session is started)."""
    try:
        out = subprocess.run([claude, "--help"], capture_output=True, text=True, timeout=60, cwd="/",
                             env=clean_env(), stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return False
    return "--setting-sources" in (out.stdout + out.stderr)


def prompt_for(project):
    return ("Run exactly this one bash command, once, and nothing else, then report its outcome in one line: "
            f"touch {project}/ran.txt")


def argv_for(claude, model, project, setting_sources):
    argv = [claude, "-p", prompt_for(project), "--model", model, "--output-format", "stream-json", "--verbose"]
    if setting_sources:
        argv += ["--setting-sources", "project"]
    argv += ["--allowedTools", "Bash"]  # last: the option takes a list
    return argv


def git_ancestor(path):
    """The first folder at or above path that holds a .git (file or folder), or None."""
    cur = os.path.realpath(path)
    while True:
        if os.path.exists(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def parse_log(path):
    starts, ticks, finishes = [], [], []
    try:
        with open(path) as f:
            lines = f.read().splitlines()
    except OSError:
        return starts, ticks, finishes
    for line in lines:
        word, _, value = line.partition(" ")
        try:
            t = float(value)
        except ValueError:
            continue
        {"started": starts, "tick": ticks, "finished": finishes}.get(word, []).append(t)
    return starts, ticks, finishes


def wait_for_hook(path, sleep_s):
    """Wait until started + sleep + SETTLE_S has passed (or `finished` is in the log), so that a hook process the
    harness left running has had time to tick on and write `finished`. Then read the log once more."""
    while True:
        starts, _, finishes = parse_log(path)
        if not starts or finishes or time.time() >= starts[0] + sleep_s + SETTLE_S:
            break
        time.sleep(0.5)
    return parse_log(path)


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(c.get("text", "") for c in content if isinstance(c, dict))
    return "" if content is None else str(content)


def parse_stream(stdout, want_hook_events):
    """Only the extracted fields; the stream itself is dropped by the caller."""
    r = {"version": None, "model": None, "session_id": None, "tool_uses": 0, "tool_results": 0,
         "tool_is_error": None, "tool_text_head": None, "result_head": None, "result_subtype": None,
         "result_is_error": None, "system_subtypes": {}, "hook_events": []}
    for line in stdout.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if not isinstance(o, dict):
            continue
        kind = o.get("type")
        if kind == "system" and o.get("subtype") == "init":
            r["version"], r["model"], r["session_id"] = (o.get("claude_code_version"), o.get("model"),
                                                         o.get("session_id"))
        elif kind == "system":
            sub = str(o.get("subtype"))
            r["system_subtypes"][sub] = r["system_subtypes"].get(sub, 0) + 1
            if want_hook_events and "hook" in sub and len(r["hook_events"]) < 20:
                ev = {k: (str(o[k])[:EVENT_HEAD] if isinstance(o[k], str) else o[k])
                      for k in HOOK_EVENT_KEYS if k in o}
                ev["keys"] = sorted(o.keys())
                r["hook_events"].append(ev)
        elif kind in ("assistant", "user"):
            content = (o.get("message") or {}).get("content")
            for c in content if isinstance(content, list) else []:
                if not isinstance(c, dict):
                    continue
                if c.get("type") == "tool_use":
                    r["tool_uses"] += 1
                elif c.get("type") == "tool_result":
                    r["tool_results"] += 1
                    if r["tool_results"] == 1:
                        r["tool_is_error"] = c.get("is_error")
                        r["tool_text_head"] = text_of(c.get("content"))[:HEAD]
        elif kind == "result":
            r["result_head"] = text_of(o.get("result"))[:HEAD]
            r["result_subtype"] = o.get("subtype")
            r["result_is_error"] = o.get("is_error")
    return r


def drain(pipe, sink):
    try:
        for line in pipe:
            sink.append(line)
    except (OSError, ValueError):
        pass


def stop_group(proc):
    """End the session's process group (its own, by start_new_session)."""
    for sig, wait in ((signal.SIGTERM, 5), (signal.SIGKILL, 5)):
        try:
            os.killpg(proc.pid, sig)
        except OSError:
            return
        try:
            proc.wait(timeout=wait)
            return
        except subprocess.TimeoutExpired:
            continue


def plan_for(args, setting_sources):
    event, limit, sleep_s, code, mandatory = CASES[args.case]
    project = os.path.join(os.path.abspath(args.base), f"{args.case}-{args.run}")
    return {
        "case": args.case, "run": args.run, "mandatory": mandatory, "hook_event": event,
        "limit": limit if limit is not None else "none", "hook_sleep_s": sleep_s, "would_exit": code,
        "wall_limit_s": sleep_s + WALL_EXTRA_S, "setting_sources_flag": setting_sources,
        "project": project, "settings_path": os.path.join(project, ".claude", "settings.json"),
        "settings": settings_for(args.case, project), "argv": argv_for(args.claude, args.model, project,
                                                                       setting_sources),
        "env_variables_removed": removed_env_count(),
        "out_json": os.path.join(os.path.abspath(args.out), f"{args.case}-{args.run}.json"),
        "out_pid": os.path.join(os.path.abspath(args.out), f"{args.case}-{args.run}.pid"),
    }


def rnd(x):
    return None if x is None else round(x, 2)


def run_case(args, plan):
    project, out_dir = plan["project"], os.path.abspath(args.out)
    sleep_s = plan["hook_sleep_s"]
    os.makedirs(os.path.join(project, ".claude"), exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    for name in ("hook.log", "ran.txt"):
        if os.path.exists(os.path.join(project, name)):
            os.remove(os.path.join(project, name))
    with open(plan["settings_path"], "w") as f:
        json.dump(plan["settings"], f, indent=1)

    start_epoch = time.time()
    proc = subprocess.Popen(plan["argv"], cwd=project, env=clean_env(), stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    print(f"pid {proc.pid}", flush=True)
    with open(plan["out_pid"], "w") as f:
        f.write(f"{proc.pid}\n")
    # The pipes are drained in threads and the wall time is taken when the process itself exits, so that a hook
    # process left running with the session's pipes open cannot stretch the wall time.
    out_chunks, err_chunks = [], []
    readers = [threading.Thread(target=drain, args=(proc.stdout, out_chunks), daemon=True),
               threading.Thread(target=drain, args=(proc.stderr, err_chunks), daemon=True)]
    for t in readers:
        t.start()
    session = "completed"
    try:
        try:
            proc.wait(timeout=plan["wall_limit_s"])
        except subprocess.TimeoutExpired:
            session = "timed out"
            stop_group(proc)
    finally:
        if proc.poll() is None:
            stop_group(proc)
    wall = time.time() - start_epoch
    for t in readers:
        t.join(timeout=10)
    pipes_open = any(t.is_alive() for t in readers)
    stdout, stderr = "".join(out_chunks), "".join(err_chunks)

    starts, ticks, finishes = wait_for_hook(os.path.join(project, "hook.log"), sleep_s)
    started = starts[0] if starts else None
    ran = os.path.join(project, "ran.txt")
    ran_exists = os.path.exists(ran)
    if not ran_exists:
        ran_after = "not run"
    elif started is None:
        ran_after = "no hook start in the log"
    else:
        ran_after = rnd(os.stat(ran).st_mtime - started)
    parsed = parse_stream(stdout, args.hook_events)
    if started is None:
        hook_process = "never started"
    elif finishes:
        hook_process = "ran to its end"
    else:
        hook_process = "ended before finishing"
    rec = {
        "case": args.case, "run": args.run, "harness_version": parsed["version"], "model": parsed["model"],
        "model_requested": args.model, "hook_event": plan["hook_event"], "limit": plan["limit"],
        "hook_sleep_s": sleep_s, "would_exit": plan["would_exit"],
        "call_ran_after_hook_start_s": ran_after,
        "session_wall_s": rnd(wall),
        "session_end_after_hook_start_s": rnd(start_epoch + wall - started) if started is not None else None,
        "hook_starts": len(starts), "hook_finished": bool(finishes),
        "finished_offset_s": rnd(finishes[-1] - started) if finishes and started is not None else None,
        "ticks": len(ticks),
        "last_tick_offset_s": rnd(max(ticks) - started) if ticks and started is not None else None,
        "hook_process": hook_process,
        "ran_txt_exists": ran_exists,
        "tool_uses": parsed["tool_uses"], "tool_results": parsed["tool_results"],
        "tool_is_error": parsed["tool_is_error"], "tool_text_head": parsed["tool_text_head"],
        "result_head": parsed["result_head"], "result_subtype": parsed["result_subtype"],
        "result_is_error": parsed["result_is_error"],
        "system_subtypes": parsed["system_subtypes"],
        "session": session, "exit_code": proc.returncode, "pipes_open_10s_after_exit": pipes_open, "session_id": parsed["session_id"],
        "project": project, "start_epoch": round(start_epoch, 3), "pid": proc.pid,
        "setting_sources_flag": plan["setting_sources_flag"], "hook_events_flag": args.hook_events,
        "stderr_head": (stderr or "")[:HEAD],
    }
    if args.hook_events:
        rec["hook_events"] = parsed["hook_events"]
    line = json.dumps(rec)
    with open(plan["out_json"], "w") as f:
        f.write(line + "\n")
    print(line, flush=True)
    try:
        os.remove(plan["out_pid"])  # the session's group is gone; a stale pid file could name a reused pid
    except OSError:
        pass
    return 0 if session == "completed" else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--case", required=True, choices=sorted(CASES), help="the case id (one per call)")
    ap.add_argument("--run", required=True, choices=("a", "b"), help="run a or b of the case")
    ap.add_argument("--base", required=True, help="folder for the throwaway projects (outside every git repository)")
    ap.add_argument("--out", required=True, help="folder for <case>-<run>.json and .pid")
    ap.add_argument("--model", required=True, help="model id for the session")
    ap.add_argument("--claude", default=DEFAULT_CLAUDE, help=f"the claude program (default {DEFAULT_CLAUDE})")
    ap.add_argument("--dry-run", action="store_true", help="print the plan (settings, command), start no session")
    ap.add_argument("--hook-events", action="store_true",
                    help="also pass --include-hook-events and keep a whitelist of its fields (off by default)")
    args = ap.parse_args()

    ancestor = git_ancestor(args.base)
    if ancestor:
        print(f"refused: --base {args.base} lies inside the git repository at {ancestor}", file=sys.stderr)
        return 2
    setting_sources = has_setting_sources(args.claude)
    plan = plan_for(args, setting_sources)
    if args.hook_events:
        plan["argv"].insert(plan["argv"].index("--verbose") + 1, "--include-hook-events")
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0
    if not (os.path.isfile(args.claude) and os.access(args.claude, os.X_OK)):
        print(f"refused: {args.claude} is not an executable file", file=sys.stderr)
        return 2
    return run_case(args, plan)


if __name__ == "__main__":
    sys.exit(main())
