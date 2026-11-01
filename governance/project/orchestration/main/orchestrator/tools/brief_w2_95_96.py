"""DEC-959: run-1 lead briefs for W2-96 (the opaque runner) and W2-95 (core-pathmap)."""
import pathlib
import subprocess
O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
ACC = "tests/" + "acceptance"
for w2, tid, prof, paths, srcs, impl, est in [
    ("W2-96", "DAEO-ouet", "FULL", f"src/gov/accept/**, tests/unit/accept/test_w2_96*, and the test designer's {ACC}/W2-96/",
     "DEC-959, DEC-957, DEC-820, DEC-317, MR-3", "DEC-959", "about 250 lines, about 6 to 8 hours"),
    ("W2-95", "DAEO-57hm", "STANDARD", f"src/gov/check/pathmap.py, tests/unit/check/test_w2_95*, and the test designer's {ACC}/W2-95/",
     "DEC-959, DEC-954, DEC-694, DEC-381", "DEC-959", "about 60 lines, about 4 to 6 hours")]:
    r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(O / f"briefs/{w2}-part-run1.md"),
                        str(O / f"briefs/{w2}-A5-run1.md"), f"ID={tid}", f"W2={w2}", f"PROFILE={prof}",
                        "PATHS=" + paths, "ROWS=none", "SOURCES=" + srcs, "IMPL=" + impl, "EST=" + est],
                       capture_output=True, text=True)
    t = (O / f"briefs/{w2}-A5-run1.md").read_text()
    print(w2, r.returncode, r.stderr.strip()[:200], "chars", len(t), "left", t.count("@@"), "DEC-959" in t)
