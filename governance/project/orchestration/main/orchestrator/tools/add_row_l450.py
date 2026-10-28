"""Adds row W2-L450 (W2-07's run 5 discovery) after W2-L449 and updates the counts."""
import pathlib
import sys

LIST = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/plan/WAVE_2_LIST.md")
ROW = ("| W2-L450 | `tests/acceptance/W2-57/test_w2_57_designer_read_p95.py` (a `serial: latency` entry, not on "
       "`load_sensitive`) fails when other sessions load the machine, though the close runs it alone in its serial "
       "phase: 245 to 256 ms per round against its 100 ms bound at load 20 to 32 (W2-07's run 5, 2026-10-28), passed "
       "alone at load 6; W2-57's README records red at load 64 to 70 and 55 ms on a quiet machine. A close that runs "
       "while leads load the machine can be refused on it | engineer | The case measures the designer's read in a way "
       "load from other sessions does not decide (for example the CPU time of the read, or a bound set from the "
       "machine's measured idle figure), or the close's serial phase runs only on a quiet machine; never a weaker "
       "bound and never a load_sensitive entry without the owner. | W2-07's run 5, 2026-10-28 (ordinary work: yes; "
       "other: fails closed) |")
text = LIST.read_text(encoding="utf-8")
lines = text.split("\n")
at = next(i for i, l in enumerate(lines) if l.startswith("| W2-L449 |"))
lines.insert(at + 1, ROW)
text = "\n".join(lines)
for old, new in [
    ("W2-M407 (DEC-933), so 960 were opened;", "W2-M407 (DEC-933), W2-L450 (W2-07's run 5), so 961 were opened;"),
    ("so 944 are open, 61 of them high, 395 medium and 445 low.", "so 945 are open, 61 of them high, 395 medium and 446 low."),
    ("### 3.3 low (445)", "### 3.3 low (446)"),
]:
    if text.count(old) != 1:
        sys.exit("not found once: " + old[:50])
    text = text.replace(old, new)
LIST.write_text(text, encoding="utf-8")
print("added W2-L450")
