"""Fix MR-2 (DEC-1246 (3)(b)): criticality no longer varies the model.

``criticality.yaml`` has no ``opus:`` key and ``gov.launch.criticality.load`` refuses a file that has one; the launcher's
promotion (probe-record verdicts) and probe (second review round on Opus) are retired; a C3 ticket launches Sonnet, high;
an explicit request for Opus (``--trial`` naming it, a caller's ``--model claude-opus-*``) is refused as any other
non-Sonnet model. Criticality still gives the class. Reading: a review round of two or more launches (no refusal for a
repeated setting, which the probe's max used to avoid) on the table's setting, as the ticket's verify says "launch
Sonnet, not max".
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

import w2_201_mr_support as m
import w2_201_support as k

s, b = k.s, k.b
GOOD = {"version": 1, "default": "C2", "rules": []}


def _records(sandbox):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(sandbox.records).glob("*.json"))]


def _ready(project):
    m.crit_without_opus(project)
    m.write_table(project)
    k.plant_real_role(project, k.QA)


def _sonnet_high(result, cls):
    b.assert_launched(result)
    assert {"--model": result.values("--model"), "--effort": result.values("--effort")} == {
        "--model": [m.SONNET], "--effort": ["high"]}, f"the launch line is\n{result.args}"
    record = result.record()
    assert record["criticality"] == cls and record["model"] == m.SONNET and record["effort"] == "high", record
    assert record["model_source"] not in ("promotion", "probe") and record.get("promotion") is None
    return record


# --------------------------------------------------------------------------------------------------------------------
# The file and its reader
# --------------------------------------------------------------------------------------------------------------------

def test_mr2_the_real_criticality_file_has_no_opus_key_and_still_loads():
    """Red on the base: the file carries ``opus: claude-opus-5-5``."""
    from gov.launch import criticality
    data = yaml.safe_load((m.REPO / s.CRITICALITY_REL).read_text(encoding="utf-8"))
    assert "opus" not in data, "criticality.yaml still has an `opus:` key"
    assert set(criticality.load(m.REPO)) == {"version", "default", "rules"}


def test_mr2_load_accepts_version_default_rules_only(tmp_path):
    """Red on the base: ``load`` demands the ``opus`` key."""
    from gov.launch import criticality
    b.write(tmp_path / s.CRITICALITY_REL, yaml.safe_dump(GOOD))
    assert set(criticality.load(tmp_path)) == {"version", "default", "rules"}


@pytest.mark.parametrize("value", ["claude-opus-5-5", "opus", "claude-sonnet-5-5"])
def test_mr2_load_refuses_a_file_that_still_carries_opus_naming_the_key(tmp_path, value):
    """Red on the base: ``load`` requires the key; the refusal after the change names it as the cause."""
    from gov.cli.errors import GovError
    from gov.launch import criticality
    b.write(tmp_path / s.CRITICALITY_REL, yaml.safe_dump({**GOOD, "opus": value}))
    b.write(tmp_path / "ok" / s.CRITICALITY_REL, yaml.safe_dump(GOOD))
    assert set(criticality.load(tmp_path / "ok")) == set(GOOD)
    with pytest.raises(GovError) as caught:
        criticality.load(tmp_path)
    assert caught.value.code == "LAUNCH_REFUSED" and "opus" in str(caught.value).lower()


# --------------------------------------------------------------------------------------------------------------------
# A C3 ticket, a planted probe record and a review round change neither model nor effort
# --------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("role", [k.ENGINEER, k.TEST_DESIGNER, k.QA])
def test_mr2_a_c3_ticket_launches_its_worker_on_sonnet_high(project, launch, role):
    """Red on the base: the criticality file in its new form (no ``opus``) is refused."""
    _ready(project)
    tk = s.ticket(project, k.ENGINEER, "C3")
    _sonnet_high(launch(role, tk), "C3")


@pytest.mark.parametrize("kind", ["two-failed", "fail-open"])
@pytest.mark.parametrize("role", [k.ENGINEER, k.TEST_DESIGNER, k.AUDITOR])
def test_mr2_a_planted_probe_record_with_a_promoting_verdict_changes_neither_model_nor_effort(
        sandbox, project, launch, role, kind):
    """Red on the base: the new-form file is refused (and the old launcher promoted)."""
    _ready(project)
    tk = s.ticket(project, k.ENGINEER, "C2")
    if kind == "two-failed":
        s.promote_two_failed(project, tk)
    else:
        s.plant_probe(project, tk, "00-open.md", "fail", verdict=s.verdict_block("fails open"))
    _sonnet_high(launch(role, tk), "C2")
    assert not [r for r in _records(sandbox) if r.get("model_source") in ("promotion", "probe")]


def test_mr2_a_ticket_in_review_round_two_launches_sonnet_not_max(sandbox, project, launch):
    """Red on the base: the new-form file is refused (and the old launcher's round 2 was Opus max). Round 1 runs on
    ``--effort xhigh`` so that round 2 repeats no setting, whichever rule on repeats stays."""
    _ready(project)
    tk = s.ticket(project, k.ENGINEER, "C2", "FULL")
    first = launch(k.AUDITOR, tk, "--effort", "xhigh")
    b.assert_launched(first)
    record = _sonnet_high(launch(k.AUDITOR, tk), "C2")
    assert record["effort_source"] != "probe"
    assert not [r for r in _records(sandbox) if r.get("model_source") in ("promotion", "probe")
                or r.get("effort_source") == "probe" or r.get("effort") == "max"]


def test_mr2_no_launch_record_holds_a_promotion_or_probe_source_after_a_mixed_run(sandbox, project, launch):
    """Failure line. Red on the base: the launches are refused."""
    _ready(project)
    tk = s.ticket(project, k.ENGINEER, "C3", "FULL")
    s.promote_two_failed(project, tk)
    first = launch(k.AUDITOR, tk, "--effort", "xhigh")
    b.assert_launched(first)
    for role in (k.ENGINEER, k.AUDITOR):
        _sonnet_high(launch(role, tk), "C3")
    records = _records(sandbox)
    assert len(records) == 3
    assert not [r for r in records if "promotion" in (r.get("model_source"), r.get("effort_source"))
                or "probe" in (r.get("model_source"), r.get("effort_source"))]


# --------------------------------------------------------------------------------------------------------------------
# An explicit request for Opus is refused as any other non-Sonnet model
# --------------------------------------------------------------------------------------------------------------------

def test_mr2_a_trial_naming_opus_with_no_exceptions_entry_is_refused(project, launch):
    """Red on the base: the plain launch of the control step is refused (new-form file)."""
    _ready(project)
    tk = s.ticket(project, k.ENGINEER, "C2")
    _sonnet_high(launch(k.ENGINEER, tk), "C2")
    s.plant_trial(project, "trial-opus", tk=tk, model=m.OPUS)
    result = launch(k.ENGINEER, tk, trial="trial-opus")
    s.refused(result)
    assert "opus" in b.said(result).lower()


@pytest.mark.parametrize("model", ["claude-opus-5-5", "claude-opus-5-6"])
def test_mr2_a_callers_opus_model_after_the_double_dash_is_refused(project, launch, model):
    """Red on the base: the plain launch of the control step is refused (new-form file)."""
    _ready(project)
    tk = s.ticket(project, k.ENGINEER, "C2")
    _sonnet_high(launch(k.ENGINEER, tk), "C2")
    result = launch(k.ENGINEER, tk, "--model", model)
    s.refused(result, model)
