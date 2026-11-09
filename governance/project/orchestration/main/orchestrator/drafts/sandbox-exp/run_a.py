"""SANDBOX-GUARD-EXP-1, set-up A's runner (the declaration §7 (a)): each action passed to the copied live hook, its
own decision recorded. Nothing is executed: set-up A is the path-map guard alone, and with no sandbox an action the
hook allows does whatever it does, so the hook's decision is A's whole answer.

The judging is the reviewed replays' (drafts/sets-root-guard/replay_sets.py, drafts/sandbox-seal/replay_seal.py): one
PreToolUse event per action on stdin, the hook run on the pinned python with -E; exit 2 is a refusal, a JSON answer
gives allow, deny or ask, no output is an allow. Each action's /home/usain spelling is first rewritten onto the
substituted home (common.rewrite); an action that still names the real home is dropped and counted, never judged.
The hook runs with HOME set to the substituted home, CLAUDE_PROJECT_DIR set to the session's tree there (the clone
for the main tree), GOV_ROLE and GOV_TICKET from the action record.

  python3 run_a.py trees [--sets-root R] [--exp E]
      the worktree names the actions' folders name, both halves together, into <exp>/A/trees.txt (prepare_a.sh's
      input); prints the count only
  python3 run_a.py run --half tuning|held-out --round N [--sets-root R] [--exp E] [--dry] [--workers 6]
        [--max-seconds S] [--home H] [--clone C] [--hook P] [--py P] [--input FILE ...] [--out FILE]
      judges the half's actions (corpus/actions.jsonl and planted/cases.jsonl in the half's folder) and writes
      <half>/results/A-<round>.jsonl ({id, decision, why}) and its manifest; prints counts and sha256s only.
      The held-out half's folder is derived in code from --sets-root (ACT-SANDBOX-SEAL-1). It runs once per round:
      --round live (the prepared clone's copy of the live hook) and --round tuned (--hook: the frozen tuned hook, its
      SHA256SUMS beside it), so Q8 can compare them; an existing result is never overwritten.
      --dry reads and rewrites, judges nothing, writes nothing, prints counts.
      --max-seconds is the runaway brake (DEC-1091, the declaration §10): the run stops, kept results are written and
      the stop is reported with its cause.
--input, --out, --home and --clone are for tests and the tuning half only; the held-out half takes no path but the
root (and the frozen hook for --round tuned).
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

INPUTS = (("corpus", "actions.jsonl"), ("planted", "cases.jsonl"))
DECISIONS = ("allow", "deny", "ask")
_TREE = re.compile(r"^/home/usain/gov-os-worktrees/([^/]+)")


def half_inputs(half: str, sets_root: str | None, exp: str) -> list[str]:
    return [C.half_dir(half, sets_root, exp, d, f) for d, f in INPUTS]


HELD_OUT_ROUNDS = ("live", "tuned")


def frozen_ok(hook: str) -> None:
    """The frozen tuned hook: every file its SHA256SUMS names, beside it, matches (the declaration §9)."""
    d = os.path.dirname(os.path.abspath(hook))
    sums = os.path.join(d, "SHA256SUMS")
    if not os.path.isfile(sums):
        C.die("the frozen hook has no SHA256SUMS beside it")
    names = set()
    for line in open(sums, encoding="utf-8"):
        if line.strip():
            want, name = line.split(None, 1)
            name = name.strip().lstrip("*")
            names.add(name)
            if C.file_sha(os.path.join(d, name)) != want:
                C.die(f"the frozen hook's {name} does not match its SHA256SUMS")
    if os.path.basename(hook) not in names:
        C.die("the frozen hook's SHA256SUMS does not name the hook")


def load_actions(paths: list[str], counts: collections.Counter) -> list[dict]:
    out, seen = [], set()
    for p in paths:
        if not os.path.exists(p):
            counts["input files absent"] += 1
            continue
        for r in C.read_jsonl(p):
            if r.get("id") in seen:
                counts["duplicate ids skipped"] += 1
                continue
            seen.add(r.get("id"))
            out.append(r)
    return out


def session_tree(cwd: str, home: str, clone: str) -> str:
    """The session's tree under the substituted home: its worktree there if prepared, else the clone."""
    m = re.match(re.escape(os.path.join(home, "gov-os-worktrees")) + r"/([^/]+)", cwd or "")
    if m:
        t = os.path.join(home, "gov-os-worktrees", m.group(1))
        if os.path.isdir(t):
            return t
    return clone


