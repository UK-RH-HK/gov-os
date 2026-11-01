"""DEC-969: W2-108's run-1 lead brief."""
import pathlib, subprocess
O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
ACC = "tests/" + "acceptance"
r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(O / "briefs/W2-108-part-run1.md"), str(O / "briefs/W2-108-A5-run1.md"),
                    "ID=DAEO-zoex", "W2=W2-108", "PROFILE=STANDARD",
                    f"PATHS=src/gov/retrieval/semantic.py and lexical.py (their freshness and status functions only), tests/unit/retrieval/test_w2_108*, docs/research/W2-108-freshness-once.md, and the test designer's {ACC}/W2-108/",
                    "ROWS=none", "SOURCES=DEC-969, DEC-968, DEC-966, DEC-860, DEC-424", "IMPL=DEC-969",
                    "EST=about 80 lines, about 4 to 6 hours"], capture_output=True, text=True)
t = (O / "briefs/W2-108-A5-run1.md").read_text()
print(r.returncode, r.stderr.strip()[:200], len(t), t.count("@@"))
