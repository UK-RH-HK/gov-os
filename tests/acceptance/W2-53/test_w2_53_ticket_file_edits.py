"""KPI 6 and failure KPI 4: a ticket-file edit made from the integration side (DEC-757 item 3).

KPI 6 [DEC-757]: "A change to the ticket's file after its probed commit, made by a commit carrying
``Role: orchestrator`` or ``Role: owner``, naming the ticket in ``Task:`` and changing only that file, is not a
change to the probed code."

Failure KPI 4 [DEC-757]: "A ticket-file change on the ticket's own side after the probe, or an integration-side
commit that changes more than the ticket's file, still refuses."

"The ticket's own side" (README, "The forms this suite fixes"): DEC-757 item 3 defines the integration side by
the commit, not by the branch it lies on. A commit is integration-side when its final trailer block carries
``Role: orchestrator`` or ``Role: owner``, its ``Task:`` names the ticket, and it changes the ticket file and
nothing else. Every other commit that changes the ticket file after the probe is on the ticket's own side: a
commit of the ticket's workers (``Role: engineer``, here), one of the integration roles that changes more, and
one that names no task (DEC-490). Wherever the edit lies, on the ticket's branch or on ``main``, the merges that
carry it in (inward and the merge-back) are git's own merges and pass.

The project: FULL ticket ``PROJ-tkfl`` on ``work``, probed; the edit follows the probe; the branch is merged back;
the probe record and the checkpoint are committed on ``main``, where the close runs.
"""

import pytest

import w2_53_support as support

TICKET, WBS = "PROJ-tkfl", "W1-tkfl"
BRANCH = "work"
FEATURE = "src/example/feature.py"
TICKET_FILE = support.base.ticket_path(TICKET)
NOTES = f"docs/notes/{TICKET}.md"
MERGE_TRAILERS = support.trailers_of(TICKET, role="orchestrator")

WHO = {"orchestrator": support.ORCHESTRATOR, "owner": support.OWNER, "engineer": support.IMPLEMENTER,
       "independent-test-designer": support.TEST_DESIGNER}


def _probed(project):
    support.create_ticket(project, TICKET, WBS, profile="FULL")
    project.checkout(BRANCH, create=True)
    return support.engineer_commit(project, TICKET, {FEATURE: "# feature\n"})


def _edit(project, trailers, who, also=None):
    """One commit, with exactly ``trailers``, that adds a note to the ticket file (and writes ``also``)."""
    text = (project.root / TICKET_FILE).read_text(encoding="utf-8")
    project.write(TICKET_FILE, text + "\nA note from the integration side, after the probe.\n")
    for rel, content in (also or {}).items():
        project.write(rel, content)
    return project.commit("a note in the ticket file", who=who, trailers=trailers, exact=True)


def _merged_back_and_recorded(project, probed):
    project.checkout("main")
    back = project.merge(BRANCH, MERGE_TRAILERS, message="merge the ticket's branch")
    support.probe_recorded(project, TICKET, probed)
    support.checkpointed(project, TICKET)
    return back


def _changed_by(project, commit):
    return support.git(project, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).split()


def _closes(project, sandbox, interface, edit):
    run = support.run_close(project, sandbox, TICKET)
    assert not support.probe_statements(run.envelope().get("error") or {}), \
        f"the probe gate counts the integration-side edit {edit[:12]} of the ticket file as a change to the " \
        f"probed code\n{run.describe()}"
    support.closed(run, interface)


def _refused_naming(project, sandbox, interface, commits, what):
    """Refused by the probe gate, one of whose statements names one of ``commits`` (the edit, or the merge-back
    that carries it in: either is where the probed code stops being the probed commit's)."""
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface)
    said = support.probe_statements(error)
    assert any(commit[:7] in text for text in said for commit in commits), \
        f"the probe gate does not refuse {' or '.join(c[:12] for c in commits)} ({what})\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# KPI 6: an integration-side edit is not a change to the probed code
# --------------------------------------------------------------------------

def test_an_orchestrators_integration_side_edit_of_the_ticket_file_on_the_branch_closes(project, sandbox, interface):
    probed = _probed(project)
    edit = _edit(project, support.trailers_of(TICKET, role="orchestrator"), support.ORCHESTRATOR)
    _merged_back_and_recorded(project, probed)
    assert _changed_by(project, edit) == [TICKET_FILE], "the fixture is wrong: the edit changes more"
    assert not support.base.judged_by_w1_50(project, sandbox, [edit]), \
        "the fixture is wrong: W1-50's judgement has a finding for the edit"

    _closes(project, sandbox, interface, edit)


