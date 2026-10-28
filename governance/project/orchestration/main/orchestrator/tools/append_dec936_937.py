"""Appends DEC-936 and DEC-937 (drafts) to the register and marks DEC-855's and DEC-934's status lines (DEC-866)."""
import pathlib
import re
import sys

REG = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md")
DRAFTS = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts")
text = REG.read_text(encoding="utf-8")
if "### DEC-936 " in text or "### DEC-937 " in text:
    sys.exit("already in the register")
# Mark the first status line of DEC-855 and of DEC-934, after their opening "ACCEPTED (".
for dec, note in (("DEC-855", "changed by DEC-936 item 2.5: only P1s and ACTs ping; P2s delegated"),
                  ("DEC-934", "item 2 changed by DEC-936 item 1: a night's P1s wait until 07:30 unless the owner is active")):
    m = re.search(r"### " + dec + r" .*?\n- \*\*Status:\*\* ACCEPTED \(", text, re.S)
    if not m:
        sys.exit(dec + "'s status line not found")
    text = text[:m.end()] + note + "; " + text[m.end():]
text = text.rstrip("\n") + "\n" + (DRAFTS / "DEC-936.md").read_text(encoding="utf-8").rstrip("\n") + "\n" \
    + (DRAFTS / "DEC-937.md").read_text(encoding="utf-8")
REG.write_text(text, encoding="utf-8")
print("appended DEC-936, DEC-937; DEC-855 and DEC-934 marked")
