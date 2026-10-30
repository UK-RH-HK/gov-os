"""KPI 1 and failure KPI 1: ``gov close`` judges a ticket by its class [W2-H045].

KPI 1: "gov close judges a ticket by its class: an implementation ticket on its acceptance tests; a specification
ticket on its closed readiness record and its acceptance tests; an audit ticket on its report and the audit
validator; a research ticket on its evidence record; an integration or coordination ticket on its named evidence
files." W2-H045: such a ticket closes "with no acceptance tests and no exception"; WBS §0 rule 1: a clean
``gov close``, exit 0, no ``--disposition``.

Failure KPI 1: "A research ticket without an evidence record closes; an audit ticket whose report fails the
validator closes."

How a ticket names its evidence (README, assumption A1): its ``acceptance_tests`` mapping holds ``evidence``, a
list of paths. The evidence is also committed by the ticket's own commits, inside its allowed paths, so a close
that finds it through those commits reads the same evidence. A class ticket here has no
``tests/acceptance/<wbs>/`` folder at all.
"""

import pytest

import w2_07_support as support

WBS = "W9-clss"


def _class_ticket(project, ticket, cls, allowed, evidence, files):
    """A ticket of ``cls`` without acceptance tests, naming ``evidence``; its role's commit writes ``files``; then
    the orchestrator's checkpoint."""
    support.create_ticket(project, ticket, WBS, cls=cls, allowed_paths=allowed, tests=False,
                          acceptance=support.judged_by_class(cls, evidence))
    role = support.CLASS_ROLES[cls]
    support.work(project, ticket, files, role=role, who=support.TEST_DESIGNER if role.startswith("independent-test")
                 else None)
    support.checkpointed(project, ticket)
    assert not (project.root / "tests" / "acceptance" / WBS).exists(), "the fixture is wrong: the ticket has tests"


def _closed_cleanly(project, sandbox, interface, ticket):
    run = support.run_close(project, sandbox, ticket)
    support.closed(run, interface)
    assert support.ticket_status(project.root, ticket) == "closed", f"the ticket is not closed\n{run.describe()}"
    assert support.base.close_records(project.root, ticket), f"no close record was written\n{run.describe()}"
    return run


def _refused_not_closed(project, sandbox, interface, ticket):
    run = support.run_close(project, sandbox, ticket)
    error = support.refused(run, interface)
    support.base.assert_not_closed(project, ticket)
    return run, error


# --------------------------------------------------------------------------
# Research: its evidence record
# --------------------------------------------------------------------------

RESEARCH = "PROJ-rsch"
RESEARCH_PATHS = ("docs/research/W9/**",)
RECORD_REL = "docs/research/W9/EXP-w9.md"


def test_a_research_ticket_closes_on_its_evidence_record(project, sandbox, interface):
    _class_ticket(project, RESEARCH, "research", RESEARCH_PATHS, [RECORD_REL],
                  {RECORD_REL: support.research_record("EXP-w9")})
    _closed_cleanly(project, sandbox, interface, RESEARCH)


def test_a_research_ticket_without_its_evidence_record_is_refused(project, sandbox, interface):
    """Failure KPI 1: the record the ticket names is not there; its work wrote notes, not a record."""
    _class_ticket(project, RESEARCH, "research", RESEARCH_PATHS, [RECORD_REL],
                  {"docs/research/W9/notes.txt": "notes, not an evidence record\n"})
    run, error = _refused_not_closed(project, sandbox, interface, RESEARCH)
    assert support.names_any(error, RECORD_REL, "evidence"), \
        f"the refusal does not name the missing evidence record\n{run.describe()}"


# --------------------------------------------------------------------------
# Audit: its report and the audit validator
# --------------------------------------------------------------------------

AUDIT = "PROJ-audt"
AUDIT_PATHS = ("docs/audit/W9/**",)
REPORT_REL = "docs/audit/W9/AUD-w9.md"


@pytest.mark.parametrize("valid", [True, False], ids=["report-passes-the-validator", "report-fails-the-validator"])
def test_an_audit_ticket_is_judged_on_its_report_and_the_audit_validator(valid, project, sandbox, interface):
    """Failure KPI 1: an audit ticket whose report fails the validator does not close (an invalid class)."""
    audited = support.head_of(project)
    rows = [("The README", "OK" if valid else "BOGUS", "README.md")]
    _class_ticket(project, AUDIT, "audit", AUDIT_PATHS, [REPORT_REL], {REPORT_REL: support.audit_report(audited, rows)})
    code, said = support.audit_validator(project, sandbox, REPORT_REL)
    assert code == (0 if valid else 1), f"the fixture is wrong: the validator answers {code}\n{said}"
    if valid:
        _closed_cleanly(project, sandbox, interface, AUDIT)
    else:
        run, error = _refused_not_closed(project, sandbox, interface, AUDIT)
        assert support.names_any(error, "AUDIT_INVALID_CLASS", "validator"), \
            f"the refusal does not name the audit validator's finding\n{run.describe()}"


