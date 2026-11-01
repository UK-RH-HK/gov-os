"""Build one lead brief from a part (DEC-991 session, the ten-lead plan): fill @@ID@@, then build_lead_brief.py with
the ticket's own fields. @@HEAD@@ is left for the CTO (filled after the worktree is created or merged).

    python3 build_ten.py <W2> <part.md> <run label> <IMPL ids comma-separated> <EST text>
"""
import glob
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
B = ROOT / ".gov-runtime/scratch/orchestrator/briefs"
w2, part, run, impl, est = sys.argv[1:6]
tid = d = None
for p in glob.glob(str(ROOT / ".tickets/*.md")):
    s = open(p).read()
    try:
        fm = yaml.safe_load(s.split("\n---", 1)[0].lstrip("-\n"))
    except Exception:
        continue
    if fm.get("wbs_id") == w2:
        tid, d = fm["id"], fm
        break
if not d:
    sys.exit(f"no ticket {w2}")
filled = B / (Path(part).stem + ".filled.md")
filled.write_text(Path(part).read_text().replace("@@ID@@", tid))
out = B / f"{w2}-A5-{run}.md"
vals = {"ID": tid, "W2": w2, "PROFILE": str(d.get("profile")),
        "PATHS": ", ".join(d.get("allowed_paths") or []),
        "ROWS": ", ".join(d.get("list_rows") or []) or "none",
        "SOURCES": ", ".join(str(x) for x in (d.get("sources") or [])),
        "IMPL": impl, "EST": est}
r = subprocess.run([sys.executable, str(ROOT / ".gov-runtime/scratch/orchestrator/tools/build_lead_brief.py"),
                    str(filled), str(out), *[f"{k}={v}" for k, v in vals.items()]], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip())
txt = out.read_text() if out.exists() else ""
print(f"{w2} {tid}: @@ID@@ left {txt.count('@@ID@@')}, @@HEAD@@ {txt.count('@@HEAD@@')}, chars {len(txt)}")
sys.exit(r.returncode)
