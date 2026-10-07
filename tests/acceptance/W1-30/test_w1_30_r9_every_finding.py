"""One run of ``gov close`` reports every finding it can establish (round 9; DEC-492, first point).

DEC-492: "``gov close`` reports every finding in one run instead of stopping at the first". Until this round
the command ended at the first of its early findings (the probe record, the trailers, containment, the missing
acceptance tests) and never reached the tests and the governance checks.

**The combined refusal.** One ticket holds four findings, each planted by its own commit and each held by the
fixture before the close: a commit of the ticket without ``Implements:``, a commit W1-50's judgement flags
(a file at the project's root), a failing acceptance test, and a red hard-block check (the ticket changes a
governance file, so the checks run). One close names all four, is counted once and opens one repair ticket,
dependent on the ticket, whose file lists all four.

**An early finding and a later one.** Each early finding alone beside a failing acceptance test: the answer
names both.

**Not measured, by name.** A ticket without acceptance tests has no acceptance run. The answer says so of the
acceptance run in the words "not measured" (``support.says_not_measured``; README, round 9, settlement 14); it
still reports what it could establish, here the red check.

**Could not measure.** DEC-490 stands: a tree that is not its commit ends the run before anything is measured,
however many findings the ticket holds (exit code 1, not counted, no repair ticket).
"""

import re

import pytest

import w1_30_support as support

TICKET = "PROJ-evry"
WBS = "W1-evry"

FEATURE = "src/example/feature.py"
NOTES = "governance/project/notes.yaml"
OUTSIDE = "NOTES.md"
FAILING_TEST = "test_fail"

README_PRESENT = support.declared_check("readme-present", "test -s README.md")
LICENSE_PRESENT = support.declared_check("license-present", "test -s LICENSE", family="graph integrity")
RED_CHECK = "license-present"


def _without_implements(project, rel="src/example/more.py"):
    """A commit of the ticket, by its engineer, inside its paths, without ``Implements:``; returns its id."""
    project.write(rel, "# more\n")
    return project.commit("work without Implements", who=support.IMPLEMENTER,
                          trailers=(f"Task: {TICKET}", support.ENGINEER_ROLE), exact=True)


def _outside_the_paths(project):
    """A commit of the ticket, by its engineer, of a file at the project's root; returns its id."""
    project.write(OUTSIDE, "# planted\n")
    return project.commit(f"the engineer changes {OUTSIDE}", who=support.IMPLEMENTER,
                          trailers=support.trailers_of(TICKET), exact=True)


def _four_findings(project, sandbox):
    """The ticket with its four findings, checkpointed. Returns what names each in an answer."""
    project.add_ticket(TICKET, WBS, allowed_paths=list(support.GOVERNANCE_TICKET_PATHS))
    project.add_failing_test(WBS)
    support.engineer_commit(project, TICKET, {FEATURE: "# feature\n", NOTES: "note: one\n"})
    bare = _without_implements(project)
    outside = _outside_the_paths(project)
    support.checkpointed(project, TICKET)

    judged = support.judged_by_w1_50(project, sandbox, support.ticket_commits(project.root, TICKET))
    assert [(f["commit"], f["paths"]) for f in judged] == [(outside, [OUTSIDE])], \
        f"the fixture is wrong: W1-50's judgement of the ticket's commits is {judged}"
    red = support.red_hard_blocks(support.checks_at_head(project, sandbox))
    assert red == [RED_CHECK], f"the fixture is wrong: the red hard-block checks are {red}"
    return {
        "the commit without Implements:": (bare[:7], "Implements"),
        "the containment finding": (outside[:7], OUTSIDE),
        "the failing acceptance test": (FAILING_TEST,),
        "the red hard-block check": (RED_CHECK,),
    }


def _missing(text, named):
    """The findings ``text`` does not name: every word of a finding must be in it."""
    return [finding for finding, words in named.items() if not all(word in text for word in words)]


def _refused_naming_all(project, sandbox, interface, named):
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    missing = _missing(support.error_text(error), named)
    assert not missing, f"the one refusal does not name: {', '.join(missing)}\n{run.describe()}"
    return run


# --------------------------------------------------------------------------
# 1. The combined refusal
# --------------------------------------------------------------------------

