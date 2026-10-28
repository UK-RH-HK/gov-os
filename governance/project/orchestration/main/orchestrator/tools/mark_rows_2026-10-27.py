"""Marks the Wave 2 list's rows that the queue of 2026-10-27 closed (prompt §2 step 5).

Each mark goes at the end of the row's sources column, in the list's own form (line 30: an item that closes is
marked **closed** with its commit; a partial close names the part and says the rest stays open).
"""
import pathlib
import sys

LIST = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/plan/WAVE_2_LIST.md")
MARKS = {
    "W2-H044": "**closed** by W2-66's close, `f8d1f60a`, 2026-10-27 (its close record names each suite it ran and why)",
    "W2-M153": "**closed** by W2-66's close, `f8d1f60a`, 2026-10-27 (measured: the six scoped closes after it took "
               "10 to 28 minutes each, against 66 and 76 for the full ones)",
    "W2-L437": "**closed** by W2-72's close, `6c439d8a`, 2026-10-27",
    "W2-M404": "**closed** by W2-69's close, `07a8d624`, 2026-10-27",
    "W2-M395": "**closed** by W2-69's close, `07a8d624`, 2026-10-27 (settled by its choice: "
               "`docs/research/W2-69-secrets-scan.md` §13)",
    "W2-L373": "**closed** by W2-69's close, `07a8d624`, 2026-10-27 (the folder is `tests/unit/secrets_check/`)",
    "W2-L419": "(W2-69's part closed by its close, `07a8d624`, 2026-10-27; the rest stays open: a key export wrapped "
               "as one word over 24,000 bytes, due in Wave 3, DEC-911 item 6)",
}

lines = LIST.read_text(encoding="utf-8").split("\n")
done = set()
for i, line in enumerate(lines):
    for row, mark in MARKS.items():
        if line.startswith("| " + row + " |"):
            if mark in line:
                sys.exit(row + ": already marked")
            if not line.rstrip().endswith(" |"):
                sys.exit(row + ": the row does not end with ' |'")
            lines[i] = line.rstrip()[:-2] + " " + mark + " |"
            done.add(row)
missing = set(MARKS) - done
if missing:
    sys.exit("rows not found: " + ", ".join(sorted(missing)))
LIST.write_text("\n".join(lines), encoding="utf-8")
print("marked: " + ", ".join(sorted(done)))
