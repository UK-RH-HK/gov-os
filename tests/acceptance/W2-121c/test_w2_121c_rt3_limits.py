"""W2-121c, RT-3 slots from the machine detected at the pass, and the GPU never spills (success lines 8 and 9).

Line 8 (RT-3a): ``gov dispatch limits`` prints the detected CPUs, RAM and GPU memory and each derived limit with its
rule; each watch pass writes the same into state.json. The rules (the ticket's, computed here exactly):

- ``heavy_slots`` = max(1, min(floor(0.1 x CPUs), floor(0.5 x RAM / verification peak) when gate.json has one))
- ``workers_per_slot`` = max(1, floor((load_limit - start_below) / (margin x heavy_slots))) with ``start_below`` = 0.6 x CPUs,
  ``load_limit`` = the CPUs and ``margin`` 1.0 with no runtime log (W2-199, DAEO-rt2s, success line 3 replaced slice 1's
  ``0.15`` and ``0.9`` formulas for these two keys)
- ``sessions_max`` = max(1, min(floor(0.5 x CPUs), floor(0.6 x RAM / working size) when gate.json has one))
- ``gpu_budget_mib`` = floor(0.875 x the GPU's total MiB), 0 with no GPU

Line 9 (RT-3b): ``gov dispatch limits --gpu-need-mib <n>`` answers ``admit`` (exit 0) only when a GPU is present and
its used MiB plus ``n`` stays within ``gpu_budget_mib``, else ``wait`` with the reason (exit 3); never the CPU; with no
GPU the answer is ``refuse`` (exit 3), saying embedding and reranking jobs are refused and memory is unavailable
(amended c82d31a56, the owner's working assumption T3 (a)).

The test designer's reading of the open output shape: ``gov dispatch limits --json``'s ``result`` holds ``machine``
and ``limits`` objects with the Interface's keys, the shape state.json gives them.
"""

from __future__ import annotations

import math
import re
from fractions import Fraction as F

import pytest

import w2_121c_support as s

KEYS = ("heavy_slots", "workers_per_slot", "sessions_max", "gpu_budget_mib")


def expected(profile, peak=None, working=None, gpu=True) -> dict:
    cpus, ram = profile["cpus"], profile["ram"]
    heavy = math.floor(F(1, 10) * cpus)
    if peak:
        heavy = min(heavy, math.floor(F(1, 2) * ram / peak))
    heavy = max(1, heavy)
    sessions = math.floor(F(1, 2) * cpus)
    if working:
        sessions = min(sessions, math.floor(F(6, 10) * ram / working))
    return {"heavy_slots": heavy, "workers_per_slot": max(1, math.floor((cpus - F(6, 10) * cpus) / heavy)),
            "sessions_max": max(1, sessions),
            "gpu_budget_mib": math.floor(F(875, 1000) * profile["gpu_total"]) if gpu else 0}


def limits_of(result) -> dict:
    limits = result.get("limits") if isinstance(result, dict) else None
    assert isinstance(limits, dict), f"no limits object in the result: {result}"
    return {key: limits.get(key, "<missing>") for key in KEYS}


# --------------------------------------------------------------------------
# Line 8 (RT-3a)
# --------------------------------------------------------------------------

def test_rt3a_each_limit_follows_its_rule_on_two_planted_profiles_and_three_differ(box):
    found = {}
    for name, profile in (("A", s.PROFILE_A), ("B", s.PROFILE_B)):
        box.profile(profile, gpu_used=1000)
        result = box.ok("dispatch", "limits")
        machine = result.get("machine") or {}
        detected = {key: machine.get(key) for key in ("cpus", "ram_bytes", "gpu_total_mib")}
        assert detected == {"cpus": profile["cpus"], "ram_bytes": profile["ram"], "gpu_total_mib": profile["gpu_total"]}, (
            f"profile {name}: the detected machine is {detected}")
        assert machine.get("gpu_used_mib") == 1000, f"profile {name}: gpu_used_mib {machine.get('gpu_used_mib')!r}"
        found[name] = limits_of(result)
        assert found[name] == expected(profile), f"profile {name}: limits {found[name]}, rules {expected(profile)}"
    for key in ("heavy_slots", "sessions_max", "gpu_budget_mib"):
        assert found["A"][key] != found["B"][key], f"{key} is the same on both profiles: {found}"


def test_rt3a_the_text_form_names_the_machine_and_each_limit_with_its_value_and_rule(box):
    done = box.gov("dispatch", "limits")
    assert done.returncode == 0, s.said(done)
    want = expected(s.PROFILE_A)
    for key in KEYS:
        lines = [line for line in done.stdout.splitlines() if key in line]
        assert any(re.search(rf"(?<![\d.]){want[key]}(?![\d.])", line) for line in lines), (
            f"no line names {key} with its value {want[key]}\n{s.said(done)}")
    for ratio in ("0.1", "0.5", "0.875"):
        assert re.search(rf"(?<![\d.]){re.escape(ratio)}(?!\d)", done.stdout), (
            f"the rules are not printed (no ratio {ratio})\n{s.said(done)}")
    assert re.search(r"(?<!\d)32(?!\d)", done.stdout), f"the detected CPUs (32) are not printed\n{s.said(done)}"


