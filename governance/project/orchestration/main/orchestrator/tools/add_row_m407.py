"""Adds row W2-M407 (DEC-933 item 2, for every adopted product) after W2-M406 and updates the counts."""
import pathlib
import sys

LIST = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/plan/WAVE_2_LIST.md")
ROW = ("| W2-M407 | The nightly's window and length are an orchestrator script's (`tools/nightly.sh night`, "
       "`tools/nightly_estimate.py`), not the product's: an adopted product's `gov.close.nightly` has no window, no "
       "measured estimate, no clean-start conditions and no locks, and its green does not yet serve as a scoped "
       "close's base where the script runs it | engineer | `gov.close.nightly` applies the owner's nightly rule itself "
       "for every adopted product: the 02:00 to 05:00 window, the run booked by an estimate measured from the last full "
       "runs' per-test durations (the effective parallelism measured, not the worker count), the clean start "
       "(no close or merge in progress, the tree clean, the head stable) and its latest start, the close and "
       "verification locks during the run, closes resuming at its end, a package when the estimate no longer fits, "
       "and a green run recorded as the next day's base (after row W2-M406's fix). | The owner, 2026-10-28 "
       "(DEC-933 item 2; ordinary work: yes; other: fails open, a nightly that never runs) |")
text = LIST.read_text(encoding="utf-8")
lines = text.split("\n")
at = next(i for i, l in enumerate(lines) if l.startswith("| W2-M406 |"))
lines.insert(at + 1, ROW)
text = "\n".join(lines)
for old, new in [
    ("W2-L449 (DEC-932), so 959 were opened;", "W2-L449 (DEC-932), W2-M407 (DEC-933), so 960 were opened;"),
    ("so 943 are open, 61 of them high, 394 medium and 445 low.", "so 944 are open, 61 of them high, 395 medium and 445 low."),
    ("### 3.2 medium (394)", "### 3.2 medium (395)"),
]:
    if text.count(old) != 1:
        sys.exit("not found once: " + old[:50])
    text = text.replace(old, new)
LIST.write_text(text, encoding="utf-8")
print("added W2-M407")
