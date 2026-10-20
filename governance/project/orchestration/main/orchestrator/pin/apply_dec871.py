#!/usr/bin/env python3
"""The owner's DEC-871 (P-W2-55), for the operator: append the entry to the register, add three accepted-history
entries and two load-sensitive entries to the path map. It edits the two files only and commits nothing; the
operator commits them with Role: owner alone (DEC-862 (a)). Run from the repository root, once."""
from pathlib import Path

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
REG = ROOT / "docs/DECISION_REGISTER.md"
MAP = ROOT / "governance/project/path-map.yaml"

ENTRY = '''
## 259. The owner's answer of 2026-10-20 on W2-53's fifth refused close (register v0.259, committed by the owner with `Role: owner`, DEC-862 (a))

### DEC-871 — P-W2-55 (a): three checkpoint commits of the close queue are accepted history; W1-38's two rulesync-probe cases are load-sensitive until W2-57
- **Status:** ACCEPTED (owner, 2026-10-20; committed by the owner with `Role: owner` alone, as DEC-862 (a) keeps ratchet entries) · **Under:** DEC-734, DEC-757, DEC-762, DEC-766, DEC-862, DEC-868 · **Basis:** P-W2-55 (`governance/project/orchestration/packages/P-W2-55.md`): W2-53's close of 2026-10-20 12:30 to 13:49 (14,593 passed, 4 failed) was refused for two causes outside its code.
- **Decision:**
  1. **Accepted history (DEC-734):** the close queue's checkpoint commits `e7bf7a3e895eb42a779dbdb5eed99ad94ab1b2cf` and `851b6230603f9e63f60f45c92465c641b33b857f` (W2-53) and `7bacecd21045f56eb1d3b3da9afd9a9ccd1d5197` (W2-54) carry `Task:` and `Role:` but no `Implements:`; each holds only a `gov checkpoint` record. They are not judged by the trailer gate. The queue's checkpoint commits now carry `Implements: DEC-868`, and its gate checks every commit of a ticket for `Implements:` before the close.
  2. **Load-sensitive (DEC-757, DEC-762):** `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated_project` and `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestSettingsHandEdit::test_key_added_by_hand_is_found_and_named[top-level-env]` failed in the close's parallel regression because `rulesync --version` gave no answer within the portability check's 10-second probe (`RULESYNC_FAILED`); both pass alone (7 passed in 13.7 s, 2026-10-20). Each counts only if it passes in the isolated re-run inside the same close (DEC-757 item 3). Fixed by W2-57 (load out of the close), with row W2-M392 (the probe's limit).
- Next free id: DEC-872.

| Version | Date | Change |
|---|---|---|
| 0.259 | 2026-10-20 | Owner: DEC-871 (P-W2-55 (a): three close-queue checkpoint commits accepted history; W1-38's two rulesync-probe cases load-sensitive until W2-57). Next free id: DEC-872. |
'''

ACCEPTED = '''  - commit: "e7bf7a3e895eb42a779dbdb5eed99ad94ab1b2cf"
    decision: DEC-871
  - commit: "851b6230603f9e63f60f45c92465c641b33b857f"
    decision: DEC-871
  - commit: "7bacecd21045f56eb1d3b3da9afd9a9ccd1d5197"
    decision: DEC-871
'''

LOAD = '''  - test: "tests/acceptance/W1-38/test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated_project"
    decision: DEC-871
    reason: "rulesync --version gave no answer within the portability check's 10-second probe under the close's parallel load; passes alone, 7 of 7 in 13.7 s (W2-53's close, 2026-10-20 13:49)"
    fixed_by: W2-57
  - test: "tests/acceptance/W1-38/test_w1_38_rulesync.py::TestSettingsHandEdit::test_key_added_by_hand_is_found_and_named[top-level-env]"
    decision: DEC-871
    reason: "rulesync --version gave no answer within the portability check's 10-second probe under the close's parallel load; passes alone, 7 of 7 in 13.7 s (W2-53's close, 2026-10-20 13:49)"
    fixed_by: W2-57
'''

reg = REG.read_text()
assert "### DEC-871 " not in reg, "DEC-871 is already in the register"
assert "**Version:** 0.258 (the version table" in reg, "the register is not at v0.258"
REG.write_text(reg.rstrip("\n") + "\n" + ENTRY + "\n---\n")
REG.write_text(REG.read_text().replace("**Version:** 0.258 (the version table", "**Version:** 0.259 (the version table", 1))

text = MAP.read_text()
anchor = '    decision: DEC-717\n'
assert text.count(anchor) == 1, "the accepted_history anchor is not unique"
text = text.replace(anchor, anchor + ACCEPTED, 1)
assert text.rstrip("\n").endswith("fixed_by: W2-M384"), "load_sensitive is not the path map's last block"
MAP.write_text(text.rstrip("\n") + "\n" + LOAD)
print("edited: docs/DECISION_REGISTER.md, governance/project/path-map.yaml")
