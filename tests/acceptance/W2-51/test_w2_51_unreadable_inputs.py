"""W2-51 KPI failure line 2: "An input it cannot read is a named failure, never a pass." """

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from w2_51_support import (CITED, CITP_APPLIED, CITP_MOVED, CIT_P_NAME, DELIVERED, IDS_EXIST, LIST_COUNTS,
                           TRIAGE_COUNTS, WAVE2_TICKETS, plan_v41, plan_v42, run_validator)

CONTRACT_CHECKS = (DELIVERED, CITED, IDS_EXIST, CITP_MOVED, CITP_APPLIED)


def _remove(rel):
    def go(root):
        p = Path(root) / rel
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    return go


def _overwrite(rel, text):
    def go(root):
        (Path(root) / rel).write_text(text, encoding="utf-8")
    return go


def _directory_in_place(rel):
    def go(root):
        p = Path(root) / rel
        p.unlink()
        p.mkdir()
        (p / "inside.md").write_text("not the file\n", encoding="utf-8")
    return go


def _no_read_permission(rel):
    def go(root):
        os.chmod(Path(root) / rel, 0)
    return go


CASES = {
    # case id: (plan, change, the input's name the FAIL line must carry, checks that must not PASS)
    "contract-missing": (plan_v41, _remove("docs/contract/contract.yaml"), "contract.yaml", CONTRACT_CHECKS),
    "contract-unparsable": (plan_v41, _overwrite("docs/contract/contract.yaml",
                                                 "version: '4.1'\ncapabilities: [\n  - id: CAP-91\n    covers: {{\n"),
                            "contract.yaml", CONTRACT_CHECKS),
    "wbs-missing": (plan_v41, _remove("docs/plan/WAVE_2_WBS.md"), "WAVE_2_WBS.md", (WAVE2_TICKETS,)),
    "list-missing": (plan_v41, _remove("docs/plan/WAVE_2_LIST.md"), "WAVE_2_LIST.md", (LIST_COUNTS,)),
    "triage-is-a-folder": (plan_v41, _directory_in_place("docs/plan/WAVE_2_TRIAGE.md"), "WAVE_2_TRIAGE.md",
                           (TRIAGE_COUNTS,)),
    "tickets-folder-missing": (plan_v41, _remove(".tickets"), ".tickets", (WAVE2_TICKETS, DELIVERED)),
    "ticket-frontmatter-unparsable": (plan_v41, _overwrite(".tickets/DAEO-t002.md",
                                                           "---\nid: DAEO-t002\nwbs_id: [W2-02\n---\n# broken\n"),
                                      "DAEO-t002.md", (WAVE2_TICKETS, DELIVERED)),
    "cit-p-unreadable": (plan_v42, _no_read_permission(f"docs/changes/{CIT_P_NAME}"), CIT_P_NAME,
                         (CITP_MOVED, CITP_APPLIED)),
}


@pytest.mark.parametrize("case", sorted(CASES))
def test_an_input_it_cannot_read_is_a_named_failure_never_a_pass(tmp_path, case):
    make, change, needle, dependants = CASES[case]
    if case == "cit-p-unreadable" and os.geteuid() == 0:
        pytest.skip("root reads a file whatever its permissions")
    root = make().write(tmp_path / "tree")
    change(root)
    try:
        res = run_validator(root, tmp_path / "home")
    finally:
        if case == "cit-p-unreadable":
            os.chmod(root / "docs" / "changes" / CIT_P_NAME, 0o644)

    assert "Traceback" not in res.stderr, f"the validator crashed instead of naming the failure\n{res!r}"
    named = [l for l in res.fail_lines() if needle in l]
    assert named, f"no FAIL line names the input {needle!r}\n{res!r}"
    for name in dependants:
        passed = [s for s, _ in res.lines_for(name) if s == "PASS"]
        assert not passed, f"{name} passed although {needle} could not be read\n{res!r}"
    assert res.returncode == 1, f"a run with a failing check exits 1\n{res!r}"


def test_a_root_that_does_not_exist_passes_nothing(tmp_path):
    res = run_validator(tmp_path / "no-such-tree", tmp_path / "home")
    assert res.returncode != 0, res
    assert not [l for l in res.status_lines if l.startswith("PASS")], res
