"""Assemble W2-40-A5-run1.md: head part + JUDGEMENT.md whole + the common lead brief whole with every slot filled.
Reuses the form of drafts/w2-05/assemble.py."""
import re
import sys

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
HEAD = ROOT + "/.gov-runtime/scratch/orchestrator/drafts/w2-40/head.md"
OUT = ROOT + "/.gov-runtime/scratch/orchestrator/briefs/W2-40-A5-run1.md"

slots = {
    "{ID}": "DAEO-6ox0",
    "{W2}": "W2-40",
    "{PROFILE}": "FULL",
    "{PATHS}": "experiments/EXP-002/** (after the CTO's one-folder edit; the ticket today also names docs/research/EXP-002/**)",
    "{ROWS}": ("W2-H052, W2-I001, W2-I036, W2-I037, W2-L025, W2-L316, W2-L328, W2-M005, W2-M087, W2-M234, W2-M334, "
               "W2-M335, W2-M336, W2-M337, W2-M338, W2-M344, W2-M345, W2-M347, W2-M350 (only W2-H052, W2-M347 and "
               "W2-L328 are live: the S3 line; the others went with the lifted lines, DEC-1083)"),
    "{SOURCES}": "CAP-61.f, DEC-160, DEC-1083",
    "{IMPL}": "DEC-160, DEC-1083",
    "{EST}": "60 lines of script and record",
}

head = open(HEAD, encoding="utf-8").read().rstrip("\n") + "\n\n"
judgement = open(ROOT + "/governance/project/briefs/JUDGEMENT.md", encoding="utf-8").read().rstrip("\n")
common = open(ROOT + "/governance/project/briefs/LEAD-w2-common.md", encoding="utf-8").read()
for key, value in slots.items():
    common = common.replace(key, value)

text = (head + judgement + "\n\n\n---\n\n"
        "# The common lead brief (committed, `governance/project/briefs/LEAD-w2-common.md`), appended whole\n\n" + common)
open(OUT, "w", encoding="utf-8").write(text)

left = sorted(set(re.findall(r"\{[A-Z][A-Z0-9_:]*\}", text)))
print("bytes", len(text.encode()), "lines", text.count("\n"), "slots left", left, "@@", text.count("@@"))
sys.exit(1 if (left or "@@" in text) else 0)
