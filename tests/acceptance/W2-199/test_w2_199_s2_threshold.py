"""W2-199, success line 2 (RT-3, the start threshold comes from the machine).

``start_below`` = 0.6 x the detected CPUs and ``load_limit`` = the detected CPUs; ``gov dispatch limits`` prints both
with their rules and state.json carries them; ``GOV_HEAVY_START_BELOW`` (an absolute load) overrides ``start_below``.
The reading of the open output shape: ``gov dispatch limits --json``'s ``result`` holds ``start_below`` and
``load_limit`` in its ``limits`` object (``limits.derive`` gains the keys), as state.json's ``limits`` does; a key is
also accepted at the result's top or in ``admission``.
"""

from __future__ import annotations

import re

import pytest

import w2_199_support as s


@pytest.mark.parametrize("profile,start_below,load_limit", [(s.PROFILE_8, 4.8, 8), (s.PROFILE_32, 19.2, 32)],
                         ids=["8-cpus", "32-cpus"])
def test_s2_limits_json_gives_start_below_0_6_of_the_cpus_and_load_limit_the_cpus(make_box, profile, start_below,
                                                                                   load_limit):
    result = make_box(profile).limits()
    got_start, got_limit = s.value_of(result, "start_below"), s.value_of(result, "load_limit")
    assert s.close(got_start, start_below), (
        f"start_below is {got_start!r}, not {start_below}: {result}")
    assert got_limit == load_limit, f"load_limit is {got_limit!r}, not {load_limit}: {result}"


def test_s2_the_text_form_prints_start_below_load_limit_and_margin_with_their_rules(box):
    done = box.gov("dispatch", "limits")
    assert done.returncode == 0, s.said(done)
    for key, want in (("start_below", r"(?<![\d.])12(?:\.0+)?(?![\d.])"), ("load_limit", r"(?<![\d.])20(?![\d.])"),
                      ("margin", r"(?<![\d.])1(?:\.0+)?(?![\d.])")):
        lines = [line for line in done.stdout.splitlines() if key in line]
        assert any(re.search(want, line) for line in lines), f"no line names {key} with its value\n{s.said(done)}"
    assert "0.6" in done.stdout, f"the start_below rule (0.6 x CPUs) is not printed\n{s.said(done)}"


def test_s2_state_json_carries_both_limits_and_follows_the_planted_machine(make_box):
    box = make_box(s.PROFILE_8)
    box.run_pass()
    state = box.state()
    assert s.close(s.value_of(state, "start_below"), 4.8), f"state.json start_below: {state.get('limits')}"
    assert s.value_of(state, "load_limit") == 8, f"state.json load_limit: {state.get('limits')}"
    box.profile(s.PROFILE_32)
    box.run_pass()
    state = box.state()
    assert s.close(s.value_of(state, "start_below"), 19.2), f"state.json start_below: {state.get('limits')}"
    assert s.value_of(state, "load_limit") == 32, f"state.json load_limit: {state.get('limits')}"


def test_s2_the_override_sets_start_below_and_a_load_of_6_holds_where_the_default_does_not(make_box):
    box = make_box(s.PROFILE_32, heavy_slots=None)
    overridden = box.limits(extra_env={"GOV_HEAVY_START_BELOW": "5"})
    assert s.value_of(overridden, "start_below") == 5, f"with GOV_HEAVY_START_BELOW=5: {overridden}"
    assert s.value_of(overridden, "load_limit") == 32
    box.load(6.0)
    free = box.start("default", hold=False)  # 6 < 19.2: no hold
    free.must_start(3.0)
    assert free.finish(timeout=10)[0] == 0
    held = box.start("override", hold=False, extra_env={"GOV_HEAVY_START_BELOW": "5"})
    assert held.held_for(2.0), "load 6 is over the overridden start_below of 5: the start is held"
    box.load(3.0)
    held.must_start(3.0)
    assert held.finish(timeout=10)[0] == 0
