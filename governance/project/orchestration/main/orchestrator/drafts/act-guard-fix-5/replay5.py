#!/usr/bin/env python3
"""ACT-GUARD-FIX-5's guard replay: the logged refusals, and the last calls of the transcripts, through the hook before
and after the change; every call refused before must still be refused, and every call newly refused is listed.

  python3 -I replay5.py <hooks-before dir> <hooks-after dir> <corpus4.json> [<calls.jsonl from build_replay_calls.py>]

A hooks dir is a copy of .claude/hooks (pretooluse.py and its modules). The corpus rows are run as test_live_hook.py's
test_the_logged_refusals_replay_as_decided runs them (the role, cwd, TMPDIR and ticket as the log and the corpus give
them), by the registered line's interpreter (the pin in ~/.local/bin/gov, -E). The calls file (optional) holds the
48-hour call set's events; only a Bash call that holds a heredoc and names a shell anywhere is run (the one place the change can
differ), each by the role the file gives (else orchestrator). Prints counts and each differing call's id, never a
command. Exit 0 when no call refused before is allowed after, else 1."""
import json
import os
import re
import subprocess
import sys

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
WORKTREES = os.path.realpath(os.path.expanduser("~/gov-os-worktrees"))
PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
E, O, A = "engineer", "orchestrator", "independent-auditor"
TWIN = {50: 54, 51: 55, 52: 58, 53: 59}
ROLE = {**{i: O for i in (61, 62, 63, 70, 71, 72)}, **{i: A for i in (64, 67, 68, 69, 75, 76)},
        **{i: E for i in (65, 66, 73, 74, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86)}}
SHELL_HEREDOC = re.compile(r"\b(ba|da|z|k)?sh\b")


def decide(hooks, event, role, ticket, project, tmpdir=None):
    env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket, CLAUDE_PROJECT_DIR=project)
    env.pop("TMPDIR", None)
    env.pop("PYTHONPATH", None)
    if tmpdir:
        env["TMPDIR"] = tmpdir
    p = subprocess.run([PY, "-E", os.path.join(hooks, "pretooluse.py")], input=json.dumps(event), capture_output=True,
                       text=True, env=env, timeout=90)
    if p.returncode == 2:
        return "deny", " ".join(p.stderr.split())
    if p.returncode != 0:
        return "error", " ".join(p.stderr.split())
    if not p.stdout.strip():
        return "allow", ""
    out = json.loads(p.stdout)["hookSpecificOutput"]
    return out["permissionDecision"], " ".join(str(out.get("permissionDecisionReason", "")).split())


def corpus_calls(path):
    rows = json.load(open(path))
    for row in rows:
        src = rows[TWIN.get(row["i"], row["i"])]
        role = (src.get("launch_role") if src.get("from") == "fix-3 corpus" else ROLE.get(src["i"])) or O
        cwd = src.get("cwd") or MAIN
        m = re.match(re.escape(WORKTREES) + r"/[^/]+", cwd)
        event = {"tool_name": src["tool"], "tool_input": src["input"], "cwd": cwd, "session_id": "guard-fix-5",
                 "agent_type": src.get("agent_type")}
        tmpdir = src.get("tmpdir")
        if tmpdir is None and src.get("from") != "fix-3 corpus":
            t = re.search(r"/tmp/gov-launch-[a-z-]+-[a-z0-9]{8}", json.dumps(src.get("input")))
            tmpdir = t.group(0) if t else None
        yield f"corpus-{row['i']}", event, role, "DAEO-sdxk", m.group(0) if m else MAIN, tmpdir


def log_calls(path):
    for line in open(path):
        try:
            c = json.loads(line)
        except ValueError:
            continue
        ev = c.get("event") or {}
        cmd = (ev.get("tool_input") or {}).get("command")
        if ev.get("tool_name") != "Bash" or not isinstance(cmd, str) or "<<" not in cmd or not SHELL_HEREDOC.search(cmd):
            continue
        cwd = ev.get("cwd") or MAIN
        m = re.match(re.escape(WORKTREES) + r"/[^/]+", cwd)
        yield (str(c.get("id")), dict(ev, session_id="guard-fix-5"), c.get("role") or O, c.get("ticket") or "DAEO-sdxk",
               m.group(0) if m else MAIN, None)


def main():
    before, after, corpus = sys.argv[1:4]
    calls = list(corpus_calls(corpus))
    n_corpus = len(calls)
    if len(sys.argv) > 4:
        calls += list(log_calls(sys.argv[4]))
    ref_b, ref_a, lost, new = 0, 0, [], []
    errors, reasons = [], []
    for cid, event, role, ticket, project, tmpdir in calls:
        b, _ = decide(before, event, role, ticket, project, tmpdir)
        a, why = decide(after, event, role, ticket, project, tmpdir)
        if "error" in (a, b):
            errors.append(cid)
        ref_b += b != "allow"
        ref_a += a != "allow"
        if b != "allow" and a == "allow":
            lost.append(cid)
        if b == "allow" and a != "allow":
            new.append(cid)
            reasons.append(f"  {cid} ({role}): {why[:150]}")
    print(f"calls: {len(calls)} (corpus {n_corpus}, shell heredoc calls of the call set {len(calls) - n_corpus})")
    print(f"refused before: {ref_b}; refused after: {ref_a}")
    print(f"refused before, allowed after: {len(lost)} {' '.join(lost)}")
    print(f"allowed before, refused after (replay_refused): {len(new)} {' '.join(new)}")
    for line in reasons:
        print(line)
    print(f"hook errors: {len(errors)} {' '.join(errors)}")
    print("replay: " + ("every refused call is still refused" if not lost and not errors else "FAILED"))
    sys.exit(0 if not lost and not errors else 1)


main()
