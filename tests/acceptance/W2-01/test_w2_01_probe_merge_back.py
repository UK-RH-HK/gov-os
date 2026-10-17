"""KPI 4 and failure KPI 9: the probe gate after the integration branch is merged into the ticket branch and back.

KPI 4 [W2-H047, W2-M202]: "A ticket branch probed, then merged with the integration branch and merged back,
passes the probe gate when the probed code is unchanged." DEC-592 named the case: "the probe gate refuses when
the integration branch is merged into the ticket branch after the probe and that merge is merged back (the
probed commit is then the first parent of the merge, not the merged side)." W2-M202: "A merge that brings
exactly the probed code plus integration content passes."

Failure KPI 9: "A hand-resolved merge that changes probed code still refuses the probe gate."

"The probed code" (README, "The forms this suite fixes"): the files the probe gate guards since DEC-581, those
inside the ticket's ``allowed_paths`` and in its acceptance folder, and its ticket file (W1-30's settlement 33).
"Unchanged": each is, at the commit being closed, byte for byte what it is at the probed commit.

The project: ``main`` is the integration branch. FULL ticket ``PROJ-prbk`` is created there and worked on its
branch ``work``; its head is probed. Another ticket lands work on ``main`` outside this ticket's paths. The lead
merges ``main`` into ``work`` (one command that commits), the orchestrator merges ``work`` back into ``main``,
then commits the probe record and the checkpoint; the close runs on ``main``. Every merge here carries every
trailer (``Implements:`` too), unless the case says it is in the merge form, so that the probe gate is the only
gate with a reason (KPI 2 holds the merge form on its own).
"""

import pytest

import w2_01_support as support

TICKET, WBS = "PROJ-prbk", "W1-prbk"
OTHER, OTHER_WBS = "PROJ-othr", "W1-othr"
FEATURE = "src/example/feature.py"
BRANCH = "work"
MERGE_TRAILERS = support.trailers_of(TICKET, role="orchestrator")


def _probed_branch(project):
    support.create_ticket(project, TICKET, WBS, profile="FULL")
    project.checkout(BRANCH, create=True)
    return support.engineer_commit(project, TICKET, {FEATURE: "# feature\n"})


def _integration_goes_on(project, files=None):
    project.checkout("main")
    support.create_ticket(project, OTHER, OTHER_WBS, allowed_paths=("src/other/**", "src/example/**"))
    support.engineer_commit(project, OTHER, files or {"src/other/part.py": "# part\n"},
                            trailers=support.trailers_of(OTHER))
    project.checkout(BRANCH)


def _merged_in(project, trailers=MERGE_TRAILERS, edit=None):
    return project.merge("main", trailers, edit=edit, message="merge the integration branch into the branch")


def _merged_back(project, edit=None):
    project.checkout("main")
    return project.merge(BRANCH, MERGE_TRAILERS, edit=edit, message="merge the ticket's branch")


def _recorded(project, probed):
    support.probe_recorded(project, TICKET, probed)
    support.checkpointed(project, TICKET)


def _probe_gate_findings(error):
    """The statements of the refusal that are the probe gate's (they say "probe")."""
    return [text for text in support.strings_of(error) if "probe" in text.lower()]


@pytest.mark.parametrize("merge_in", ("every trailer", "the merge form"))
def test_probed_then_merged_with_the_integration_branch_and_back_closes(merge_in, project, sandbox, interface):
    probed = _probed_branch(project)
    _integration_goes_on(project)
    inward = _merged_in(project, trailers=MERGE_TRAILERS if merge_in == "every trailer" else support.merge_form(TICKET))
    back = _merged_back(project)
    _recorded(project, probed)
    assert support.git(project, "diff", "--name-only", probed, "HEAD", "--", "src/example", "tests/acceptance/W1-prbk",
                       ".tickets/PROJ-prbk.md").strip() == "", "the fixture is wrong: the probed code changed"

    run = support.run_close(project, sandbox, TICKET)

    assert not _probe_gate_findings(run.envelope().get("error") or {}), \
        f"the probe gate refuses the merge-back of the unchanged probed code\n{run.describe()}"
    support.closed(run, interface)
    record = support.base.the_close_record(project, TICKET)
    listed = [entry.get("commit") for entry in record.get("commits", [])]
    assert inward in listed and back in listed, f"the close record does not list both merges: {listed}"


