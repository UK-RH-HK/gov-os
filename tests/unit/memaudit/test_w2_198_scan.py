"""``gov memaudit scan``'s matcher, ids and window (W2-198 S3, F2; regression evidence only, DEC-136)."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.memaudit import scan  # noqa: E402

SINCE = datetime(2026, 11, 5, tzinfo=timezone.utc)
UNTIL = datetime(2026, 11, 20, tzinfo=timezone.utc)


def _set(tmp_path):
    folder = tmp_path / "eval" / "fixtures" / "evaluation" / "memory-audit-20261101" / "hidden"
    folder.mkdir(parents=True)
    for name in ("q01", "q02", "q03"):
        (folder / f"{name}.yaml").write_text("id: " + name + "\nquestion: SECRET QUESTION TEXT\n")
    return folder.parent


def test_ids_are_the_stems_of_the_yaml_files_under_the_set(tmp_path):
    root = _set(tmp_path)
    (root / "hidden" / "notes.txt").write_text("x")
    assert scan.set_ids(root) == ["q01", "q02", "q03"]


def test_path_forms_run_from_the_most_specific(tmp_path):
    root = _set(tmp_path)
    real = os.path.realpath(root)
    forms = scan.path_forms(root, str(tmp_path))
    assert forms == [real, "~/eval/fixtures/evaluation/memory-audit-20261101",
                     "$HOME/eval/fixtures/evaluation/memory-audit-20261101",
                     "fixtures/evaluation/memory-audit-20261101"]


def test_a_set_outside_home_and_without_the_segment_has_the_absolute_form_only(tmp_path):
    other = tmp_path / "x" / "set"
    other.mkdir(parents=True)
    assert scan.path_forms(other, str(tmp_path / "elsewhere")) == [os.path.realpath(other)]


@pytest.mark.parametrize("text, hit", [
    ("see q01 now", "q01"), ("q01", "q01"), ("(q01)", "q01"), ("a:q01.", "q01"),
    ("q010", None), ("aq01", None), ("xq01y", None), ("q01_x", None), ("Q01", None)])
def test_an_id_is_a_whole_token(text, hit):
    found = scan.Matcher([], ["q01"]).find([text])
    assert (found[1] if found else None) == hit


def test_the_most_specific_path_form_wins_and_a_line_gives_one_hit(tmp_path):
    root = _set(tmp_path)
    matcher = scan.Matcher(scan.path_forms(root, str(tmp_path)), ["q01"])
    real = os.path.realpath(root)
    assert matcher.find([f"cat {real}/hidden/q01.yaml"]) == ("path", real)
    assert matcher.find(["cat ~/eval/fixtures/evaluation/memory-audit-20261101/hidden"])[1].startswith("~/")
    assert matcher.find(["cat $HOME/eval/fixtures/evaluation/memory-audit-20261101"])[1].startswith("$HOME/")
    assert matcher.find(["fixtures/evaluation/memory-audit-20261101/hidden"]) == (
        "path", "fixtures/evaluation/memory-audit-20261101")
    assert matcher.find(["no path, q01"]) == ("id", "q01")


def test_json_escaping_hides_nothing_and_a_non_json_line_is_read_as_text():
    matcher = scan.Matcher([], ["q02"])
    line = json.dumps({"message": {"content": [{"text": "see:\nq02 here"}]}}).encode()
    assert b"\\n" in line
    assert matcher.find(scan.texts_of(line)[0]) == ("id", "q02")
    hidden = b'{"t": "\\u0071\\u0030\\u0032"}'
    assert matcher.find(scan.texts_of(hidden)[0]) == ("id", "q02")
    assert matcher.find(scan.texts_of(b'{"cut": "q02 and')[0]) == ("id", "q02")


def test_the_window_is_the_lines_timestamp_and_a_line_without_one_counts():
    inside = lambda raw: scan.in_window(scan.texts_of(raw)[1], SINCE, UNTIL)
    assert inside(b'{"timestamp": "2026-11-06T10:00:00.000Z"}')
    assert not inside(b'{"timestamp": "2026-11-04T23:59:59.000Z"}')
    assert not inside(b'{"timestamp": "2026-11-21T00:00:00Z"}')
    assert inside(b'{"timestamp": "2026-11-05T00:00:00Z"}')  # the ends are in
    assert inside(b'{"summary": "no stamp"}')
    assert inside(b'not json')


def _write(path: Path, lines, mtime):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
    os.utime(path, (mtime, mtime))


def test_scan_finds_one_per_naming_line_and_ignores_files_before_since(tmp_path):
    root, projects = _set(tmp_path), tmp_path / "projects"
    fresh = SINCE.timestamp() + 3600
    _write(projects / "p" / "sess-a.jsonl", [
        json.dumps({"sessionId": "sess-a", "timestamp": "2026-11-06T10:00:00Z", "text": "nothing"}),
        json.dumps({"sessionId": "sess-a", "timestamp": "2026-11-06T10:00:01Z", "text": "ask q02 please"}),
        json.dumps({"sessionId": "sess-a", "timestamp": "2026-11-01T10:00:01Z", "text": "q02 before"}),
    ], fresh)
    _write(projects / "p" / "sess-old.jsonl", [json.dumps({"timestamp": "2026-11-06T10:00:01Z", "t": "q01"})],
           SINCE.timestamp() - 3600)
    result = scan.scan(root, SINCE, UNTIL, None, [], projects, home=str(tmp_path))
    assert [(f["session"], f["line"], f["kind"], f["match"], f["role"]) for f in result["findings"]] == [
        ("sess-a", 2, "id", "q02", None)]
    assert result["transcripts_read"] == 1 and result["problems"] == [] and result["ids_count"] == 3


def test_scan_reads_the_role_from_the_sibling_meta_and_allows_a_session(tmp_path):
    root, projects = _set(tmp_path), tmp_path / "projects"
    fresh = SINCE.timestamp() + 3600
    sub = projects / "p" / "sess-main" / "subagents"
    _write(sub / "agent-a1b2.jsonl", [json.dumps({"sessionId": "sess-main", "t": "q03"})], fresh)
    (sub / "agent-a1b2.meta.json").write_text(json.dumps({"agentType": "independent-auditor"}))
    found = scan.scan(root, SINCE, UNTIL, None, [], projects, home=str(tmp_path))["findings"]
    assert [(f["session"], f["role"], f["file"]) for f in found] == [
        ("sess-main", "independent-auditor", str(sub / "agent-a1b2.jsonl"))]
    allowed = scan.scan(root, SINCE, UNTIL, None, ["sess-main"], projects, home=str(tmp_path))
    assert allowed["findings"] == [] and [a["session"] for a in allowed["allowed"]] == ["sess-main"]


def test_an_id_option_replaces_the_sets_ids(tmp_path):
    root, projects = _set(tmp_path), tmp_path / "projects"
    _write(projects / "s.jsonl", [json.dumps({"t": "h7 and q02"})], SINCE.timestamp() + 5)
    result = scan.scan(root, SINCE, UNTIL, ["h7"], [], projects, home=str(tmp_path))
    assert [f["match"] for f in result["findings"]] == ["h7"] and result["ids_count"] == 1


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads a mode 000 file")
def test_an_unreadable_transcript_is_a_problem_naming_the_file_and_never_its_text(tmp_path):
    root, projects = _set(tmp_path), tmp_path / "projects"
    path = projects / "locked.jsonl"
    _write(path, [json.dumps({"t": "q01"})], SINCE.timestamp() + 5)
    path.chmod(0)
    try:
        result = scan.scan(root, SINCE, UNTIL, None, [], projects, home=str(tmp_path))
    finally:
        path.chmod(0o600)
    assert result["findings"] == [] and len(result["problems"]) == 1
    assert "locked.jsonl" in result["problems"][0]["file"]
    assert "q01" not in json.dumps(result)


def test_a_missing_projects_root_is_a_problem_not_a_clean_scan(tmp_path):
    result = scan.scan(_set(tmp_path), SINCE, UNTIL, None, [], tmp_path / "nope", home=str(tmp_path))
    assert result["findings"] == [] and len(result["problems"]) == 1


def test_the_set_files_are_never_opened(tmp_path, monkeypatch):
    root = _set(tmp_path)
    opened = []
    real_open = open

    def watch(file, *a, **k):
        opened.append(str(file))
        return real_open(file, *a, **k)

    monkeypatch.setattr("builtins.open", watch)
    scan.set_ids(root)
    scan.scan(root, SINCE, UNTIL, None, [], tmp_path / "projects", home=str(tmp_path))
    assert not [o for o in opened if o.endswith(".yaml")]
