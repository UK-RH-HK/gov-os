"""W1-14 -- KPI success 1: "Tickets derived from an OpenSpec change tasks.md carry kpis, role, allowed_paths,
profile and a back-reference to the change [CAP-31.a]."

CAP-31.a: "One task DAG; task contract with class, role, inputs, allowed paths, KPIs, profile". The back-reference
is the ticket key ``specification``, holding the id of the change's specification record (DEC-307, DEC-350).
"""

from __future__ import annotations

import w1_14_support as support

DESIGN = support.task(
    "1.1", "Write the acceptance tests of the export and verify they fail before the export exists",
    role=support.TEST_DESIGNER, **{"class": "test-design"}, profile="FULL",
    allowed_paths=["tests/acceptance/export/**"],
    kpis={"success": ["Every KPI line of the export has a test", "The suite is red before implementation"],
          "failure": ["A test reads the implementation"]})
BUILD = support.task(
    "1.2", "Implement the export function and verify the export test passes",
    profile="LITE", allowed_paths=["src/export/**"],
    kpis={"success": ["The export of the sample data equals the expected file"], "failure": []})
CONTRACT = ("kpis", "role", "allowed_paths", "profile", "class")


def test_every_task_of_the_change_becomes_one_ticket(project):
    project.change([DESIGN, BUILD, support.task("2.1")])
    outcome = project.derive()
    derived = support.tickets_of(outcome, project)
    assert list(derived) == ["1.1", "1.2", "2.1"], "one ticket per task, in the order of tasks.md"
    assert sorted(derived.values()) == project.tickets(), "the project holds the derived tickets and no other"
    assert outcome.value.get(support.KEY_CHANGE) == support.CHANGE
    assert outcome.value.get(support.KEY_SPECIFICATION) == support.SPEC


def test_a_derived_ticket_carries_the_task_contract_of_its_task(project):
    """[CAP-31.a] kpis, role, allowed_paths, profile and class are the task's own, never a default of the bridge."""
    project.change([DESIGN, BUILD])
    derived = project.derived()
    for item in (DESIGN, BUILD):
        front = project.ticket_front(derived[item["number"]])
        for key in CONTRACT:
            assert front.get(key) == item["fields"][key], \
                f"task {item['number']}: the ticket's '{key}' is {front.get(key)!r}, the task says " \
                f"{item['fields'][key]!r}"


def test_a_derived_ticket_names_the_specification_of_its_change(project):
    """The back-reference: the key the READY rule reads (DEC-307) holds the record id of the change (DEC-350)."""
    project.change([DESIGN, BUILD])
    for ticket in project.derived().values():
        assert project.ticket_front(ticket).get(support.BACK_REFERENCE) == support.SPEC


def test_a_derived_ticket_says_what_its_task_says(project):
    """The task's description is the ticket's title: a reader of the ticket sees which task it is."""
    project.change([DESIGN, BUILD])
    derived = project.derived()
    for item in (DESIGN, BUILD):
        text = project.ticket_path(derived[item["number"]]).read_text(encoding="utf-8")
        assert item["text"] in text, f"the ticket of task {item['number']} does not hold the task's description"


def test_a_task_that_names_inputs_gives_a_ticket_with_those_inputs(project):
    """CAP-31.a lists inputs in the task contract; the READY rule reads them from ``inputs`` (CAP-31.d, W1-09)."""
    project.change([support.task("1.1", inputs=["DEC-101", "RES-0007"])])
    ticket = project.derived()["1.1"]
    assert project.ticket_front(ticket).get("inputs") == ["DEC-101", "RES-0007"]


def test_derivation_writes_tickets_and_nothing_else_and_commits_nothing(project):
    """As ``gov.readiness.close`` does (DEC-349): files in the working tree, no commit."""
    project.change([DESIGN, BUILD])
    project.commit()
    head, before = project.head(), project.tree()
    project.derived()
    after = project.tree()
    changed = sorted(rel for rel in set(before) | set(after) if before.get(rel) != after.get(rel))
    assert changed and all(rel.startswith(support.TICKETS_REL + "/") for rel in changed), \
        f"the bridge changed files outside {support.TICKETS_REL}/: {changed}"
    assert project.head() == head, "the bridge committed"


def test_two_changes_with_the_same_task_numbers_get_their_own_tickets(project):
    project.change([support.task("1.1"), support.task("1.2")])
    project.change([support.task("1.1")], spec_id=support.OTHER_SPEC, change=support.OTHER_CHANGE)
    first = project.derived()
    second = project.derived(support.OTHER_CHANGE)
    assert not set(first.values()) & set(second.values()), "a ticket of one change was reused for the other"
    assert len(project.tickets()) == 3
    assert project.ticket_front(first["1.1"])[support.BACK_REFERENCE] == support.SPEC
    assert project.ticket_front(second["1.1"])[support.BACK_REFERENCE] == support.OTHER_SPEC
