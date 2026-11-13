"""S9 and F1, judged on the record (README, "What the record judges").

- S9 (re-worded by DEC-1097 (1)(d), DEC-1129 (1); ``Rewrite-Reason: DEC-1129 (1)``): K9's memory line, judged once on
  the declared configuration, by the figure right end to end (at least 85 %, target 95 %) and the wrong claims (at
  most 5 %); below the bar, the memory audit brings it to the owner; hit@5 is reported beside, never judged. Judged
  on the fresh 80: 78 of 79 right, 0 wrong claims, hit@5 67 of 79 [FRESH-80-RESULT, DEC-1098 (1)].
- F1: an improvement that lowers any baseline figure of W2-15a beyond its noise band is reverted.

Neither is behaviour of W2-32's code. These cases check what a test can: the baseline record holds both figures
against their bars, over repeated runs that give a noise band; the rules as ``w2_32_record`` states them; and the
ticket's evidence file states S9's and F1's outcome. The verdict on the rounds is the reviewer's, with
``w2_32_record.py`` run on the CTO's records.

The records are read from ``W2_32_RUNS`` (default ``~/gov-os-runs/D4B``), measure 1 under ``m1/records``. Only the
records' totals and top-level fields are read: never a question's text (the hidden half's are not in them).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

import w2_32_record as r
import w2_32_support as s

RUNS = Path(os.environ.get("W2_32_RUNS") or "~/gov-os-runs/D4B").expanduser()
BASELINE = RUNS / "m1" / "records"
EVIDENCE = s.ROOT / "docs" / "changes" / "W2-32-evidence.md"


@pytest.fixture
def baseline():
    records = r.baseline_records(BASELINE) if BASELINE.is_dir() else []
    if not records:
        pytest.skip(f"no baseline measure record under {BASELINE} (set W2_32_RUNS)")
    return records


def test_the_baseline_record_holds_both_figures_against_their_bars(baseline):
    for record in baseline:
        assert r.form_problems(record) == [], r.form_problems(record)
        assert record["set"] == "memory-retrieval" and record["part"] == "all", (record["set"], record["part"])


def test_the_baseline_was_run_more_than_once_on_one_commit_so_it_has_a_noise_band(baseline):
    assert len(baseline) >= 2, "a noise band needs at least two runs of the baseline"
    assert len({(record["commit"], record["set"], record["part"]) for record in baseline}) == 1, \
        "the baseline's runs measure one commit, set and part"
    for figure in r.FIGURES:
        low, high = r.noise_band(baseline, figure)
        assert 0 <= low <= high <= r.QUESTIONS


@pytest.mark.parametrize("band, count, verdict", [
    ((28, 28), 28, "keep"), ((28, 28), 27, "revert"), ((26, 29), 26, "keep"), ((26, 29), 25, "revert"),
    ((26, 29), 35, "keep")])
def test_f1_reverts_a_round_below_the_baselines_noise_band(band, count, verdict):
    assert r.f1_verdict(band, count) == verdict


# Rewrite-Reason: DEC-1129 (1): S9 is the end-to-end figure (bar 85 %, wrong claims at most 5 %, target 95 %), judged once
@pytest.mark.parametrize("right, wrong, state", [
    (84.9, 0.0, "owner told"), (85.0, 5.0, "met, under target"), (85.0, 5.1, "owner told"),
    (94.9, 0.0, "met, under target"), (95.0, 0.0, "met"), (98.7, 0.0, "met")])
def test_s9_is_met_at_85_end_to_end_with_wrong_claims_at_most_5_and_at_target_from_95(right, wrong, state):
    assert r.s9_state(right, wrong) == state


# Rewrite-Reason: DEC-1129 (1): the same rule on counts of the fresh 80's 79 questions
@pytest.mark.parametrize("right, wrong, state", [
    (67, 0, "owner told"), (68, 3, "met, under target"), (68, 4, "owner told"), (75, 0, "met, under target"),
    (76, 0, "met"), (78, 0, "met")])
def test_s9_on_79_questions_68_right_and_3_wrong_is_the_bar_and_76_the_target(right, wrong, state):
    assert r.s9_report(right, wrong, hit_at_5=67, of=79)["state"] == state


# Rewrite-Reason: DEC-1129 (1): hit@5 is carried beside the figure, reported and never judged
@pytest.mark.parametrize("hit_at_5", [0, 67, 79])
def test_s9_reports_hit_at_5_beside_the_end_to_end_figure_and_never_judges_it(hit_at_5):
    report = r.s9_report(78, 0, hit_at_5=hit_at_5, of=79)
    assert report["state"] == "met"
    assert report["hit_at_5"] == pytest.approx(100.0 * hit_at_5 / 79)
    assert report["end_to_end"] == pytest.approx(98.7, abs=0.05) and report["wrong_claims"] == 0


# Rewrite-Reason: DEC-1129 (1): the evidence row carries the end-to-end figure, the wrong claims, hit@5 beside, FRESH-80-RESULT
def test_the_evidence_file_states_s9s_and_f1s_outcome():
    assert EVIDENCE.is_file(), f"no evidence file at {EVIDENCE.relative_to(s.ROOT)} (D4B-MEMORY-STAGE: one row per " \
                               f"KPI line, how it is verified, the command and the result)"
    lines = EVIDENCE.read_text(encoding="utf-8").splitlines()
    s9 = [line for line in lines if re.search(r"\bS9\b", line)]
    f1 = [line for line in lines if re.search(r"\bF1\b", line)]
    assert any(re.search(r"\b78 of 79\b|\b98\.7 ?%", line) and re.search(r"end[ -]to[ -]end", line, re.I) for line in s9), \
        "S9's row gives the end-to-end figure of the fresh 80 (78 of 79, or 98.7 %), named end to end"
    assert any(re.search(r"\b0 wrong claims?\b|wrong claims?:? 0\b", line) for line in s9), \
        "S9's row gives the wrong claims (0)"
    assert any(re.search(r"hit@5\s+(\d+ of 79|\d+(\.\d+)? ?%)", line) for line in s9), \
        "S9's row gives hit@5 beside the end-to-end figure (n of 79, or a percentage)"
    assert any("FRESH-80-RESULT" in line for line in s9), "S9's row names FRESH-80-RESULT"
    assert f1 and any("noise band" in line.lower() for line in f1), "F1's row names the noise band each round is " \
                                                                     "judged against"
