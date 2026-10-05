"""W1-14 -- KPI success 2: "Derived tickets pass the ticket schema and the DAG is acyclic."

- The schema is ``template/governance/kernel/schemas/ticket.schema.json`` (W1-08), read at test time.
- The DAG is the one the READY rule walks: the ``deps`` key of every ticket of ``.tickets/``, holding ticket ids
  (W1-09; its residual "only ``deps`` is read"). A task names what it depends on in ``depends_on``: task numbers
  of the same ``tasks.md``, or ids of tickets that already exist (package DP-4).
- A derived ticket is one ``gov.tasks.ready`` and ``gov.tasks.blocked`` can use.
"""

from __future__ import annotations

import pytest

import w1_14_support as support

X, Y = "pro-x001", "pro-y002"


def chain():
    """2.1 needs 1.2, 1.2 needs 1.1; 1.3 needs both 1.1 and 2.1 and is written before 2.1."""
    return [support.task("1.1"),
            support.task("1.2", depends_on=["1.1"]),
            support.task("1.3", depends_on=["1.1", "2.1"]),
            support.task("2.1", depends_on=["1.2"])]


# ---- the schema

def test_derived_tickets_pass_the_ticket_schema(project):
    project.change(chain() + [support.task("3.1", role=support.TEST_DESIGNER, **{"class": "test-design"},
                                           profile="FULL", allowed_paths=["tests/acceptance/part_3/**"])])
    derived = project.derived()
    for number, ticket in derived.items():
        front = project.ticket_front(ticket)
        assert front.get("id") == ticket, f"task {number}: the file {ticket}.md holds the id {front.get('id')!r}"
        faults = support.schema_faults(front)
        assert not faults, f"task {number}: the ticket {ticket} does not pass ticket.schema.json: {faults}"


def test_a_derived_ticket_is_an_open_ticket(project):
    project.change([support.task("1.1")])
    assert project.ticket_front(project.derived()["1.1"]).get("status") == "open"


# ---- the DAG

def test_task_dependencies_become_ticket_dependencies(project):
    project.change(chain())
    derived = project.derived()
    edges = support.graph(project)
    assert edges[derived["1.1"]] == []
    assert edges[derived["1.2"]] == [derived["1.1"]]
    assert sorted(edges[derived["1.3"]]) == sorted([derived["1.1"], derived["2.1"]]), \
        "a task may depend on a task written after it"
    assert edges[derived["2.1"]] == [derived["1.2"]]
    assert support.dag_faults(edges) == []


def test_a_task_may_depend_on_a_ticket_that_already_exists(project):
    project.existing_ticket(X)
    project.change([support.task("1.1", depends_on=[X]), support.task("1.2", depends_on=["1.1", X])])
    derived = project.derived()
    edges = support.graph(project)
    assert edges[derived["1.1"]] == [X]
    assert sorted(edges[derived["1.2"]]) == sorted([derived["1.1"], X])
    assert support.dag_faults(edges) == []


@pytest.mark.parametrize("tasks, named", [
    pytest.param([("1.1", ["1.2"]), ("1.2", ["1.1"])], ["1.1", "1.2"], id="two-tasks"),
    pytest.param([("1.1", ["1.1"])], ["1.1"], id="a-task-on-itself"),
    pytest.param([("1.1", ["2.1"]), ("1.2", ["1.1"]), ("2.1", ["1.2"]), ("2.2", [])], ["1.1", "1.2", "2.1"],
                 id="three-tasks-and-one-outside-the-cycle"),
])
def test_a_cycle_between_tasks_is_refused_and_no_ticket_is_written(project, tasks, named):
    project.change([support.task(number, depends_on=deps) for number, deps in tasks])
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert set(named) <= set(support.invalid_tasks(outcome)), "the refusal names the tasks of the cycle"


def test_a_cycle_through_tickets_that_already_exist_is_refused(project):
    """The tickets of the project are one DAG (CAP-31.a): a task may not hang a ticket on a cycle that is there."""
    project.existing_ticket(X, deps=[Y])
    project.existing_ticket(Y, deps=[X])
    project.change([support.task("1.1"), support.task("1.2", depends_on=[X])])
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert "1.2" in support.invalid_tasks(outcome)


@pytest.mark.parametrize("dependency", ["9.9", "pro-zzzz"], ids=["no-such-task", "no-such-ticket"])
def test_a_dependency_that_names_nothing_is_refused(project, dependency):
    """A ticket whose dependency does not exist is never READY (W1-09), and the graph has a dangling edge."""
    project.change([support.task("1.1"), support.task("1.2", depends_on=[dependency])])
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert "1.2" in support.invalid_tasks(outcome)


def test_a_task_number_written_as_a_yaml_number_is_refused(project):
    """``depends_on: [1.10]`` without quotes is the number 1.1 to YAML: it would silently name another task."""
    text = support.tasks_md([support.task("1.1"), support.task("1.10"), support.task("2.1", depends_on=["1.10"])])
    assert "- '1.10'" in text, "the fixture no longer writes the dependency as a quoted string"
    project.change(text.replace("- '1.10'", "- 1.10"))
    before = project.tree()
    outcome = project.derive()
    support.refused_and_nothing_written(project, before, outcome, support.TASKS_INVALID)
    assert "2.1" in support.invalid_tasks(outcome)


# ---- usable by the READY rule (W1-09)

def test_derived_tickets_move_through_the_ready_rule(project):
    project.change([support.task("1.1"), support.task("1.2", depends_on=["1.1"])])
    derived = project.derived()
    first, second = derived["1.1"], derived["1.2"]

    ready, blocked = project.queue()
    assert ready == [], "an implementation ticket is not READY before its acceptance tests exist (MR-3)"
    assert blocked.get(first) == [support.NO_ACCEPTANCE_TESTS], \
        f"the specification is closed and nothing else holds task 1.1: {blocked.get(first)!r}"
    assert support.DEPENDENCY_OPEN in blocked.get(second, []), f"task 1.2 waits for task 1.1: {blocked!r}"
    assert support.SPEC_NOT_CLOSED not in blocked[first] + blocked[second]

    project.tests_folder(first)
    project.tests_folder(second)
    ready, blocked = project.queue()
    assert ready == [first] and blocked.get(second) == [support.DEPENDENCY_OPEN]

    project.set_ticket_status(first, "closed")
    ready, blocked = project.queue()
    assert ready == [second] and blocked == {}


def test_derived_tickets_are_held_when_their_specification_is_reopened(project):
    """The back-reference is the one the READY rule follows (DEC-307)."""
    project.change([support.task("1.1")])
    ticket = project.derived()["1.1"]
    project.tests_folder(ticket)
    assert project.queue()[0] == [ticket]
    project.set_specification_status(support.STATUS_OPEN)
    ready, blocked = project.queue()
    assert ready == [] and blocked.get(ticket) == [support.SPEC_NOT_CLOSED]
