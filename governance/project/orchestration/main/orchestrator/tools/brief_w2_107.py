"""DEC-967: W2-107's run-1 lead brief."""
import pathlib, subprocess
O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
ACC = "tests/" + "acceptance"
r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(O / "briefs/W2-107-part-run1.md"), str(O / "briefs/W2-107-A5-run1.md"),
                    "ID=DAEO-kiar", "W2=W2-107", "PROFILE=FULL",
                    f"PATHS=src/gov/secrets/__init__.py, src/gov/secrets/cache.py, tests/unit/secrets/test_w2_107*, and the test designer's {ACC}/W2-107/",
                    "ROWS=none", "SOURCES=DEC-966, DEC-967, DEC-939, DEC-911, DEC-285, DEC-898", "IMPL=DEC-966, DEC-967",
                    "EST=about 180 lines, about 6 to 8 hours"], capture_output=True, text=True)
t = (O / "briefs/W2-107-A5-run1.md").read_text()
print(r.returncode, r.stderr.strip()[:200], len(t), t.count("@@"))