def test_rt3a_changing_the_planted_profile_between_two_passes_changes_state_json_limits(box):
    box.profile(s.PROFILE_A)
    box.run_pass()
    assert limits_of(box.state()) == expected(s.PROFILE_A), f"state.json's limits on profile A: {box.state()}"
    box.profile(s.PROFILE_B)
    box.run_pass()
    assert limits_of(box.state()) == expected(s.PROFILE_B), f"state.json's limits on profile B: {box.state()}"
    assert box.state().get("machine", {}).get("cpus") == 8, f"state.json's machine: {box.state().get('machine')}"


@pytest.mark.parametrize("peak_gib,working_gib,binds", [(16, 8, True), (1, 1, False)],
                         ids=["ram-term-smaller-binds", "ram-term-larger-does-not-bind"])
def test_rt3a_a_measured_size_in_gate_json_binds_where_its_ram_term_is_smaller(box, peak_gib, working_gib, binds):
    box.profile(s.PROFILE_A)
    box.plant_gate(peak_gib * s.GIB, working_gib * s.GIB)
    want = expected(s.PROFILE_A, peak_gib * s.GIB, working_gib * s.GIB)
    assert (want != expected(s.PROFILE_A)) is binds  # the case's own premise: 2 and 4 against 4 and 16
    got = limits_of(box.ok("dispatch", "limits"))
    assert got == want, f"with a peak of {peak_gib} GiB and a working size of {working_gib} GiB: {got}, rules {want}"


def test_rt3a_with_no_gpu_the_budget_is_0(box):
    box.profile(s.PROFILE_A, gpu=False)
    got = limits_of(box.ok("dispatch", "limits"))
    assert got == expected(s.PROFILE_A, gpu=False), f"limits with no nvidia-smi: {got}"


# --------------------------------------------------------------------------
# Line 9 (RT-3b)
# --------------------------------------------------------------------------

BUDGET_A = expected(s.PROFILE_A)["gpu_budget_mib"]  # 21504 MiB of 24576
NEED = 4000


def _answer(box, need=NEED):
    done = box.gov("dispatch", "limits", "--gpu-need-mib", str(need))
    text = done.stdout + "\n" + done.stderr
    assert not s.cpu_offers(text), f"the answer offers the CPU as a place to run: {s.cpu_offers(text)}\n{s.said(done)}"
    return done, text


@pytest.mark.parametrize("used", [10_000, BUDGET_A - NEED], ids=["well-within", "exactly-the-budget"])
def test_rt3b_admit_exit_0_when_used_plus_need_stays_within_the_budget(box, used):
    box.profile(s.PROFILE_A, gpu_used=used)
    done, text = _answer(box)
    assert done.returncode == 0, f"used {used} + need {NEED} <= {BUDGET_A}: exit {done.returncode}, not 0\n" \
                                 f"{s.said(done)}"
    assert re.search(r"\badmit\b", text, re.I), f"the answer does not say admit\n{s.said(done)}"


@pytest.mark.parametrize("used", [BUDGET_A - NEED + 1, 20_000], ids=["one-mib-over", "well-over"])
def test_rt3b_wait_exit_3_with_the_reason_when_used_plus_need_exceeds_the_budget(box, used):
    box.profile(s.PROFILE_A, gpu_used=used)
    done, text = _answer(box)
    assert done.returncode == 3, f"used {used} + need {NEED} > {BUDGET_A}: exit {done.returncode}, not 3\n" \
                                 f"{s.said(done)}"
    assert re.search(r"\bwait\b", text, re.I), f"the answer does not say wait\n{s.said(done)}"
    assert re.search(r"budget|(?<!\d)21504(?!\d)", text.replace(",", ""), re.I), (
        f"the wait does not give its reason (the budget)\n{s.said(done)}")


def test_rt3b_with_no_gpu_the_answer_is_refuse_saying_memory_is_unavailable(box):
    box.profile(s.PROFILE_A, gpu=False)
    done, text = _answer(box, need=1)
    assert done.returncode == 3, f"with no nvidia-smi: exit {done.returncode}, not 3\n{s.said(done)}"
    assert re.search(r"\brefuse", text, re.I), f"the answer does not say refuse\n{s.said(done)}"
    assert not re.search(r"\badmit\b", text, re.I), f"the answer with no GPU says admit\n{s.said(done)}"
    assert re.search(r"memory[^.\n]{0,40}unavailable|unavailable[^.\n]{0,40}memory", text, re.I), (
        f"the refusal does not say memory is unavailable\n{s.said(done)}")
    assert re.search(r"embed", text, re.I) and re.search(r"rerank", text, re.I), (
        f"the refusal does not name the embedding and reranking jobs\n{s.said(done)}")
