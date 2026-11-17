"""G-1 (who wrote the acceptance tests) and the path notice, on planted branches (W2-115b success 5 and 6)."""
from __future__ import annotations

from gov.queue import checks

from queue_support import TICKET, WBS

SUITE = f"tests/acceptance/{WBS}/"
PLACES = ["tests/acceptance/", SUITE]


def _authors(project, branch):
    return checks.test_authors(project.root, project.sha("main"), project.sha(branch), PLACES)


def test_an_engineer_commit_to_the_acceptance_tests_is_named(project):
    tip = project.branch("a", {f"{SUITE}test_x.py": "def test_x():\n    pass\n"}, f"Task: {TICKET}",
                         "Role: engineer")
    assert [b["commit"] for b in _authors(project, "a")] == [tip]


def test_a_commit_without_a_role_is_named(project):
    tip = project.branch("a", {f"{SUITE}test_x.py": "def test_x():\n    pass\n"}, f"Task: {TICKET}")
    assert [b["commit"] for b in _authors(project, "a")] == [tip]


def test_mixed_roles_are_named(project):
    tip = project.branch("a", {f"{SUITE}test_x.py": "def test_x():\n    pass\n"}, "Role: owner", "Role: engineer")
    assert [b["commit"] for b in _authors(project, "a")] == [tip]


def test_the_test_designer_s_and_the_owner_s_commits_pass(project):
    project.branch("a", {f"{SUITE}test_x.py": "def test_x():\n    pass\n"}, "Role: independent-test-designer")
    project.branch("b", {f"{SUITE}test_y.py": "def test_y():\n    pass\n"}, "Role: owner")
    assert _authors(project, "a") == [] and _authors(project, "b") == []


def test_an_engineer_commit_elsewhere_is_not_named(project):
    project.branch("a", {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}, "Role: engineer")
    assert _authors(project, "a") == []


def test_a_commit_to_the_ticket_s_own_acceptance_path_is_named(project):
    tip = project.branch("a", {"tests/checks/W-1/test_c.py": "def test_c():\n    pass\n"}, "Role: engineer")
    found = checks.test_authors(project.root, project.sha("main"), tip, ["tests/acceptance/", "tests/checks/W-1/"])
    assert [b["commit"] for b in found] == [tip]


def _designer_and_work(project):
    project.branch("tests", {f"{SUITE}test_new.py": "def test_new():\n    assert 1\n"},
                   "Role: independent-test-designer")
    project.branch("work", {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}, "Role: engineer")
    project.git("checkout", "-q", "work")


def test_a_clean_merge_of_the_test_designer_s_branch_passes(project):
    _designer_and_work(project)
    project.git("merge", "--no-ff", "-q", "-m", "merge tests\n\nRole: engineer", "tests")
    project.git("checkout", "-q", "main")
    assert _authors(project, "work") == []


def test_a_merge_whose_resolution_edits_an_acceptance_test_is_named(project):
    _designer_and_work(project)
    project.git("merge", "--no-ff", "--no-commit", "-q", "tests")
    (project.root / SUITE / "test_new.py").write_text("def test_new():\n    assert 0 == 0\n")
    project.git("add", "-A")
    project.git("commit", "-q", "--no-gpg-sign", "-m", "merge tests", "--trailer", "Role: engineer")
    merge = project.sha()
    project.git("checkout", "-q", "main")
    assert [b["commit"] for b in _authors(project, "work")] == [merge]


def test_a_path_outside_the_allowed_paths_is_a_notice_and_one_inside_is_not(project):
    inside = project.branch("a", {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}, "Role: engineer")
    project.git("checkout", "-q", "a")
    outside = project.commit("notes", "Role: engineer", files={"governance/project/notes.yaml": "a: 1\n",
                                                                f".tickets/{TICKET}.md": "---\nid: x\n---\n"})
    project.git("checkout", "-q", "main")
    found = checks.path_notices(project.root, project.sha("main"), outside,
                                ["src/pkg/feature.py", f"{SUITE}**"], checks.record_places(TICKET, SUITE))
    assert found == [{"commit": outside, "path": "governance/project/notes.yaml"}]
    assert inside not in [f["commit"] for f in found]
