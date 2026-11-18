"""``gov decisions basis``: the entries, the rule words, the incident test and the range (W2-198 S4, S5; regression)."""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.decisions import basis  # noqa: E402

REGISTER = "docs/DECISION_REGISTER.md"
HEAD = "# Register\n\n"


def _entry(n, title="A title", body=()):
    return f"### DEC-{n} — {title}\n" + "".join(line + "\n" for line in body) + "\n"


def _one(text):
    (found,) = basis.parse_entries(text)
    return found


def test_entries_are_cut_at_the_next_heading_and_the_dash_forms_are_read():
    text = (HEAD + _entry(1, "em", ["- **Decision:** x"]) + "### DEC-2 – en\n- **Decision:** y\n\n### DEC-3 - hy\n"
            "#### sub heading\nmore\n\n## Section\n\n### DEC-4 — four\n")
    found = basis.parse_entries(text)
    assert [(e["id"], e["title"]) for e in found] == [("DEC-1", "em"), ("DEC-2", "en"), ("DEC-3", "hy"),
                                                      ("DEC-4", "four")]
    assert "more" in "\n".join(found[2]["lines"]) and "Section" not in "\n".join(found[2]["lines"])


RULE_CASES = [
    ("New rule here", [], True), ("Plain", ["- **Decision:** the gate holds"], True),
    ("Plain", ["- **Decision:** checked daily"], True), ("Plain", ["- **Decision:** Standing orders"], True),
    ("Plain", ["- **Decision:** practices change"], True), ("Plain", ["- **Decision:** rules"], True),
    ("Plain", ["- **Decision:** a ruler, a gateway, a checkpoint, outstanding, practical"], False),
    ("Plain", ["- **Decision:** nothing"], False),
    ("Plain", ["- **Decision:** a rule", "- **Adds:** no rule"], False),
    ("Plain", ["- **Basis:** the rule of 2026-01-01", "- **Governing sources:** gate, check"], False),
    ("Plain", ["- **Basis:** a", "  continued rule", "- **Decision:** none"], False),
    ("Plain", ["- **Governing sources:** DEC-1", "  the gate", "- **Decision:** none"], False),
]


def test_a_rule_word_outside_basis_and_governing_sources_makes_a_rule_entry():
    for title, body, rule in RULE_CASES:  # one function: the suite's opt-in cut keeps a parametrised one's first row only
        assert basis.adds_rule(_one(_entry(9, title, body))) is rule, (title, body)


def test_the_basis_line_is_read_with_its_continuation_lines_whitespace_folded():
    entry = _one(_entry(9, "t", ["- **Status:** ACCEPTED", "- **Basis:** the owner wrote:", "  \"stop   now\"", "",
                                 "- **Decision:** x"]))
    assert basis.basis_of(entry) == 'the owner wrote: "stop now"'
    assert basis.basis_of(_one(_entry(9, "t", ["- **Decision:** x"]))) is None


def test_an_inline_basis_after_a_status_field_is_read():
    entry = _one(_entry(9, "t", ["- **Status:** ACCEPTED · **Basis:** package DP-17 option (a) · **Under:** DEC-317"]))
    assert basis.basis_of(entry) == "package DP-17 option (a)"


def _judge(text, existing=()):
    return basis.judge({"id": "DEC-9", "title": "a rule", "lines": ["- **Basis:** " + text]}, lambda p: p in existing)


def test_a_date_and_five_more_words_name_an_incident():
    assert _judge("on 2026-11-16 the guard let a push through unreviewed twice")[0] == "pass"
    assert _judge("2026-11-16 the guard failed")[0] == "fail"  # four words
    assert _judge("the guard let a push through unreviewed twice")[0] == "fail"  # no date
    assert _judge("2026-11-16 16:28 12:30 99 100 7")[0] == "fail"  # numbers are not words


