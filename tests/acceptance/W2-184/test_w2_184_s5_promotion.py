"""W2-184, KPI success 5 -- RETIRED: promotion no longer exists (fix MR-2 under W2-201, DEC-1246 (3)(b)).

Rewrite-Reason: DEC-1246 (3)(b): MR-2: the launcher's promotion (two failed probe reviews or a fail-open finding) is
retired with criticality's `opus` key: planted probe records change neither the model nor the effort, no launch record
holds a promotion, and a model after ``--`` other than the table's is refused as any non-Sonnet model. What these cases
pinned before (a promotion with its reason and record, a refused ``--trial``) is now this: nothing happens.
"""

from __future__ import annotations

import pytest

import w2_184_support as s

ENG = s.ENGINEER
TK = "DAEO-pr01"


@pytest.fixture()
def tk(project):
    """An engineer ticket in C2: the table says Sonnet, high; the criticality file has no `opus` key."""
    s.write_criticality(project)
    return s.ticket(project, ENG, "C2", tk=TK)


def _unchanged(launch, tk, *args):
    return s.assert_session(launch(ENG, tk, *args), *s.TABLES[ENG]["C2"], criticality="C2",
                            model_source="by criticality", effort_source="by criticality")


@pytest.mark.parametrize("first,second", [("fail", "fail"), ("fail", "failed"), ("failed", "failed")])
def test_s5_two_failed_reviews_promote_nothing(project, launch, tk, first, second):
    s.plant_probe(project, tk, "01-review.md", first)
    s.plant_probe(project, tk, "02-review.md", second)
    _unchanged(launch, tk)


def test_s5_a_fail_open_finding_promotes_nothing(project, launch, tk):
    s.plant_probe(project, tk, "00-open.md", "fail", verdict=s.verdict_block("fails open"))
    _unchanged(launch, tk)


def test_s5_an_unreadable_probe_record_is_not_read_so_it_refuses_nothing(project, launch, tk):
    s.plant_probe(project, tk, "09-garbled.md", raw="---\ntype: probe\njudgement: [fail\n---\n")
    _unchanged(launch, tk)


@pytest.mark.parametrize("given", [s.OPUS, s.HAIKU5, "opus"])
def test_s5_a_model_after_the_double_dash_other_than_the_table_s_is_refused(project, launch, tk, given):
    _unchanged(launch, tk)
    s.refused(launch(ENG, tk, "--model", given), "--model", s.SONNET)
