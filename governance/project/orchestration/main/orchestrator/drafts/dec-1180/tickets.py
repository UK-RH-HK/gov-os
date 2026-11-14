#!/usr/bin/env python3
"""DEC-1180 (1): N2 (b) into W2-61h (DAEO-h2k3) and W2-187 (DAEO-0cd2). Run from the repo root."""
import sys

def edit(path, pairs, tail):
    t = open(path, encoding="utf-8").read()
    for old, new in pairs:
        if t.count(old) != 1:
            sys.exit(f"{path}: anchor count {t.count(old)} for {old[:60]!r}")
        t = t.replace(old, new, 1)
    t = t.rstrip("\n") + "\n\n" + tail + "\n"
    open(path, "w", encoding="utf-8").write(t)

N2 = ("a heading-cited source whose section text (from its heading line to the next heading of the same or a higher "
      "level, or the end of the file) differs between the source's own commit and the head is listed too, though its "
      "heading is still found")

edit(".tickets/DAEO-h2k3.md", [], (
    "**N2 (b), 2026-11-14 (the owner, DEC-1180 (1)):** the changed-lines list also holds " + N2 + "; an entry is listed "
    "once even when two of its alternatives changed (row N1, fixed in the same flow, DEC-1180 (4)). One more test "
    "revision by an independent test designer (`w2_61h_support.py`, the README, the case files only where needed; "
    "`Rewrite-Reason: DEC-1180 (1)`), proved on planted data, then a narrow independent check "
    "(`docs/probes/DAEO-h2k3/PR-DAEO-h2k3-n2.md`). W2-61h closes on this revision and the owner's operator's walled "
    "re-run."))

edit(".tickets/DAEO-0cd2.md", [
    ("(W2-61h S4''s list: question id and entry number only,",
     "(W2-61h S4''s list, with N2 (b), DEC-1180 (1): " + N2.replace("'", "''") + "; question id and entry number only,"),
    ("re-anchoring runs in memory, so a block moved unchanged is not listed.",
     "re-anchoring runs in memory, so a block moved unchanged is not listed. With N2 (b) (DEC-1180 (1)), " + N2 +
     ", though `matcher` resolves it; an entry is listed once."),
], (
    "**Amended 2026-11-14 (the CTO within purpose, DEC-1157 (12); the owner's N2 (b), DEC-1180 (1)):** S10 (6) and I10 "
    "item 6 also list " + N2 + ", matching W2-61h S4's list. The lead brings this in at its next merge of "
    "`w2/integrate`; the test designer's S10 cases take it with `Rewrite-Reason: DEC-1180 (1)`."))
print("ok")
