"""Builder tests for gov.guard.role_paths, the path map's role separation for what a search hands a caller (W2-13 S5;
DEC-1065 (2), DEC-1052 G-14). Regression evidence only (DEC-136): planted trees, tickets and git answers; no git
history is read but what a case plants.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.guard import role_paths  # noqa: E402

SECTION = ("role_paths:\n  engineer:\n    reads_denied: [\"{ticket_tests}\"]\n"
           "  independent-test-designer:\n    reads_denied: [\"{ticket_impl}\"]\n")
ALLOWED = ["src/gov/pier.py", "docs/changes/W2-99-evidence.md", "tests/acceptance/W2-99/**", "tests/unit/pier/**"]


def _tree(at: Path, section: str | None = SECTION) -> Path:
    (at / "governance/project").mkdir(parents=True)
    (at / "governance/project/path-map.yaml").write_text("version: 1\n" + (section or ""), encoding="utf-8")
    (at / ".tickets").mkdir()
    (at / ".tickets/DAEO-pier.md").write_text(
        "---\nid: DAEO-pier\nwbs_id: W2-99\nallowed_paths:\n" + "".join(f"- {p}\n" for p in ALLOWED) + "---\n# x\n",
        encoding="utf-8")
    return at


@pytest.fixture()
def tree(tmp_path, monkeypatch):
    monkeypatch.setattr(role_paths, "WORKTREES", str(tmp_path / "worktrees"))
    monkeypatch.delenv("GOV_ROLE", raising=False)
    monkeypatch.delenv("GOV_TICKET", raising=False)
    return _tree(tmp_path / "main")


def _filter(root, role=None, ticket="DAEO-pier", links=None, main=None):
    return role_paths.caller(root, role, ticket, main=main or str(root), links=links or (lambda *_a: set()))


def test_no_section_no_role_or_no_rule_filled_is_no_filter(tmp_path, tree, monkeypatch):
    bare = _tree(tmp_path / "bare", section=None)
    assert _filter(bare, "engineer") is None  # no role_paths: section
    assert _filter(tree) is None  # no role at all
    assert _filter(tree, "orchestrator") is None  # a role the section does not name
    assert _filter(tree, "engineer", ticket="DAEO-none") is None  # a ticket that fills no rule
    monkeypatch.setenv("GOV_ROLE", "engineer")
    assert _filter(tree, ticket=None) is None  # GOV_TICKET unset


def test_the_engineer_is_withheld_its_own_acceptance_tests_only(tree):
    f = _filter(tree, "engineer")
    assert f.denied("tests/acceptance/W2-99/test_pier.py") == (
        "engineer", "{ticket_tests}", "tests/acceptance/W2-99/**")
    assert f.denied("tests/acceptance/W2-98/test_other.py") is None  # another ticket's tests stay readable
    assert f.denied("src/gov/pier.py") is None and f.denied("tests/unit/pier/test_pier.py") is None


def test_a_case_revised_for_the_ticket_in_another_folder_is_withheld_too(tree):
    f = _filter(tree, "engineer", links=lambda _main, names, wbs: {"tests/acceptance/W2-98/test_moved.py"}
                if wbs == "W2-99" and "DAEO-pier" in names else set())
    assert f.denied("tests/acceptance/W2-98/test_moved.py")[1] == "{ticket_tests}"
    assert f.denied("tests/acceptance/W2-98/test_other.py") is None


def test_the_ticket_is_read_from_the_env_and_a_given_role_adds_but_never_lifts(tree, monkeypatch):
    monkeypatch.setenv("GOV_TICKET", "DAEO-pier")
    assert role_paths.caller(tree, "engineer", main=str(tree), links=lambda *_a: set()).ticket == "DAEO-pier"
    monkeypatch.setenv("GOV_ROLE", "engineer")
    f = role_paths.caller(tree, "orchestrator", main=str(tree), links=lambda *_a: set())  # --role cannot lift it
    assert f is not None and f.roles == ["engineer"] and f.denied("tests/acceptance/W2-99/a.py")
    assert role_paths.roles_of("independent-test-designer") == ["engineer", "independent-test-designer"]


def test_the_designer_is_withheld_the_engineers_new_work_in_its_tree_not_the_integrated_code(tree, tmp_path,
                                                                                              monkeypatch):
    own = tmp_path / "worktrees/W2-99"
    _tree(own)
    changed = {"src/gov/pier.py", "tests/unit/pier/test_pier.py", "tests/unit/pier/conftest.py"}
    monkeypatch.setattr(role_paths, "changed", lambda at: changed if at == str(own) else None)
    f = _filter(own, "independent-test-designer", main=str(tree))
    assert f.denied("src/gov/pier.py") == ("independent-test-designer", "{ticket_impl}", "src/gov/pier.py")
    assert f.denied("tests/unit/pier/test_pier.py")[2] == "tests/unit/pier/**"
    assert f.denied("tests/unit/pier/conftest.py") is None  # a shared test file stays readable (c3)
    assert f.denied("docs/changes/W2-99-evidence.md") is None  # an allowed path the branch has not changed
    assert f.denied("tests/acceptance/W2-99/test_pier.py") is None  # its own tests are the designer's
    # the main tree holds the integrated code: nothing of it is withheld
    assert _filter(tree, "independent-test-designer").denied("src/gov/pier.py") is None


def test_the_designers_tests_tree_withholds_what_the_engineers_commits_carried_in(tree, tmp_path, monkeypatch):
    tests_tree = tmp_path / "worktrees/W2-99-tests"
    _tree(tests_tree)
    monkeypatch.setattr(role_paths, "engineer_side", lambda at, wbs: {"src/gov/pier.py"})
    f = _filter(tests_tree, "independent-test-designer", main=str(tree))
    assert f.denied("src/gov/pier.py")[1] == "{ticket_impl}"
    assert f.denied("tests/unit/pier/test_pier.py") is None


def test_a_plain_glob_applies_in_every_tree(tmp_path, tree):
    plain = _tree(tmp_path / "plain", section="role_paths:\n  engineer:\n    reads_denied: [\"secrets/**\"]\n")
    f = _filter(plain, "engineer", ticket=None)
    assert f.denied("secrets/key.txt") == ("engineer", "secrets/**", "secrets/**")
    assert f.denied("src/key.txt") is None


@pytest.mark.parametrize("section", [
    "role_paths:\n  engineer: [\"{ticket_tests}\"]\n",
    "role_paths:\n  engineer:\n    reads_denied: [\"/abs/path\"]\n",
    "role_paths:\n",
    "role_paths:\n  engineer:\n    reads_denied: [\"{ticket_tests}\"]\nrole_paths:\n  x: {}\n",
    "role_paths:\n  engineer:\n    reads_denied: [\"{ticket_tests\"\n",
])
def test_a_section_that_cannot_be_read_fails_closed(tmp_path, section):
    bad = _tree(tmp_path / "bad", section=section)
    with pytest.raises(role_paths.RolePathsError):
        _filter(bad, "engineer")


def test_a_yaml_error_elsewhere_in_the_map_does_not_stop_the_filter(tmp_path):
    odd = _tree(tmp_path / "odd", section=SECTION + "other: [unclosed\n")
    assert _filter(odd, "engineer").denied("tests/acceptance/W2-99/x.py")


def test_what_is_withheld_is_counted_by_rule_a_chunk_once(tree):
    f = _filter(tree, "engineer")
    lexical = [{"path": "tests/acceptance/W2-99/a.py", "chunk_id": "c1"}, {"path": "src/x.py", "chunk_id": "c2"},
               {"path": "tests/acceptance/W2-99/b.py", "chunk_id": "c3"}]
    semantic = [{"path": "tests/acceptance/W2-99/a.py", "chunk_id": "c1"}]
    assert f.keep(lexical) == [{"path": "src/x.py", "chunk_id": "c2"}] and f.keep(semantic) == []
    assert f.summary() == {
        "roles": ["engineer"], "ticket": "DAEO-pier", "rule": role_paths.RULE,
        "withheld": {"paths": 2, "chunks": 2},
        "by": [{"role": "engineer", "rule": "{ticket_tests}", "glob": "tests/acceptance/W2-99/**", "paths": 2,
                "chunks": 2}]}


def test_the_main_tree_is_the_common_git_folders_and_a_folder_without_git_is_its_own(tmp_path):
    import subprocess
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "sub").mkdir()
    assert role_paths.main_tree(repo / "sub") == str(repo.resolve())
    assert role_paths.main_tree(tmp_path) == str(tmp_path.resolve())
