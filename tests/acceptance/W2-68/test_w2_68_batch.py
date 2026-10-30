"""A batch (DEC-883 item 1, DEC-890): queued closes of two tickets on one integrated head share one rebuild, one
``gov check`` and one full regression on that head; then each ticket's own checks run (its acceptance suite, the
record-reading set, its trailers, paths, probe record and checkpoint); each close record cites the batch's run
(its fingerprint, its commit, its JUnit XML) and its scope.

The project: tickets A (widget) and C (gadget), each with its work and its checkpoint committed, and no record
store yet. One ``python3 -m gov.close.batch run PROJ-aaaa PROJ-cccc`` closes both.

Red reason (README): ``gov.close.batch`` does not exist (``No module named gov.close.batch``: no envelope).
"""

import json

import pytest

import w2_68_support as support


class Batch:
    """One batch of A and C, run once for the module's cases; each case asserts on what it left."""

    def __init__(self, base):
        self.sandbox = support.make_sandbox(base)
        self.env = support.env_without_endpoint(self.sandbox)
        self.project = support.Project(base / "project", base / "told")
        project = self.project
        project.work({support.WIDGET: "# the widget, changed\n"}, ticket=support.A)
        project.work({support.GADGET: "# the gadget, changed\n"}, ticket=support.C)
        project.ready(self.sandbox, ticket=support.A)
        project.ready(self.sandbox, ticket=support.C)
        self.head = project.head()
        self.before = project.runs()
        self.checks_before = project.gov_checks_run()
        self.answer = support.batch(project, self.env, support.A, support.C)

    def passed(self):
        return self.answer.ok()


@pytest.fixture(scope="module")
def ran(tmp_path_factory):
    return Batch(tmp_path_factory.mktemp("w2_68_batch"))


def test_the_batch_closes_both_tickets(ran):
    ran.passed()
    for ticket in (support.A, support.C):
        assert support.ticket_closed(ran.project, ticket), f"{ticket} is not closed after the batch\n" \
                                                            f"{ran.answer.describe()}"
        support.the_close_record(ran.project, ticket)  # exactly one close record each


def test_one_gov_check_for_the_whole_batch(ran):
    ran.passed()
    checks = ran.project.gov_checks_run() - ran.checks_before
    assert checks == 1, (f"the batch of two tickets ran gov check {checks} times; one gov check on the batch's "
                         "head is shared by both closes (DEC-883 item 1 a)")


def test_one_full_regression_on_the_head_then_each_ticket_s_own_checks(ran):
    ran.passed()
    project = ran.project
    told = project.told_runs()
    since = project.runs_since(ran.before)
    # The full regression: every case of the project, once for the whole batch, whatever ticket it belongs to.
    shared = [support.CASE(wbs) for wbs in support.ALL_SUITES if wbs not in (support.A_WBS, support.C_WBS)]
    shared += [support.UNIT_CASE, *support.SERIAL_CASES]
    counts = {case: since.get(case, 0) for case in shared}
    assert all(count == 1 for count in counts.values()), \
        f"the cases of the full regression did not each run once for the batch (one regression, DEC-883 1 a): {counts}"
    regression_end = max(time for case in shared for _, time in told[case][-1:])
    # Then each ticket's own checks: its acceptance suite and the record-reading set, after the regression.
    for wbs in (support.A_WBS, support.C_WBS):
        later = [time for _, time in told.get(support.CASE(wbs), []) if time > regression_end]
        assert later, f"{wbs}'s acceptance suite did not run as its ticket's own check after the regression: {since}"
    record_reading = [time for _, time in told.get(support.RR_CASE, []) if time > regression_end]
    assert len(record_reading) == 2, (f"the record-reading set ran {len(record_reading)} times after the regression; "
                                      f"once for each ticket's own checks is expected: {since}")


