"""ACT-W2-57-LS-1 (owner, 2026-10-28): the path-map change of the first of W2-57's two ACTs.

1. Removes the 6 load_sensitive entries whose fix is in force in a close under the current pin:
   W1-38 x3 and W1-07 [doctor] (product code these tests run from src/, merged 57e363c5), W1-30 r13 (test-side),
   and the unit close follow-up case (no fix: not reproduced; the clone run decides).
   The 24 whose fix is the judge's nightly route (W1-46 x23, W1-19 warm p95) stay until the second re-pin.
2. Adds W2-57's two DEC-927 corrections to accepted_history.
Applies to the working copy only; the orchestrator saves the diff and restores the file.
"""
import pathlib
import sys

PM = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/path-map.yaml")
KEEP_FILES = ("tests/acceptance/W1-46/test_w1_46_live_sessions.py", "tests/acceptance/W1-19/test_w1_19_real_models.py")
SOURCES = "[DEC-813, DEC-823, DEC-871, DEC-883, DEC-889, DEC-890, DEC-892, DEC-784]"
CORRECTIONS = [
    '  - commit: "6be837bbbe4158768ca88ae47972308386e008cf"', "    decision: DEC-927", "    should_implement: " + SOURCES,
    '  - commit: "d0bfeb6afd9523b4ee6a4e6e2da5333f54b283bf"', "    decision: DEC-927", "    should_implement: " + SOURCES,
]

lines = PM.read_text(encoding="utf-8").split("\n")
# 1. load_sensitive: drop each entry (its "- test:" line and the indented lines after it) not in KEEP_FILES.
start = lines.index("load_sensitive:")
end = start + 1
while end < len(lines) and lines[end].startswith("  "):
    end += 1
kept, removed, entry = [], [], []
for line in lines[start + 1:end] + ["  - test: END"]:
    if line.startswith("  - test:"):
        if entry:
            test = entry[0].split('"')[1]
            (kept if test.split("::")[0] in KEEP_FILES else removed).append((test, entry))
        entry = [line]
    else:
        entry.append(line)
if len(removed) != 6 or len(kept) != 24:
    sys.exit("expected 6 removed and 24 kept, found %d and %d" % (len(removed), len(kept)))
lines[start + 1:end] = [x for _, e in kept for x in e]
# 2. accepted_history: the two corrections go after its last entry, before the comment above acceptance_exemptions.
hist = lines.index("accepted_history:")
stop = hist + 1
while stop < len(lines) and lines[stop].startswith("  "):
    stop += 1
lines[stop:stop] = CORRECTIONS
PM.write_text("\n".join(lines), encoding="utf-8")
for test, _ in removed:
    print("removed:", test)
print("kept: %d; corrections added: 2" % len(kept))