# --------------------------------------------------------------------------
# Integration and coordination: their named evidence files
# --------------------------------------------------------------------------

EVIDENCE_PATHS = ("docs/plan/W9/**",)
NAMED = ["docs/plan/W9/gate-evidence.md", "docs/plan/W9/run.log"]


@pytest.mark.parametrize("cls", ["integration", "coordination"])
def test_an_integration_or_coordination_ticket_closes_on_its_named_evidence_files(cls, project, sandbox, interface):
    ticket = "PROJ-intg" if cls == "integration" else "PROJ-cord"
    _class_ticket(project, ticket, cls, EVIDENCE_PATHS, NAMED,
                  {NAMED[0]: "# Gate evidence\n\nEach line passed.\n", NAMED[1]: "run 1: passed\n"})
    _closed_cleanly(project, sandbox, interface, ticket)


@pytest.mark.parametrize("cls", ["integration", "coordination"])
def test_an_integration_or_coordination_ticket_missing_a_named_evidence_file_is_refused(cls, project, sandbox,
                                                                                       interface):
    ticket = "PROJ-intg" if cls == "integration" else "PROJ-cord"
    _class_ticket(project, ticket, cls, EVIDENCE_PATHS, NAMED, {NAMED[0]: "# Gate evidence\n\nEach line passed.\n"})
    run, error = _refused_not_closed(project, sandbox, interface, ticket)
    assert support.names(error, NAMED[1]), f"the refusal does not name the missing evidence file\n{run.describe()}"


# --------------------------------------------------------------------------
# Specification: its closed readiness record and its acceptance tests
# --------------------------------------------------------------------------

SPEC_TICKET = "PROJ-spec"
SPEC_ID = "SPEC-w9"
CHANGE = "w9-feature"


@pytest.mark.parametrize("closed_record", [True, False], ids=["readiness-closed", "a-required-row-open"])
def test_a_specification_ticket_is_judged_on_its_readiness_record_and_its_tests(closed_record, project, sandbox,
                                                                               interface):
    """The readiness record is closed when ``gov readiness --ticket`` passes (no required row open, DEC-085); its
    acceptance tests are its own telling test, which must have run in a close that passes."""
    project.write(support.READINESS_SCHEMA_REL, support.readiness_schema_text())
    project.setup_commit("the feature-readiness schema")
    support.create_ticket(project, SPEC_TICKET, WBS, cls="specification",
                          allowed_paths=(f"openspec/changes/{CHANGE}/**",), specification=SPEC_ID)
    support.work(project, SPEC_TICKET, support.specification_files(SPEC_ID, CHANGE, () if closed_record else (1,)),
                 role="product-spec")
    support.checkpointed(project, SPEC_TICKET)
    assert support.readiness(project, sandbox, SPEC_TICKET) == (0 if closed_record else 3), \
        "the fixture is wrong: gov readiness does not judge the record as intended"
    if closed_record:
        _closed_cleanly(project, sandbox, interface, SPEC_TICKET)
        assert support.ACCEPTANCE_MARK in project.ran(), "the specification ticket closed without running its tests"
    else:
        run, error = _refused_not_closed(project, sandbox, interface, SPEC_TICKET)
        assert support.names_any(error, "readiness", "SPEC_NOT_CLOSED"), \
            f"the refusal does not name the open readiness record\n{run.describe()}"


# --------------------------------------------------------------------------
# Implementation: its acceptance tests, whatever else it names
# --------------------------------------------------------------------------

def test_an_implementation_ticket_naming_evidence_but_without_acceptance_tests_is_refused(project, sandbox, interface):
    """The class decides what judges a ticket: evidence files do not stand in for an implementation ticket's
    acceptance tests."""
    support.create_ticket(project, "PROJ-impl", WBS, cls="implementation", tests=False,
                          acceptance=support.judged_by_class("implementation", ["src/example/feature.py"]))
    support.work(project, "PROJ-impl", {"src/example/feature.py": "# feature\n"})
    support.checkpointed(project, "PROJ-impl")
    run, error = _refused_not_closed(project, sandbox, interface, "PROJ-impl")
    assert support.names(error, "acceptance"), f"the refusal does not name the missing acceptance tests\n{run.describe()}"
