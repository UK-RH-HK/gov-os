"""The scan's id match and question key (EXAMIN's F-033; W2-204 S13 to S16): regression evidence for the helpers.

An id counts beside the set's audit name or tag, a question's text read counts (kind ``text``, match the id), the path
counts as before and wins; the key is the normalised question cut to 48 characters, none under 24."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.memaudit import scan  # noqa: E402

SINCE = datetime(2026, 11, 5, tzinfo=timezone.utc)
UNTIL = datetime(2026, 11, 20, tzinfo=timezone.utc)
LONG = "Which amber clause of the Ollivane harbour charter fixes the night toll for skiffs?"


def _set(tmp_path, name="memory-audit-20261101"):
    folder = tmp_path / "eval" / name / "hidden"
    folder.mkdir(parents=True)
    return folder


def test_names_are_the_audit_name_components_and_their_digits(tmp_path):
    folder = _set(tmp_path)
    assert scan.set_names(folder) == ["memory-audit-20261101", "20261101"]
    standing = tmp_path / "x" / "memory-standing-20260102" / "set"
    standing.mkdir(parents=True)
    assert scan.set_names(standing) == ["memory-standing-20260102", "20260102"]


def test_a_set_without_an_audit_name_uses_its_folders_name_and_no_tag(tmp_path):
    plain = tmp_path / "somefolder" / "hidden"
    plain.mkdir(parents=True)
    assert scan.set_names(plain) == ["somefolder"]
    assert scan.set_names(tmp_path / "somefolder") == ["somefolder"]
    short = tmp_path / "ab" / "set"
    short.mkdir(parents=True)
    assert scan.set_names(short) == []


def test_a_bare_id_is_no_finding_and_an_id_beside_the_tag_is(tmp_path):
    matcher = scan.Matcher(["/nowhere/set"], ["q07"], ["memory-audit-20261101", "20261101"])
    assert matcher.find(["we did q07 today"]) is None
    assert matcher.find(["20261101 then q07"]) == ("id", "q07")
    assert matcher.find(["see memory-audit-20261101", "and q07"]) == ("id", "q07")
    assert matcher.find(["x120261101 q07"]) is None  # the tag is a whole token too


def test_a_matcher_without_names_finds_no_id():
    assert scan.Matcher(["/s"], ["q07"]).find(["q07 20261101"]) is None


def test_key_is_normalised_cut_to_48_and_none_under_24(tmp_path):
    folder = _set(tmp_path)
    (folder / "q01.yaml").write_text(f"id: q01\nquestion: |\n  {LONG[:25]}\n    {LONG[26:]}\n")
    (folder / "q02.yaml").write_text("id: q02\nquestion: Too short here\n")
    (folder / "q03.yaml").write_text("id: q03\ngold_answer: nothing\n")
    problems = []
    keys = scan.set_keys(folder, problems)
    assert problems == [] and keys == {" ".join(LONG.split()).lower()[:48]: "q01"}


def test_an_unreadable_question_file_is_a_problem(tmp_path):
    folder = _set(tmp_path)
    (folder / "q01.yaml").write_text("question: [unclosed\n")
    (folder / "q02.yaml").write_bytes(b"\xff\xfe\x00bad")
    problems = []
    assert scan.set_keys(folder, problems) == {}
    assert sorted(Path(p["file"]).name for p in problems) == ["q01.yaml", "q02.yaml"]
    assert all(p["error"] for p in problems)


def test_a_key_in_any_text_value_is_a_text_finding_with_the_ids_match():
    key = " ".join(LONG.split()).lower()[:48]
    matcher = scan.Matcher(["/s"], ["q05"], ["20261101"], {key: "q05"})
    assert matcher.find(["noise", "  " + LONG.upper().replace(" ", "\n ") + " more"]) == ("text", "q05")
    assert matcher.find(["Which amber clause of the other charter fixes the toll"]) is None
    assert matcher.find(["/s/q05.yaml " + LONG]) == ("path", "/s")  # path first
    assert matcher.find([LONG + " 20261101 q05"]) == ("text", "q05")  # text before id


def test_scan_reports_text_without_printing_it_and_ignores_a_bare_id(tmp_path):
    folder = _set(tmp_path)
    (folder / "q05.yaml").write_text(f"id: q05\nquestion: {LONG}\ngold_answer: the Pennifold rule\n")
    projects = tmp_path / "projects"
    path = projects / "p" / "s.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text("\n".join([
        json.dumps({"t": "item q05 of the list"}),
        json.dumps({"t": "Read:   " + LONG.lower().replace(" ", "  ")}),
        json.dumps({"t": "memory-audit-20261101 q05"})]) + "\n")
    os.utime(path, (SINCE.timestamp() + 5, SINCE.timestamp() + 5))
    result = scan.scan(folder.parent, SINCE, UNTIL, None, [], projects, home=str(tmp_path))
    assert [(f["line"], f["kind"], f["match"]) for f in result["findings"]] == [(2, "text", "q05"), (3, "id", "q05")]
    assert "Ollivane" not in json.dumps(result) and "Pennifold" not in json.dumps(result)


def test_an_unreadable_question_file_makes_the_scan_incomplete_not_clean(tmp_path):
    folder = _set(tmp_path)
    (folder / "q01.yaml").write_text("question: [unclosed\n")
    result = scan.scan(folder.parent, SINCE, UNTIL, None, [], tmp_path / "projects", home=str(tmp_path))
    assert any(p["file"].endswith("q01.yaml") for p in result["problems"])
