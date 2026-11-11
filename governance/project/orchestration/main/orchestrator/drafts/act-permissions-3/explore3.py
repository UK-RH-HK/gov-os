#!/usr/bin/env python3
"""Exploration 3 (not the rehearsal): which part of the queued Bash call at 01:16:25 made the CLI ask. Each step is
one candidate, run by a headless Haiku session in a stand-in project (git init) under the user's own settings.

    python3 explore3.py <scratch folder> <step number ...>
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

CLAUDE = Path.home() / ".local/bin/claude"
S = Path(sys.argv[1]).resolve()
pick = [int(x) for x in sys.argv[2:]]
shutil.rmtree(S, ignore_errors=True)
proj, tmp = S / "proj", S / "tmp"
proj.mkdir(parents=True)
subprocess.run(["git", "init", "-q", str(proj)], check=True)
a = tmp / "gov-os-emg-a"
for d in (a / "stagedhook", a / "s1", a / "tmp"):
    d.mkdir(parents=True)
(proj / "hook.py").write_text("print('hook')\n")
(proj / ".claude/hooks").mkdir(parents=True)
(proj / ".claude/hooks/bash_writes.py").write_text("x=1\n")
(proj / "slot.sh").write_text('#!/usr/bin/env bash\n"$@"\n')
cfg = S / "settings.json"
cfg.write_text(json.dumps({"permissions": {}}))
cands = {
    1: f"cd {proj}; export TMPDIR={a}/tmp GOV_PIN_PY={a}/py; cp hook.py {a}/stagedhook/; G14_HOOK={a}/stagedhook/h.py bash {proj}/slot.sh python3 -c 'print(1)' > {a}/s1/o.txt 2>&1; tail -12 {a}/s1/o.txt | cut -c1-300",
    2: f"cd {proj}; export TMPDIR={a}/tmp GOV_PIN_PY={a}/py; echo ok",
    3: f"cd {proj}; cp hook.py {a}/stagedhook/",
    4: f"cd {proj}; G14_HOOK={a}/stagedhook/h.py bash {proj}/slot.sh python3 -c 'print(1)' > {a}/s1/o2.txt 2>&1",
    6: f"cd {proj}; cp .claude/hooks/bash_writes.py {a}/stagedhook/",
    7: f"cp {proj}/.claude/hooks/bash_writes.py {a}/stagedhook/b2.py",
    5: f"cd {proj}; bash {proj}/slot.sh python3 -c 'print(1)' > {a}/s1/o3.txt 2>&1; tail -12 {a}/s1/o3.txt | cut -c1-300",
}
steps = [f"Run with the Bash tool exactly: {cands[n]}" for n in pick]
lines = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
prompt = ("Do exactly these steps, nothing else, each as one tool call, in order, even if one is refused. Then answer "
          f"with one line per step: `<n>: done` or `<n>: DENIED`.\n{lines}")
r = subprocess.run([str(CLAUDE), "-p", prompt, "--settings", str(cfg), "--model", "claude-haiku-5-5",
                    "--output-format", "json", "--max-turns", "10"], cwd=proj, capture_output=True, text=True,
                   timeout=600)
out = json.loads(r.stdout)
print("steps:", pick)
print("answer:", out.get("result"))
for d in out.get("permission_denials") or []:
    print("denied:", d.get("tool_name"), json.dumps(d.get("tool_input"))[:260])