def test_probed_then_merged_with_the_integration_branch_closes_on_the_branch(project, sandbox, interface):
    """The same merge, before it is merged back: the close runs at the head of the ticket's branch."""
    probed = _probed_branch(project)
    _integration_goes_on(project)
    _merged_in(project)
    _recorded(project, probed)

    run = support.run_close(project, sandbox, TICKET)

    assert not _probe_gate_findings(run.envelope().get("error") or {}), \
        f"the probe gate refuses the merge of the integration branch into the probed branch\n{run.describe()}"
    support.closed(run, interface)


# --------------------------------------------------------------------------
# Failure KPI 9: a hand-resolved merge that changes probed code still refuses
# --------------------------------------------------------------------------

def test_a_hand_resolved_merge_into_the_branch_that_changes_probed_code_refuses(project, sandbox, interface):
    """The integration branch changed the probed file too; the conflict is resolved by hand into new text."""
    probed = _probed_branch(project)
    _integration_goes_on(project, files={FEATURE: "# the other ticket's feature\n"})
    inward = _merged_in(project, edit={FEATURE: "# feature, resolved by hand\n"})
    back = _merged_back(project)
    _recorded(project, probed)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    said = _probe_gate_findings(error)
    assert said and any(inward[:7] in text or back[:7] in text for text in said), \
        f"the probe gate does not refuse the hand-resolved merge {inward[:12]} or its merge-back {back[:12]}\n" \
        f"{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


@pytest.mark.parametrize("edit", ({FEATURE: "# feature, changed in the merge-back\n"},
                                  {"src/example/added.py": "# added in the merge-back\n"}),
                         ids=("a probed file changed", "a file added inside the ticket's paths"))
def test_a_merge_back_that_changes_probed_code_by_hand_refuses(edit, project, sandbox, interface):
    probed = _probed_branch(project)
    _integration_goes_on(project)
    _merged_in(project)
    back = _merged_back(project, edit=edit)
    _recorded(project, probed)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    said = _probe_gate_findings(error)
    assert said and any(back[:7] in text for text in said), \
        f"the probe gate does not refuse the merge-back {back[:12]} that changed probed code\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# Added after implementation began (DEC-136, the review of round 1): a merge after the probed commit whose
# probed code is not the probed commit's refuses, whichever side's version it took. The measure is the probed
# code itself (DEC-505): at each merge after the probed commit it is what it is at the probed commit.
# --------------------------------------------------------------------------

INTEGRATION_FEATURE = "# the other ticket's feature\n"
LAYOUTS = ("merged back only", "merged in, then back")
WRONG_MERGE_BACKS = ("a conflict on a probed file resolved to the integration side",
                     "a probed file the ticket added removed",
                     "made from the integration side with the ours strategy")


def _integration_changes(project, files, first):
    """Another ticket's work lands on ``main`` (that ticket created there first when ``first``); ends on ``main``."""
    project.checkout("main")
    if first:
        support.create_ticket(project, OTHER, OTHER_WBS, allowed_paths=("src/other/**", "src/example/**"))
    support.engineer_commit(project, OTHER, files, trailers=support.trailers_of(OTHER))


def _merged_back_by(project, wrong):
    project.checkout("main")
    if wrong == WRONG_MERGE_BACKS[0]:
        how = dict(edit={FEATURE: INTEGRATION_FEATURE})
    elif wrong == WRONG_MERGE_BACKS[1]:
        how = dict(remove=(FEATURE,))
    else:
        how = dict(strategy="ours")
    return support.merge_by_hand(project, BRANCH, MERGE_TRAILERS, message="merge the ticket's branch", **how)


