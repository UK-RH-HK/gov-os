"""W2-184, KPI success 4 -- RETIRED: the probe (a second review round on Opus at max) no longer exists (fix MR-2 under
W2-201, DEC-1246 (3)(b)).

Rewrite-Reason: DEC-1246 (3)(b): MR-2: the launcher's probe and its same-setting refusal are retired with criticality's
`opus` key. Every review round of an auditor launches the table's setting (Sonnet, high here), no round is `max`, no
record holds `probe`; a ``max`` effort still needs ``--reason`` as on any launch. Reading (the review round and the
same-setting refusal are not named by MR-2; the ticket's verify "a ticket in review round 2 launches Sonnet, not max"
needs the second launch accepted): round 2 on a setting other than round 1's is accepted; whether a repeated setting still
needs the owner is left to the round limit (W2-184 r1_rows F2) and is not pinned here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w2_184_support as s

AUD, ENG = s.AUDITOR, s.ENGINEER
FULL = "DAEO-rv01"


@pytest.fixture()
def full(project):
    s.write_criticality(project)
    return s.ticket(project, ENG, "C2", "FULL", tk=FULL)


def _first_on_xhigh(launch):
    """Round 1, given ``--effort xhigh`` after ``--``: a setting round 2 does not repeat (so a same-setting rule, if one
    stays, does not refuse round 2)."""
    result = launch(AUD, FULL, "--effort", "xhigh")
    s.assert_session(result, s.SONNET, "xhigh", criticality="C2", model_source="by criticality",
                     effort_source="after --", review_round=1)


def _second(launch):
    result = launch(AUD, FULL)
    s.assert_session(result, s.SONNET, "high", criticality="C2", model_source="by criticality",
                     effort_source="by criticality", review_round=2)
    return result


def test_s4_the_second_review_round_launches_the_table_s_sonnet_high_not_the_probe(full, launch):
    _first_on_xhigh(launch)
    _second(launch)


def test_s4_no_launch_record_names_a_probe_or_holds_max(sandbox, full, launch):
    _first_on_xhigh(launch)
    _second(launch)
    for path in Path(sandbox.records).glob("*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        assert record.get("effort") != "max" and "probe" not in (record.get("model_source"), record.get("effort_source"))


@pytest.mark.parametrize("profile", ["STANDARD", "LITE"])
def test_s4_a_ticket_that_is_not_full_launches_the_same_every_time(project, launch, profile):
    s.write_criticality(project)
    tk = s.ticket(project, ENG, "C2", profile, tk="DAEO-rv02")
    for effort in ("xhigh", "high"):
        s.assert_session(launch(AUD, tk, "--effort", effort), s.SONNET, effort, criticality="C2",
                         model_source="by criticality", effort_source="after --")  # Rewrite-Reason: DEC-1246 (3)(b): MR-2: an --effort equal to the table's is `after --`


def test_s4_max_on_any_review_still_needs_a_reason(full, launch):
    s.refused(launch(AUD, FULL, "--effort", "max"), "max", "reason")
