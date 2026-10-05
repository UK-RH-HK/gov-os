"""W1-14 -- a second run on the same change (KPI success 2, "the DAG": one ticket per task, never two).

Package DP-5: a task that already has its ticket keeps it, untouched; a task added since gets a new one.
"""

from __future__ import annotations

import w1_14_support as support


def tasks():
    return [support.task("1.1"), support.task("1.2", depends_on=["1.1"])]


def test_a_second_run_creates_no_duplicate_ticket(project):
    project.change(tasks())
    first = project.derived()
    files = project.ticket_files()
    second = project.derived()
    assert second == first, "the second run names other tickets than the first"
    assert project.ticket_files() == files, "the second run added or rewrote a ticket"


def test_a_second_run_does_not_reopen_work_and_derives_only_the_new_task(project):
    project.change(tasks())
    first = project.derived()
    project.set_ticket_status(first["1.1"], "closed")
    files = project.ticket_files()

    project.tasks(tasks() + [support.task("1.3", depends_on=["1.1"])])
    second = project.derived()
    assert {number: second[number] for number in first} == first
    assert len(project.tickets()) == 3, "exactly one ticket is new"
    assert {ticket: text for ticket, text in project.ticket_files().items() if ticket in files} == files, \
        "a ticket that existed was rewritten: the closed one may have been reopened"
    new = project.ticket_front(second["1.3"])
    assert new.get("deps") == [first["1.1"]] and new.get(support.BACK_REFERENCE) == support.SPEC
    assert support.dag_faults(support.graph(project)) == []


def test_a_refused_second_run_leaves_the_first_runs_tickets_alone(project):
    project.change(tasks())
    project.derived()
    project.tasks(tasks() + [support.task("1.3", kpis=None)])
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert support.invalid_tasks(outcome) == ["1.3"]
