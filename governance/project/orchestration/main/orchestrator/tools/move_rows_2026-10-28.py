"""Moves the six rows the queue of 2026-10-27 closed to section 4 (the list's own practice since W2-02's close:
the counts line names them "now in section 4"), corrects the counts, and adds row W2-L449 (DEC-932 item 2).

76fb5f18 marked them **closed** in place; that mark is taken off as each row moves, and its content goes in the
"Closed by" column. W2-L419's partial mark stays (the rest of it stays open).
"""
import pathlib
import re
import sys

LIST = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/plan/WAVE_2_LIST.md")
CLOSED_BY = {
    "W2-H044": "W2-66, closed by `gov close` (`f8d1f60a`, 2026-10-27); its close record names each suite it ran and why",
    "W2-M153": "W2-66, closed by `gov close` (`f8d1f60a`, 2026-10-27); measured: the six scoped closes after it took "
               "10 to 28 minutes each, against 66 and 76 for the full ones",
    "W2-L437": "W2-72, closed by `gov close` (`6c439d8a`, 2026-10-27)",
    "W2-M404": "W2-69, closed by `gov close` (`07a8d624`, 2026-10-27)",
    "W2-M395": "W2-69, closed by `gov close` (`07a8d624`, 2026-10-27); settled by its choice "
               "(`docs/research/W2-69-secrets-scan.md` §13)",
    "W2-L373": "W2-69, closed by `gov close` (`07a8d624`, 2026-10-27); the folder is `tests/unit/secrets_check/`",
}
NEW_ROW = ("| W2-L449 | Run without `PYTHONPATH`, the pin's interpreter loads the pinned wheel's `gov`, not the project's "
           "`src/`: a lone `pytest tests/unit/close/test_serial.py` fails to import `gov.close.serial` (new in W2-57). "
           "Every run the close starts sets `PYTHONPATH` to `src/`, so a narrow scoped selection passes (W2-57's unit "
           "test 11 of 11, `tests/unit/close` 428 of 428, 2026-10-28) | engineer | A unit test run outside the close "
           "imports the project's own code, or says that it runs the pin's (for example the root conftest putting "
           "`src/` first). | The orchestrator, 2026-10-28 (DEC-932 item 2; ordinary work: no; other: fails closed) |")

text = LIST.read_text(encoding="utf-8")
lines = text.split("\n")
moved = []
for row in CLOSED_BY:
    idx = [i for i, l in enumerate(lines) if l.startswith("| " + row + " |")]
    if len(idx) != 1:
        sys.exit(row + ": found %d times" % len(idx))
    cells = lines[idx[0]].split(" | ")
    item, sources = cells[1], cells[-1].rstrip(" |")
    sources = re.sub(r" \*\*closed\*\* by W2-\d+'s close.*$", "", sources)
    moved.append("| %s | %s | %s | %s |" % (row, item, CLOSED_BY[row], sources))
    del lines[idx[0]]
# The new row goes after W2-L448.
at = next(i for i, l in enumerate(lines) if l.startswith("| W2-L448 |"))
lines.insert(at + 1, NEW_ROW)
# Section 4's table ends at the file's last row.
last = max(i for i, l in enumerate(lines) if l.startswith("| W2-"))
lines[last + 1:last + 1] = moved
text = "\n".join(lines)
REPL = [
    ("W2-L447 and W2-L448 (W2-67's run 4), so 958 were opened;",
     "W2-L447 and W2-L448 (W2-67's run 4), W2-L449 (DEC-932), so 959 were opened;"),
    ("W2-50's close (2026-10-22) closed 1 (W2-M355, now in section 4), so 948 are open, 62 of them high, 397 medium and 446 low.",
     "W2-50's close (2026-10-22) closed 1 (W2-M355, now in section 4), and the queue of 2026-10-27 closed 6 (W2-H044 and "
     "W2-M153 by W2-66, W2-L437 by W2-72, W2-M404, W2-M395 and W2-L373 by W2-69, now in section 4), so 943 are open, 61 of "
     "them high, 394 medium and 445 low."),
    ("### 3.1 high (62)", "### 3.1 high (61)"),
    ("### 3.2 medium (397)", "### 3.2 medium (394)"),
    ("### 3.3 low (446)", "### 3.3 low (445)"),
]
for old, new in REPL:
    if text.count(old) != 1:
        sys.exit("not found once: " + old[:60])
    text = text.replace(old, new)
LIST.write_text(text, encoding="utf-8")
print("moved: " + ", ".join(CLOSED_BY) + "; added W2-L449")