def test_each_close_record_cites_the_batch_s_run_and_states_its_scope(ran):
    ran.passed()
    project = ran.project
    for ticket in (support.A, support.C):
        evidence = support.close_evidence(project, ticket)
        scope, block = support.cited_run(evidence)
        assert scope == support.REUSED, f"{ticket}'s close record states scope {scope!r}, not the batch's run reused"
        assert block is not None, f"{ticket}'s evidence has no {support.REUSED_KEY!r} block: {sorted(evidence)}"
        fingerprint = evidence.get(support.CODE_FINGERPRINT)
        assert isinstance(fingerprint, str) and fingerprint, \
            f"{ticket}'s evidence states no {support.CODE_FINGERPRINT}: {sorted(evidence)}"
        records = evidence.get(support.RECORDS_FINGERPRINT)
        assert isinstance(records, str) and records, \
            f"{ticket}'s evidence states no {support.RECORDS_FINGERPRINT}: {sorted(evidence)}"
        assert fingerprint in json.dumps(block), \
            f"{ticket} cites a run of another code fingerprint than its own {fingerprint}: {json.dumps(block)[:1500]}"
        assert support.names_commit(block, ran.head), \
            f"{ticket} does not cite the batch's commit {ran.head}: {json.dumps(block)[:1500]}"
        named = support.xml_files(project, block)
        assert named, f"{ticket}'s reused block names no JUnit XML of the batch's run: {json.dumps(block)[:1500]}"
        for rel, path in named:
            assert path.is_file(), f"{ticket} cites the JUnit XML {rel}, which does not exist"
        held = set().union(*(support.junit_names(path) for _, path in named))
        assert support.CASE("W1-dd") in held and support.UNIT_CASE in held, \
            f"the JUnit XML {ticket} cites does not hold the batch's full regression: {sorted(held)}"


def test_the_batch_s_closes_reuse_its_governance_checks(ran):
    ran.passed()
    for ticket in (support.A, support.C):
        front = support.the_close_record(ran.project, ticket)
        evidence = front.get("evidence") or {}
        stated = evidence.get(support.GOVERNANCE_CHECKS_REUSED, front.get(support.GOVERNANCE_CHECKS_REUSED))
        assert stated, (f"{ticket}'s close record does not state {support.GOVERNANCE_CHECKS_REUSED}: the batch's one "
                        f"gov check is the evidence of its governance checks")


def test_the_batch_s_run_record_states_its_head_its_fingerprint_and_its_junit_xml(ran):
    ran.passed()
    project = ran.project
    rel, record, text = support.the_batch_record(project)
    assert support.names_commit(record, ran.head), f"{rel} does not name the batch's head {ran.head}"
    fingerprint = support.close_evidence(project, support.A).get(support.CODE_FINGERPRINT)
    assert isinstance(fingerprint, str) and fingerprint and fingerprint in text, \
        f"{rel} does not state the code fingerprint the closes cite ({fingerprint!r})"
    named = support.xml_files(project, record)
    assert named and all(path.is_file() for _, path in named), \
        f"{rel} names no JUnit XML file that exists (DEC-889 item 2 b): {[n for n, _ in named]}"


def test_a_ticket_of_the_batch_whose_own_check_fails_does_not_close_and_the_other_does(tmp_path):
    """C has no checkpoint: its own checks refuse it (the watchdog), and A still closes on the batch's run."""
    sandbox = support.make_sandbox(tmp_path)
    env = support.env_without_endpoint(sandbox)
    project = support.Project(tmp_path / "project", tmp_path / "told")
    project.work({support.WIDGET: "# the widget, changed\n"}, ticket=support.A)
    project.work({support.GADGET: "# the gadget, changed\n"}, ticket=support.C)
    project.ready(sandbox, ticket=support.A)

    answer = support.batch(project, env, support.A, support.C)

    answer.envelope()
    assert support.ticket_closed(project, support.A), f"A did not close on the batch's run\n{answer.describe()}"
    assert not support.ticket_closed(project, support.C), f"C closed without its checkpoint\n{answer.describe()}"
    assert support.CHECKPOINT_MISSING in answer.text(), \
        f"the batch does not say why C was refused ({support.CHECKPOINT_MISSING})\n{answer.describe()}"
    scope, _ = support.cited_run(support.close_evidence(project, support.A))
    assert scope == support.REUSED, f"A's close record states scope {scope!r}, not the batch's run reused"
