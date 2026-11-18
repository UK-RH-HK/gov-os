"""``select.scoped``'s ``change``: paths unioned into the change it counts (W2-115b success 1), the selection
unchanged without it."""
from __future__ import annotations

from gov.close import select

from queue_support import TICKET, WBS


def _work(project):
    project.commit("feature", f"Task: {TICKET}", "Role: engineer",
                   files={"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"})
    project.commit("slip without a task", "Role: engineer", files={"src/pkg/other.py": "def other():\n    return 1  # x\n"})


def test_without_change_only_the_ticket_s_own_commits_count(project):
    _work(project)
    chosen = select.scoped(project.root, TICKET)
    assert chosen["suites"] == [f"tests/acceptance/{WBS}/"]
    assert "src/pkg/other.py" not in chosen["changed"]


def test_the_change_given_is_counted_and_reaches_its_importer(project):
    _work(project)
    chosen = select.scoped(project.root, TICKET, change=["src/pkg/other.py"])
    assert "src/pkg/other.py" in chosen["changed"]
    assert "tests/unit/test_other.py" in chosen["suites"]
    assert "tests/unit/test_lonely.py" not in chosen["suites"]
