"""S6 and F2: the status reconciliation: the owner's list, the owner's decision (DEC-1098 (3)) before any status
changed, LINK-RECONCILIATION.md, R-12, and no spent or PROPOSED decision counted as drift."""

from __future__ import annotations

import json
import re
import subprocess
import sys

import pytest

import w2_130_support as s


def _sitting() -> list[dict]:
    rows = s.sitting_rows(s.show(s.SITTING_COMMIT, s.SITTING))
    assert rows, "the sitting file holds no row of groups A to F"
    return rows


# ----------------------------------------------------------------------------------------------------- history


def test_s6_the_sitting_list_exists_in_2f9c80b1f_an_ancestor_of_the_starting_head():
    assert s.show(s.SITTING_COMMIT, s.SITTING) is not None, f"{s.SITTING} is not in 2f9c80b1f"
    assert s.is_ancestor(s.SITTING_COMMIT, s.START)


def test_s6_the_sitting_lists_the_150_ids_of_the_110_spent_and_the_40_proposed():
    rows = _sitting()
    assert len(rows) == 150 and len({row["id"] for row in rows}) == 150, f"{len(rows)} rows in groups A to F"
    assert sum(1 for row in rows if row["group"] in "ABC") == 40, "groups A to C are the 40 PROPOSED entries"
    assert sum(1 for row in rows if row["group"] in "DEF") == 110, "groups D to F are the 110 spent ones"
    assert all(row["proposal"] and row["reason"] for row in rows), "a sitting row without a proposal or reason"


def test_f2_the_owners_decision_9546edd61_is_an_ancestor_of_c4420040f():
    assert s.is_ancestor(s.DEC1098_COMMIT, s.SECOND)
    assert not s.is_ancestor(s.DEC1098_COMMIT, s.FIRST), "e12f8a30c is the commit made before the owner decided"


def test_f2_e12f8a30c_changes_no_status_word_and_no_done_tag():
    changed = [c["id"] for c in s.register_delta(s.START, s.FIRST)["changes"]
               if s.status_word(c["old"]) != s.status_word(c["new"]) or s.has_done_tag(c["old"]) != s.has_done_tag(c["new"])]
    assert not changed, f"status words changed before the owner decided: {changed[:6]}"


def test_s6_c4420040f_changes_a_status_only_to_the_word_the_sitting_proposed_and_keeps_the_old_text():
    """F1 and S6: each status DEC-1098 (3) names (it accepted groups A to G as proposed) is written new word first,
    the old status text kept after ``; it was``; no status changes for a row the sitting did not change."""
    rows = {row["id"]: row for row in _sitting()}
    delta = s.register_delta(s.parent(s.SECOND), s.SECOND)
    assert delta["same_ids"] and delta["masked_equal"], "c4420040f changes a register line that is no status line"
    decided = {c["id"]: c for c in delta["changes"] if c["kind"] == "status"}
    other = [c["id"] for c in delta["changes"] if c["kind"] == "other"]
    assert not other, f"status lines changed in a way DEC-1098 (3) does not name: {other[:5]}"
    expected = {i: re.match(r"[A-Z]+", row["proposal"]).group(0) for i, row in rows.items() if row["group"] in "ABCDE"}
    assert set(decided) == set(expected), (f"decided but not proposed: {sorted(set(decided) - set(expected))[:5]}; "
                                           f"proposed but not written: {sorted(set(expected) - set(decided))[:5]}")
    wrong = [(i, s.status_word(c["new"]), expected[i]) for i, c in decided.items()
             if s.status_word(c["new"]) != expected[i]]
    assert not wrong, f"{wrong[:5]}"


# --------------------------------------------------------------------------------------------- the record's commits


def test_f2_the_owners_decision_is_an_ancestor_of_every_status_commit_the_record_names(record):
    commits = record.commit_list("status")
    assert s.full(s.SECOND) in commits, "commits.status lacks c4420040f"
    assert all(s.is_ancestor(s.DEC1098_COMMIT, c) for c in commits)


