#!/usr/bin/env python3
"""The guard's refusals, harvested from every Claude Code session transcript on this machine (owner, DEC-958).

    python3 guard_refusals.py [--since 2026-10-30T21:30] [--quiet]

Scans ~/.claude/projects/**/*.jsonl (main tree, worktrees, subagents) for tool results refused by a PreToolUse hook.
Each refusal not yet in log/guard-refusals.jsonl is appended with: time, transcript, cwd, tool, the command's form
(first 200 characters, one line), the hook's reason (the rule). The fields `verdict` (true | false-positive), `cost`
and `note` start empty; the orchestrator fills them by hand (`--classify <key> <verdict> "<cost>" "<note>"`).
Prints the new ones, then the counts: total, false positives, unclassified.
"""
import argparse
import glob
import json
import os
from pathlib import Path

LOG = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl")
ACT1 = "2026-10-30T21:30"


def load():
    rows = []
    if LOG.is_file():
        rows = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
    return rows


def save(rows):
    # Atomic: a temp file in the same folder, then a rename, so a reader never sees a truncated log (dispatcher review
    # round 2, F1).
    tmp = LOG.with_name(LOG.name + ".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    tmp.replace(LOG)


def form(inp):
    if not isinstance(inp, dict):
        return str(inp)[:200]
    text = inp.get("command") or inp.get("file_path") or inp.get("path") or json.dumps(inp)[:200]
    return " ".join(str(text).split())[:200]


def harvest(since):
    found = []
    for path in glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True):
        try:
            if os.path.getmtime(path) < 0:
                continue
            lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        if not any("hook error" in l or '"source":"hook"' in l for l in lines):
            continue
        uses, cwd = {}, ""
        for l in lines:
            try:
                rec = json.loads(l)
            except ValueError:
                continue
            cwd = rec.get("cwd") or cwd
            msg = rec.get("message") or {}
            content = msg.get("content") if isinstance(msg, dict) else None
            if not isinstance(content, list):
                continue
            for c in content:
                if not isinstance(c, dict):
                    continue
                if c.get("type") == "tool_use":
                    uses[c.get("id")] = (c.get("name"), c.get("input"))
                elif c.get("type") == "tool_result" and c.get("is_error"):
                    pd = rec.get("permissionDecision") or {}
                    text = c.get("content")
                    text = text if isinstance(text, str) else json.dumps(text)
                    if pd.get("source") != "hook" and "hook error" not in text:
                        continue
                    if "DEC-953 item 2" not in text:  # the five-rule hook's own reasons only (not the old guard's)
                        continue
                    ts = rec.get("timestamp", "")
                    if ts < since:
                        continue
                    name, inp = uses.get(c.get("tool_use_id"), ("?", None))
                    reason = text.split("hook error:", 1)[-1].strip()[:300]
                    row = {"key": c.get("tool_use_id"), "time": ts, "transcript": path, "cwd": cwd,
                           "tool": name, "form": form(inp), "rule": reason, "verdict": "", "cost": "", "note": ""}
                    if name == "Bash" and isinstance(inp, dict) and now_allowed(name, inp, cwd):
                        row.update(verdict="false-positive", cost="about 1 min (estimated)",
                                   note="auto: the live hook now allows it (fixed by ACT-GUARD-FIX-1 or -2; the "
                                        "session started before the fix reached its tree)")
                    found.append(row)
    return found


def now_allowed(tool, inp, cwd):
    """Whether the main tree's live five-rule hook allows this call now, judged for the engineer (the role rule 1 is
    strictest for). A refusal it now allows was a false positive fixed since; one it still refuses wakes the CTO."""
    import subprocess
    root = "/home/usain/Dynamic-Agentic-Engineering-OS"
    py = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
    event = {"tool_name": tool, "tool_input": inp, "cwd": cwd or root, "session_id": "refusal-scan"}
    env = dict(os.environ, GOV_ROLE="engineer", GOV_TICKET="DAEO-sdxk", CLAUDE_PROJECT_DIR=root)
    try:
        p = subprocess.run([py, "-E", root + "/.claude/hooks/pretooluse.py"], input=json.dumps(event),
                           capture_output=True, text=True, env=env, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    if p.returncode == 2:
        return False
    out = p.stdout.strip()
    return not out or json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "allow"


def known_pattern(command, cwd):
    """ACT-GUARD-FIX-1's pattern: the write parser calls the command read-only (None) and it is no inline code."""
    import re
    import sys
    sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/src")
    try:
        from gov.guard.decide import _extract_bash_write_targets
        read_only = _extract_bash_write_targets(command, cwd or "/tmp") is None
    except Exception:
        return False
    return read_only and not re.search(r"\b(python3?|perl|node|ruby)\s+(-\w*\s+)*-[cei]\b", command)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=ACT1)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--classify", nargs=4, metavar=("KEY", "VERDICT", "COST", "NOTE"))
    a = ap.parse_args()
    rows = load()
    if a.classify:
        key, verdict, cost, note = a.classify
        for r in rows:
            if r.get("key", "").endswith(key):
                r.update(verdict=verdict, cost=cost, note=note)
        save(rows)
    else:
        seen = {r.get("key") for r in rows}  # hand-written rows carry no key
        new = [r for r in harvest(a.since) if r["key"] not in seen]
        new.sort(key=lambda r: r["time"])
        rows += new
        save(rows)
        if not a.quiet:
            for r in new:
                if r.get("verdict"):  # a known pattern, marked automatically: counted, not woken for
                    continue
                print(f"NEW {r['key'][-10:]} {r['time'][:19]} {r['cwd']} {r['tool']}: {r['form'][:120]} -> {r['rule'][:120]}")
    fp = sum(1 for r in rows if (r.get("verdict") or r.get("judgement")) == "false-positive")
    un = sum(1 for r in rows if not (r.get("verdict") or r.get("judgement")))
    print(f"guard refusals since ACT 1: {len(rows)} total, {fp} false positives, {un} unclassified")


if __name__ == "__main__":
    main()
