"""W1-14 -- KPI failure 1: "A derived ticket lacks KPIs or allowed_paths." And MR-2: closed specifications generate
the work.

No derivation may leave such a ticket. A task that does not carry what a ticket needs is refused, and so is the
whole derivation: no ticket of the change is written (package DP-2). The tasks.md template of W1-12 gives a task a
number and a description only, so a task written from the template alone is refused.

A change whose specification is not closed gives no tickets (MR-2; DEC-307: closed is the record's status
``CLOSED``; package DP-3 for a record closed by hand with a required row open).
"""

from __future__ import annotations

import pytest

import w1_14_support as support

LACKING = [
    pytest.param({"kpis": None}, id="no-kpis"),
    pytest.param({"kpis": {}}, id="kpis-empty"),
    pytest.param({"kpis": {"success": [], "failure": ["It breaks"]}}, id="no-success-line"),
    pytest.param({"kpis": {"failure": ["It breaks"]}}, id="no-success-key"),
    pytest.param({"kpis": {"success": [""], "failure": []}}, id="success-line-empty"),
    pytest.param({"kpis": "It works"}, id="kpis-not-a-map"),
    pytest.param({"allowed_paths": None}, id="no-allowed-paths"),
    pytest.param({"allowed_paths": []}, id="allowed-paths-empty"),
    pytest.param({"allowed_paths": [""]}, id="allowed-path-empty"),
    pytest.param({"allowed_paths": "src/feature/**"}, id="allowed-paths-not-a-list"),
    pytest.param({"role": None}, id="no-role"),
]


# ---- a task that lacks what a ticket needs

@pytest.mark.parametrize("changes", LACKING)
def test_a_task_that_lacks_kpis_allowed_paths_or_role_gives_no_ticket(project, changes):
    project.change([support.task("1.1", **changes)])
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert support.invalid_tasks(outcome) == ["1.1"]


def test_one_lacking_task_refuses_the_whole_derivation(project):
    """Package DP-2: no partial set of tickets, whose dependencies would point at tickets that were never made."""
    project.change([support.task("1.1"), support.task("1.2", kpis=None, depends_on=["1.1"]),
                    support.task("2.1", allowed_paths=None), support.task("2.2", depends_on=["1.2"])])
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert support.invalid_tasks(outcome) == ["1.2", "2.1"], "every lacking task is named, and no other"


def test_a_task_with_no_block_gives_no_ticket(project):
    task = support.task("1.2")
    task["fields"] = {}
    project.change([support.task("1.1"), task])
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert support.invalid_tasks(outcome) == ["1.2"]


def test_the_tasks_template_as_delivered_gives_no_ticket(project):
    """W1-12's ``tasks.md`` template carries a number and a description per task, and nothing a ticket needs."""
    project.specification()
    project.tasks((support.TEMPLATES / "tasks.md").read_text(encoding="utf-8"))
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert support.invalid_tasks(outcome) == ["1.1", "1.2", "2.1", "2.2"]


@pytest.mark.parametrize("key", ["profile", "class"])
def test_no_ticket_is_derived_without_a_profile_or_a_class(project, key):
    """MR-2 names class and profile among what a generated ticket has. Whether a task without one is refused or
    takes a stated default is package DP-2; either way no ticket is left without it."""
    project.change([support.task("1.1", **{key: None})], profile="LITE")
    before = project.tree()
    outcome = project.derive()
    if not outcome.ok:
        support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
        return
    front = project.ticket_front(support.tickets_of(outcome, project)["1.1"])
    assert isinstance(front.get(key), str) and front[key].strip(), f"the derived ticket has no '{key}'"
    assert not support.schema_faults(front)


# ---- a specification that is not closed (MR-2)

@pytest.mark.parametrize("rows", [support.open_rows, support.complete_rows], ids=["a-row-open", "rows-complete"])
def test_a_specification_that_is_not_closed_gives_no_ticket(project, rows):
    """DEC-307: closed is the status ``CLOSED``. Rows that would pass do not close a specification (DEC-349)."""
    project.change([support.task("1.1")], status=support.STATUS_OPEN, rows=rows())
    before = project.tree()
    support.refused_and_nothing_written(project, before, project.derive(), support.SPEC_NOT_CLOSED)


def test_a_specification_closed_by_hand_with_a_required_row_open_gives_no_ticket(project):
    """Package DP-3: the status alone is not trusted (DEC-348: the verdict comes from the rows)."""
    project.change([support.task("1.1")], status=support.STATUS_CLOSED, rows=support.open_rows())
    before = project.tree()
    support.refused_and_nothing_written(project, before, project.derive(), support.SPEC_NOT_CLOSED)


def test_closing_the_specification_lets_its_tickets_be_derived(project):
    project.change([support.task("1.1")], status=support.STATUS_OPEN)
    support.refused(project.derive(), support.SPEC_NOT_CLOSED)
    project.set_specification_status(support.STATUS_CLOSED)
    assert list(project.derived()) == ["1.1"]


# ---- a change that cannot be read

def test_a_change_that_does_not_exist_is_refused(project):
    project.change([support.task("1.1")])
    before = project.tree()
    support.refused_and_nothing_written(project, before, project.derive("zq99-no-such-change"))


def test_a_change_without_tasks_is_refused(project):
    project.specification()
    before = project.tree()
    support.refused_and_nothing_written(project, before, project.derive())


def test_a_change_without_a_specification_record_is_refused(project):
    """A ``proposal.md`` written from today's template has no frontmatter (DEC-350): it is no closed specification."""
    project.change([support.task("1.1")])
    support.write(project.root, f"{support.CHANGES_REL}/{support.CHANGE}/proposal.md",
                  (support.TEMPLATES / "proposal.md").read_text(encoding="utf-8"))
    before = project.tree()
    support.refused_and_nothing_written(project, before, project.derive())
