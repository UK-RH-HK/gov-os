"""S9 and F1, judged on the record (README, "What the record judges").

- S9: if memory is below 85 % after two improvement rounds, the orchestrator escalates to the owner with the reasons;
  at the third the owner decides. At 85 % or above but under 95 %, with room for improvement found, memory is not
  closed: an escalation to the owner [DEC-954 Q9e, DEC-957].
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


@pytest.mark.parametrize("percents, room, state", [
    ([70.0], True, "next round"), ([70.0, 80.0], True, "owner decides"), ([84.9, 84.9], True, "owner decides"),
    ([85.4], True, "owner told: not closed"), ([90.0], False, "none"), ([95.8], True, "none")])
def test_s9_escalates_below_85_after_two_rounds_and_under_95_with_room(percents, room, state):
    assert r.s9_state(percents, room) == state


def test_the_evidence_file_states_s9s_and_f1s_outcome():
    assert EVIDENCE.is_file(), f"no evidence file at {EVIDENCE.relative_to(s.ROOT)} (D4B-MEMORY-STAGE: one row per " \
                               f"KPI line, how it is verified, the command and the result)"
    lines = EVIDENCE.read_text(encoding="utf-8").splitlines()
    s9 = [line for line in lines if re.search(r"\bS9\b", line)]
    f1 = [line for line in lines if re.search(r"\bF1\b", line)]
    assert s9 and any(re.search(r"\b\d{1,2} of 48\b|\b\d{1,3}(\.\d+)? ?%", line) for line in s9), \
        "S9's row gives the hit@5 reached after the rounds (n of 48, or a percentage)"
    assert f1 and any("noise band" in line.lower() for line in f1), "F1's row names the noise band each round is " \
                                                                     "judged against"
