#!/usr/bin/env python3
"""Show each non-allow live decision with the matched call's input (first 260 chars), for hand labelling."""
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


rows = []
for path in sorted(glob.glob(os.path.expanduser("~/.gov-os/guard-calls/????-??-??.jsonl"))):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if UUID.match(r.get("session", "")) and r.get("tree") in ("main", "worktree") and r["decision"] != "allow":
                rows.append(r)
want = {r["sha256"]: r for r in rows}
inputs = {}
root = os.path.expanduser("~/.claude/projects")
files = glob.glob(os.path.join(root, "-home-usain-Dynamic-Agentic-Engineering-OS", "**", "*.jsonl"), recursive=True)
files += glob.glob(os.path.join(root, "-home-usain-gov-os-worktrees-*", "**", "*.jsonl"), recursive=True)
for p in files:
    if os.path.getmtime(p) < 1762650000:
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
                    if h in want and h not in inputs:
                        inputs[h] = b["input"]
for i, r in enumerate(rows, 1):
    tin = inputs.get(r["sha256"])
    if tin is None:
        text = "(no match)"
    else:
        text = tin.get("command") or tin.get("file_path") or tin.get("pattern") or json.dumps(tin)
        text = re.sub(r"\s+", " ", str(text))[:260]
    print("%2d %s %-9s %-26s %-5s %-12s | %s" % (i, r["time"][5:16], r["rule"], r["role"], r["tool"], r["ticket"], text))
