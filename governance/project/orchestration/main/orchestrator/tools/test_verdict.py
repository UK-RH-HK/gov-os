import json
from verdict import ready


def rec(kpis):
    return "probe\n```verdict\n" + json.dumps({"kpis": kpis}) + "\n```\n"


def test_no_block_is_none():
    assert ready("judgement: pass") == (None, [])


def test_out_of_scope_and_other_findings_do_not_block():
    ok, why = ready(rec([{"kpi": "S1", "verdict": "fail", "findings": [
        {"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"},
        {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]))
    assert ok and why == []


def test_an_in_scope_ordinary_fail_open_blocks():
    ok, why = ready(rec([{"kpi": "S2", "verdict": "fail", "findings": [
        {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"}]}]))
    assert not ok and "F2 blocks" in why[0]


def test_malformed_blocks():
    assert ready("```verdict\nnot json\n```")[0] is False
    assert ready(rec([{"kpi": "S1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in"}]}]))[0] is False
    assert ready(rec([]))[0] is False