def test_f2_no_cleanup_commit_without_9546edd61_as_ancestor_changes_a_status_word_or_done_tag(record):
    bad = []
    for commit in record.commit_list("cleanup"):
        if s.is_ancestor(s.DEC1098_COMMIT, commit):
            continue
        for c in s.register_delta(s.parent(commit), commit)["changes"]:
            if s.status_word(c["old"]) != s.status_word(c["new"]) or s.has_done_tag(c["old"]) != s.has_done_tag(c["new"]):
                bad.append((commit[:12], c["id"]))
    assert not bad, f"{bad[:5]}"


def test_s6_gov_links_reports_no_status_conflict_at_head(head_findings):
    bad = [(f["ids"], f["path"]) for f in head_findings if f["code"] == "STATUS_CONFLICT"]
    assert not bad, f"{bad[:5]}"


def test_s6_the_r_12_commit_changes_only_decisions_in_force_and_only_its_r_12_line(record, head_tree):
    commit = record.commit_list("r12")[0]
    assert s.changed_files(commit) == {s.IN_FORCE: "M"}, f"changes {sorted(s.changed_files(commit))}"
    diff = s.git("diff", "-U0", s.parent(commit), commit, "--", s.IN_FORCE)
    moved = [line for line in diff.splitlines() if line[:1] in "+-" and line[:3] not in ("+++", "---")]
    assert moved and all(line[1:].startswith("- R-12 (") for line in moved), "a line other than R-12's changed"
    assert commit in record.commit_list("status"), "the R-12 commit is a status commit of the record"
    lines = [line for line in (head_tree / s.IN_FORCE).read_text(encoding="utf-8").splitlines()
             if line.startswith("- R-12 (")]
    assert lines, "DECISIONS-IN-FORCE.md has no R-12 line"


def test_s6_linkreconciliation_names_the_sitting_file_and_dec_1098_3_and_carries_each_sitting_row(head_tree):
    if not (head_tree / s.RECONCILIATION).is_file():
        pytest.fail(f"{s.RECONCILIATION} does not exist at HEAD")
    text = (head_tree / s.RECONCILIATION).read_text(encoding="utf-8")
    assert "governance/project/orchestration/packages/W2-130-SITTING.md" in text, "it does not name the sitting file"
    assert "DEC-1098 (3)" in text, "it does not name DEC-1098 (3)"
    have, bad = s.reconciliation_rows(text), []
    for row in _sitting():
        got = have.get(row["id"])
        if got is None:
            bad.append((row["id"], "no row"))
        elif (got["group"], got["proposal"], got["reason"]) != (row["group"], row["proposal"], row["reason"]):
            bad.append((row["id"], "group, proposal or reason differs from the sitting row"))
        elif not got["ruling"]:
            bad.append((row["id"], "no ruling"))
    assert not bad, f"{len(bad)} of 150 sitting rows: {bad[:5]}"


def test_f2_the_drift_list_at_head_holds_no_sitting_id_that_dec_1098_3_did_not_rule_current(record, head_tree):
    """DEC-1098 (3) accepted groups A to G as proposed: A and B (ACCEPTED) and F (in force) are current; C (SUPERSEDED,
    WITHDRAWN, DEFERRED), D and E (DONE) are not, so none of their ids may be counted as drift."""
    done = subprocess.run([sys.executable, "-"], input=record.block("drift", "python"), cwd=head_tree,
                          capture_output=True, text=True, check=False, timeout=300)
    assert done.returncode == 0, f"the drift script failed: {done.stderr.strip()[-300:]}"
    drift = {s.pair(item)[0] for item in json.loads(done.stdout)["drift"]}
    not_current = {row["id"] for row in _sitting() if row["group"] in "CDE"}
    assert not drift & not_current, f"drift counts decisions DEC-1098 (3) did not rule current: {sorted(drift & not_current)[:6]}"
