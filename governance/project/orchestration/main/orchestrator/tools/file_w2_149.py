"""DEC-1101 (2)-(3) step 2, DEC-1109 (2): files W2-149 (the independent sessions' launch script) from its draft
(tk create, the draft written in place), as W2-111 and W2-146 were. Writes log/tickets-2026-11-09-w2-149.json.
Safe to re-run."""
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
D = ROOT / ".gov-runtime/scratch/orchestrator/drafts"
MAP = ROOT / ".gov-runtime/scratch/orchestrator/log/tickets-2026-11-09-w2-149.json"

if MAP.exists():
    tid = json.loads(MAP.read_text())["W2-149"]
else:
    text = (D / "tickets/W2-149.md").read_text(encoding="utf-8")
    title = re.search(r"^title: '(.*)'$", text, re.M).group(1).replace("''", "'")
    tid = subprocess.run(["tk", "create", title, "-p", "1", "--external-ref", "W2-149"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip().split()[-1]
    path = ROOT / ".tickets" / (tid + ".md")
    created = re.search(r"^created: (\S+)$", path.read_text(encoding="utf-8"), re.M).group(1)
    text = text.replace("ID-PLACEHOLDER", tid).replace("CREATED-PLACEHOLDER", created)
    path.write_text(text, encoding="utf-8")
    MAP.write_text(json.dumps({"W2-149": tid}) + "\n", encoding="utf-8")
print("W2-149", tid)
