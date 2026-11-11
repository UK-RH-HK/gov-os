"""Assemble W2-105-A5-r4-tests.md: head part (it ends with the common brief's heading) + the common lead brief whole with every slot filled.
Form of drafts/w2-05/assemble.py; W2-105 is STANDARD with no reviewer, so JUDGEMENT.md is not appended (the head's own note says so)."""
import re
import sys

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
HEAD = ROOT + "/.gov-runtime/scratch/orchestrator/drafts/w2-105/head.md"
OUT = ROOT + "/.gov-runtime/scratch/orchestrator/briefs/W2-105-A5-r4-tests.md"

slots = {
    "{ID}": "DAEO-zpdj",
    "{W2}": "W2-105",
    "{PROFILE}": "STANDARD",
    "{PATHS}": "template/.rulesync/permissions.jsonc",
    "{ROWS}": "none (the ticket takes no list rows)",
    "{SOURCES}": "DEC-966, DEC-172, DEC-957, DEC-965, DEC-971",
    "{IMPL}": "DEC-966, DEC-172",
    "{EST}": "10 lines (the change is 2 deleted lines; this run writes none)",
}

head = open(HEAD, encoding="utf-8").read().rstrip("\n") + "\n\n"
common = open(ROOT + "/governance/project/briefs/LEAD-w2-common.md", encoding="utf-8").read()
for key, value in slots.items():
    common = common.replace(key, value)

text = head + common
open(OUT, "w", encoding="utf-8").write(text)

left = sorted(set(re.findall(r"\{[A-Z][A-Z0-9_:]*\}", text)))
ats = text.count("@@")
full_hashes = re.findall(r"\b[0-9a-f]{40}\b", text)
print("bytes", len(text.encode()), "lines", text.count("\n"), "slots left", left, "@@", ats, "40-hex", len(full_hashes))
sys.exit(1 if (left or ats or full_hashes or not text.strip()) else 0)
