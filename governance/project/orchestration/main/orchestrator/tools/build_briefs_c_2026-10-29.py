"""Builds the briefs of W2-78, W2-76, W2-64 and W2-81 (claimed 2026-10-29, worktrees at 135ae00947cb): each part's
@@HEAD@@ filled with its worktree's head, then build_lead_brief.py with the values below."""
import pathlib
import subprocess
import sys

O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
SPECS = [
    ("W2-78", "DAEO-v4is", "STANDARD",
     "src/gov/close/ratchet.py, src/gov/close/history.py, src/gov/close/gates.py, src/gov/close/traceability.py, "
     "src/gov/close/select.py, governance/project/records/**, governance/project/test-map.yaml, "
     "template/governance/kernel/schemas/**, tests/unit/close/test_w2_78*",
     "none", "DEC-941, DEC-929, DEC-889, DEC-880, DEC-757, DEC-766, DEC-862", "DEC-941, DEC-929", "about 150 lines"),
    ("W2-76", "DAEO-tgk2", "STANDARD", "src/gov/rebuild/**, tests/unit/rebuild/test_w2_76*", "W2-M408, W2-L451",
     "DEC-939, DEC-889, DEC-866, DEC-898", "DEC-939", "about 80 lines"),
    ("W2-64", "DAEO-0uhh", "STANDARD",
     "template/governance/kernel/schemas/close.schema.json, src/gov/check/schema.py, tests/unit/check/test_schema*",
     "none", "DEC-831, DEC-844, DEC-872, DEC-890, DEC-833, DEC-941", "DEC-872, DEC-844, DEC-890",
     "120 lines, about 6 hours"),
    ("W2-81", "DAEO-l78m", "FULL", "tests/acceptance/W2-81/**", "none",
     "DEC-941, DEC-936, DEC-930, DEC-833, DEC-820, DEC-845, DEC-873, DEC-911, DEC-728, DEC-899", "DEC-941, DEC-936",
     "about 1,200 lines, about 9 hours"),
]
for w2, tid, prof, paths, rows, srcs, impl, est in SPECS:
    head = subprocess.run(["git", "-C", "/home/usain/gov-os-worktrees/" + w2, "rev-parse", "--short=12", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    part = (O / "briefs" / (w2 + "-part-run1.md")).read_text(encoding="utf-8")
    if "@@HEAD@@" not in part:
        sys.exit(w2 + ": no @@HEAD@@ in its part")
    filled = O / "briefs" / (w2 + "-part-run1.filled.md")
    filled.write_text(part.replace("@@HEAD@@", head), encoding="utf-8")
    r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(filled), str(O / "briefs" / (w2 + "-A5-run1.md")),
                        "ID=" + tid, "W2=" + w2, "PROFILE=" + prof, "PATHS=" + paths, "ROWS=" + rows,
                        "SOURCES=" + srcs, "IMPL=" + impl, "EST=" + est], capture_output=True, text=True)
    print(w2, head, (r.stdout + r.stderr).strip()[-90:])
    if r.returncode:
        sys.exit(1)
