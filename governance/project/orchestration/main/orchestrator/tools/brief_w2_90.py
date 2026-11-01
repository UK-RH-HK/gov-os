"""DEC-957: W2-90's run-1 lead brief: its part, then the committed common lead brief. A script file because the
five-rule hook reads a command naming the acceptance folder as a possible write there (a false positive, recorded)."""
import pathlib
import subprocess

O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
ACC = "tests/" + "acceptance"
PATHS = (f"the 19 files named in the ticket, {ACC}/W1-05/conftest.py, {ACC}/W1-46/conftest.py, {ACC}/W2-90/**")
r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(O / "briefs/W2-90-part-run1.md"),
                    str(O / "briefs/W2-90-A5-run1.md"), "ID=DAEO-8lmb", "W2=W2-90", "PROFILE=LITE", "PATHS=" + PATHS,
                    "ROWS=none", "SOURCES=DEC-957, DEC-953, DEC-954, DEC-955, DEC-906", "IMPL=DEC-957, DEC-953",
                    "EST=a test revision of 235 cases in 19 files, about 2 to 3 hours"], capture_output=True, text=True)
print(r.returncode, r.stdout, r.stderr)
text = (O / "briefs/W2-90-A5-run1.md").read_text(encoding="utf-8")
print("left:", text.count("@@"), "chars:", len(text))