@pytest.mark.parametrize("layout", LAYOUTS)
@pytest.mark.parametrize("wrong", WRONG_MERGE_BACKS)
def test_a_merge_back_that_drops_probed_code_refuses_and_names_the_merge_back(wrong, layout, project, sandbox,
                                                                              interface):
    probed = _probed_branch(project)
    first = True
    if layout == "merged in, then back":
        _integration_changes(project, {"src/other/part.py": "# part\n"}, first=True)
        project.checkout(BRANCH)
        _merged_in(project)
        first = False
    if wrong == WRONG_MERGE_BACKS[0]:
        _integration_changes(project, {FEATURE: INTEGRATION_FEATURE}, first=first)
    elif first:
        _integration_changes(project, {"src/other/part.py": "# part\n"}, first=True)
    back = _merged_back_by(project, wrong)
    _recorded(project, probed)
    assert support.content_at(project, back, FEATURE) != support.content_at(project, probed, FEATURE), \
        "the fixture is wrong: the merge-back holds the probed code"

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    said = _probe_gate_findings(error)
    assert said and any(back[:7] in text for text in said), \
        f"the probe gate does not refuse the merge-back {back[:12]} ({wrong}) whose probed code is not the " \
        f"probed commit's\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


def test_a_merge_into_the_branch_resolved_to_the_integration_side_refuses(project, sandbox, interface):
    """Inward: the conflict on the probed file is resolved to the integration side's version, then merged back."""
    probed = _probed_branch(project)
    _integration_changes(project, {FEATURE: INTEGRATION_FEATURE}, first=True)
    project.checkout(BRANCH)
    inward = _merged_in(project, edit={FEATURE: INTEGRATION_FEATURE})
    back = _merged_back(project)
    _recorded(project, probed)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    said = _probe_gate_findings(error)
    assert said and any(inward[:7] in text or back[:7] in text for text in said), \
        f"the probe gate does not refuse the merge {inward[:12]} resolved to the integration side, or its " \
        f"merge-back {back[:12]}\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# Added after implementation began (DEC-136, DEC-739; the second review's first finding): the merge-back that
# brings the probed commit into the closed branch is measured by the probed code whatever task it names. A
# plain ``git merge`` (no trailer, the message git writes) or a merge naming another ticket's task that drops
# or replaces the probed code refuses, naming the merge-back. DEC-490 ("a commit that names another ticket is
# that ticket's") holds for the other commits, not for this merge-back.
# --------------------------------------------------------------------------

PLAIN_MERGE = "Merge branch 'work'"
NAMES = {"no task": (), "another ticket's task": support.trailers_of(OTHER, role="orchestrator")}
TASKLESS_DROPS = ([("no task", wrong, layout) for wrong in WRONG_MERGE_BACKS for layout in LAYOUTS]
                  + [("another ticket's task", wrong, LAYOUTS[0]) for wrong in WRONG_MERGE_BACKS]
                  + [("another ticket's task", WRONG_MERGE_BACKS[2], LAYOUTS[1])])


def _merged_back_naming(project, names, wrong=None):
    """The merge-back onto ``main``, naming ``names`` (a plain ``git merge`` for no task); made in the
    ``wrong`` way, or bringing the branch unchanged when ``wrong`` is ``None``."""
    project.checkout("main")
    if wrong == WRONG_MERGE_BACKS[0]:
        how = dict(edit={FEATURE: INTEGRATION_FEATURE})
    elif wrong == WRONG_MERGE_BACKS[1]:
        how = dict(remove=(FEATURE,))
    elif wrong == WRONG_MERGE_BACKS[2]:
        how = dict(strategy="ours")
    else:
        how = {}
    message = PLAIN_MERGE if names == "no task" else "merge the ticket's branch"
    return support.merge_by_hand(project, BRANCH, NAMES[names], message=message, **how)


@pytest.mark.parametrize("names, wrong, layout", TASKLESS_DROPS,
                         ids=[f"{names}-{wrong}-{layout}" for names, wrong, layout in TASKLESS_DROPS])
