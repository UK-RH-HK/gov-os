"""W2-184, KPI success 5 -- a ticket whose review records show two failed reviews or a fail-open finding launches its next
round on Opus at the table's effort, recorded as ``promotion``; a lower model is refused.

KPI success-5 [DEC-1120 (3)]. Verify: planted review records: one with two failed reviews, one with a fail-open
finding, one with neither.

Interface 5: the ticket's probe records are the ``.md`` files under ``docs/probes/<ticket id>/`` of the launch root, at
any depth, in sorted path order. A file's front matter that is not YAML refuses the launch naming the file; a file with no
front matter, or whose front matter is not a map with ``type: probe``, is skipped. A promotion applies when (a) a record
holds a fenced ``verdict`` block (JSON) with a finding whose ``consequence`` is ``fails open`` (a block that is not JSON of
that shape refuses, naming the file) or (b) two or more records have ``judgement`` fail or failed; (a) is checked first.
Reason: ``a fail-open finding`` or ``two failed reviews``; record: the root-relative path of the first record holding a
fail-open finding, or of the second failed record. The session's model is ``criticality.yaml``'s ``opus`` at the table's
effort; a model after ``--`` other than it is refused naming both; ``--trial`` is refused.
"""

from __future__ import annotations

import pytest

import w2_184_support as s

ENG, AUD = s.ENGINEER, s.AUDITOR
TK = "DAEO-pr01"
PROMOTED = dict(model_source="promotion", effort_source="by criticality")


@pytest.fixture()
def tk(project):
    """An engineer ticket in C2: the table says Sonnet, high."""
    return s.ticket(project, ENG, "C2", tk=TK)


def _promoted(launch, tk, reason, record, **kw):
    return s.assert_session(launch(ENG, tk, **kw), s.OPUS, "high", criticality="C2",
                            promotion={"reason": reason, "record": record}, **PROMOTED)


def _not_promoted(launch, tk):
    return s.assert_session(launch(ENG, tk), *s.TABLES[ENG]["C2"], criticality="C2", model_source="by criticality",
                            effort_source="by criticality")


# --------------------------------------------------------------------------
# The three planted sets
# --------------------------------------------------------------------------

@pytest.mark.parametrize("first,second", [("fail", "fail"), ("fail", "failed"), ("failed", "failed")])
def test_s5_two_failed_reviews_promote_the_next_round_to_opus_at_the_table_s_effort(
        project, launch, tk, first, second):
    s.plant_probe(project, tk, "00-pass.md", "pass")
    s.plant_probe(project, tk, "01-review.md", first)
    record = s.plant_probe(project, tk, "02-review.md", second)
    s.plant_probe(project, tk, "03-review.md", "fail")
    _promoted(launch, tk, "two failed reviews", record)


def test_s5_a_fail_open_finding_promotes_the_next_round(project, launch, tk):
    s.plant_probe(project, tk, "01-review.md", "pass")
    record = s.plant_probe(project, tk, "02-review.md", "pass", verdict=s.verdict_block("other", "fails open"))
    _promoted(launch, tk, "a fail-open finding", record)


def test_s5_the_first_record_holding_a_fail_open_finding_is_the_one_recorded(project, launch, tk):
    record = s.plant_probe(project, tk, "01-open.md", "fail", verdict=s.verdict_block("fails open"))
    s.plant_probe(project, tk, "02-open.md", "pass", verdict=s.verdict_block("fails open"))
    _promoted(launch, tk, "a fail-open finding", record)


def test_s5_a_fail_open_finding_is_checked_before_two_failed_reviews(project, launch, tk):
    s.plant_probe(project, tk, "01-failed.md", "fail")
    s.plant_probe(project, tk, "02-failed.md", "fail")
    record = s.plant_probe(project, tk, "03-open.md", "pass", verdict=s.verdict_block("fails open"))
    _promoted(launch, tk, "a fail-open finding", record)


