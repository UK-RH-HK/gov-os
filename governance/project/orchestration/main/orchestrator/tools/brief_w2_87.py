"""DEC-953: W2-87's run-1 lead brief: its part with @@ID@@ and @@HEAD@@ filled and a DEC-953 note on top, then the
committed common lead brief (with its DEC-953 block)."""
import pathlib
import subprocess

O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
NOTE = ("**DEC-953 (owner, 2026-10-30), read with the common brief's DEC-953 block:** the Gov OS's features are lifted "
        "as gates on this repository's development; your ticket closes on the audit's 10 practices. Where this part "
        "names a lifted rule (the close queue, a ratchet list, re-probes after merges, the 90-minute budget), the "
        "common brief's DEC-953 block holds. W2-61's measure tool is merged (`758cd53f`). W2-03 is merged and closing "
        "in today's batch. The path map's `retrieval_authority` block is yours (DEC-952 item 1); nothing else in that "
        "file changes. Verify with `select_tests.py` as the common brief says.\n\n")
part = (O / "briefs/W2-87-part-run1.md").read_text(encoding="utf-8")
part = part.replace("@@ID@@", "DAEO-s9qc").replace("@@HEAD@@", "df0782fa4c4e")
(O / "briefs/W2-87-part-run1.filled.md").write_text(NOTE + part, encoding="utf-8")
r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(O / "briefs/W2-87-part-run1.filled.md"),
                    str(O / "briefs/W2-87-A5-run1.md"), "ID=DAEO-s9qc", "W2=W2-87", "PROFILE=STANDARD",
                    "PATHS=src/gov/retrieval/authority.py, src/gov/retrieval/retrieve.py, governance/project/path-map.yaml, "
                    "tests/unit/retrieval/test_w2_87*, docs/research/W2-87-memory-measure.md",
                    "ROWS=none", "SOURCES=DEC-952, DEC-953, DEC-866, DEC-423, DEC-424, DEC-791, DEC-694, DEC-860, "
                    "DEC-877, DEC-941, DEC-833, CAP-10", "IMPL=DEC-952, CAP-10", "EST=about 120 lines, about 9 hours"],
                   capture_output=True, text=True)
print(r.stdout, r.stderr)
text = (O / "briefs/W2-87-A5-run1.md").read_text(encoding="utf-8")
print("left:", text.count("@@"), "DEC-953 block:", "DEC-953 (owner, standing, 2026-10-30)" in text)
