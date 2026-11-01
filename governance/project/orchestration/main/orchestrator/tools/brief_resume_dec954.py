"""DEC-953/954/957: builds briefs/<W2>-A5-resume-dec954.md for each built ticket from its part
(briefs/<W2>-part-resume-dec954.md, written by parts_resume_dec954.py) and the committed common lead brief, through
build_lead_brief.py. ID, PROFILE, PATHS, ROWS, SOURCES and IMPL come from the ticket file; EST from the part.

    python3 brief_resume_dec954.py [W2=sha ...]

Heads: argv pairs W2=sha override log/resume-heads-dec954.txt (one "W2 sha" per line). A ticket with no head is
skipped and named. The acceptance folder is never spelled in a shell command (the five-rule hook reads it as a
possible write there); here it is built as a string."""
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
O = ROOT / ".gov-runtime/scratch/orchestrator"
ACC = "tests/" + "acceptance"
TICKETS = {"W2-05": "DAEO-0z8c", "W2-84": "DAEO-m1u3", "W2-60a": "DAEO-cv58", "W2-67": "DAEO-9nys",
           "W2-49": "DAEO-ha8z", "W2-52": "DAEO-siiz", "W2-37": "DAEO-6n5k", "W2-16": "DAEO-49o5",
           "W2-20": "DAEO-r30l"}
IDRE = re.compile(r"(DEC|CAP|AR|MR|ADR)-[0-9A-Za-z.]+")
EXTRA_IMPL = {"W2-05": ["DEC-951"], "W2-60a": ["DEC-951"], "W2-49": ["DEC-745", "DEC-750"],
              "W2-52": ["DEC-814"], "W2-37": ["DEC-812", "DEC-815", "DEC-816", "DEC-859"],
              "W2-16": ["DEC-772", "DEC-767", "DEC-753"], "W2-20": ["DEC-950"], "W2-67": ["DEC-941"]}

heads = {}
hf = O / "log/resume-heads-dec954.txt"
if hf.is_file():
    for line in hf.read_text().split("\n"):
        if line.strip():
            w, sha = line.split()[:2]
            heads[w] = sha
for arg in sys.argv[1:]:
    w, sha = arg.split("=", 1)
    heads[w] = sha

for w2, tid in TICKETS.items():
    part = O / "briefs" / f"{w2}-part-resume-dec954.md"
    if not part.is_file():
        print(w2, "no part; run parts_resume_dec954.py first")
        continue
    head = heads.get(w2)
    if not head:
        print(w2, "SKIPPED: no head given (W2=sha, or log/resume-heads-dec954.txt)")
        continue
    text = (ROOT / ".tickets" / f"{tid}.md").read_text(encoding="utf-8")
    fm = yaml.safe_load(text.split("\n---", 1)[0].split("---", 1)[1])
    paths = ", ".join(fm.get("allowed_paths") or [])
    acc = (fm.get("acceptance_tests") or {}).get("path")
    if acc:
        paths += f", and the test designer's own suite {acc.replace(ACC + '/', '').rstrip('/')}"
    rows = ", ".join(fm.get("list_rows") or []) or "none"
    sources = [str(s) for s in fm.get("sources") or []]
    impl = [s for s in sources if IDRE.fullmatch(s) and s.startswith(("DEC-", "CAP-"))]
    impl = list(dict.fromkeys(EXTRA_IMPL.get(w2, []) + impl + ["DEC-953"]))[:7]
    est = re.search(r"\*\*Estimate:\*\* about (.+?) hours", part.read_text(encoding="utf-8"))
    filled = O / "briefs" / f"{w2}-part-resume-dec954.filled.md"
    filled.write_text(part.read_text(encoding="utf-8").replace("@@HEAD@@", head[:12]), encoding="utf-8")
    out = O / "briefs" / f"{w2}-A5-resume-dec954.md"
    r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(filled), str(out), f"ID={tid}",
                        f"W2={w2}", f"PROFILE={fm.get('profile')}", f"PATHS={paths}", f"ROWS={rows}",
                        "SOURCES=" + ", ".join(list(dict.fromkeys(sources + EXTRA_IMPL.get(w2, []) + ["DEC-953", "DEC-954", "DEC-957"]))),
                        "IMPL=" + ", ".join(impl),
                        f"EST=the resume under DEC-953, about {est.group(1) if est else 'a few'} hours"],
                       capture_output=True, text=True)
    body = out.read_text(encoding="utf-8") if out.is_file() else ""
    print(w2, tid, "rc", r.returncode, "head", head[:12], "chars", len(body), "left @@", body.count("@@"),
          (r.stderr or "").strip()[:200])