def test_s5_neither_one_failed_review_nor_findings_that_do_not_fail_open_promote(project, launch, tk):
    s.plant_probe(project, tk, "01-failed.md", "fail")
    s.plant_probe(project, tk, "02-pass.md", "pass", verdict=s.verdict_block("loses work", "other"))
    s.plant_probe(project, tk, "03-pass.md", "pass", verdict=s.verdict_block())
    _not_promoted(launch, tk)


def test_s5_records_at_any_depth_count_and_the_second_failed_one_in_sorted_order_is_named(project, launch, tk):
    s.plant_probe(project, tk, "01-round/PR.md", "fail")
    record = s.plant_probe(project, tk, "02-round/PR.md", "fail")
    s.plant_probe(project, tk, "03-round/PR.md", "fail")
    _promoted(launch, tk, "two failed reviews", record)


@pytest.mark.parametrize("how", [
    "a-failed-review-of-another-ticket", "a-record-that-is-not-a-probe", "a-file-with-no-front-matter",
    "a-file-that-is-not-markdown", "a-verdict-in-a-record-that-is-not-a-probe", "a-front-matter-that-is-a-list"])
def test_s5_what_is_not_this_ticket_s_probe_record_is_skipped(project, launch, tk, how):
    s.plant_probe(project, tk, "01-failed.md", "fail")  # the one failed review of this ticket
    if how == "a-failed-review-of-another-ticket":
        s.plant_probe(project, "DAEO-other", "02-failed.md", "fail")
        s.plant_probe(project, "DAEO-other", "03-open.md", "pass", verdict=s.verdict_block("fails open"))
    elif how == "a-record-that-is-not-a-probe":
        s.plant_probe(project, tk, "02-note.md", "fail", kind="evidence")
    elif how == "a-file-with-no-front-matter":
        s.plant_probe(project, tk, "02-note.md", raw="# A note\n\njudgement: fail\n\n" + s.verdict_block("fails open"))
    elif how == "a-file-that-is-not-markdown":
        s.plant_probe(project, tk, "02-note.txt", "fail")
        s.plant_probe(project, tk, "03-note.json", "fail")
    elif how == "a-verdict-in-a-record-that-is-not-a-probe":
        s.plant_probe(project, tk, "02-note.md", "pass", kind="evidence", verdict=s.verdict_block("fails open"))
    else:
        s.plant_probe(project, tk, "02-note.md", raw="---\n- judgement\n- fail\n---\n" + s.verdict_block("fails open"))
    _not_promoted(launch, tk)


# --------------------------------------------------------------------------
# Every worker role; the Opus model is the criticality file's
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role,cls", [(s.ENGINEER, "C2"), (s.TEST_DESIGNER, "C1"), (s.AUDITOR, "C1"),
                                      (s.PRODUCT_SPEC, "C0"), (s.RESEARCH, "C1")])
def test_s5_a_promotion_applies_to_every_worker_role_at_the_table_s_effort(project, launch, role, cls):
    tk = s.ticket(project, role, cls)
    record = s.promote_two_failed(project, tk)
    s.assert_session(launch(role, tk), s.OPUS, s.TABLES[role][cls][1], criticality=cls,
                     promotion={"reason": "two failed reviews", "record": record}, **PROMOTED)


def test_s5_the_promoted_model_is_the_one_the_criticality_file_names(project, launch, tk):
    s.write_criticality(project, s.crit_text(opus="claude-opus-9-9"))
    record = s.promote_two_failed(project, tk)
    s.assert_session(launch(ENG, tk), "claude-opus-9-9", "high", criticality="C2",
                     promotion={"reason": "two failed reviews", "record": record}, **PROMOTED)


def test_s5_a_ticket_already_on_opus_is_still_recorded_as_promoted(project, launch):
    tk = s.ticket(project, ENG, "C3")
    record = s.promote_two_failed(project, tk)
    s.assert_session(launch(ENG, tk), s.OPUS, "high", criticality="C3",
                     promotion={"reason": "two failed reviews", "record": record}, **PROMOTED)


