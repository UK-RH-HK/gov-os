"""What stays unchanged, and which code the cases run.

- W2-49's CIT-P, the row on W2-24: its fixture adoption runs A0 to A6 and A8 with no A7 or A10 gate; that is
  unchanged. The session fixture ``after_a8`` is exactly that adoption (every stage through W1-41's ``ok``).
- DEC-732: every run uses this worktree's ``src/``.
"""

from __future__ import annotations

import re

import w2_52_support as gates

support = gates.support


def test_a8_runs_after_a6_without_an_a7_record(after_a8):
    """W2-24's row: A8 after A6, no A7 record anywhere in the adoption run's folder; A0 to A6 and A8 recorded."""
    assert set(after_a8.stages) == set(support.STAGES), sorted(after_a8.stages)
    folder = gates.posixpath.dirname(after_a8.stages["A0"].record)
    gate_records = []
    for rel in support.tree(after_a8.root):
        if gates.posixpath.dirname(rel) == folder:
            text = (support.at_head(after_a8.root, rel) or b"").decode("utf-8", "replace")
            if re.search(r"^stage:\s*['\"]?A(7|10)['\"]?\s*$", text, re.M):
                gate_records.append(rel)
    assert not gate_records, f"A8 ran after A6, yet the folder holds a gate record: {gate_records}"


def test_the_cases_run_this_worktrees_gov(tmp_path):
    """DEC-732: the child the cases start imports ``gov`` from this worktree's ``src/``."""
    sandbox = support.make_sandbox(tmp_path / "sandbox")
    found = gates.gov_file(sandbox).resolve()
    expected = (gates.REPO_ROOT / "src").resolve()
    assert found.is_relative_to(expected), f"the cases' gov is {found}, not under {expected}"
