"""Assemble W2-05-A5-r7-fix.md: head part + JUDGEMENT.md whole + the common lead brief whole with every slot filled."""
import re
import sys

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
HEAD = ROOT + "/.gov-runtime/scratch/orchestrator/drafts/w2-05/head.md"
OUT = ROOT + "/.gov-runtime/scratch/orchestrator/briefs/W2-05-A5-r7-fix.md"

slots = {
    "{ID}": "DAEO-0z8c",
    "{W2}": "W2-05",
    "{PROFILE}": "FULL",
    "{PATHS}": ("tests/conftest.py, src/gov/**/*.py (limited to calls that start git), src/gov/util/gitenv.py, lefthook.yml, "
                "template/lefthook.yml, template/.rulesync/hooks.jsonc, tests/unit/gitenv/**, docs/research/AR-2-git-sweep.md"),
    "{ROWS}": "W2-L109, W2-L160, W2-M012, W2-M105, W2-M113, W2-M161, W2-M231, W2-M281",
    "{SOURCES}": ("DEC-710, DEC-971, DEC-580, DEC-712, DEC-777, DEC-783, DEC-802, DEC-804, DEC-805, DEC-807, DEC-906, "
                  "DEC-951, DEC-953, DEC-970, DEC-980"),
    "{IMPL}": "DEC-710, DEC-712, DEC-580",
    "{EST}": "100 lines of code, tests and record",
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
print("bytes", len(text.encode()), "lines", text.count("\n"), "slots left", left)
sys.exit(1 if left else 0)
