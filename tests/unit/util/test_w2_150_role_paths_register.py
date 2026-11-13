"""Unit tests for gov.util.role_paths and gov.util.register, moved whole by W2-150 (DEC-136; S5).

Each is the same module object as its old name (``gov.guard.role_paths``, ``gov.decisions.register``), whose own
builder cases stay in tests/unit/guard and tests/unit/decisions. Planted trees only; no git history is read.
"""

from __future__ import annotations

import pytest

from gov.util import register, role_paths

SECTION = "role_paths:\n  engineer:\n    reads_denied: [\"{ticket_tests}\"]\n"


def _tree(at, section=SECTION):
    (at / "governance/project").mkdir(parents=True)
    (at / "governance/project/path-map.yaml").write_text("version: 1\n" + section, encoding="utf-8")
    (at / ".tickets").mkdir()
    (at / ".tickets/DAEO-pier.md").write_text("---\nid: DAEO-pier\nwbs_id: W2-99\n---\n# x\n", encoding="utf-8")
    return at


def test_the_old_names_are_the_same_modules():
    import gov.decisions.register as old_register
    from gov.guard import role_paths as old_role_paths

    assert old_role_paths is role_paths and old_register is register


def test_the_role_filter_withholds_the_engineer_s_own_tests_and_counts_them(tmp_path, monkeypatch):
    monkeypatch.setattr(role_paths, "WORKTREES", str(tmp_path / "worktrees"))
    monkeypatch.delenv("GOV_ROLE", raising=False)
    tree = _tree(tmp_path / "main")
    f = role_paths.caller(tree, "engineer", "DAEO-pier", main=str(tree), links=lambda *_a: set())
    assert f.denied("tests/acceptance/W2-99/test_a.py") == ("engineer", "{ticket_tests}", "tests/acceptance/W2-99/**")
    assert f.denied("tests/acceptance/W2-98/test_a.py") is None
    assert f.keep([{"path": "tests/acceptance/W2-99/a.py", "chunk_id": "c1"}, {"path": "src/a.py", "chunk_id": "c2"}]) \
        == [{"path": "src/a.py", "chunk_id": "c2"}]
    assert f.summary()["withheld"] == {"paths": 1, "chunks": 1}


def test_a_name_set_on_the_old_module_reaches_the_moved_code(tmp_path, monkeypatch):
    from gov.guard import role_paths as old_role_paths

    monkeypatch.setattr(old_role_paths, "WORKTREES", str(tmp_path / "set-on-the-old-name"))
    assert role_paths.WORKTREES == str(tmp_path / "set-on-the-old-name")


def test_a_ticket_the_role_filter_cannot_read_fails_closed(tmp_path, monkeypatch):
    monkeypatch.delenv("GOV_ROLE", raising=False)
    tree = _tree(tmp_path / "main")
    (tree / ".tickets/DAEO-pier.md").write_text("---\nid: DAEO-pier\nwbs_id: 'two words'\n---\n", encoding="utf-8")
    with pytest.raises(role_paths.RolePathsError):
        role_paths.caller(tree, "engineer", "DAEO-pier", main=str(tree), links=lambda *_a: set())


def test_register_ids_and_tags():
    assert register.ids("DEC-1, DEC-22 and DEC-1; xDEC-3 DEC-4a") == ["DEC-1", "DEC-22"]
    assert register._tags("domain: guard · scope: kernel · lands in: `a/`, b · done") == {
        "done": True, "domain": "guard", "scope": "kernel", "lands in": "`a/`, b", "places": ["a/", "b"]}


def test_left_out_record_counts_and_sorts():
    reg = {"superseded": {"DEC-3": ["DEC-9"], "DEC-1": []}, "done": {"DEC-2"}}
    assert register.left_out_record(reg, {"DEC-3", "DEC-2", "DEC-1", "DEC-7"}) == {
        "count": 4, "superseded": ["DEC-1", "DEC-3"], "done": ["DEC-2"]}


def test_leave_out_passes_evidence_without_lines_through(tmp_path):
    evidence = [{"path": "docs/a.md", "chunk_id": "c"}]
    assert register.leave_out(tmp_path, evidence) == (evidence, None)
