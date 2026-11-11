#!/usr/bin/env python3
"""Exploration (not the rehearsal): which of the form's calls does the permission layer ask about, with and without a
candidate rule? Headless Haiku sessions in a stand-in project of its own (git init, so the main tree's settings and
hooks are not read). Every path is under the given scratch folder; nothing real is read or written.

    python3 explore.py <scratch folder> <variant>   variant: base | rule
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

CLAUDE = Path.home() / ".local/bin/claude"
S = Path(sys.argv[1]).resolve()
variant = sys.argv[2]
shutil.rmtree(S, ignore_errors=True)
proj, tmp = S / "proj", S / "tmp"
proj.mkdir(parents=True)
subprocess.run(["git", "init", "-q", str(proj)], check=True)
for d in ("gov-os-emg-a", "other", "claude-1000/-home-usain/Dynamic"):
    (tmp / d).mkdir(parents=True)
(tmp / "gov-os-emg-a/r.txt").write_text("TOKEN-R\n")
(tmp / "gov-os-emg-a/e.txt").write_text("before\n")
(tmp / "other/r.txt").write_text("TOKEN-OTHER\n")

settings = {"permissions": {}}
if variant == "rule":
    settings["permissions"]["allow"] = [f"Edit(/{tmp}/gov-os-emg-*/**)", f"Read(/{tmp}/gov-os-emg-*/**)"]
cfg = S / "settings.json"
cfg.write_text(json.dumps(settings, indent=2))

steps = [
    f"Write the text hello to the new file {tmp}/gov-os-emg-a/w1.txt with the Write tool.",
    f"Read {tmp}/gov-os-emg-a/e.txt with the Read tool, then use the Edit tool on it to replace the text before with after (two tool calls).",
    f"Read the file {tmp}/gov-os-emg-a/r.txt with the Read tool.",
    f"Write the text hello to the new file {tmp}/other/w2.txt with the Write tool.",
    f"Read the file {tmp}/other/r.txt with the Read tool.",
    f"Write the text hello to the new file {tmp}/claude-1000/-home-usain/Dynamic/x.txt with the Write tool.",
    f"Run with the Bash tool: echo hi > {tmp}/gov-os-emg-a/o.txt",
]
lines = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
prompt = ("Do exactly these steps, nothing else, each as one tool call, in order, even if one is refused. Then answer "
          f"with one line per step: `<n>: done` or `<n>: DENIED`.\n{lines}")
r = subprocess.run([str(CLAUDE), "-p", prompt, "--settings", str(cfg), "--model", "claude-haiku-5-5",
                    "--output-format", "json", "--max-turns", "14"], cwd=proj, capture_output=True, text=True,
                   timeout=600)
try:
    out = json.loads(r.stdout)
except ValueError:
    print(r.stdout, r.stderr)
    sys.exit(1)
print("answer:", out.get("result"))
for d in out.get("permission_denials") or []:
    print("denied:", d.get("tool_name"), json.dumps(d.get("tool_input"))[:160])
for rel in ("gov-os-emg-a/w1.txt", "gov-os-emg-a/o.txt", "other/w2.txt", "claude-1000/-home-usain/Dynamic/x.txt"):
    print("exists" if (tmp / rel).exists() else "absent ", rel)
print("e.txt:", (tmp / "gov-os-emg-a/e.txt").read_text().strip())