def test_one_refusal_names_every_finding_of_the_ticket(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    named = _four_findings(project, sandbox)

    _refused_naming_all(project, sandbox, interface, named)
    support.assert_not_closed(project, TICKET)


def test_the_refusal_for_several_findings_is_counted_once(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    named = _four_findings(project, sandbox)

    run = _refused_naming_all(project, sandbox, interface, named)
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"one refusal with four findings is counted {support.iteration_count(project.root, TICKET)} times\n" \
        f"{run.describe()}"


def test_the_refusal_for_several_findings_opens_one_repair_ticket_that_lists_them_all(
        project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    named = _four_findings(project, sandbox)

    run = support.run_close(project, sandbox, TICKET)
    support.refused(run, interface, support.EXIT_CHECK_FAILED)

    repair = support.assert_dependent_repair_ticket(project, TICKET, run)
    missing = _missing(repair.read_text(encoding="utf-8"), named)
    assert not missing, f"the repair ticket {repair.name} does not list: {', '.join(missing)}\n{run.describe()}"


# --------------------------------------------------------------------------
# 2. Each early finding beside a failing acceptance test: both are named
# --------------------------------------------------------------------------

def _no_probe_record(project):
    support.build_ticket(project, TICKET, WBS, failing=True, profile="FULL")
    assert not (project.root / "docs" / "probes" / TICKET).exists(), "the fixture is wrong: a probe record exists"
    return [re.compile("probe", re.IGNORECASE)]


def _a_commit_without_implements(project):
    support.build_ticket(project, TICKET, WBS, failing=True)
    bare = _without_implements(project)
    support.checkpointed(project, TICKET)
    return [re.compile(re.escape(bare[:7])), re.compile("Implements")]


def _a_containment_finding(project):
    support.build_ticket(project, TICKET, WBS, failing=True)
    outside = _outside_the_paths(project)
    support.checkpointed(project, TICKET)
    return [re.compile(re.escape(outside[:7])), re.compile(re.escape(OUTSIDE))]


@pytest.mark.parametrize("early", [_no_probe_record, _a_commit_without_implements, _a_containment_finding],
                         ids=["no-probe-record", "no-implements", "containment"])
def test_an_early_finding_does_not_hide_the_failing_acceptance_test(early, project, sandbox, interface):
    patterns = early(project)

    run = support.run_close(project, sandbox, TICKET)

    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    for pattern in patterns:
        assert pattern.search(text), f"the answer does not name the early finding ({pattern.pattern})\n{run.describe()}"
    assert FAILING_TEST in text, \
        f"the answer names the early finding and not the failing acceptance test: the tests were not reached\n" \
        f"{run.describe()}"
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the refusal is counted {support.iteration_count(project.root, TICKET)} times\n{run.describe()}"
    support.assert_dependent_repair_ticket(project, TICKET, run)


# --------------------------------------------------------------------------
# 3. What an earlier part made unmeasurable is said as not measured, by name
# --------------------------------------------------------------------------

def _no_acceptance_tests_and_a_red_check(project, sandbox):
    project.add_ticket(TICKET, WBS, allowed_paths=list(support.GOVERNANCE_TICKET_PATHS))
    support.engineer_commit(project, TICKET, {FEATURE: "# feature\n", NOTES: "note: one\n"})
    support.checkpointed(project, TICKET)
    tests = list((project.root / "tests" / "acceptance" / WBS).rglob("test_*.py"))
    assert not tests, f"the fixture is wrong: the ticket has acceptance tests: {tests}"
    red = support.red_hard_blocks(support.checks_at_head(project, sandbox))
    assert red == [RED_CHECK], f"the fixture is wrong: the red hard-block checks are {red}"


def test_without_acceptance_tests_the_acceptance_run_is_said_as_not_measured(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    _no_acceptance_tests_and_a_red_check(project, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "acceptance" in support.error_text(error).lower(), \
        f"the answer does not name the missing acceptance tests\n{run.describe()}"
    assert support.says_not_measured(error, "acceptance"), \
        f"the answer does not say of the acceptance run that it was not measured\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_without_acceptance_tests_the_governance_checks_are_still_reported(project_with_checks, sandbox, interface):
    """The checks do not depend on the acceptance tests: the red check is a finding of the same run."""
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    _no_acceptance_tests_and_a_red_check(project, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    assert "acceptance" in text.lower(), f"the answer does not name the missing acceptance tests\n{run.describe()}"
    assert RED_CHECK in text, \
        f"the answer does not name the red hard-block check {RED_CHECK}: the checks were not reached\n{run.describe()}"
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the refusal is counted {support.iteration_count(project.root, TICKET)} times\n{run.describe()}"


def test_a_measured_part_is_not_said_as_not_measured(project_with_checks, sandbox, interface):
    """The other side: the four-finding ticket has acceptance tests and they ran, so nothing says of the
    acceptance run that it was not measured. An answer that says it of every part, whatever ran, fails here."""
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    _four_findings(project, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert FAILING_TEST in support.error_text(error), f"the acceptance tests did not run\n{run.describe()}"
    assert not support.says_not_measured(error, "acceptance"), \
        f"the answer says of the acceptance run that it was not measured, although it names its failing test\n" \
        f"{run.describe()}"


# --------------------------------------------------------------------------
# 4. "Could not measure" still ends the run before anything is measured (DEC-490)
# --------------------------------------------------------------------------

def test_a_tree_that_is_not_its_commit_still_ends_the_run_before_any_finding(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    named = _four_findings(project, sandbox)
    project.write("stray.txt", "not committed\n")

    run = support.run_close(project, sandbox, TICKET)

    text = support.error_text(support.refused_without_a_finding(run, interface))
    assert "stray.txt" in text, f"the refusal does not name the file that is not committed\n{run.describe()}"
    reported = [finding for finding in named if finding not in _missing(text, named)]
    assert not reported, f"a close that could not measure reports findings: {reported}\n{run.describe()}"
    support.assert_nothing_counted(project, TICKET, run)
    support.assert_no_repair_ticket(project, run, TICKET)
    support.assert_not_closed(project, TICKET)