def test_s5_with_no_criticality_file_two_failed_reviews_promote_nothing(project, launch, tk):
    """Interface 1.4 as amended: no file, no promotion (section 5 is off); the launch is as before W2-184. The earlier
    1.4 refused here, naming the file."""
    s.write_role(project, ENG, table=None)
    s.drop_criticality(project)
    s.promote_two_failed(project, tk)
    s.assert_session(launch(ENG, tk), *s.DEFAULT, criticality=None, model_source="role default",
                     effort_source="role default", promotion=None)


# --------------------------------------------------------------------------
# After a promotion: a lower model, a trial; the effort
# --------------------------------------------------------------------------

@pytest.mark.parametrize("given", [s.SONNET, s.HAIKU5, "opus"])
def test_s5_a_lower_model_after_the_double_dash_on_a_promoted_ticket_is_refused_naming_both(
        project, launch, tk, given):
    s.promote_two_failed(project, tk)
    s.refused(launch(ENG, tk, "--model", given), "--model", given, s.OPUS)


def test_s5_the_promoted_model_after_the_double_dash_is_accepted(project, launch, tk):
    record = s.promote_two_failed(project, tk)
    s.assert_session(launch(ENG, tk, "--model", s.OPUS), s.OPUS, "high", criticality="C2",
                     promotion={"reason": "two failed reviews", "record": record}, **PROMOTED)


def test_s5_an_effort_after_the_double_dash_applies_on_a_promoted_ticket_down_to_the_floor(project, launch, tk):
    record = s.promote_two_failed(project, tk)
    s.assert_session(launch(ENG, tk, "--effort", "xhigh"), s.OPUS, "xhigh", criticality="C2",
                     promotion={"reason": "two failed reviews", "record": record}, model_source="promotion",
                     effort_source="after --")
    s.refused(launch(ENG, tk, "--effort", "medium"), "effort", "medium", "high")


def test_s5_a_trial_is_refused_on_a_promoted_ticket(project, launch, tk):
    s.promote_two_failed(project, tk)
    s.plant_trial(project, "trial-1", tk=tk)
    s.refused(launch(ENG, tk, trial="trial-1"), "trial", "promot")


def test_s5_a_promoted_full_ticket_s_second_review_is_still_the_probe(project, launch):
    tk = s.ticket(project, ENG, "C2", "FULL", tk="DAEO-pr02")
    record = s.promote_two_failed(project, tk)
    promotion = {"reason": "two failed reviews", "record": record}
    s.assert_session(launch(AUD, tk), s.OPUS, "high", criticality="C2", promotion=promotion, review_round=1,
                     **PROMOTED)
    s.assert_session(launch(AUD, tk), s.OPUS, "max", criticality="C2", promotion=promotion, review_round=2,
                     model_source="promotion", effort_source="probe")


# --------------------------------------------------------------------------
# A probe record that cannot be read
# --------------------------------------------------------------------------

BAD_RECORDS = {
    "a-front-matter-that-is-not-yaml": "---\ntype: probe\njudgement: [fail\n---\n\n# Probe\n",
    "a-verdict-block-that-is-not-json": "---\ntype: probe\njudgement: pass\n---\n\n```verdict\nnot json at all\n```\n",
    "a-verdict-that-is-a-list": "---\ntype: probe\njudgement: pass\n---\n\n```verdict\n[1, 2]\n```\n",
    "a-verdict-whose-kpis-is-not-a-list": ("---\ntype: probe\njudgement: pass\n---\n\n"
                                           "```verdict\n{\"kpis\": \"fail\"}\n```\n"),
}


@pytest.mark.parametrize("case", sorted(BAD_RECORDS))
def test_s5_a_probe_record_that_cannot_be_read_refuses_the_launch_naming_the_file(project, launch, tk, case):
    s.plant_probe(project, tk, "09-garbled.md", raw=BAD_RECORDS[case])
    s.refused(launch(ENG, tk), "09-garbled.md")
