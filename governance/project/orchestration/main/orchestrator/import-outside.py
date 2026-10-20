"""DEC-560, DEC-564: import the five outside sources as records, each with its origin and sha256, checked first.

The four owner records are read from the archive commit docs/SOURCES.md names; EXP-001's evidence file by its exact
path. The bytes are held against the recorded sha256 before anything is written; one mismatch stops the import.
The text is carried word for word below the frontmatter. Then the research-catalogue ids are listed as external
references (the file's existing form).
"""
import hashlib
import subprocess
import sys

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS/"
ARCHIVE = "bb6ec3a8d8242fda7a76f86f0f0eff46813bc65f"
OWNER = [
    ("OWNER-DECISION-P2-0001", "owner-records/phase-2/OWNER-DECISION-P2-0001-AGENT-ROLE-IDENTITY.md",
     "612849ba65c310c5ff41999e72e3382048842f526048a3fe49ab1a5b5a88b0ce"),
    ("OWNER-DECISION-P2-0008", "owner-records/phase-2/OWNER-DECISION-P2-0008-COMPLETE-PHASE-2.md",
     "c7bb4cbae6a8595c3bba9608d7d31bd7911abf876825e3427a39ad5a10a90af8"),
    ("OWNER-DIRECTION-BR-0004", "owner-records/bridge/OWNER-DIRECTION-BR-0004-CHECKPOINT-DISCIPLINE.md",
     "7783efcba342d765250dc0c1083c518e78788ae4bfdfb1f508cdafd93c84e134"),
    ("OWNER-AMENDMENT-P2-0010", "owner-records/phase-2/OWNER-AMENDMENT-P2-0010-CONTEXT-RETRIEVAL-BRIDGE.md",
     "8cc0f3bbf74238f5d0c8b28f00b581c2878154faa69895af35a7f35447c3c7b3"),
]
EXP = ("EXP-001", "/home/usain/gov-os-workbench/spike-sandbox/EVIDENCE.md",
       "84ce1d1390d40a25ae1b5a8af224db871132ebcd8d5b0842b64796f1e0ad7714")
TYPES = {"owner": sys.argv[1], "exp": sys.argv[2]}  # the record types, given by the caller

out = {}
for ident, rel, want in OWNER:
    data = subprocess.run(["git", "-C", ROOT, "show", f"{ARCHIVE}:docs/source/{rel}"], capture_output=True, check=True).stdout
    if hashlib.sha256(data).hexdigest() != want:
        sys.exit(f"{ident}: sha256 differs from the recorded value; nothing written")
    head = (f"---\nid: {ident}\ntype: {TYPES['owner']}\nstatus: ACCEPTED\nstate_class: HISTORICAL\n"
            f"origin: \"git show {ARCHIVE}:docs/source/{rel}\"\norigin_sha256: {want}\n"
            f"imported: 2026-10-11, at this repository's adoption step (DEC-560)\n---\n\n")
    out[f"docs/imported/{ident}.md"] = head + data.decode("utf-8")
data = open(EXP[1], "rb").read()
if hashlib.sha256(data).hexdigest() != EXP[2]:
    sys.exit("EXP-001: sha256 differs from the recorded value; nothing written")
head = (f"---\nid: EXP-001\ntype: {TYPES['exp']}\nstatus: ACCEPTED\nstate_class: EVIDENCE\n"
        f"origin: \"{EXP[1]}\"\norigin_sha256: {EXP[2]}\n"
        f"imported: 2026-10-11, at this repository's adoption step (DEC-560, DEC-564)\n---\n\n")
out["docs/imported/EXP-001.md"] = head + data.decode("utf-8")

S0A = "01 02 03 04 06 07 09 10 11 15".split()
S0B2 = "01 02 03 04 05 06 07 08 09 10 11 12 14 15 17 18 19 20 21 22 25".split()
refs = ""
for n in S0A:
    refs += (f"  - id: S0a-G-{n}\n"
             f"    location: \"S0a STACK_OPTIONS §3, item S0a-G-{n} (named in docs/plan/WAVE_1_WBS.md, the table of source items)\"\n"
             f"    reason: \"research catalogue of stage S0a, kept outside the repository; its requirement is restated in the citing ticket's KPI lines\"\n")
for n in S0B2:
    refs += (f"  - id: G-{n}\n"
             f"    location: \"S0b2 GLUE_REQUIREMENTS, item G-{n} (named in docs/plan/WAVE_1_WBS.md, the table of source items)\"\n"
             f"    reason: \"research catalogue of stage S0b2, kept outside the repository; its requirement is restated in the citing ticket's KPI lines\"\n")

import os
os.makedirs(ROOT + "docs/imported", exist_ok=True)
for rel, text in out.items():
    with open(ROOT + rel, "w", encoding="utf-8") as f:
        f.write(text)
    print("written", rel, len(text))
path = ROOT + "governance/project/external-references.yaml"
old = open(path, encoding="utf-8").read()
if "S0a-G-01" not in old:
    with open(path, "w", encoding="utf-8") as f:
        f.write(old + ("" if old.endswith("\n") else "\n") + refs)
    print("external references added:", len(S0A) + len(S0B2))
