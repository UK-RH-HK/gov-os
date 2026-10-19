"""Which tickets' allowed_paths hold the files of the fix round (DEC-612, DEC-613, DEC-616)?"""
import fnmatch
import glob
import yaml

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS/"
FILES = [
    "src/gov/check/runner.py", "src/gov/context/context_check.py", "src/gov/check/schema.py",
    "src/gov/cli/checks.py", "governance/kernel/checks/core-schema.yaml",
    "template/governance/kernel/checks/retrieval-regression.yaml",
    "governance/kernel/schemas/record.schema.json", ".rulesync/subagents/orchestrator.md",
    ".rulesync/skills/orchestration/SKILL.md", "template/.rulesync/skills/orchestration/SKILL.md",
    "src/gov/checkpoint/__init__.py",
]
for path in sorted(glob.glob(ROOT + ".tickets/*.md")):
    text = open(path, encoding="utf-8").read()
    front = yaml.safe_load(text.split("---")[1])
    pats = front.get("allowed_paths") or []
    hits = [f for f in FILES if any(fnmatch.fnmatch(f, p) or f.startswith(p.rstrip("*").rstrip("/") + "/") for p in pats)]
    if hits:
        print(front.get("wbs_id"), front.get("id"), front.get("status"), front.get("profile"), "|", hits)
