"""KPI success 1 and failure 1: Stage A0 names the CTO, so the orchestrator on the new ticket is asked at once.

Interface I1: A0 creates the coordination ticket (title ``<project> coordination``, ``class: coordination``), writes
``governance/project/roster.yaml`` with the top-level ``coordination_ticket: <new id>``, records both in A0's record and
commits them in A0's commit with its set-up files. Interface I3: the planted repository is generated from the template,
then ``gov adopt --lite --stage A0`` runs, and nobody edits a roster or a ticket after it.
"""

from __future__ import annotations

import pytest

import w2_113_support as support
from w2_113_support import w110

w23 = support.w23


def test_a0_succeeds_on_a_planted_repository(adoption):
    """The precondition of every case here: A0 runs on the planted repository and ends well, as it does today."""
    support.assert_succeeded(adoption("standard"))


# --- success 1, first half: the roster's key names the ticket A0 created ------------------------------------------------

def test_a0_creates_exactly_one_ticket_and_the_roster_names_it(adoption):
    adopted = adoption("standard")
    support.assert_succeeded(adopted)
    assert adopted.before.roster is None, f"the planted repository already held {support.ROSTER_REL}"
    ticket = adopted.new_ticket()              # exactly one new file in .tickets/
    data = support.roster_data(adopted.project)
    assert isinstance(data, dict), f"A0 wrote no {support.ROSTER_REL} that parses as a mapping (found {data!r})"
    assert data.get(support.KEY) == ticket, (
        f"the top-level key {support.KEY} of {support.ROSTER_REL} must be the id of the ticket A0 created "
        f"({ticket!r}); it is {data.get(support.KEY)!r}")


def test_the_new_ticket_is_the_coordination_ticket_of_the_project(adoption):
    """``class: coordination``, titled ``<project> coordination`` where the project is the repository's folder name."""
    adopted = adoption("standard")
    support.assert_succeeded(adopted)
    ticket = adopted.new_ticket()
    front, title = support.read_ticket(adopted.project, ticket)
    assert front.get("id") == ticket, f"the ticket file {ticket}.md names itself {front.get('id')!r}"
    assert front.get("class") == "coordination", (
        f"the ticket's frontmatter must carry `class: coordination`; it has class={front.get('class')!r}")
    assert title == support.TITLE, (
        f"the ticket's title must be '<project> coordination' = {support.TITLE!r} (the project is {support.PROJECT!r}, "
        f"the folder of the repository); it is {title!r}")


def test_a0_s_record_names_the_ticket_and_the_roster(adoption):
    adopted = adoption("standard")
    support.assert_succeeded(adopted)
    ticket = adopted.new_ticket()
    record = (adopted.project / support.A0_RECORD)
    assert record.is_file(), f"A0 left no record at {support.A0_RECORD}"
    text = record.read_text(encoding="utf-8")
    assert ticket in text, f"A0's record {support.A0_RECORD} does not name the coordination ticket {ticket}"
    assert support.ROSTER_REL in text, f"A0's record {support.A0_RECORD} does not name the roster {support.ROSTER_REL}"


def test_the_ticket_and_the_roster_are_in_a0_s_commit_and_the_tree_is_clean(adoption):
    """The commit A0 made (HEAD): one commit on the planted head, holding the ticket, the roster and the record."""
    adopted = adoption("standard")
    support.assert_succeeded(adopted)
    ticket = adopted.new_ticket()
    project = adopted.project
    assert support.commit_count(project) == adopted.before.commits + 1, (
        f"A0 makes one commit; the repository went from {adopted.before.commits} to {support.commit_count(project)}")
    assert w23.git(project, "rev-parse", "HEAD~1").strip() == adopted.before.head, "A0's commit does not stand on the planted head"
    files = adopted.a0_commit_files()
    for rel in (f"{support.TICKETS_REL}/{ticket}.md", support.ROSTER_REL, support.A0_RECORD):
        assert rel in files, f"{rel} is not in A0's commit (which holds {files})"
    assert w23.porcelain(project) == "", f"A0 left the tree dirty:\n{w23.porcelain(project)}"
    for rel in (f"{support.TICKETS_REL}/{ticket}.md", support.ROSTER_REL):
        assert w23.at_head(project, rel) == (project / rel).read_bytes(), f"{rel} is not committed as it stands"


# --- failure 1 and success 1, second half: the orchestrator on that ticket is asked, with no edit ----------------------

@pytest.mark.parametrize("command", support.INSTALLS)
def test_the_orchestrator_on_the_new_ticket_is_asked_for_an_install(adoption, decide, command):
    """Failure 1: the CTO's install refused until the key is written by hand. Here no hand edit is made."""
    adopted = adoption("standard")
    support.assert_succeeded(adopted)
    ticket = adopted.new_ticket()
    answer = decide(w110.cto(ticket), command)
    assert answer.settings_rule is None, f"a generated settings rule refuses the call before the hook: {answer.describe()}"
    assert answer.decision == "ask", (
        f"in a freshly adopted repository the orchestrator on the coordination ticket {ticket} must be asked for "
        f"`{command}`, with no key edited by hand; the decision was {answer.decision}: {answer.describe()}")