def test_an_owners_integration_side_edit_of_the_ticket_file_is_no_finding_of_the_probe_gate(
        project, sandbox, interface):
    """The owner's edit is integration-side too. W1-50's judgement has a finding for every ``Role: owner`` commit a
    ticket's commits hold ("a Role: owner commit made during an agent's call", DEC-360), and ``gov close`` adds no
    exemption to it (DEC-453), so this close does not succeed: the case holds that the probe gate does not count
    the edit as a change to the probed code (README, package P-1)."""
    probed = _probed(project)
    edit = _edit(project, support.trailers_of(TICKET, role="owner"), support.OWNER)
    _merged_back_and_recorded(project, probed)
    assert _changed_by(project, edit) == [TICKET_FILE], "the fixture is wrong: the edit changes more"

    run = support.run_close(project, sandbox, TICKET)

    assert not support.probe_statements(run.envelope().get("error") or {}), \
        f"the probe gate counts the owner's integration-side edit {edit[:12]} of the ticket file as a change to " \
        f"the probed code\n{run.describe()}"


LAYOUTS = ("merged back only", "merged in, then back")


@pytest.mark.parametrize("layout", LAYOUTS)
def test_an_integration_side_edit_made_on_main_and_carried_in_by_the_merges_closes(layout, project, sandbox,
                                                                                  interface):
    """The orchestrator's edit lies on ``main``: the merge-back (and, before it, the inward merge) carry it in."""
    probed = _probed(project)
    project.checkout("main")
    edit = _edit(project, support.trailers_of(TICKET, role="orchestrator"), support.ORCHESTRATOR)
    if layout == LAYOUTS[1]:
        project.checkout(BRANCH)
        inward = project.merge("main", MERGE_TRAILERS, message="merge the integration branch into the branch")
        assert support.content_at(project, inward, TICKET_FILE) == support.content_at(project, edit, TICKET_FILE)
    _merged_back_and_recorded(project, probed)
    assert support.content_at(project, "HEAD", TICKET_FILE) == support.content_at(project, edit, TICKET_FILE), \
        "the fixture is wrong: the closed head does not hold the edit"

    _closes(project, sandbox, interface, edit)


# --------------------------------------------------------------------------
# Failure KPI 4: an edit on the ticket's own side, or one that changes more, still refuses
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", ("engineer", "independent-test-designer"))
def test_a_ticket_file_edit_on_the_tickets_own_side_after_the_probe_refuses(role, project, sandbox, interface):
    probed = _probed(project)
    edit = _edit(project, support.trailers_of(TICKET, role=role), WHO[role])
    back = _merged_back_and_recorded(project, probed)
    assert _changed_by(project, edit) == [TICKET_FILE], "the fixture is wrong: the edit changes more"

    _refused_naming(project, sandbox, interface, (edit, back), f"a ticket-file edit by Role: {role}")


def test_an_orchestrators_commit_that_changes_the_ticket_file_and_more_refuses(project, sandbox, interface):
    """The other file is outside the ticket's work: the commit refuses for the ticket file."""
    probed = _probed(project)
    edit = _edit(project, support.trailers_of(TICKET, role="orchestrator"), support.ORCHESTRATOR,
                 also={NOTES: "# notes\n"})
    back = _merged_back_and_recorded(project, probed)
    assert sorted(_changed_by(project, edit)) == sorted([TICKET_FILE, NOTES]), "the fixture is wrong"

    _refused_naming(project, sandbox, interface, (edit, back),
                    "an orchestrator's commit that changes more than the ticket")


def test_an_orchestrators_ticket_file_edit_that_names_no_task_refuses(project, sandbox, interface):
    """It does not name the ticket in ``Task:``: not integration-side; DEC-490 counts it with the ticket's work."""
    probed = _probed(project)
    edit = _edit(project, ("Role: orchestrator",), support.ORCHESTRATOR)
    back = _merged_back_and_recorded(project, probed)

    _refused_naming(project, sandbox, interface, (edit, back), "a ticket-file edit naming no task")
