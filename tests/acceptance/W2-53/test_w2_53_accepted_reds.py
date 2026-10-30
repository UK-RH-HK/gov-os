"""KPI 5 and failure KPI 3: the owner-accepted known-red list, as a ratchet, in ``gov close`` (DEC-757 item 2).

KPI 5 [DEC-757]: "A red whose exact test id the path map's ``accepted_reds`` lists, with an ACCEPTED owner decision
naming it, a reason and the ticket that fixes it, does not refuse the close; the close names it with its decision
and fixing ticket. An entry counts only when the commit that added it carries ``Role: owner``."

Failure KPI 3 [DEC-757]: "A red not on ``accepted_reds`` refuses the close. A listed red that passes refuses the
close, naming the entry to remove. An entry added by a commit without ``Role: owner``, or whose decision is not an
ACCEPTED owner entry naming that test id, is refused, naming the entry; the list never grows without an owner
decision."

The forms (README, "The forms this suite fixes"): a test id is the pytest node id relative to the project's root;
an entry covers exactly its id. The decision names a test id when its text holds the test's own name (with its
parameter set, as a whole word) and its file. The commit that added an entry is every commit of the closed head's
history whose path map holds the entry (its ``test`` and ``decision``) while none of its parents' does; each must
carry ``Role: owner`` in its final trailer block.

The project: a stand-in of W1-42's exit report file, with the two tests the owner's first entries name (DEC-757),
committed by the owner; the owner's register entry; the path map's list; then STANDARD ticket ``PROJ-rtch``, whose
own acceptance test passes. The close's regression run (every test under ``tests/`` but the ticket's folder) runs
W1-42's file.
"""

import pytest

import w2_53_support as support

TICKET, WBS = "PROJ-rtch", "W1-rtch"
DECISION = "DEC-901"
RETR_RED, RETR_GREEN, SHARE_RED = support.RETR_RED, support.RETR_GREEN, support.SHARE_RED


def _reds_in_the_project(project, red=("RETR-X-02",), share_red=False):
    project.write(support.W1_42_FILE, support.w1_42_file(red=red, share_red=share_red))
    support.setup_commit(project, "W1-42's exit report")


def _decision(project, *named, status=support.OWNER_ACCEPTED):
    project.record_decision(DECISION, status, support.owner_text_naming(*named))


def _ticket_done(project):
    support.create_ticket(project, TICKET, WBS)
    support.engineer_commit(project, TICKET, {"src/example/feature.py": "# feature\n"})
    support.checkpointed(project, TICKET)


def _covered(answer, test_id):
    return [report for report in support.red_reports(answer)
            if report.get("test") == test_id and report.get("result") == support.RESULT_FAILED]


def _refused_entry(error, test_id, *words):
    found = support.naming(support.findings_coded(error, support.ACCEPTED_RED_REFUSED), test_id, *words)
    assert found, (f"no {support.ACCEPTED_RED_REFUSED} finding names the entry {test_id} "
                   f"with {list(words)}:\n{support.text_of(error)}")


# --------------------------------------------------------------------------
# KPI 5: a listed red with an ACCEPTED owner decision does not refuse, and is named
# --------------------------------------------------------------------------

def test_listed_reds_with_the_owners_decision_do_not_refuse_the_close_and_are_named(project, sandbox, interface):
    """The owner's two first entries, as DEC-757 gives them: one parameter set of a parameterised test (fixed by
    W2-13) and one plain test (fixed by W2-14), one decision naming both."""
    _reds_in_the_project(project, share_red=True)
    _decision(project, RETR_RED, SHARE_RED)
    support.add_entries(project, support.ACCEPTED_REDS, [
        support.red_entry(RETR_RED, DECISION, fixed_by="W2-13"),
        support.red_entry(SHARE_RED, DECISION, fixed_by="W2-14"),
    ])
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    result = support.closed(run, interface)
    for test_id, fixed_by in ((RETR_RED, "W2-13"), (SHARE_RED, "W2-14")):
        reports = [report for report in _covered(result, test_id)
                   if report.get("decision") == DECISION and report.get("fixed_by") == fixed_by]
        assert reports, (f"the close does not name the listed red {test_id} with its decision {DECISION} and "
                         f"fixing ticket {fixed_by} under {support.ACCEPTED_REDS!r}\n{run.describe()}")


# --------------------------------------------------------------------------
# Failure KPI 3: a red the list does not cover refuses
# --------------------------------------------------------------------------

UNCOVERED = {
    # case: (the entry's test id or None, the reds of the file (parameter sets, the share test), the uncovered red)
    "nothing listed": (None, (("RETR-X-02",), False), RETR_RED),
    "another parameter of the same test": (RETR_RED, (("RETR-X-01", "RETR-X-02"), False), RETR_GREEN),
    "the bare function name": (f"{support.W1_42_FILE}::{support.RETR_FUNCTION}", (("RETR-X-02",), False), RETR_RED),
    "a name the red's own name begins with": (f"{support.W1_42_FILE}::test_governance_share_is_measured",
                                              ((), True), SHARE_RED),
    "the same name in another file": (RETR_RED.replace("W1-42/", "W1-41/"), (("RETR-X-02",), False), RETR_RED),
}


