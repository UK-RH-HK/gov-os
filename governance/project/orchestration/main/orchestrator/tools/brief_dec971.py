"""DEC-971: the lead briefs of W2-110 and W2-109 (run 1) and W2-52 and W2-105 (resumes)."""
import pathlib
import subprocess

O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
ACC = "tests/" + "acceptance"
RUNS = [
    ("W2-110", "DAEO-3r1j", "FULL", "W2-110-part-run1.md", "W2-110-A5-run1.md",
     f"template/governance/kernel/hooks/pretooluse.py, src/gov/guard/install.py, tests/unit/guard/test_w2_110*, and the test designer's {ACC}/W2-110/",
     "DEC-971, DEC-957, DEC-966, DEC-163, DEC-083", "DEC-971, DEC-957", "about 80 lines, about 5 to 7 hours"),
    ("W2-105", "DAEO-zpdj", "STANDARD", "W2-105-part-resume-dec971.md", "W2-105-A5-resume-dec971.md",
     f"template/.rulesync/permissions.jsonc, and the test designer's {ACC}/W2-105/",
     "DEC-966, DEC-172, DEC-957, DEC-965, DEC-971", "DEC-966, DEC-971", "a verification resume, about 2 hours"),
    ("W2-52", "DAEO-siiz", "FULL", "W2-52-part-resume-dec971.md", "W2-52-A5-resume-dec971.md",
     f".claude/skills/adopt/SKILL.md (in place, not to be touched), src/gov/adopt/lite_gates.py, src/gov/adopt/stages.py, template/governance/kernel/skills/adopt/**, tests/unit/adopt/test_lite_gates*, and the test designer's {ACC}/W2-52/",
     "DEC-741, DEC-722, DEC-738, CAP-44.f, CAP-44.h, DEC-971", "DEC-741, DEC-971", "a review-and-verify resume, about 3 hours"),
    ("W2-109", "DAEO-6b2q", "STANDARD", "W2-109-part-run1.md", "W2-109-A5-run1.md",
     f"docs/contract/contract.yaml, docs/contract/CONTRACT_v4.md, docs/contract/capabilities/**, docs/contract/SOURCE_MAP.csv, docs/changes/W2-109-CIT-P.md, docs/changes/W2-109-CIT-E.md, docs/plan/tools/validate_w2.py, tests/unit/plan/test_validate_w2_forms*, and the test designer's {ACC}/W2-109/",
     "DEC-971, DEC-841, DEC-825, DEC-880, DEC-741, DEC-614, CAP-33", "DEC-971, DEC-841", "about 300 lines, about 6 to 8 hours"),
]
lines = []
for w2, tid, prof, part, out, paths, srcs, impl, est in RUNS:
    r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(O / "briefs" / part), str(O / "briefs" / out),
                        f"ID={tid}", f"W2={w2}", f"PROFILE={prof}", "PATHS=" + paths, "ROWS=none", "SOURCES=" + srcs,
                        "IMPL=" + impl, "EST=" + est], capture_output=True, text=True)
    t = (O / "briefs" / out).read_text()
    print(w2, r.returncode, r.stderr.strip()[:200], "chars", len(t), "left", t.count("@@"), "DEC-971" in t)
    lines.append(f"{w2} {tid} {out} {out[:-3]}.json")
(O / "log/chain-2026-10-31f.txt").write_text("\n".join(lines) + "\n")
print((O / "log/chain-2026-10-31f.txt").read_text())
