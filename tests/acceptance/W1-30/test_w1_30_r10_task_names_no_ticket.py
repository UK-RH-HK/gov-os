"""A ``Task:`` that names no ticket of the project names no task (DEC-500, second behaviour; finding 1).

"Such a commit is judged as a commit without a task is (DEC-490): where it changes the ticket's work it refuses
the close, and where it changes a governance file the checks run. Ordinary shape: a mistyped id, and this
project's own commits whose ``Task:`` names a kind of record and not a ticket."

The cases are those of ``test_w1_30_r8_commits.py`` ("Commits that name no task") with one difference: the
commit carries a ``Task:`` trailer, and what it names is no ticket file of the project. Two such names:

- a mistyped id (``PROJ-cmtz`` for ``PROJ-cmts``), on a commit with the engineer's other trailers;
- the id of a record that exists and is no ticket (``DEC-000``, the decision every fixture ticket names as
  its source).

Each commit changes one kind of path and nothing else:

- the ticket's acceptance test (weakened so that it passes), a new file inside the ticket's allowed paths, the
  ticket's own file (its FULL profile lowered, no probe record): refused, a finding (exit code 3) that names
  the commit and says "task", as for the commit without a task;
- a file in a folder of notes, nobody's work here: refuses nothing, the ticket closes.

A commit that names another existing ticket is that ticket's, as before:
``test_a_commit_that_names_another_ticket_refuses_nothing`` holds it and is unchanged.
"""

import re

import pytest

import w1_30_support as support

TICKET = "PROJ-cmts"
WBS = "W1-cmts"
MISTYPED = "PROJ-cmtz"
A_RECORD = support.BASE_SOURCE
INSIDE = "src/example/more.py"
NOTES = "notes/meeting.txt"
ACCEPTANCE_TEST = f"tests/acceptance/{WBS}/test_fail.py"
PASSING = "def test_fail():\n    assert True\n"


def _commit_naming(project, named, files):
    """One commit that writes ``files`` with the engineer's trailers and ``Task: <named>``, where ``named`` is
    no ticket of the project; returns its id."""
    assert not (project.root / support.ticket_path(named)).exists(), f"the fixture is wrong: {named} is a ticket"
    for rel, text in files.items():
        project.write(rel, text)
    commit = project.commit("work under a task that is none", who=support.IMPLEMENTER,
                            trailers=support.trailers_of(named), exact=True)
    assert commit not in support.ticket_commits(project.root, TICKET)
    assert commit in support.ticket_commits(project.root, named), "the fixture is wrong: the trailer is not read"
    out = support.git(project.root, "diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    assert sorted(rel for rel in out.split("\n") if rel) == sorted(files), \
        f"the fixture is wrong: the commit changes {out.split()}"
    return commit


def _the_acceptance_test_weakened(project):
    support.build_ticket(project, TICKET, WBS, failing=True)
    return MISTYPED, {ACCEPTANCE_TEST: PASSING}


def _a_file_inside_the_allowed_paths(project):
    support.build_ticket(project, TICKET, WBS)
    return A_RECORD, {INSIDE: "# inside the ticket's paths\n"}


def _the_tickets_own_file(project):
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    rel = support.ticket_path(TICKET)
    text = (project.root / rel).read_text(encoding="utf-8")
    assert text.count("profile: FULL\n") == 1, "the fixture is wrong: the ticket file has no FULL profile line"
    return MISTYPED, {rel: text.replace("profile: FULL\n", "profile: STANDARD\n")}


@pytest.mark.parametrize("work", [_the_acceptance_test_weakened, _a_file_inside_the_allowed_paths,
                                  _the_tickets_own_file],
                         ids=["the acceptance test, a mistyped id", "the allowed paths, a record's id",
                              "the ticket's file, a mistyped id"])
def test_a_commit_whose_task_names_no_ticket_and_that_changes_the_tickets_work_refuses(
        work, project, sandbox, interface):
    named, files = work(project)
    commit = _commit_naming(project, named, files)
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    assert commit[:7] in text, f"the refusal does not name the commit {commit[:7]}\n{run.describe()}"
    assert re.search("task", text, re.IGNORECASE), f"the refusal does not say 'task'\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_a_commit_whose_task_names_no_ticket_and_that_changes_nobodys_work_refuses_nothing(
        project, sandbox, interface):
    """The converse: the folder holds none of the ticket's acceptance tests, is not inside its allowed paths,
    holds neither its file nor a governance file."""
    support.build_ticket(project, TICKET, WBS)
    _commit_naming(project, MISTYPED, {NOTES: "# none of the ticket's\n"})
    support.checkpointed(project, TICKET)
    assert not NOTES.startswith(support.GOVERNANCE_PREFIXES + (support.ACCEPTANCE_PREFIX, support.TICKETS_PREFIX,
                                                               "src/example/"))

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
