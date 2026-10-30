"""Rebuilds the queued leads' briefs (chain-2026-10-30b) from their parts with the common brief as it now stands
(P-R1's filter and the brief-gap fixes, 2026-10-30). Same values as their first builds."""
import pathlib
import subprocess
import sys

O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
SPECS = [
    ("W2-84-part-run1.filled.md", "W2-84-A5-run1.md", "DAEO-m1u3", "W2-84", "FULL",
     "src/gov/guard/reads.py, tests/unit/guard/test_w2_84*, docs/changes/W2-84-CIT-E.md", "W2-H063",
     "DEC-950, DEC-820, DEC-821, DEC-845, DEC-873, DEC-946, DEC-728, DEC-801, DEC-562, DEC-880, DEC-866, CAP-33.a",
     "DEC-950, DEC-820, DEC-845", "about 120 lines, about a lead-day with the full run and one review"),
    ("W2-26-part-mergeback.md", "W2-26-A5-mergeback.md", "DAEO-2ds6", "W2-26", "STANDARD",
     "docs/research/EXP-003/examin/**", "W2-I041", "DEC-728, DEC-078, DEC-727", "DEC-941", "about 1.5 hours"),
    ("W2-51-part-mergeback.md", "W2-51-A5-mergeback.md", "DAEO-egsy", "W2-51", "STANDARD",
     "docs/plan/tools/validate_w2.py, tests/unit/plan/**", "none", "DEC-744, DEC-723, DEC-741", "DEC-941",
     "about 2.5 hours, up to 4.5 with one repair batch"),
    ("W2-67-part-resume.md", "W2-67-A5-resume.md", "DAEO-9nys", "W2-67", "FULL",
     "tests/unit/close/**, tests/unit/guard/**, tests/conftest.py", "none",
     "DEC-889, DEC-892, DEC-898, DEC-899, DEC-904, DEC-907", "DEC-941, DEC-895",
     "about 3.5 hours this run, up to 7 with one repair batch and a second review"),
    ("W2-78-part-run1.filled.md", "W2-78-A5-run1.md", "DAEO-v4is", "W2-78", "STANDARD",
     "src/gov/close/ratchet.py, src/gov/close/history.py, src/gov/close/gates.py, src/gov/close/traceability.py, "
     "src/gov/close/select.py, governance/project/records/**, governance/project/test-map.yaml, "
     "template/governance/kernel/schemas/**, tests/unit/close/test_w2_78*", "none",
     "DEC-941, DEC-929, DEC-889, DEC-880, DEC-757, DEC-766, DEC-862", "DEC-941, DEC-929", "about 150 lines"),
    ("W2-76-part-run1.filled.md", "W2-76-A5-run1.md", "DAEO-tgk2", "W2-76", "STANDARD",
     "src/gov/rebuild/**, tests/unit/rebuild/test_w2_76*", "W2-M408, W2-L451", "DEC-939, DEC-889, DEC-866, DEC-898",
     "DEC-939", "about 80 lines"),
    ("W2-64-part-run1.filled.md", "W2-64-A5-run1.md", "DAEO-0uhh", "W2-64", "STANDARD",
     "template/governance/kernel/schemas/close.schema.json, src/gov/check/schema.py, tests/unit/check/test_schema*",
     "none", "DEC-831, DEC-844, DEC-872, DEC-890, DEC-833, DEC-941", "DEC-872, DEC-844, DEC-890",
     "120 lines, about 6 hours"),
    ("W2-20-part-run3.md", "W2-20-A5-run3.md", "DAEO-r30l", "W2-20", "STANDARD",
     "src/gov/resources/**, src/gov/check/commands.py, src/gov/launch/gate*, tests/unit/resources/**",
     "W2-M188, W2-M244, W2-M262", "DEC-729, DEC-742, DEC-747, DEC-898, DEC-941, DEC-942, DEC-947, DEC-950",
     "DEC-950, DEC-942, DEC-947, DEC-898", "about 200 code lines and 20 to 25 test cases, about 1.5 to 2 lead-days"),
    ("W2-81-part-run1.filled.md", "W2-81-A5-run1.md", "DAEO-l78m", "W2-81", "FULL", "tests/acceptance/W2-81/**", "none",
     "DEC-941, DEC-936, DEC-930, DEC-833, DEC-820, DEC-845, DEC-873, DEC-911, DEC-728, DEC-899", "DEC-941, DEC-936",
     "about 1,200 lines, about 9 hours"),
]
for part, out, tid, w2, prof, paths, rows, srcs, impl, est in SPECS:
    r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(O / "briefs" / part), str(O / "briefs" / out),
                        "ID=" + tid, "W2=" + w2, "PROFILE=" + prof, "PATHS=" + paths, "ROWS=" + rows, "SOURCES=" + srcs,
                        "IMPL=" + impl, "EST=" + est], capture_output=True, text=True)
    ok = r.returncode == 0 and "P-R1 (delegated" in (O / "briefs" / out).read_text(encoding="utf-8")
    print(w2, "ok" if ok else "FAILED " + (r.stdout + r.stderr)[-200:])
    if not ok:
        sys.exit(1)
