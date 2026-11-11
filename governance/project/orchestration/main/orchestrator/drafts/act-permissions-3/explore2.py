#!/usr/bin/env python3
"""Exploration 2 (not the rehearsal): the Bash and Monitor forms. Headless Haiku sessions in a stand-in project.

    python3 explore2.py <scratch folder> <variant> [allow rule ...]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

CLAUDE = Path.home() / ".local/bin/claude"
S = Path(sys.argv[1]).resolve()
variant = sys.argv[2]
rules = sys.argv[3:]
shutil.rmtree(S, ignore_errors=True)
proj, tmp = S / "proj", S / "tmp"
proj.mkdir(parents=True)
subprocess.run(["git", "init", "-q", str(proj)], check=True)
(tmp / "gov-os-emg-a").mkdir(parents=True)
(proj / "f.txt").write_text("F\n")
(tmp / "gov-os-emg-a/log.txt").write_text("run done\n")

settings = {"permissions": {"allow": [r.replace("TMP", f"/{tmp}") for r in rules]}} if rules else {"permissions": {}}
cfg = S / "settings.json"
cfg.write_text(json.dumps(settings, indent=2))
a = f"{tmp}/gov-os-emg-a"
steps = [
    f"Run with the Bash tool: cd {a} && python3 -m venv --without-pip v1; ls v1 | head -3",
    f"Run with the Bash tool: cp {proj}/f.txt {a}/f2.txt",
    f"Run with the Bash tool: cd {proj}; export TMPDIR={a}/t; mkdir -p $TMPDIR; python3 -c 'print(1)' > {a}/out.txt 2>&1; tail -2 {a}/out.txt | cut -c1-50",
    f"Use the Monitor tool with the command: until grep -q done {a}/log.txt; do sleep 1; done; echo finished",
]
lines = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
prompt = ("Do exactly these steps, nothing else, each as one tool call, in order, even if one is refused. Then answer "
          f"with one line per step: `<n>: done` or `<n>: DENIED`, adding the exact tool error text if a tool is not available.\n{lines}")
r = subprocess.run([str(CLAUDE), "-p", prompt, "--settings", str(cfg), "--model", "claude-haiku-5-5",
                    "--output-format", "json", "--max-turns", "10"], cwd=proj, capture_output=True, text=True,
                   timeout=600)
try:
    out = json.loads(r.stdout)
except ValueError:
    print(r.stdout, r.stderr)
    sys.exit(1)
print("answer:", out.get("result"))
for d in out.get("permission_denials") or []:
    print("denied:", d.get("tool_name"), json.dumps(d.get("tool_input"))[:200])
for rel in ("v1", "f2.txt", "out.txt", "t"):
    print("exists" if (tmp / "gov-os-emg-a" / rel).exists() else "absent ", rel)