@pytest.mark.parametrize("case", tuple(UNCOVERED))
def test_a_red_the_list_does_not_cover_by_its_exact_id_refuses_the_close(case, project, sandbox, interface):
    entry, (red, share_red), uncovered = UNCOVERED[case]
    _reds_in_the_project(project, red=red, share_red=share_red)
    if entry is not None:
        _decision(project, entry)
        support.add_entries(project, support.ACCEPTED_REDS, [support.red_entry(entry, DECISION)])
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    assert support.name_of(uncovered) in support.text_of(error), \
        f"the refusal does not name the red {uncovered} the list does not cover ({case})\n{run.describe()}"
    assert not _covered(error, uncovered), f"the close reports {uncovered} as a listed red ({case})"
    assert not support.findings_coded(error, support.ACCEPTED_RED_REFUSED), \
        f"the entry {entry} is refused, though the owner added it and the decision names it\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


def test_a_listed_red_that_passes_refuses_the_close_naming_the_entry_to_remove(project, sandbox, interface):
    _reds_in_the_project(project, red=())
    _decision(project, RETR_RED)
    support.add_entries(project, support.ACCEPTED_REDS, [support.red_entry(RETR_RED, DECISION)])
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    found = support.naming(support.findings_coded(error, support.ACCEPTED_RED_PASSES), RETR_RED, "remov")
    assert found, (f"no {support.ACCEPTED_RED_PASSES} finding names the entry {RETR_RED} to remove\n"
                   f"{run.describe()}")
    support.base.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# Failure KPI 3: an entry that the owner did not add does not count
# --------------------------------------------------------------------------

ADDERS = ("Role: orchestrator", "Role: owner outside the final trailer block",
          "a second entry added by the orchestrator after the owner's")
OUTSIDE_THE_BLOCK = ("the path map's accepted_reds\n\nRole: owner\n\nAs the owner asked in the review.\n\n"
                     "Task: setup\nRole: orchestrator\n")


@pytest.mark.parametrize("adder", ADDERS)
def test_an_entry_the_owner_did_not_add_does_not_count_and_is_refused_naming_it(adder, project, sandbox,
                                                                                interface):
    _reds_in_the_project(project, share_red=adder == ADDERS[2])
    if adder == ADDERS[2]:
        _decision(project, RETR_RED, SHARE_RED)
        support.add_entries(project, support.ACCEPTED_REDS, [support.red_entry(SHARE_RED, DECISION, fixed_by="W2-14")])
    else:
        _decision(project, RETR_RED)
    message = OUTSIDE_THE_BLOCK if adder == ADDERS[1] else None
    added = support.add_entries(project, support.ACCEPTED_REDS, [support.red_entry(RETR_RED, DECISION)],
                                role="orchestrator", message=message)
    assert support.final_roles(project, added) == ["orchestrator"], "the fixture is wrong: the adding commit's role"
    if adder == ADDERS[1]:
        assert "Role: owner" in support.git(project, "log", "-1", "--format=%B", added)
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    _refused_entry(error, RETR_RED, added[:7])
    assert not _covered(error, RETR_RED), f"the close reports {RETR_RED} as a listed red ({adder})"
    if adder == ADDERS[2]:
        assert not support.naming(support.findings_coded(error, support.ACCEPTED_RED_REFUSED), SHARE_RED), \
            f"the owner's own entry {SHARE_RED} is refused too\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# Failure KPI 3: an entry whose decision is not an ACCEPTED owner entry naming its test id does not count
# --------------------------------------------------------------------------

DECISIONS = {
    # case: (the decision's status or None for no entry in the register, the test its text names, the words)
    "no entry in the register": (None, RETR_RED, "no entry"),
    "a proposed decision": (support.PROPOSED, RETR_RED, "not accepted"),
    "a delegated decision": (support.DELEGATED, RETR_RED, "not the owner"),
    "an owner's decision that names another parameter set": (support.OWNER_ACCEPTED, RETR_GREEN, "does not name"),
}


@pytest.mark.parametrize("case", tuple(DECISIONS))
def test_an_entry_without_an_accepted_owner_decision_naming_its_test_does_not_count(case, project, sandbox,
                                                                                    interface):
    status, named, words = DECISIONS[case]
    _reds_in_the_project(project)
    if status is not None:
        _decision(project, named, status=status)
    support.add_entries(project, support.ACCEPTED_REDS, [support.red_entry(RETR_RED, DECISION)])
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    _refused_entry(error, RETR_RED, DECISION, words)
    assert not _covered(error, RETR_RED), f"the close reports {RETR_RED} as a listed red ({case})"
    support.base.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# Settled: an entry whose test the close did not run
# --------------------------------------------------------------------------

def test_an_entry_whose_test_the_close_did_not_run_does_not_refuse_and_is_reported_not_run(project, sandbox,
                                                                                            interface):
    """README, settlement R-5: it covers nothing and refuses nothing, and the close names it as not run."""
    gone = f"{support.W1_42_FILE}::test_a_case_that_was_removed"
    _reds_in_the_project(project, red=())
    _decision(project, gone)
    support.add_entries(project, support.ACCEPTED_REDS, [support.red_entry(gone, DECISION, fixed_by="W2-13")])
    _ticket_done(project)

    run = support.run_close(project, sandbox, TICKET)

    result = support.closed(run, interface)
    reports = [report for report in support.red_reports(result)
               if report.get("test") == gone and report.get("result") == support.RESULT_NOT_RUN
               and report.get("decision") == DECISION and report.get("fixed_by") == "W2-13"]
    assert reports, f"the close does not report the listed test {gone} as not run\n{run.describe()}"