def test_a_merge_back_naming_no_task_or_another_that_drops_probed_code_refuses_and_names_it(
        names, wrong, layout, project, sandbox, interface):
    probed = _probed_branch(project)
    first = True
    if layout == "merged in, then back":
        _integration_changes(project, {"src/other/part.py": "# part\n"}, first=True)
        project.checkout(BRANCH)
        _merged_in(project)
        first = False
    if wrong == WRONG_MERGE_BACKS[0]:
        _integration_changes(project, {FEATURE: INTEGRATION_FEATURE}, first=first)
    elif first:
        _integration_changes(project, {"src/other/part.py": "# part\n"}, first=True)
    back = _merged_back_naming(project, names, wrong)
    _recorded(project, probed)
    message = support.git(project, "log", "-1", "--format=%B", back)
    assert f"Task: {TICKET}" not in message, "the fixture is wrong: the merge-back names the ticket's task"
    assert support.content_at(project, back, FEATURE) != support.content_at(project, probed, FEATURE), \
        "the fixture is wrong: the merge-back holds the probed code"

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    said = _probe_gate_findings(error)
    assert said and any(back[:7] in text for text in said), \
        f"the probe gate does not refuse the merge-back {back[:12]} naming {names} ({wrong}) whose probed code " \
        f"is not the probed commit's\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


@pytest.mark.parametrize("layout", LAYOUTS)
def test_a_plain_merge_back_of_the_unchanged_probed_code_closes(layout, project, sandbox, interface):
    """KPI 4's success line with the merge-back as git writes it (no trailer): it still closes."""
    probed = _probed_branch(project)
    _integration_goes_on(project)
    if layout == "merged in, then back":
        _merged_in(project)
    back = _merged_back_naming(project, "no task")
    _recorded(project, probed)
    assert support.git(project, "log", "-1", "--format=%B", back).strip() == PLAIN_MERGE, \
        "the fixture is wrong: the merge-back is not a plain git merge"
    assert support.git(project, "diff", "--name-only", probed, "HEAD", "--", "src/example", "tests/acceptance/W1-prbk",
                       ".tickets/PROJ-prbk.md").strip() == "", "the fixture is wrong: the probed code changed"

    run = support.run_close(project, sandbox, TICKET)

    assert not _probe_gate_findings(run.envelope().get("error") or {}), \
        f"the probe gate refuses the plain merge-back {back[:12]} of the unchanged probed code\n{run.describe()}"
    support.closed(run, interface)


# --------------------------------------------------------------------------
# Added after implementation began (DEC-136, DEC-750; the third review's first two findings). The merge-back is
# the merge after the probed commit whose first parent lacks the probed commit and whose other parent holds it.
# Every later merge that holds the probed commit and changes probed code refuses, whatever task it names, and
# the refusal names it. A merge that holds the probed commit on neither side (another ticket's merge on the
# integration branch) is judged as before: it is not the merge-back and does not by itself refuse.
# --------------------------------------------------------------------------

OTHER_BRANCH = "other"
SECOND, SECOND_WBS = "PROJ-scnd", "W1-scnd"
SECOND_FEATURE = "src/second/feature.py"
LATER_DROPS = ("a probed file the ticket added removed", "a probed file replaced in the merge")
LATER_DROP_CASES = ((LATER_DROPS[0], LAYOUTS[0]), (LATER_DROPS[1], LAYOUTS[0]), (LATER_DROPS[0], LAYOUTS[1]))
OTHER_MERGES = ((LAYOUTS[0], "with that ticket's trailers"), (LAYOUTS[1], "a plain git merge"))


def _holds(project, commit, merge):
    """Whether ``merge`` holds ``commit`` (``commit`` is ``merge`` or one of its ancestors)."""
    return commit in support.git(project, "rev-list", merge).split()


def _parents(project, merge):
    return support.git(project, "rev-list", "--parents", "-n", "1", merge).split()[1:]


