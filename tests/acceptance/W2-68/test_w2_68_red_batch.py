"""A red batch (DEC-883 item 2, DEC-889 item 2 b): failing tests re-run alone first; a red that passes alone is a
flaky candidate and is not bisected; a red that fails alone is attributed (by ``git bisect`` over the batch's
merges, or by the failing test's own ticket) with the evidence; nothing closes on a red run, and a close after it
does not cite it.

The project: tickets A (widget) and C (gadget) queued in one batch. C's work breaks the gadget, which W1-dd's test
reads (a red that fails alone, caused by C's commit; W1-dd's own ticket is ``PROJ-dddd``). W1-cp's test fails on
its first run only (a red that passes alone). Both planted tests tell the commit they ran at.

Red reason (README): ``gov.close.batch`` does not exist (``No module named gov.close.batch``: no envelope).
"""

import json

import pytest

import w2_68_support as support


class RedBatch:
    def __init__(self, base):
        self.sandbox = support.make_sandbox(base)
        self.env = support.env_without_endpoint(self.sandbox)
        self.project = support.Project(base / "project", base / "told", plant_reds=True)
        project = self.project
        project.work({support.WIDGET: "# the widget, changed\n"}, ticket=support.A)
        self.cause = project.work({support.GADGET: "# the gadget, BROKEN\n"}, ticket=support.C)
        project.ready(self.sandbox, ticket=support.A)
        project.ready(self.sandbox, ticket=support.C)
        self.head = project.head()
        self.answer = support.batch(project, self.env, support.A, support.C)
        self.later = None
        if self.answer.data is None:
            return
        project.commit_left()
        self.later = project.close(self.sandbox, ticket=support.A, env=self.env)

    def refused(self):
        return self.answer.refused()

    def said(self):
        """Everything the batch said and recorded: its answer and every batch run record, as one text."""
        return "\n".join([self.answer.text(), *(text for _, _, text in support.batch_records(self.project))])


@pytest.fixture(scope="module")
def red(tmp_path_factory):
    return RedBatch(tmp_path_factory.mktemp("w2_68_red_batch"))


def test_nothing_closes_on_a_red_batch(red):
    red.refused()
    for ticket in (support.A, support.C):
        assert not support.ticket_closed(red.project, ticket), f"{ticket} closed on a red batch\n{red.answer.describe()}"
        records = support.close_support.close_records(red.project.root, ticket)
        assert not records, f"{ticket} has a close record after a red batch: {[rel for rel, _ in records]}"


def test_failing_tests_re_run_alone_first_at_the_batch_s_head(red):
    red.refused()
    for case in (support.RED_CASE, support.FLAKY_CASE):
        runs = red.project.commits_told(case)
        first = [commit for _, commit in runs[:2]]
        assert first == [red.head, red.head], (f"{case} did not run twice at the batch's head (the regression, then "
                                               f"alone) before anything else: {runs}")
        assert len(runs) >= 2, f"{case} was not re-run alone after it failed: {runs}"


def test_a_red_that_passes_alone_is_a_flaky_candidate_and_is_not_bisected(red):
    red.refused()
    runs = red.project.commits_told(support.FLAKY_CASE)
    elsewhere = [commit for _, commit in runs if commit != red.head]
    assert not elsewhere, f"the red that passed alone was run at other commits (bisected): {runs}"
    assert len(runs) == 2, f"the red that passed alone ran {len(runs)} times; the regression, then once alone: {runs}"
    said = red.said()
    assert support.FLAKY_CASE in said and "flaky candidate" in support.normalised(said), \
        f"the batch does not name {support.FLAKY_CASE} a flaky candidate\n{red.answer.describe()}"


def test_a_red_that_fails_alone_is_attributed_with_the_evidence(red):
    red.refused()
    said = red.said()
    assert support.RED_CASE in said and support.RED_TEXT in said, \
        f"the batch does not state the red test and its failure text\n{red.answer.describe()}"
    by_bisect = support.names_commit(said, red.cause)
    by_own_ticket = support.D_TICKET in said
    assert by_bisect or by_own_ticket, (
        f"the red that fails alone is attributed neither to the commit that caused it ({red.cause[:12]}, C's work: "
        f"git bisect over the batch's merges) nor to the failing test's own ticket ({support.D_TICKET})\n"
        f"{red.answer.describe()}")
    runs = red.project.commits_told(support.RED_CASE)
    assert len(runs) >= 2 and runs[1][1] == red.head, f"the red was not re-run alone before it was attributed: {runs}"


def test_a_close_after_a_red_batch_does_not_cite_its_run(red):
    red.refused()
    assert red.later is not None
    support.assert_does_not_cite(red.later, red.head, "A's close after the red batch")
    for rel, record, _ in support.batch_records(red.project):
        assert rel not in json.dumps(support.evidence_of_any(red.later) or {}), \
            f"A's close after the red batch names its run record {rel}"