def judge(hook: str, py: str, event: dict, env: dict, timeout: float) -> tuple[str, str]:
    """The hook's own decision on one event: (allow|deny|ask|error, reason). Stopped by its process group."""
    p = subprocess.Popen([py, "-E", hook], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, env=env, start_new_session=True)
    try:
        out, err = p.communicate(json.dumps(event), timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.communicate()
        return "error", f"the harness stopped the hook after {timeout:.0f} s"
    if p.returncode == 2:
        return "deny", "exit 2: " + err.strip()[-160:]
    if p.returncode != 0:
        return "error", f"exit {p.returncode}: " + err.strip()[-160:]
    if out.strip():
        try:
            o = json.loads(out)["hookSpecificOutput"]
            d = o["permissionDecision"]
        except (ValueError, KeyError, TypeError):
            return "error", "an answer the harness cannot read"
        return (d if d in DECISIONS else "error"), str(o.get("permissionDecisionReason", ""))
    return "allow", ""


def event_and_env(rec: dict, home: str, clone: str) -> tuple[dict | None, dict | None, str]:
    """The rewritten event and the hook's environment, or (None, None, why) when the action is dropped."""
    tin = C.rewrite(rec.get("input") or {}, home)
    cwd = C.rewrite(rec.get("cwd") or C.MAIN, home)
    if C.escapes(C.canon(tin) + " " + cwd, home):
        return None, None, "dropped: still names the real home"
    event = {"tool_name": rec.get("tool"), "tool_input": tin, "cwd": cwd, "session_id": "sandbox-exp-a",
             "agent_type": rec.get("agent")}
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTHONPATH", "GOV_ROLE", "GOV_TICKET", "CLAUDE_PROJECT_DIR", "HOME")}
    env.update(HOME=home, CLAUDE_PROJECT_DIR=session_tree(cwd, home, clone))
    role = rec.get("role")
    if role and role != "unknown":
        env["GOV_ROLE"] = role
    if rec.get("ticket"):
        env["GOV_TICKET"] = rec["ticket"]
    return event, env, ""


def cmd_trees(a) -> int:
    names, counts = set(), collections.Counter()
    for half in C.HALVES:
        if half == "held-out" and not a.sets_root:
            continue
        for r in load_actions(half_inputs(half, a.sets_root, a.exp), counts):
            m = _TREE.match(r.get("cwd") or "")
            if m:
                names.add(m.group(1))
    out = os.path.join(a.exp, "A", "trees.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write("".join(n + "\n" for n in sorted(names)))
    C.say(f"trees: {len(names)} worktree names (both halves together) into A/trees.txt; absent inputs "
          f"{counts['input files absent']}")
    return 0


def cmd_run(a) -> int:
    t0 = time.monotonic()
    if a.half == "held-out":
        if a.input or a.out or a.home or a.clone:
            C.die("the held-out half takes no path but --sets-root (and, for --round tuned, --hook)")
        if not a.sets_root:
            C.die("the held-out half needs --sets-root")
        if a.round not in HELD_OUT_ROUNDS:
            C.die("the held-out half's rounds are 'live' (A as live) and 'tuned' (A frozen after tuning)")
        if (a.round == "tuned") != bool(a.hook):
            C.die("--round tuned takes the frozen hook (--hook, a SHA256SUMS beside it); --round live takes none")
        if a.hook:
            frozen_ok(a.hook)
        if os.path.exists(C.half_dir(a.half, a.sets_root, a.exp, "results", f"A-{a.round}.jsonl")):
            C.die(f"the held-out half runs once per round; A-{a.round} exists")
    home = os.path.realpath(a.home or C.planted_home(a.exp))
    clone = os.path.realpath(a.clone) if a.clone else os.path.join(home, "Dynamic-Agentic-Engineering-OS")
    hook = a.hook or os.path.join(clone, ".claude", "hooks", "pretooluse.py")
    py = a.py or C.pin_python()
    counts = collections.Counter()
    paths = a.input or half_inputs(a.half, a.sets_root, a.exp)
    actions = load_actions(paths, counts)
    counts["actions read"] = len(actions)
    todo, dropped = [], []
    for r in actions:
        ev, env, why = event_and_env(r, home, clone)
        if ev is None:
            dropped.append(r["id"])
            continue
        todo.append((r, ev, env))
    counts["dropped (names the real home)"] = len(dropped)
    counts["to judge"] = len(todo)
    by_tool = collections.Counter(r.get("tool") for r, _e, _v in todo)
    by_role = collections.Counter(r.get("role") for r, _e, _v in todo)
    C.say(f"set-up A, half {a.half}, round {a.round}: home {'(substituted)' if not a.home else '(given)'}")
    for k in sorted(counts):
        C.say(f"  {k}: {counts[k]}")
    C.say("  by tool:", dict(sorted(by_tool.items())))
    C.say("  by role:", dict(sorted((str(k), v) for k, v in by_role.items())))
    if a.dry:
        C.say("dry: nothing judged, nothing written")
        return 0
    if not os.path.isfile(hook):
        C.die("no hook at the clone (run prepare_a.sh first)")
    results, stop = {}, threading.Event()
    brake = {"why": ""}

    def one(item):
        r, ev, env = item
        if stop.is_set():
            return r["id"], None
        if a.max_seconds and time.monotonic() - t0 > a.max_seconds:
            brake["why"] = f"the runaway brake: past {a.max_seconds:.0f} s (twice the projection)"
            stop.set()
            return r["id"], None
        return r["id"], judge(hook, py, ev, env, a.timeout)

    with concurrent.futures.ThreadPoolExecutor(a.workers) as ex:
        for rid, got in ex.map(one, todo):
            if got is not None:
                results[rid] = got
    rows = [{"id": rid, "decision": d, "why": w[:200]} for rid, (d, w) in sorted(results.items())]
    out = a.out or C.half_dir(a.half, a.sets_root, a.exp, "results", f"A-{a.round}.jsonl")
    n, digest = C.write_jsonl(out, rows)
    dec = collections.Counter(r["decision"] for r in rows)
    manifest = {"setup": "A", "half": a.half, "round": a.round, "results_sha256": digest, "judged": n,
                "dropped_ids": sorted(dropped), "not_judged": len(todo) - n, "stopped": brake["why"],
                "decisions": dict(sorted(dec.items())), "hook_sha256": C.file_sha(hook),
                "hooks_sha256": {h: C.file_sha(os.path.join(clone, h)) for h in C.LIVE_HOOKS
                                 if os.path.isfile(os.path.join(clone, h))},
                "map_sha256": (C.file_sha(os.path.join(clone, "governance/project/path-map.yaml"))
                               if os.path.isfile(os.path.join(clone, "governance/project/path-map.yaml")) else None),
                "python": py, "inputs_sha256": {os.path.basename(os.path.dirname(p)) + "/" + os.path.basename(p):
                                                C.file_sha(p) for p in paths if os.path.exists(p)},
                "seconds": round(time.monotonic() - t0, 1)}
    with open(out[:-len(".jsonl")] + ".manifest.json", "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    C.say(f"judged {n} of {len(todo)}: {dict(sorted(dec.items()))}; results sha256 {digest}; "
          f"{manifest['seconds']} s")
    if brake["why"]:
        C.say("STOPPED:", brake["why"])
        return 3
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("trees")
    t.add_argument("--sets-root")
    t.add_argument("--exp", default=C.EXP)
    r = sub.add_parser("run")
    r.add_argument("--half", choices=C.HALVES, required=True)
    r.add_argument("--round", default="1")
    r.add_argument("--sets-root")
    r.add_argument("--exp", default=C.EXP)
    r.add_argument("--home")
    r.add_argument("--hook")
    r.add_argument("--clone")
    r.add_argument("--py")
    r.add_argument("--input", action="append")
    r.add_argument("--out")
    r.add_argument("--workers", type=int, default=int(os.environ.get("SGX_WORKERS", "6")))
    r.add_argument("--timeout", type=float, default=90.0)
    r.add_argument("--max-seconds", type=float, default=0.0)
    r.add_argument("--dry", action="store_true")
    a = p.parse_args(argv)
    return cmd_trees(a) if a.cmd == "trees" else cmd_run(a)


if __name__ == "__main__":
    sys.exit(main())