def _unchanged(project, probed):
    return support.git(project, "diff", "--name-only", probed, "HEAD", "--", "src/example", "tests/acceptance/W1-prbk",
                       ".tickets/PROJ-prbk.md").strip() == ""


def _notes_on_the_branch(project):
    """More work on the ticket's branch after the merge-back: a task-less notes commit outside the ticket's paths
    (DEC-490: it refuses nothing). Ends on the branch."""
    project.checkout(BRANCH)
    project.write("docs/notes/PROJ-prbk.md", "# notes after the merge-back\n")
    return project.commit("notes", who=support.ORCHESTRATOR, trailers=("Role: orchestrator",), exact=True)


def _other_ticket_branch(project):
    """Another ticket is created on ``main`` and worked on its own branch ``other``, inside its own paths only.
    Ends on ``main``."""
    project.checkout("main")
    support.create_ticket(project, OTHER, OTHER_WBS, allowed_paths=("src/other/**",))
    project.checkout(OTHER_BRANCH, create=True)
    support.engineer_commit(project, OTHER, {"src/other/part.py": "# part\n"}, trailers=support.trailers_of(OTHER))
    project.checkout("main")


def _other_ticket_merged(project, plain):
    """The other ticket's branch merged into ``main``: a plain ``git merge`` (no trailer) or with that ticket's
    trailers. Returns the merge."""
    project.checkout("main")
    if plain:
        return support.merge_by_hand(project, OTHER_BRANCH, (), message=f"Merge branch '{OTHER_BRANCH}'")
    return support.merge_by_hand(project, OTHER_BRANCH, support.trailers_of(OTHER, role="orchestrator"),
                                 message="merge the other ticket's branch")


@pytest.mark.parametrize("wrong, layout", LATER_DROP_CASES, ids=[f"{wrong}-{layout}" for wrong, layout in LATER_DROP_CASES])
def test_a_later_merge_back_naming_another_ticket_that_drops_probed_code_refuses_and_names_it(
        wrong, layout, project, sandbox, interface):
    """The ticket is merged back with the probed code unchanged; after more work on the branch it is merged back
    a second time, that merge naming another ticket's task and dropping or replacing the probed code."""
    probed = _probed_branch(project)
    _integration_goes_on(project)
    if layout == "merged in, then back":
        _merged_in(project)
    first = _merged_back(project)
    _notes_on_the_branch(project)
    project.checkout("main")
    how = dict(remove=(FEATURE,)) if wrong == LATER_DROPS[0] else dict(edit={FEATURE: INTEGRATION_FEATURE})
    later = support.merge_by_hand(project, BRANCH, NAMES["another ticket's task"],
                                  message="merge the ticket's branch again", **how)
    _recorded(project, probed)
    assert support.content_at(project, first, FEATURE) == support.content_at(project, probed, FEATURE), \
        "the fixture is wrong: the first merge-back does not hold the probed code"
    assert all(_holds(project, probed, parent) for parent in _parents(project, later)), \
        "the fixture is wrong: the later merge-back does not hold the probed commit on both sides"
    assert f"Task: {OTHER}" in support.git(project, "log", "-1", "--format=%B", later), \
        "the fixture is wrong: the later merge-back does not name another ticket's task"
    assert support.content_at(project, later, FEATURE) != support.content_at(project, probed, FEATURE), \
        "the fixture is wrong: the later merge-back holds the probed code"

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    said = _probe_gate_findings(error)
    assert said and any(later[:7] in text for text in said), \
        f"the probe gate does not refuse the later merge-back {later[:12]} naming {OTHER} ({wrong}) whose probed " \
        f"code is not the probed commit's\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


