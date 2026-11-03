"""Every Bash call with an rm in the transcripts since 2026-10-30 (the main tree's, the worktrees' and their
subagents'), judged by the candidate's rm rule in-process (rm_refusal), to count what it would refuse.
Run by the pinned interpreter with -E: rm_history.py <hook dir> <out.json>"""
import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, sys.argv[1])
import pretooluse as h  # noqa: E402

SINCE = time.mktime((2026, 10, 30, 0, 0, 0, 0, 0, -1))
RM = re.compile(r"(?<![\w.-])rm(?![\w.-])")
files = [f for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")) +
         glob.glob(os.path.expanduser("~/.claude/projects/*/*/subagents/*.jsonl")) if os.path.getmtime(f) >= SINCE]
seen, calls = set(), []
for f in files:
    for line in open(f, errors="replace"):
        if '"Bash"' not in line or "rm" not in line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        for blk in (ev.get("message") or {}).get("content") or []:
            if isinstance(blk, dict) and blk.get("type") == "tool_use" and blk.get("name") == "Bash":
                cmd = (blk.get("input") or {}).get("command") or ""
                cwd = ev.get("cwd") or "/home/usain/Dynamic-Agentic-Engineering-OS"
                if RM.search(cmd) and (cmd, cwd) not in seen:
                    seen.add((cmd, cwd))
                    calls.append((cmd, cwd))
m = re.compile(r"(/home/usain/gov-os-worktrees/[^/]+)")
out, t0 = [], time.time()
for cmd, cwd in calls:
    root = (m.match(cwd).group(1) if m.match(cwd) else "/home/usain/Dynamic-Agentic-Engineering-OS")
    h._JUDGED.clear()
    s = time.time()
    try:
        why = h.rm_refusal(cmd, cwd, root)
        deletes = h.bash_judgement(cmd, cwd)
        n = len(deletes.deletes) if deletes is not None else -1
    except Exception as exc:  # noqa: BLE001
        why, n = "CRASH " + repr(exc), -2
    out.append({"command": cmd, "cwd": cwd, "refused": why, "deletes": n, "s": round(time.time() - s, 3)})
json.dump(out, open(sys.argv[2], "w"), indent=1)
ref = [o for o in out if o["refused"]]
print(f"{len(files)} transcripts, {len(out)} distinct Bash calls with an rm word; "
      f"{sum(o['deletes'] > 0 for o in out)} with rm operands read, {sum(o['deletes'] == -1 for o in out)} unreadable "
      f"(crude scan), {sum(o['deletes'] == -2 for o in out)} crashed; refused {len(ref)}; slowest "
      f"{max((o['s'] for o in out), default=0)} s; total {time.time() - t0:.0f} s")
for o in ref:
    print("  REFUSED:", repr(o["command"][:160]), "| cwd", o["cwd"][-40:], "|", o["refused"][:140])
