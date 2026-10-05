"""W1-14 -- KPI failure 2: "An implementer ticket allowed_paths covers tests/acceptance/**."

MR-3: the builder never writes its own acceptance tests; the guard refuses ``tests/acceptance/**`` "to every role
but the Independent Test Designer" (Contract v4, MR-3, DEC-156). So a task of any other role whose
``allowed_paths`` could match a path at or under ``tests/acceptance/`` gives no ticket, and neither does the rest
of its change. A pattern is read as the guard reads it: ``*`` stays inside one path segment, ``**`` crosses them,
and a folder covers what is under it. The Independent Test Designer's own tasks name that folder, and are derived.
"""

from __future__ import annotations

import pytest

import w1_14_support as support

COVERING = [
    "tests/acceptance/**",            # the KPI's own spelling
    "tests/**",                       # a parent, by glob
    "**",                             # everything
    "tests/",                         # a parent directory
    "tests",                          # the same, without the slash
    "tests/acceptance",               # the exact folder
    "tests/acceptance/",              # the exact folder, with the slash
    "tests/acceptance/W9-01/**",      # a folder inside it
    "tests/acceptance/W9-01/test_export.py",   # a file inside it
    "tests/*/**",                     # a wildcard in place of the folder's name
    "./tests/acceptance/**",          # the same path, spelled with a leading ./
]
NOT_COVERING = ["tests/unit/**", "tests/acceptance-data/**", "src/tests/acceptance/**", "docs/tests/acceptance.md"]


@pytest.mark.parametrize("path", COVERING)
def test_an_engineer_task_whose_paths_cover_the_acceptance_tests_gives_no_ticket(project, path):
    project.change([support.task("1.1", allowed_paths=["src/feature/**", path])])
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert support.invalid_tasks(outcome) == ["1.1"]


@pytest.mark.parametrize("role", ["product-spec", "orchestrator", "independent-auditor"])
def test_no_role_but_the_test_designer_gets_the_acceptance_tests(project, role):
    """MR-3 as the Contract states it: every role but the Independent Test Designer."""
    project.change([support.task("1.1", role=role, allowed_paths=["tests/acceptance/W9-01/**"])])
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert support.invalid_tasks(outcome) == ["1.1"]


def test_the_test_designers_task_may_name_the_acceptance_tests(project):
    paths = ["tests/acceptance/W9-01/**"]
    project.change([support.task("1.1", role=support.TEST_DESIGNER, **{"class": "test-design"},
                                 allowed_paths=paths),
                    support.task("1.2", depends_on=["1.1"])])
    derived = project.derived()
    front = project.ticket_front(derived["1.1"])
    assert front.get("role") == support.TEST_DESIGNER and front.get("allowed_paths") == paths


def test_one_covering_engineer_task_refuses_the_whole_derivation(project):
    project.change([support.task("1.1", role=support.TEST_DESIGNER, **{"class": "test-design"},
                                 allowed_paths=["tests/acceptance/W9-01/**"]),
                    support.task("1.2"),
                    support.task("1.3", allowed_paths=["tests/**"])])
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert support.invalid_tasks(outcome) == ["1.3"]


def test_paths_that_only_look_like_the_acceptance_tests_are_derived(project):
    """The refusal is about ``tests/acceptance/``, not about every path with those words in it."""
    project.change([support.task("1.1", allowed_paths=list(NOT_COVERING))])
    ticket = project.derived()["1.1"]
    assert project.ticket_front(ticket).get("allowed_paths") == NOT_COVERING
