"""Appends DEC-938 (drafts/DEC-938.md) to the register and marks DEC-855's and DEC-936's status lines (DEC-866)."""
import pathlib
import re
import sys

REG = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md")
DRAFT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/DEC-938.md")
text = REG.read_text(encoding="utf-8")
if "### DEC-938 " in text:
    sys.exit("already in the register")
for dec, note in (("DEC-855", "night-time notification changed by DEC-938: the morning package and one 07:30 ping"),
                  ("DEC-936", "item 1's night-time pings replaced by DEC-938's morning package")):
    m = re.search(r"### " + dec + r" .*?\n- \*\*Status:\*\* ACCEPTED \(", text, re.S)
    if not m:
        sys.exit(dec + "'s status line not found")
    text = text[:m.end()] + note + "; " + text[m.end():]
REG.write_text(text.rstrip("\n") + "\n" + DRAFT.read_text(encoding="utf-8"), encoding="utf-8")
print("appended DEC-938; DEC-855 and DEC-936 marked")