def test_a_later_merge_holding_the_probed_commit_that_leaves_the_probed_code_closes(project, sandbox, interface):
    """Boundary (guard): after the merge-back, another ticket's branch is merged into ``main`` (a plain git merge)
    touching only its own paths. The merge holds the probed commit and leaves the probed code as it was."""
    probed = _probed_branch(project)
    _other_ticket_branch(project)
    _merged_back(project)
    later = _other_ticket_merged(project, plain=True)
    _recorded(project, probed)
    assert _holds(project, probed, _parents(project, later)[0]), \
        "the fixture is wrong: the later merge's first parent does not hold the probed commit"
    assert _unchanged(project, probed), "the fixture is wrong: the probed code changed"

    run = support.run_close(project, sandbox, TICKET)

    assert not _probe_gate_findings(run.envelope().get("error") or {}), \
        f"the probe gate refuses the later merge {later[:12]} that leaves the probed code as it was\n{run.describe()}"
    support.closed(run, interface)


@pytest.mark.parametrize("layout, form", OTHER_MERGES, ids=[f"{layout}-{form}" for layout, form in OTHER_MERGES])
def test_another_tickets_merge_on_the_integration_branch_is_not_the_merge_back(layout, form, project, sandbox,
                                                                              interface):
    """After the ticket branched, another ticket reaches ``main`` through its own branch and a merge, which holds
    the probed commit on neither side; then the ticket's branch is merged back with the probed code unchanged."""
    probed = _probed_branch(project)
    _other_ticket_branch(project)
    others = _other_ticket_merged(project, plain=form == "a plain git merge")
    if layout == "merged in, then back":
        project.checkout(BRANCH)
        _merged_in(project)
    back = _merged_back(project)
    _recorded(project, probed)
    assert not any(_holds(project, probed, parent) for parent in _parents(project, others)), \
        "the fixture is wrong: the other ticket's merge holds the probed commit"
    assert not _holds(project, probed, _parents(project, back)[0]) and _holds(project, probed, back), \
        "the fixture is wrong: the ticket's merge-back is not the merge that brings the probed commit"
    assert _unchanged(project, probed), "the fixture is wrong: the probed code changed"

    run = support.run_close(project, sandbox, TICKET)

    assert not _probe_gate_findings(run.envelope().get("error") or {}), \
        f"the probe gate refuses: the other ticket's merge {others[:12]} ({form}) is not the merge-back " \
        f"{back[:12]}\n{run.describe()}"
    support.closed(run, interface)


def test_a_later_full_ticket_closes_after_an_earlier_ones_merge_back(project, sandbox, interface):
    """KPI 4 seen from the next ticket: one FULL ticket is probed, merged back and closed; a second FULL
    ticket, probed with its probed code unchanged, is merged back after it and closes. The first ticket's
    merge-back holds the second ticket's probed commit on neither side."""
    support.create_ticket(project, SECOND, SECOND_WBS, profile="FULL", allowed_paths=("src/second/**",))
    probed = _probed_branch(project)
    project.checkout("main")
    project.checkout("second", create=True)
    second_probed = support.engineer_commit(project, SECOND, {SECOND_FEATURE: "# second\n"},
                                            trailers=support.trailers_of(SECOND))
    first_back = _merged_back(project)
    _recorded(project, probed)
    support.closed(support.run_close(project, sandbox, TICKET), interface)
    if project.waiting_paths():
        project.commit(f"{TICKET} closed", who=support.ORCHESTRATOR,
                       trailers=support.trailers_of(TICKET, role="orchestrator"), exact=True)
    second_back = project.merge("second", support.trailers_of(SECOND, role="orchestrator"),
                                message="merge the second ticket's branch")
    support.probe_recorded(project, SECOND, second_probed)
    support.checkpointed(project, SECOND)
    assert not any(_holds(project, second_probed, parent) for parent in _parents(project, first_back)), \
        "the fixture is wrong: the first ticket's merge-back holds the second ticket's probed commit"
    assert support.content_at(project, "HEAD", SECOND_FEATURE) == "# second\n", \
        "the fixture is wrong: the second ticket's probed code changed"

    run = support.run_close(project, sandbox, SECOND)

    assert not _probe_gate_findings(run.envelope().get("error") or {}), \
        f"the probe gate refuses the second ticket: the first ticket's merge-back {first_back[:12]} is not its " \
        f"merge-back {second_back[:12]}\n{run.describe()}"
    support.closed(run, interface)
