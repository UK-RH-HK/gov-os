"""Finds what was decided or proposed but never reached its home (DEC-1012: slipped twice on 2026-11-01).

1. Every decision draft (a file named DEC-<n>.md or _DEC-<n>.md under drafts/) has its heading in the register.
2. Every quoted KPI line in a package (a backticked or double-quoted text ending in a [DEC-...] or [ACT-...] citation)
   is found in some ticket, by its first 60 letters and digits. A line left out on purpose goes in
   applied_check.ignore (one package name and the line's first 40 characters, tab-separated, then the reason).

Run at every handover and in the morning package. Exits 1 when anything is missing. Prints one line per gap.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
ORCH = ROOT / ".gov-runtime/scratch/orchestrator"
REGISTER = (ROOT / "docs/DECISION_REGISTER.md").read_text(encoding="utf-8")
TICKETS = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in (ROOT / ".tickets").glob("*.md"))
IGNORE = ORCH / "tools/applied_check.ignore"


def norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower().replace("''", "'"))


TICKETS_N = norm(TICKETS)
ignored = set()
if IGNORE.is_file():
    for line in IGNORE.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and not line.startswith("#"):
            ignored.add((parts[0], norm(parts[1])[:30]))

gaps = []
for draft in sorted((ORCH / "drafts").rglob("*.md")):
    m = re.fullmatch(r"_?DEC-(\d+)\.md", draft.name)
    if m and not re.search(rf"^### DEC-{m.group(1)}\b", REGISTER, re.M):
        gaps.append(f"draft not in the register: DEC-{m.group(1)} ({draft.relative_to(ROOT)})")

QUOTED = re.compile(r"(?:`'|\")([A-Z`][^\"`]{40,}?\[(?:DEC|ACT)-[^\]]*\])'?(?:`|\")", re.S)
for pkg in sorted((ROOT / "governance/project/orchestration/packages").glob("*.md")):
    for m in QUOTED.finditer(pkg.read_text(encoding="utf-8")):
        text = re.sub(r"\s+", " ", m.group(1))
        key = norm(re.sub(r"\[[^\]]*\]$", "", text))[:60]
        if len(key) < 30 or key in TICKETS_N or (pkg.stem, key[:30]) in ignored:
            continue
        gaps.append(f"package line in no ticket: {pkg.stem}: {text[:110]}")

for gap in gaps:
    print(gap)
print(f"applied_check: {len(gaps)} gap(s)")
sys.exit(1 if gaps else 0)
