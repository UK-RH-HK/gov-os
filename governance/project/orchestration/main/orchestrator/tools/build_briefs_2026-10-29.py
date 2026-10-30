"""Builds today's lead briefs (DEC-941) with build_lead_brief.py: PATHS, ROWS, SOURCES and PROFILE from each ticket
file; IMPL and EST given here; `@@HEAD@@` in a part filled with its worktree's head first (into a filled copy).
Run with PYTHONPATH=<main tree>/src."""
import pathlib
import subprocess
import sys

from gov.tasks.tickets import frontmatter

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
B = ROOT / ".gov-runtime/scratch/orchestrator/briefs"
BUILD = ROOT / ".gov-runtime/scratch/orchestrator/tools/build_lead_brief.py"
# W2, ticket, part, brief out, IMPL, EST
SPECS = [
    ("W2-61", "DAEO-iw1f", "W2-61-part-run1.md", "W2-61-A5-run1.md", "DEC-828, DEC-833, DEC-860, DEC-820, DEC-941",
     "about 180 lines, about a day with the baseline and the full run"),
    ("W2-03", "DAEO-ym8a", "W2-03-part-mergeback.md", "W2-03-A5-run3.md", "DEC-941, DEC-729",
     "about 3 hours (up to 5 with one repair batch)"),
    ("W2-05", "DAEO-0z8c", "W2-05-part-mergeback.md", "W2-05-A5-run3.md",
     "DEC-941, DEC-804, DEC-805, DEC-807, DEC-783, DEC-895", "about 1 to 1.5 days, about 140 lines"),
    ("W2-77", "DAEO-b6hm", "W2-77-part-run1.md", "W2-77-A5-run1.md", "DEC-939, DEC-915",
     "about 20 lines, about 5 hours with the full run and one review"),
    ("W2-56", "DAEO-wnnz", "W2-56-part-run1.md", "W2-56-A5-run1.md", "DEC-799, DEC-826, DEC-877, DEC-941",
     "about 250 lines, about two days with the full runs and the reviews"),
    ("W2-57", "DAEO-cy5o", "W2-57-part-run4b.md", "W2-57-A5-run4b.md", "DEC-895",
     "about 1 to 1.5 hours"),
    ("W2-60a", "DAEO-cv58", "W2-60a-part-run1.md", "W2-60a-A5-run1.md", "DEC-826, DEC-838, DEC-839, DEC-832, DEC-941",
     "about 250 lines, about two days with the full runs and the reviews"),
]
for w2, tid, part, out, impl, est in SPECS:
    fm = frontmatter(ROOT / ".tickets" / (tid + ".md")) or {}
    head = subprocess.run(["git", "-C", "/home/usain/gov-os-worktrees/" + w2, "rev-parse", "--short=12", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    text = (B / part).read_text(encoding="utf-8")
    if "@@HEAD@@" in text:
        filled = B / part.replace(".md", ".filled.md")
        filled.write_text(text.replace("@@HEAD@@", head), encoding="utf-8")
        part_path = filled
    else:
        if head not in text:
            sys.exit(w2 + ": the part names no head and not " + head)
        part_path = B / part
    rows = fm.get("list_rows") or []
    args = ["python3", str(BUILD), str(part_path), str(B / out), "ID=" + tid, "W2=" + w2,
            "PROFILE=" + str(fm.get("profile")), "PATHS=" + ", ".join(fm.get("allowed_paths") or []),
            "ROWS=" + (", ".join(rows) if rows else "none"), "SOURCES=" + ", ".join(fm.get("sources") or []),
            "IMPL=" + impl, "EST=" + est]
    r = subprocess.run(args, capture_output=True, text=True)
    print(w2, head, (r.stdout + r.stderr).strip()[-160:])
    if r.returncode:
        sys.exit(1)
