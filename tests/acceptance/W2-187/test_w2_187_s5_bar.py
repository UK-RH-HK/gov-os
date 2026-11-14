"""S5: the bar at 95 % (Interface I5).

``declare.bar(n)`` gives ``need_right = ceil(95 n / 100)``, ``max_wrong = floor(5 n / 100)`` and ``target_right = need_right`` (on
80 judged that is 76, on 79 it is 76, on 40 it is 38); a verdict passes when right end to end at A2 reaches ``need_right``.
``declare.ROUNDING`` says the bar applies to standing and fresh runs alike. The figures are computed in a child process that
imports the tool, never by the suite's own formula alone (the revised W2-170 helper ``bar``, read by W2-88's S15 case, is
compared with the same table: it returns the Interface's dict key for key).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

import pytest

import w2_187_world as W

TABLE = {20: (19, 1), 36: (35, 1), 37: (36, 1), 40: (38, 2), 69: (66, 3), 70: (67, 3), 77: (74, 3), 79: (76, 3),
         80: (76, 4), 100: (95, 5)}
ROUNDING = ("need_right = ceil(95 n / 100); max_wrong = floor(5 n / 100); target_right = need_right; integer arithmetic; "
            "standing and fresh runs alike (DEC-1179 (2))")


def child(code: str) -> str:
    done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120,
                          env={"PYTHONPATH": str(W.SRC), "PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"})
    assert done.returncode == 0, done.stderr[-800:]
    return done.stdout


@pytest.mark.parametrize("n,expected", sorted(TABLE.items()))
def test_s5_declare_bar_gives_the_95_percent_figures(n, expected):
    got = json.loads(child(f"import json; from gov.memaudit import declare; print(json.dumps(declare.bar({n})))"))
    need, wrong = expected
    assert got == {"need_right": need, "max_wrong": wrong, "target_right": need}, got


def test_s5_the_rounding_text_names_standing_and_fresh_runs_alike():
    assert child("from gov.memaudit import declare; print(declare.ROUNDING)").strip() == ROUNDING


def test_s5_the_revised_w2_170_helper_returns_the_interfaces_dict_key_for_key():
    """W2-88's S15 case reads ``V.bar`` of W2-170's world and passes unedited when the helper is the Interface's dict."""
    sys.path.insert(0, str(W.ACCEPT / "W2-170"))
    import w2_170_world as V
    for n, (need, wrong) in TABLE.items():
        assert V.bar(n) == {"need_right": need, "max_wrong": wrong, "target_right": need}
    assert V.ROUNDING == ROUNDING
    assert W.W171.bar(80) == V.bar(80)


def test_s5_right_at_need_right_passes_and_one_below_is_a_miss_in_a_planted_run(ran_std):
    passed, ok = ran_std("pass76")
    missed, bad = ran_std("five")
    assert ok.code == 0 and bad.code == 0, (ok, bad)
    assert (W.StdExpected(passed.sc).right, W.StdExpected(missed.sc).right) == (76, 75), "the planted boundary"
    fig = passed.std_json("FIGURES.json")
    assert fig["verdict"]["right"] == 76 and fig["verdict"]["right_ok"] is True and fig["verdict"]["passes"] is True
    assert ok.lines[-1] == f"STANDING {passed.week} right 76 of 80: passes"
    miss = missed.std_json("FIGURES.json")
    assert miss["verdict"]["right"] == 75 and miss["verdict"]["right_ok"] is False and miss["verdict"]["passes"] is False
    assert bad.lines[-1] == f"STANDING {missed.week} right 75 of 80: misses"
    assert passed.std_json("DECLARATION.json")["bar"] == fig["bar"] == {"need_right": 76, "max_wrong": 4, "target_right": 76}


def test_s5_the_standing_digests_verdict_line_prints_the_new_figure(ran_std):
    world, run = ran_std("pass76")
    assert run.code == 0, run
    line = W.digest_line(world.std_digest_lines(), "VERDICT")
    assert re.fullmatch(r"VERDICT right 76 of 80; wrong \d+; not found \d+; bar 76 right: passes", line), line


def test_s5_a_fresh_audits_digest_prints_the_same_bar_at_n_40(ran_fresh):
    world, run = ran_fresh("not_yet")
    assert run.code == 0, run
    verdict = world.digest()[2]
    m = re.fullmatch(r"VERDICT right (\d+) of (\d+); wrong (\d+); exact .*; bar (\d+) right, (\d+) wrong: (passes|misses)",
                     verdict)
    assert m and (m[2], m[4], m[5]) == ("40", "38", "2"), verdict
    assert world.figures()["bar"] == {"need_right": 38, "max_wrong": 2, "target_right": 38}
    assert world.json_of("DECLARATION.json")["rounding"] == ROUNDING, "a fresh run's declaration says it too"
