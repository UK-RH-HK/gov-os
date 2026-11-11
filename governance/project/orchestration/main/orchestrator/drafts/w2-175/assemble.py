"""Assemble W2-175-A5-run1.md: head part (KPI table from `gov brief lead W2-175 --run build`'s own output, JUDGEMENT.md whole)
+ the common lead brief whole with every slot filled. Form of drafts/w2-05/assemble.py."""
import re
import sys

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
SCRATCH = ROOT + "/.gov-runtime/scratch/orchestrator/drafts/w2-175"
HEAD = SCRATCH + "/head.md"
GOVBRIEF = SCRATCH + "/tmp/gb-lead-build.txt"
OUT = ROOT + "/.gov-runtime/scratch/orchestrator/briefs/W2-175-A5-run1.md"

slots = {
    "{ID}": "DAEO-wahn",
    "{W2}": "W2-175",
    "{PROFILE}": "STANDARD",
    "{PATHS}": "template/governance/kernel/templates/role-*.md, docs/changes/W2-175-CIT-P.md",
    "{ROWS}": "none (the ticket takes no list rows)",
    "{SOURCES}": ("DEC-1137, DEC-820, DEC-861, DEC-1116, DEC-1050, DEC-1121, DEC-957, DEC-963, DEC-1073, DEC-315, CAP-33, "
                  "DAEO-t8mp, DAEO-k7hz, DAEO-h4rh"),
    "{IMPL}": "DEC-1137, DEC-820, DEC-861",
    "{EST}": "60 lines of template text and record",
}

govbrief = open(GOVBRIEF, encoding="utf-8").read()
start = govbrief.index("## What must be true")
stop = govbrief.index("## Inputs")
table = govbrief[start:stop].rstrip("\n")
table = table.replace("{DATE}", "[DATE]")  # the ticket writes the template key in braces; shown in brackets so no brace slot is left
table += ("\n(This table is `gov brief lead W2-175 --run build`'s own, 2026-11-11 20:00 UTC; the ticket file holds the truth. "
          "Where the ticket writes a template key in braces, here DATE, it is shown in square brackets.)")

head = open(HEAD, encoding="utf-8").read()
assert "<<KPI-TABLE>>" in head and "<<JUDGEMENT>>" in head
head = head.replace("<<KPI-TABLE>>", table)
judgement = open(ROOT + "/governance/project/briefs/JUDGEMENT.md", encoding="utf-8").read().rstrip("\n")
head = head.replace("<<JUDGEMENT>>", judgement)
head = head.rstrip("\n") + "\n\n"

common = open(ROOT + "/governance/project/briefs/LEAD-w2-common.md", encoding="utf-8").read()
for key, value in slots.items():
    common = common.replace(key, value)

text = head + common
open(OUT, "w", encoding="utf-8").write(text)

left = sorted(set(re.findall(r"\{[A-Z][A-Z0-9_:]*\}", text)))
ats = text.count("@@")
markers = re.findall(r"<<[A-Z-]+>>", text)
full_hashes = re.findall(r"\b[0-9a-f]{40}\b", text)
print("bytes", len(text.encode()), "lines", text.count("\n"), "slots left", left, "@@", ats, "markers", markers, "40-hex", len(full_hashes))
sys.exit(1 if (left or ats or markers or full_hashes or not text.strip()) else 0)
