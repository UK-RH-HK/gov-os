"""Appends DEC-939, DEC-940 and DEC-941 (drafts) to the register and marks the status lines they change (DEC-866):
DEC-938 (by DEC-939 item 1 and DEC-941 item 4c), DEC-831 and DEC-847 (by DEC-941), DEC-936 (by DEC-941 item 4c)."""
import pathlib
import re
import sys

REG = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md")
DRAFTS = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts")
text = REG.read_text(encoding="utf-8")
for dec in ("DEC-939", "DEC-940", "DEC-941"):
    if "### " + dec + " " in text:
        sys.exit(dec + " is already in the register")
MARKS = (
    ("DEC-938", "item 3's schedule applied with background waits and a 07:45 watchdog (DEC-939 item 1); its digest "
                "folded into the morning package (DEC-941 item 4c)"),
    ("DEC-936", "item 2.5's digest folded into the morning package (DEC-941 item 4c)"),
    ("DEC-847", "the leads' ceiling: up to 4 at once beside one verification run, until W2-20 (DEC-941 item 1d)"),
    ("DEC-831", "the slot order replaced by the re-plan's blocks (DEC-941 item 1)"),
)
for dec, note in MARKS:
    m = re.search(r"### " + dec + r" .*?\n- \*\*Status:\*\* [A-Z]+ \(", text, re.S)
    if not m:
        sys.exit(dec + "'s status line not found")
    text = text[:m.end()] + note + "; " + text[m.end():]
text = (text.rstrip("\n") + "\n" + (DRAFTS / "DEC-939.md").read_text(encoding="utf-8").rstrip("\n") + "\n"
        + (DRAFTS / "DEC-940-941.md").read_text(encoding="utf-8"))
REG.write_text(text, encoding="utf-8")
print("appended DEC-939, DEC-940, DEC-941; marked " + ", ".join(d for d, _ in MARKS))