def test_a_path_that_exists_names_an_incident_and_one_that_does_not_does_not():
    existing = {"docs/audit/incident-7.md", "src/x.py"}
    assert _judge("see docs/audit/incident-7.md", existing) == ("pass", "basis names an incident")
    assert _judge("see `docs/audit/incident-7.md`.", existing)[0] == "pass"
    assert _judge("docs/audit/incident-7.md:12", existing)[0] == "pass"
    assert _judge("see src/x.py (the failure)", existing)[0] == "pass"
    assert _judge("see docs/audit/missing.md", existing) == ("fail", "basis names no incident")
    assert _judge("question 1 (role separation)", existing) == ("fail", "basis names no incident")


def test_no_basis_line_is_its_own_reason_and_a_non_rule_passes_without_one():
    rule = {"id": "DEC-9", "title": "the rule", "lines": []}
    assert basis.judge(rule, lambda p: False) == ("fail", "no basis line")
    plain = {"id": "DEC-9", "title": "Plain", "lines": ["- **Decision:** x"]}
    assert basis.judge(plain, lambda p: False)[0] == "pass"


def _git(cwd, *args, env=None):
    subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                   capture_output=True, env={**os.environ, **(env or {})})


def _commit(root, text, when=None):
    (root / "docs").mkdir(exist_ok=True)
    (root / REGISTER).write_text(text)
    _git(root, "add", "-A")
    env = {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when} if when else None
    _git(root, "commit", "-q", "-m", "c", env=env)


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "r"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    return root


def test_the_range_reads_git_objects_at_its_two_ends_never_the_working_tree(repo):
    _commit(repo, HEAD + _entry(1, "old rule"))
    _commit(repo, HEAD + _entry(1, "old rule") + _entry(2, "new rule", ["- **Decision:** x"]))
    (repo / REGISTER).write_text(HEAD + _entry(3, "uncommitted rule"))
    result = basis.check_range(repo, "HEAD^..HEAD", REGISTER)
    assert [(e["id"], e["verdict"], e["reason"]) for e in result["entries"]] == [("DEC-2", "fail", "no basis line")]
    assert result["range"] == "HEAD^..HEAD"


def test_a_head_with_no_parent_reads_every_entry_as_new_by_default_only(repo):
    _commit(repo, HEAD + _entry(1, "first rule"))
    assert [e["id"] for e in basis.check_range(repo, None, REGISTER)["entries"]] == ["DEC-1"]
    with pytest.raises(basis.BasisError):
        basis.check_range(repo, "HEAD^..HEAD", REGISTER)


def test_a_basis_path_is_looked_up_in_the_tree_at_the_ranges_end(repo):
    _commit(repo, HEAD)
    (repo / "docs" / "incident.md").write_text("x")
    _commit(repo, HEAD + _entry(1, "a rule", ["- **Basis:** docs/incident.md"]))
    assert basis.check_range(repo, "HEAD^..HEAD", REGISTER)["entries"][0]["verdict"] == "pass"
    (repo / "docs" / "incident.md").unlink()  # the working tree is not read either
    assert basis.check_range(repo, "HEAD^..HEAD", REGISTER)["entries"][0]["verdict"] == "pass"


def test_week_lists_the_entries_gained_since_the_date_with_the_commit_date_that_added_them(repo):
    _commit(repo, HEAD + _entry(1, "ten days"), "2026-11-08T12:00:00+00:00")
    _commit(repo, HEAD + _entry(1, "ten days") + _entry(2, "two days", ["- **Basis:** a", "  b"]),
            "2026-11-16T12:00:00+00:00")
    now = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)
    week = basis.week(repo, None, REGISTER, now)
    assert [e["id"] for e in week["entries"]] == ["DEC-2"]
    assert week["entries"][0]["added"] == "2026-11-16" and week["entries"][0]["basis"] == "a b"
    everything = basis.week(repo, "2026-11-01", REGISTER, now)
    assert [e["id"] for e in everything["entries"]] == ["DEC-1", "DEC-2"]
    assert everything["entries"][0]["added"] == "2026-11-08"
