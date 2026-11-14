"""W2-174 S2: ``gov adopt --verify-apply`` appends the clauses to the named lines and adds the one marker line."""
from __future__ import annotations

import datetime

import pytest

from .test_w2_174_support import DONE, answers_file, gov, gov_json, repo_with, snapshot, ticket

from gov.adopt import verify_pass
from gov.cli.errors import GovError

TODAY = datetime.date(2026, 11, 13)
FIVE = ['plain first line [DEC-1]   # a comment after it', '"double \\"quoted\\" second line"',
        "'single quoted ''third'' line'", DONE, "plain fifth line"]


def five(tmp_path):
    return repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=FIVE[:3] + [DONE], failure=["plain fifth line"])})


def test_apply_changes_only_the_appended_clauses_and_the_one_marker_line(tmp_path):
    root = five(tmp_path)
    path = root / ".tickets/DAEO-a1.md"
    old = path.read_text(encoding="utf-8")
    answers = answers_file(tmp_path, {"DAEO-a1": {"S1": "first clause", "S2": 'says "yes"', "S3": "it's third",
                                                  "F1": "fifth clause"}})
    assert verify_pass.apply(root, answers, "sess-1", TODAY) == ["DAEO-a1"]
    expected = (old.replace("plain first line [DEC-1]   # a comment", "'plain first line [DEC-1] Verify: first clause'"
                            "   # a comment")
                .replace('second line"', 'second line Verify: says \\"yes\\""')
                .replace("third'' line'", "third'' line Verify: it''s third'")
                .replace("  - plain fifth line", "  - 'plain fifth line Verify: fifth clause'")
                .replace("# end of the keys\n---", "# end of the keys\nverify_pass: 2026-11-13 sess-1\n---"))
    assert path.read_text(encoding="utf-8") == expected
    assert expected != old and expected.count("verify_pass:") == 1


def test_a_plain_line_becomes_a_single_quoted_scalar_with_its_clause_whatever_the_clause_holds(tmp_path):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=["first line", "second line", "third line"])})
    path = root / ".tickets/DAEO-a1.md"
    old = path.read_text(encoding="utf-8")
    answers = {"DAEO-a1": {"S1": "run it: it passes", "S2": "see # note", "S3": "plain, fine"}}
    verify_pass.apply(root, answers_file(tmp_path, answers), "s", TODAY)
    new = path.read_text(encoding="utf-8")
    assert [line for line in new.split("\n") if line not in old.split("\n")] == [
        "  - 'first line Verify: run it: it passes'", "  - 'second line Verify: see # note'",
        "  - 'third line Verify: plain, fine'", "verify_pass: 2026-11-13 s"]
    from gov.brief.build import kpi_rows
    from gov.util.frontmatter import parse
    rows = {label: verify for label, _, verify in kpi_rows(parse(new, rstrip=True))}
    assert rows == {"S1": "run it: it passes", "S2": "see # note", "S3": "plain, fine"}


def test_a_flow_style_list_gets_its_clause_inside_a_quoted_scalar(tmp_path):
    text = ticket("DAEO-a1", success=["x"]).replace("  success:\n  - x\n", "  success: [one, two]\n")
    root = repo_with(tmp_path, {"DAEO-a1": text})
    verify_pass.apply(root, answers_file(tmp_path, {"DAEO-a1": {"S1": "a, b", "S2": "c"}}), "s", TODAY)
    new = (root / ".tickets/DAEO-a1.md").read_text(encoding="utf-8")
    assert "  success: ['one Verify: a, b', 'two Verify: c']\n" in new


def test_a_multi_line_clause_is_joined_to_one_line(tmp_path):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=["one line"])})
    verify_pass.apply(root, answers_file(tmp_path, {"DAEO-a1": {"S1": "first\nsecond"}}), "s", TODAY)
    assert "  - 'one line Verify: first second'\n" in (root / ".tickets/DAEO-a1.md").read_text(encoding="utf-8")


def test_a_ticket_that_already_has_the_marker_gets_it_replaced_in_place(tmp_path):
    text = ticket("DAEO-a1", success=["one line"], extra="verify_pass: 2026-11-01 old-session\nowner: me")
    root = repo_with(tmp_path, {"DAEO-a1": text})
    verify_pass.apply(root, answers_file(tmp_path, {"DAEO-a1": {"S1": "c"}}), "new", TODAY)
    new = (root / ".tickets/DAEO-a1.md").read_text(encoding="utf-8")
    assert new.count("verify_pass:") == 1
    assert "verify_pass: 2026-11-13 new\nowner: me\n" in new


def test_apply_leaves_other_tickets_and_files_alone_and_a_mapping_line_is_never_edited(tmp_path):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=["one", DONE]),
                                "DAEO-b2": ticket("DAEO-b2", success=["not named"]),
                                "DAEO-c3": ticket("DAEO-c3", success=[DONE])})
    before = snapshot(root)
    answers = answers_file(tmp_path, {"DAEO-a1": {"S1": "c"}})
    assert verify_pass.apply(root, answers, "s", TODAY) == ["DAEO-a1"]
    after = snapshot(root)
    assert {name for name in after if after[name] != before[name]} == {".tickets/DAEO-a1.md"}
    assert set(after) == set(before)
    assert DONE in after[".tickets/DAEO-a1.md"].decode()


def test_a_block_scalar_line_is_refused_and_nothing_is_written(tmp_path):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=["one", "|\n    block line"])})
    before = snapshot(root)
    with pytest.raises(GovError) as refused:
        verify_pass.apply(root, answers_file(tmp_path, {"DAEO-a1": {"S1": "c", "S2": "d"}}), "s", TODAY)
    assert refused.value.code == "VERIFY_PASS_EDIT_FAILED"
    assert snapshot(root) == before


def test_the_command_needs_a_session_and_writes_the_marker_with_it(tmp_path):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=["one"])})
    answers = answers_file(tmp_path, {"DAEO-a1": {"S1": "c"}})
    before = snapshot(root)
    code, _, err = gov("adopt", "--verify-apply", str(answers), "--root", str(root))
    assert code == 2 and "--session" in err and snapshot(root) == before
    code, envelope, _ = gov_json("adopt", "--verify-apply", str(answers), "--root", str(root), "--session", "S-9")
    assert code == 0 and envelope["result"] == {"changed": ["DAEO-a1"]}
    assert "verify_pass: " in (root / ".tickets/DAEO-a1.md").read_text(encoding="utf-8")
    assert "S-9\n---" in (root / ".tickets/DAEO-a1.md").read_text(encoding="utf-8")
    assert gov_json("adopt", "--verify-list", "--root", str(root))[1]["result"]["text"] == "none"


def test_a_session_that_would_not_read_back_as_the_marker_is_refused(tmp_path):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=["one"])})
    before = snapshot(root)
    with pytest.raises(GovError) as refused:
        verify_pass.apply(root, answers_file(tmp_path, {"DAEO-a1": {"S1": "c"}}), "12:30:00", TODAY)
    assert refused.value.code == "VERIFY_PASS_EDIT_FAILED" and snapshot(root) == before
