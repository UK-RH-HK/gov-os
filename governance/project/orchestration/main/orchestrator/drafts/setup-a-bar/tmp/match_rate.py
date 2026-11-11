#!/usr/bin/env python3
"""Can the call log's live lines be matched to a transcript's tool_use by the action hash? Counts only.
Reads the log's day files (hashes only; never salt.key) and the transcripts' tool_use blocks (name, input only)."""
import collections
import glob
import hashlib
import json
import os
import re

UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def action_hash(tool, tin):
    b = json.dumps({"tool": tool, "input": tin}, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False).encode("utf-8", "surrogatepass")
    return hashlib.sha256(b).hexdigest()


logrows = collections.defaultdict(list)
for path in sorted(glob.glob(os.path.expanduser("~/.gov-os/guard-calls/????-??-??.jsonl"))):
    day = os.path.basename(path)[:10]
    if day < "2026-11-10":
        continue
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if UUID.match(r.get("session", "")) and r.get("tree") in ("main", "worktree"):
                logrows[day].append(r)
want = {r["sha256"] for rows in logrows.values() for r in rows}
found = set()
root = os.path.expanduser("~/.claude/projects")
files = glob.glob(os.path.join(root, "-home-usain-Dynamic-Agentic-Engineering-OS", "**", "*.jsonl"), recursive=True)
files += glob.glob(os.path.join(root, "-home-usain-gov-os-worktrees-*", "**", "*.jsonl"), recursive=True)
for p in files:
    if os.path.getmtime(p) < 1762650000:  # before 2026-11-09
        continue
    with open(p, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"tool_use"' not in line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            content = (rec.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use" and isinstance(b.get("input"), dict):
                    h = action_hash(b.get("name", ""), b["input"])
                    if h in want:
                        found.add(h)
for day, rows in sorted(logrows.items()):
    cov = collections.Counter()
    for r in rows:
        k = "file/bash" if r["tool"] in ("Read", "Grep", "Glob", "Edit", "Write", "MultiEdit", "NotebookEdit", "Bash") else "other-tool"
        cov[k + (" matched" if r["sha256"] in found else " unmatched")] += 1
    refused = [r for r in rows if r["decision"] != "allow"]
    print(day, len(rows), dict(cov), "non-allow:", len(refused), "of them matched:", sum(1 for r in refused if r["sha256"] in found))
