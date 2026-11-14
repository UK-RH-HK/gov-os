"""Fills ACT-CLASS-RULES-AGENTS-1.package.md's placeholders after the rehearsal and finalize (prose only; the bash blocks
are asserted unchanged, since part 5 of the rehearsal ran them as printed)."""
import re
from pathlib import Path

p = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/ACT-CLASS-RULES-AGENTS-1.package.md")
t = p.read_text()
blocks = re.findall(r"```bash\n.*?```", t, re.S)
M = "244d5a399df53418f02e93f97b44222605645260dea20ffe7bc17f1734aadc09"
rep = {
    "CASES cases, ends `failures: FAILS`": "91 cases, ends `failures: 0`",
    "**Over PAIRS (root, path) pairs**": "**Over 226 (root, path) pairs**",
    "its 57 ACT file lists made manifests its own way: TRIAL57.**": "its 57 ACT file lists made manifests its own way: none changes class** (6 a, 19 b, 32 O under both tables).",
    "Every ACT file in\n  the packages folder (TRIALALL).": "Every ACT file in\n  the packages folder (94): none changes class (10 a, 51 b, 33 O under both).",
    "Every bundle under `acts/` (BUNDLES).": "Every bundle under `acts/` (44): one changes, ACT-CLAUDE-RULES-1, (O) to (b).",
    "`tests/acceptance/W2-148`: TESTS.**": "`tests/acceptance/W2-148`: 654 passed, 0 failed.** The clone's only change is the table.",
    "(`build_act.py gates`, read only): GATES": "(`build_act.py gates`, read only): `validate_manifest` pass; 18 files hash as the\nmanifest says, none unlisted, no `__pycache__`; the path rule passes on `apply.sh` and all five checks; `act_class.classify`: class O (three\nrows `operator-own`), no hit, also on the LANDING base's rows and under its own after table. Clone head: `8801ffd17df9`.",
    "REHEARSALSHA": "e3652b6668bf3494f933e8bf116277bbf729ffd582a2cf6c23f786e4f88b6ddc",
    "MANIFESTSHA": M,
    "**The owner's line: `yes ACT-CLASS-RULES-AGENTS-1 SHA8`** (the first 8 digits of the manifest's sha256, section 8).\n\n": "",
    "LANDING would then refuse at `check` (exit 3, \"moved: install/class-rules.yaml\")": "LANDING would then refuse at `check` (exit 3, \"moved: home/gov-os-operator/install/APPROVED\"; its `keep.txt` also pins today's table)",
    "## 8. Files and hashes": "## 9. Files and hashes",
    "## 7. Risks": "## 8. Risks",
    "## 6. The order with": "## 7. The order with",
    "(its `verify` run first; section 6)": "(its `verify` run first; section 7)",
    "**Not yet independently reviewed** (section 7).": "**Not yet independently reviewed** (section 8).",
}
for a, b in rep.items():
    assert a in t, a
    t = t.replace(a, b)
yes = ("## 6. The yes line\n**After the independent review is in `review.md`** (its fenced verdict block), the owner sends, on its own line:\n\n"
       f"yes ACT-CLASS-RULES-AGENTS-1 {M[:8]}\n\n(the first 8 digits of the manifest's sha256 `{M}`, section 9). Then the owner's "
       "operator runs section 5.\n\n")
t = t.replace("## 7. The order with", yes + "## 7. The order with")
assert "SHA8" not in t and not re.search(r"\b(CASES|FAILS|PAIRS|TRIAL57|TRIALALL|BUNDLES|TESTS|GATES)\b", t)
assert re.findall(r"```bash\n.*?```", t, re.S) == blocks
p.write_text(t)
print("filled")
