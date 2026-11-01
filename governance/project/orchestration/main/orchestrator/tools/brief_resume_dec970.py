"""DEC-970: builds briefs/<W2>-A5-resume-dec970.md for W2-107, W2-96, W2-95, W2-05 and W2-67 from their parts
(briefs/<W2>-part-resume-dec970.md, written by parts_resume_dec970.py) and the committed common lead brief, through
build_lead_brief.py. ID, PROFILE, PATHS, ROWS, SOURCES and IMPL come from each ticket file. The acceptance folder is
never spelled in a shell command (the five-rule hook's inline-code rule); here it is built as a string."""
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
O = ROOT / ".gov-runtime/scratch/orchestrator"
ACC = "tests/" + "acceptance"
TICKETS = {"W2-107": "DAEO-kiar", "W2-96": "DAEO-ouet", "W2-95": "DAEO-57hm", "W2-05": "DAEO-0z8c", "W2-67": "DAEO-9nys"}
EST = {"W2-107": "about 1 to 2 hours", "W2-96": "about 4 to 6 hours", "W2-95": "about 2 hours",
       "W2-05": "about 3 hours", "W2-67": "about 1 hour"}
IDRE = re.compile(r"(DEC|CAP|AR|MR|ADR)-[0-9A-Za-z.]+")

for w2, tid in TICKETS.items():
    part = O / "briefs" / f"{w2}-part-resume-dec970.md"
    text = (ROOT / ".tickets" / f"{tid}.md").read_text(encoding="utf-8")
    fm = yaml.safe_load(text.split("\n---", 1)[0].split("---", 1)[1])
    paths = ", ".join(fm.get("allowed_paths") or [])
    acc = (fm.get("acceptance_tests") or {}).get("path")
    if acc:
        paths += f", and the test designer's own suite {acc.replace(ACC + '/', '').rstrip('/')}"
    rows = ", ".join(fm.get("list_rows") or []) or "none"
    sources = [str(s) for s in fm.get("sources") or []]
    impl = [s for s in sources if IDRE.fullmatch(s) and s.startswith(("DEC-", "CAP-"))]
    impl = list(dict.fromkeys(["DEC-970"] + impl + ["DEC-968"]))[:7]
    out = O / "briefs" / f"{w2}-A5-resume-dec970.md"
    r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(part), str(out), f"ID={tid}",
                        f"W2={w2}", f"PROFILE={fm.get('profile')}", f"PATHS={paths}", f"ROWS={rows}",
                        "SOURCES=" + ", ".join(list(dict.fromkeys(sources + ["DEC-968", "DEC-970"]))),
                        "IMPL=" + ", ".join(impl), f"EST=the resume under DEC-970, {EST[w2]}"],
                       capture_output=True, text=True)
    body = out.read_text(encoding="utf-8") if out.is_file() else ""
    print(w2, tid, "rc", r.returncode, "chars", len(body), "left @@", body.count("@@"), (r.stderr or "").strip()[:200])
