"""DEC-954 Q3: W2-85's run-1 lead brief (its part with the ids filled and a DEC-953/954 note), then the common brief."""
import pathlib
import subprocess

O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
NOTE = ("**DEC-953 and DEC-954 (owner, 2026-10-30), read with the common brief's DEC-953 block:** the Gov OS's features "
        "are lifted as gates on this repository's development, and this ticket closes on the audit's 10 practices. "
        "Where this part names a lifted rule (the close queue, the ratchet lists, the quiet windows), the common "
        "brief's block holds. The owner confirmed this ticket goes ahead (DEC-954 Q3). Verification: the two routed "
        "cases in the close's serial form, plus the selection `select_tests.py` gives; no full run.\n\n")
part = (O / "briefs/W2-85-part-run1.md").read_text(encoding="utf-8")
part = part.replace("@@ID85@@", "DAEO-gdzh").replace("@@HEAD@@", "403d70b396ff")
(O / "briefs/W2-85-part-run1.filled.md").write_text(NOTE + part, encoding="utf-8")
r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(O / "briefs/W2-85-part-run1.filled.md"),
                    str(O / "briefs/W2-85-A5-run1.md"), "ID=DAEO-gdzh", "W2=W2-85", "PROFILE=LITE",
                    "PATHS=tests/acceptance/W2-54/**, tests/acceptance/serial-only.txt", "ROWS=none",
                    "SOURCES=DEC-951, DEC-915, DEC-906, DEC-953, DEC-954", "IMPL=DEC-951",
                    "EST=about 10 lines, about 2 hours"], capture_output=True, text=True)
print(r.stdout, r.stderr)
text = (O / "briefs/W2-85-A5-run1.md").read_text(encoding="utf-8")
print("left:", text.count("@@"))
