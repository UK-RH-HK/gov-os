"""DEC-982: files W2-112, W2-113 and W2-114 from their drafts (tk create, the draft written in place).
Writes log/tickets-2026-10-31-dec982.json. Safe to re-run."""
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
D = ROOT / ".gov-runtime/scratch/orchestrator/drafts/tickets"
MAP = ROOT / ".gov-runtime/scratch/orchestrator/log/tickets-2026-10-31-dec982.json"
done = json.loads(MAP.read_text()) if MAP.exists() else {}
for w2 in ("W2-112", "W2-113", "W2-114"):
    if w2 in done:
        continue
    text = (D / f"{w2}.md").read_text(encoding="utf-8")
    title = re.search(r"^title: '(.*)'$", text, re.M).group(1).replace("''", "'")
    prio = re.search(r"^priority: (\d)$", text, re.M).group(1)
    tid = subprocess.run(["tk", "create", title, "-p", prio, "--external-ref", w2], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip().split()[-1]
    path = ROOT / ".tickets" / (tid + ".md")
    created = re.search(r"^created: (\S+)$", path.read_text(encoding="utf-8"), re.M).group(1)
    path.write_text(text.replace("ID-PLACEHOLDER", tid).replace("CREATED-PLACEHOLDER", created), encoding="utf-8")
    done[w2] = tid
    MAP.write_text(json.dumps(done) + "\n", encoding="utf-8")
print(json.dumps(done))
