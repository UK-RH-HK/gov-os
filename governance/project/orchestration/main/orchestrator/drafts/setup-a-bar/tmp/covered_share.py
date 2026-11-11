#!/usr/bin/env python3
"""Rough share of live tool calls whose input text names a path-map-covered place. Reads only the tool_use blocks
(name, input) of assistant records since the call log began; never a tool result. Counts only; prints no input text."""
import collections
import glob
import json
import os
import sys
from datetime import datetime, timezone

SINCE = datetime(2026, 11, 9, 18, 13, tzinfo=timezone.utc)
MARKERS = {
    "acceptance": "tests/acceptance",
    "sets-root": "gov-os-eval",
    "hidden-dir": "/hidden",
    "operator": "gov-os-operator",
    "call-log": ".gov-os/guard-calls",
    "projects-dir": ".claude/projects",
    "memory-verdict": "memory-verdict",
}
TOOLS = ("Read", "Grep", "Glob", "Edit", "Write", "MultiEdit", "NotebookEdit", "Bash")
root = os.path.expanduser("~/.claude/projects")
files = []
for d in glob.glob(os.path.join(root, "-home-usain-Dynamic-Agentic-Engineering-OS")) + \
        glob.glob(os.path.join(root, "-home-usain-gov-os-worktrees-*")):
    for p in glob.glob(os.path.join(d, "**", "*.jsonl"), recursive=True):
        if os.path.getmtime(p) >= SINCE.timestamp():
            files.append(p)
tot = collections.Counter()
by_tool = collections.Counter()
hit_tool = collections.Counter()
seen = set()
for p in files:
    try:
        fh = open(p, encoding="utf-8", errors="replace")
    except OSError:
        continue
    with fh:
        for line in fh:
            if '"tool_use"' not in line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            ts = rec.get("timestamp", "")
            try:
                t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                continue
            if t < SINCE:
                continue
            msg = rec.get("message") or {}
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for b in content:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                if b.get("name") not in TOOLS:
                    continue
                uid = b.get("id")
                if uid in seen:
                    continue
                seen.add(uid)
                text = json.dumps(b.get("input", {}))
                tot["calls"] += 1
                by_tool[b["name"]] += 1
                hit = [k for k, m in MARKERS.items() if m in text]
                if hit:
                    tot["any"] += 1
                    hit_tool[b["name"]] += 1
                for k in hit:
                    tot[k] += 1
print("files", len(files))
print(dict(tot))
print("by tool", dict(by_tool))
print("hit by tool", dict(hit_tool))
