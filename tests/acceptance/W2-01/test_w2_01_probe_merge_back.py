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
