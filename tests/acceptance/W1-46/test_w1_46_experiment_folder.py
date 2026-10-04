"""W1-46 -- which directory a research ticket's one folder may be (batch 3, after implementation).

Described behaviour D of the review after implementation (DEC-136).

DEC-242: ``gov launch`` "refuses a research ticket whose ``allowed_paths`` isn't
exactly one experiment folder". What makes a directory an experiment folder is
not written down: see DP-13 in the README. Three cases are decided by other
lines, whatever DP-13's answer is, and only they are tested here.

- ``tests/acceptance/**``. MR-3: an implementer write there is "refused by the
  guard", which "refuses to it as to every role but the Independent Test
  Designer". The research role is not the test designer, so the guard refuses
  its write there, also on a ticket that names the directory, and no research
  session is started with that directory as its folder.
- ``.gov-runtime/**``. KPI success 10 (DEC-180): the settings built "for every
  worker role" deny ``.gov-runtime/**`` except scratch, and a file-tool write
  to the freeze flag, the snapshots, the findings or the records fails.
- An entry with ``..`` in it. The fence (KPI success 4) and the guard's
  per-ticket allow-list (KPI success 5) must speak of the same folder: the
  launch is refused, or both hold the session to the folder the entry resolves
  to.

No session is started.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

w47 = support.w47
RESEARCH = support.RESEARCH
FOLDER = support.EXPERIMENT_REL
SIBLING = "experiments/spikes/exp-900"
NEW_TICKET = "DAEO-zz98"
ACCEPTANCE_FILE = "tests/acceptance/W1-90/test_fixture.py"


# --------------------------------------------------------------------------
# tests/acceptance/** (MR-3)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("entry", ("tests/acceptance/**", "tests/acceptance/W1-90/**"))
def test_a_research_ticket_on_the_acceptance_tests_refuses_the_launch(launch, project, entry):
    launch(RESEARCH).session()
    ticket = support.write_ticket(project, NEW_TICKET, RESEARCH, allowed_paths=(entry,))
    support.assert_refused(launch(RESEARCH, ticket), "allowed_paths", "experiment folder", "tests/acceptance")


@pytest.mark.parametrize("tool", ("Write", "Edit"))
def test_the_guard_refuses_a_research_write_to_an_acceptance_test_on_a_ticket_that_names_them(guard, project, tool):
    ticket = support.write_ticket(project, NEW_TICKET, RESEARCH, allowed_paths=("tests/acceptance/**",))
    for rel in (ACCEPTANCE_FILE, "tests/acceptance/W1-90/test_new.py"):
        result = guard(tool, w47.write_input(tool, project / rel), RESEARCH, ticket)
        w47.assert_stopped(result, f"{tool} to {rel} by research on a ticket that names tests/acceptance/**")


def test_the_guard_refuses_a_research_bash_write_to_an_acceptance_test_on_a_ticket_that_names_them(guard, project):
    ticket = support.write_ticket(project, NEW_TICKET, RESEARCH, allowed_paths=("tests/acceptance/**",))
    command = f"echo changed > {ACCEPTANCE_FILE}"
    result = guard("Bash", w47.bash_input(command), RESEARCH, ticket, cwd=project)
    w47.assert_stopped(result, f"`{command}` by research on a ticket that names tests/acceptance/**")


# --------------------------------------------------------------------------
# .gov-runtime/** (KPI success 10, DEC-180)
# --------------------------------------------------------------------------

def test_a_research_ticket_on_the_runtime_directory_opens_nothing_there(launch, guard, project, sandbox):
    """Refused, or launched with every protected runtime path still denied; the guard refuses the file tools."""
    ticket = support.write_ticket(project, NEW_TICKET, RESEARCH, allowed_paths=(".gov-runtime/**",))
    result = launch(RESEARCH, ticket)
    if result.run.returncode != 0:
        support.assert_refused(result, "allowed_paths", "experiment folder", ".gov-runtime")
    else:
        open_paths = [rel for rel in support.PROTECTED_RUNTIME
                      if not support.edit_denied(result, rel, project, sandbox)]
        assert open_paths == [], f"a research session with .gov-runtime as its folder may edit {open_paths}"
    for rel in (".gov-runtime/freeze", ".gov-runtime/findings.jsonl", ".gov-runtime/records.jsonl",
                ".gov-runtime/snapshots/keep.json"):
        answer = guard("Write", w47.write_input("Write", project / rel), RESEARCH, ticket)
        w47.assert_stopped(answer, f"Write to {rel} by research on a ticket that names .gov-runtime/**")


# --------------------------------------------------------------------------
# An entry that is not written as the folder it reaches
# --------------------------------------------------------------------------

def test_an_entry_with_dot_dot_is_refused_or_the_fence_and_the_guard_hold_the_same_folder(launch, guard, project,
                                                                                         sandbox):
    """``<folder>/../<sibling>/**``: never a fence around one folder and a guard that allows the other."""
    ticket = support.write_ticket(project, NEW_TICKET, RESEARCH, allowed_paths=(f"{FOLDER}/../exp-900/**",))
    result = launch(RESEARCH, ticket)
    if result.run.returncode != 0:
        support.assert_refused(result, "allowed_paths", "experiment folder")
        return
    assert not support.edit_denied(result, f"{SIBLING}/data.txt", project, sandbox), (
        "the fence closes the folder the entry resolves to"
    )
    assert support.edit_denied(result, f"{FOLDER}/README.md", project, sandbox), (
        "the fence leaves open the folder the entry only passes through"
    )
    inside = guard("Write", w47.write_input("Write", project / SIBLING / "notes.md"), RESEARCH, ticket)
    w47.assert_allowed(inside, "a research Write in the folder the fence was built around")
    outside = guard("Write", w47.write_input("Write", project / FOLDER / "notes.md"), RESEARCH, ticket)
    w47.assert_stopped(outside, "a research Write in the folder the entry only passes through")
