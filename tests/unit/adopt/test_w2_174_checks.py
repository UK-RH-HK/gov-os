"""W2-174 S4 and F1: the answers file is checked whole before anything is written; one refusal writes nothing."""
from __future__ import annotations

import datetime

import pytest

from .test_w2_174_support import DONE, answers_file, gov, gov_json, repo_with, snapshot, ticket

from gov.adopt import verify_pass
from gov.cli.errors import GovError

TODAY = datetime.date(2026, 11, 13)


def refused(root, answers, code, tmp_path):
    before = snapshot(root)
    with pytest.raises(GovError) as raised:
        verify_pass.apply(root, answers_file(tmp_path, answers) if isinstance(answers, dict) else answers, "s", TODAY)
    assert raised.value.code == code
    assert snapshot(root) == before  # nothing written, no marker, no temporary file


def base(tmp_path):
    return repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=["one", "two", DONE], failure=["three"]),
                                "DAEO-c3": ticket("DAEO-c3", "closed", success=["closed line"])})


def test_unknown_ticket(tmp_path):
    refused(base(tmp_path), {"DAEO-a1": {"S1": "a", "S2": "b", "F1": "c"}, "DAEO-zz": {"S1": "x"}},
            "VERIFY_PASS_UNKNOWN_TICKET", tmp_path)


def test_closed_ticket(tmp_path):
    refused(base(tmp_path), {"DAEO-c3": {"S1": "x"}}, "VERIFY_PASS_CLOSED", tmp_path)


def test_unknown_label(tmp_path):
    for entry in ({"S1": "a", "S2": "b", "F1": "c", "S9": "d"}, {"S1": "a", "S2": "b", "F1": "c", "S3": "d"},
                  {"S1": "a", "S2": "b", "F1": "c", "F2": "d"}, {"S1": "a", "S2": "b", "F1": "c", "x": "d"}):
        refused(base(tmp_path / str(len(entry)) / str(sorted(entry)[-1])), {"DAEO-a1": entry},
                "VERIFY_PASS_UNKNOWN_LABEL", tmp_path)


def test_an_unanswered_line_is_refused_and_the_ticket_stays_unmarked(tmp_path):
    root = base(tmp_path)
    refused(root, {"DAEO-a1": {"S1": "a", "F1": "c"}}, "VERIFY_PASS_UNANSWERED", tmp_path)
    assert "verify_pass" not in (root / ".tickets/DAEO-a1.md").read_text(encoding="utf-8")
    refused(root, {"DAEO-a1": {}}, "VERIFY_PASS_UNANSWERED", tmp_path)


@pytest.mark.parametrize("clause", ["", "   ", "TBD", "tbd", "Todo.", " N/A ", "none", "None.", ".", None, 5, ["x"],
                                    {"a": "b"}])
def test_an_empty_or_placeholder_clause(tmp_path, clause):
    refused(base(tmp_path), {"DAEO-a1": {"S1": clause, "S2": "b", "F1": "c"}}, "VERIFY_PASS_EMPTY_CLAUSE", tmp_path)


def test_a_clause_that_only_starts_like_a_placeholder_is_text_of_its_own(tmp_path):
    root = base(tmp_path)
    changed = verify_pass.apply(root, answers_file(tmp_path, {"DAEO-a1": {"S1": "TBD by the designer: names the case",
                                                                         "S2": "none of the above", "F1": "n/a case"}}),
                                "s", TODAY)
    assert changed == ["DAEO-a1"]


@pytest.mark.parametrize("content", [None, "not: [yaml", "- a\n- b\n", "plain text", "DAEO-a1: oops\n", ""])
def test_an_answers_file_that_is_missing_or_not_a_mapping_of_mappings(tmp_path, content):
    root = base(tmp_path)
    path = tmp_path / "bad.yaml"
    if content is not None:
        path.write_text(content, encoding="utf-8")
    refused(root, path, "VERIFY_PASS_ANSWERS_UNREADABLE", tmp_path)


def test_nine_good_entries_and_one_bad_leave_the_whole_tree_byte_identical(tmp_path):
    tickets = {f"DAEO-t{n}": ticket(f"DAEO-t{n}", success=["a line", "b line"]) for n in range(10)}
    root = repo_with(tmp_path, tickets)
    (root / "README.md").write_text("decoy\n", encoding="utf-8")
    answers = {name: {"S1": "x", "S2": "y"} for name in tickets}
    answers["DAEO-t9"]["S3"] = "no such line"
    refused(root, answers, "VERIFY_PASS_UNKNOWN_LABEL", tmp_path)
    answers["DAEO-t9"] = {"S1": "x", "S2": "   "}
    refused(root, answers, "VERIFY_PASS_EMPTY_CLAUSE", tmp_path)


def test_a_failed_check_through_the_command_is_gov_exit_1_with_the_code(tmp_path):
    root = base(tmp_path)
    before = snapshot(root)
    answers = answers_file(tmp_path, {"DAEO-c3": {"S1": "x"}})
    code, envelope, _ = gov_json("adopt", "--verify-apply", str(answers), "--root", str(root), "--session", "s")
    assert code == 1 and envelope["ok"] is False and envelope["error"]["code"] == "VERIFY_PASS_CLOSED"
    code, _, err = gov("adopt", "--verify-apply", str(answers), "--root", str(root), "--session", "s")
    assert code == 1 and "VERIFY_PASS_CLOSED" in err and snapshot(root) == before


def test_a_ticket_the_answers_do_not_name_is_never_edited_even_with_missing_lines(tmp_path):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=["one"]), "DAEO-b2": ticket("DAEO-b2", success=["two"])})
    before = snapshot(root)
    verify_pass.apply(root, answers_file(tmp_path, {"DAEO-a1": {"S1": "x"}}), "s", TODAY)
    assert snapshot(root)[".tickets/DAEO-b2.md"] == before[".tickets/DAEO-b2.md"]
