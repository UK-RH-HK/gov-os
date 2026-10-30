"""Build the throwaway rules-probe repository (W2-60a, KPI line 9, lens G Q4).

Built from scratch in the lead's temp folder, the way W1-46's live tests build theirs: a fixture
engineer ticket, the repository's committed settings (less the absolute Read deny rules, as W1-46's
make_project does) and the kernel hook scripts, copied as single named files. Nothing else of this
tree is copied. Usage: python3 build_probe.py <with-rule|without-rule>
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE = Path("/home/usain/gov-os-worktrees/W2-60a")
TARGET = Path("/tmp/gov-os-lead-W2-60a/rules-probe")
TICKET = "DAEO-zp60"
HOOKS = ("posttooluse.py", "precompact.py", "pretooluse.py", "sessionstart.py", "stop.py", "subagentstop.py")
RULE = """---
paths:
  - "src/probe/**"
---
# Probe rule (W2-60a rules probe)

The probe token is KESTREL-7731-BASALT. When you are asked for the probe token, give it exactly.

EDIT-TARGET: original
"""
SAME = "VALUE = 1\n\n\ndef probe():\n    return VALUE\n"
TICKET_TEXT = f"""---
id: {TICKET}
status: in_progress
deps: []
links: []
created: 2026-10-29T16:00:00Z
type: task
priority: 1
assignee: engineer
external-ref: P60-rules-probe
tags: [probe]
wbs_id: P60-rules-probe
title: Rules probe fixture ticket
class: implementation
role: engineer
depends_on: []
allowed_paths:
- src/probe/**
- lib/probe/**
kpis:
  success:
  - The fixture component exists
  failure:
  - The fixture component is missing
profile: FULL
acceptance_tests:
  path: tests/acceptance/P60/
---
# P60 Rules probe fixture ticket
"""


def git(*args):
    subprocess.run(["git", "-C", str(TARGET), *args], check=True, capture_output=True, text=True)


def main(mode):
    if TARGET.exists():
        shutil.rmtree(TARGET)
    files = {
        "README.md": "# Rules probe fixture\n",
        ".gitignore": ".gov-runtime/\n__pycache__/\n",
        f".tickets/{TICKET}.md": TICKET_TEXT,
        "src/probe/alpha.py": SAME,
        "lib/probe/alpha.py": SAME,
    }
    if mode == "with-rule":
        files[".claude/rules/probe.md"] = RULE
    settings = json.loads((SOURCE / ".claude/settings.json").read_text(encoding="utf-8"))
    deny = settings.get("permissions", {}).get("deny", [])
    settings["permissions"]["deny"] = [r for r in deny if not r.replace(" ", "").startswith("Read(//")]
    files[".claude/settings.json"] = json.dumps(settings, indent=2) + "\n"
    for rel, text in files.items():
        path = TARGET / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for name in HOOKS:
        target = TARGET / "template/governance/kernel/hooks" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / "template/governance/kernel/hooks" / name, target)
    subprocess.run(["git", "init", "-q", "-b", "main", str(TARGET)], check=True)
    git("config", "user.name", "rules-probe")
    git("config", "user.email", "rules-probe@example.invalid")
    git("add", "-A")
    git("commit", "-q", "-m", f"rules probe fixture ({mode})")
    (TARGET / ".gov-runtime/scratch").mkdir(parents=True, exist_ok=True)
    print(f"built {TARGET} ({mode})")


if __name__ == "__main__":
    main(sys.argv[1])
