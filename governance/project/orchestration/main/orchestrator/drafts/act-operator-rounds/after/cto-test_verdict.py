import json
from verdict import ready


def rec(kpis):
    return "probe\n```verdict\n" + json.dumps({"kpis": kpis}) + "\n```\n"


def test_no_block_is_none():
    assert ready("judgement: pass") == (None, [])


def test_out_of_scope_and_other_findings_do_not_block():
    ok, why = ready(rec([{"kpi": "S1", "verdict": "pass", "findings": [
        {"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"},
        {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]))
    assert ok and why == []


def test_an_in_scope_ordinary_fail_open_blocks():
    ok, why = ready(rec([{"kpi": "S2", "verdict": "fail", "findings": [
        {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"}]}]))
    assert not ok and any("F2 blocks" in w for w in why)


def test_the_last_block_decides_a_second_round():
    first = rec([{"kpi": "A", "verdict": "fail", "findings": [
        {"id": "A1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}])
    second = rec([{"kpi": "A", "verdict": "pass", "findings": [
        {"id": "A1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}])
    assert ready(first + "round 2\n" + second) == (True, [])
    assert ready(second + "round 2\n" + first)[0] is False


def test_malformed_blocks():
    assert ready("```verdict\nnot json\n```")[0] is False
    assert ready(rec([{"kpi": "S1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in"}]}]))[0] is False
    assert ready(rec([]))[0] is False


def test_a_kpi_line_marked_fail_blocks_with_no_finding_or_with_non_blocking_ones():
    """DEC-1131 (3): READY needs no KPI line marked fail."""
    ok, why = ready(rec([{"kpi": "S1", "verdict": "fail", "findings": []}]))
    assert ok is False and "S1" in why[0] and "marked fail" in why[0]
    ok, why = ready(rec([{"kpi": "S1", "verdict": "fail", "findings": [
        {"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}]))
    assert ok is False and "marked fail" in why[0]
    ok, why = ready(rec([{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "fail"}]))
    assert ok is False and why == ["S2: the KPI line is marked fail"]


def test_a_kpi_line_with_no_or_an_unknown_verdict_blocks_fail_closed():
    for v in ({"kpi": "S1", "findings": []}, {"kpi": "S1", "verdict": "partial"}, {"kpi": "S1", "verdict": "PASS"}):
        ok, why = ready(rec([v]))
        assert ok is False and "neither pass nor fail" in why[0]


def test_the_last_block_decides_when_a_later_round_clears_the_failed_line():
    failed = rec([{"kpi": "A", "verdict": "fail", "findings": []}])
    passed = rec([{"kpi": "A", "verdict": "pass", "findings": []}])
    assert ready(failed + "round 2\n" + passed) == (True, [])
    assert ready(passed + "round 2\n" + failed)[0] is False
