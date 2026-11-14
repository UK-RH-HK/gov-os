"""F1: the clean-up changes nothing but status-line marks, the owner's decided statuses, tickets' ``sources:`` and
the owner-decided KPI 4 line; history is not rewritten."""

from __future__ import annotations

import fnmatch

import pytest
import yaml

import w2_130_support as s

BRACKET = "[changed, DEC-1098 (3); DEC-1088 (6)]"


def _register_problems(commit: str) -> list:
    delta = s.register_delta(s.parent(commit), commit)
    if not delta["same_ids"]:
        return [(commit[:12], "an entry was added or removed")]
    if not delta["masked_equal"]:
        return [(commit[:12], "a register line other than a status line changed")]
    rows = {row["id"]: row for row in s.sitting_rows(s.show(s.SITTING_COMMIT, s.SITTING))}
    bad = []
    for change in delta["changes"]:
        if change["kind"] == "append":
            continue
        decided = commit == s.full(s.SECOND) and change["kind"] == "status" and rows.get(change["id"], {}).get("group") in tuple("ABCDE")
        if not decided:
            bad.append((commit[:12], change["id"], change["kind"], "not marks appended, nor a status DEC-1098 (3) names"))
    return bad


def _ticket_problems(commit: str) -> list:
    bad = []
    for path, (old, new) in s.ticket_changes(commit).items():
        if old is None or new is None:
            bad.append((commit[:12], path, "a ticket file added or removed"))
            continue
        delta = s.ticket_delta(old, new)
        allowed = {"sources"} | ({"kpis"} if commit == s.full(s.SECOND) and path == s.TICKET else set())
        if not delta["same_keys"] or delta["fields"] - allowed or delta["body"]:
            bad.append((commit[:12], path, f"fields {sorted(delta['fields'] - allowed)} or body or key order changed"))
        elif "kpis" in delta["fields"]:
            before, after = s.ticket_kpis(old), s.ticket_kpis(new)
            same = (before.get("failure") == after.get("failure") and len(before["success"]) == len(after["success"])
                    and [x for i, x in enumerate(before["success"]) if i != 3] == [x for i, x in enumerate(after["success"]) if i != 3])
            if not same or BRACKET not in after["success"][3] or BRACKET in before["success"][3]:
                bad.append((commit[:12], path, f"more than KPI 4 changed, or it does not carry {BRACKET}"))
    return bad


@pytest.mark.parametrize("commit", [s.FIRST, s.SECOND])
def test_f1_register_changes_of_e12f8a30c_and_c4420040f_are_status_lines_marks_appended_or_decided(commit):
    assert not _register_problems(s.full(commit))


@pytest.mark.parametrize("commit", [s.FIRST, s.SECOND])
def test_f1_ticket_fields_other_than_sources_and_bodies_are_byte_identical_across_e12f8a30c_and_c4420040f(commit):
    assert not _ticket_problems(s.full(commit))


@pytest.mark.parametrize("commit", [s.FIRST, s.SECOND])
def test_f1_the_two_commits_change_only_the_paths_the_ticket_allows(commit):
    allowed = yaml.safe_load(s.split_ticket(s.show("HEAD", s.TICKET))[1]["allowed_paths"])["allowed_paths"]
    bad = [p for p in s.changed_files(commit) if not any(fnmatch.fnmatch(p, g) for g in allowed)]
    assert not bad, f"paths outside allowed_paths: {bad[:5]}"


def test_f1_every_cleanup_commit_the_record_names_changes_only_status_lines_marks_sources_and_allowed_paths(record):
    allowed = yaml.safe_load(s.split_ticket(s.show("HEAD", s.TICKET))[1]["allowed_paths"])["allowed_paths"]
    bad = []
    for commit in record.commit_list("cleanup"):
        bad += _register_problems(commit) + _ticket_problems(commit)
        bad += [(commit[:12], p, "outside allowed_paths") for p in s.changed_files(commit)
                if not any(fnmatch.fnmatch(p, g) for g in allowed)]
    assert not bad, f"{bad[:6]}"


def test_f1_each_follow_up_marks_commit_changes_the_register_and_no_other_file(record):
    bad = [(c[:12], sorted(s.changed_files(c))) for c in record.commit_list("marks")[2:]
           if set(s.changed_files(c)) != {s.REGISTER}]
    assert not bad, f"{bad}"
    assert record.commit_list("marks")[2:], "commits.marks names no follow-up marks commit (DEC-1115 and DEC-026 are marked by one)"


def test_f1_the_starting_head_is_an_ancestor_of_head():
    assert s.is_ancestor(s.START, "HEAD")
