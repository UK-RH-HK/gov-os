#!/usr/bin/env python3
"""Exploration 4 (not the rehearsal): does a session started in a git worktree read the main tree's untracked
.claude/settings.local.json? Stand-in repository and worktree; a headless Haiku session in the worktree.

    python3 explore4.py <scratch folder>
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

CLAUDE = Path.home() / ".local/bin/claude"
S = Path(sys.argv[1]).resolve()
shutil.rmtree(S, ignore_errors=True)
main, wt, tmp = S / "main", S / "wt", S / "tmp"
main.mkdir(parents=True)
(tmp / "gov-os-emg-a").mkdir(parents=True)
(tmp / "gov-os-emg-a/r.txt").write_text("TOKEN-R\n")
run = lambda *a, cwd=main: subprocess.run(a, cwd=cwd, check=True, capture_output=True)
run("git", "init", "-q", "-b", "main")
(main / "f.txt").write_text("f\n")
run("git", "add", "f.txt")
run("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x")
run("git", "worktree", "add", "-q", str(wt), "-b", "w")
(main / ".claude").mkdir()
(main / ".claude/settings.local.json").write_text(json.dumps(
    {"permissions": {"allow": [f"Read(/{tmp}/gov-os-emg-*/**)"]}}))
print("worktree has settings.local.json:", (wt / ".claude/settings.local.json").exists())
prompt = f"Read the file {tmp}/gov-os-emg-a/r.txt with the Read tool and answer with its text, or DENIED if refused."
for name, cwd in (("main", main), ("worktree", wt)):
    r = subprocess.run([str(CLAUDE), "-p", prompt, "--model", "claude-haiku-5-5", "--output-format", "json",
                        "--max-turns", "4"], cwd=cwd, capture_output=True, text=True, timeout=300)
    out = json.loads(r.stdout)
    print(name, "->", str(out.get("result")).strip()[:120].replace("\n", " "),
          "| denials:", len(out.get("permission_denials") or []))
(main / ".claude/settings.local.json").unlink()
r = subprocess.run([str(CLAUDE), "-p", prompt, "--model", "claude-haiku-5-5", "--output-format", "json",
                    "--max-turns", "4"], cwd=wt, capture_output=True, text=True, timeout=300)
out = json.loads(r.stdout)
print("control, worktree without the file ->", str(out.get("result")).strip()[:120].replace("\n", " "),
      "| denials:", len(out.get("permission_denials") or []))
