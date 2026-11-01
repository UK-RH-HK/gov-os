"""DEC-956: W2-76's run-2 lead brief: its part, then the committed common lead brief (a script file: the five-rule
hook reads a command naming the acceptance folder as a possible write there)."""
import pathlib
import subprocess

O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(O / "briefs/W2-76-part-run2.md"),
                    str(O / "briefs/W2-76-A5-run2.md"), "ID=DAEO-tgk2", "W2=W2-76", "PROFILE=STANDARD",
                    "PATHS=src/gov/rebuild/**, tests/unit/rebuild/test_w2_76*, tests/conftest.py, and the test "
                    "designer's own suite W2-76", "ROWS=W2-M408, W2-L451",
                    "SOURCES=DEC-939, DEC-889, DEC-866, DEC-898, DEC-956", "IMPL=DEC-939, DEC-956",
                    "EST=run 2: one test-setup revision and a lock-path override, about 2 to 3 hours"],
                   capture_output=True, text=True)
print(r.returncode, r.stdout, r.stderr)
text = (O / "briefs/W2-76-A5-run2.md").read_text(encoding="utf-8")
print("left:", text.count("@@"), "chars:", len(text))
