"""S3 (and F3's "a stopped audit's set measured later"): a stop is a stop (Interface items 2 and 5).

Any child exit other than 0 stops the cycle: ``STOPPED <step> <exit>`` is printed, ``COUNTS.json`` names the step and the
code (``stop`` and the last of ``steps``), the digest is written (``STOP <step> exit <code>``), nothing is appended to
``HISTORY.jsonl`` before ``USED``, and the run exits 2. Only a launch step's exit 16 (the canary) is run once more, with the
same command line; a second 16 stops. A stop before ``USED`` leaves the set unmeasured and the next audit (another date) a
new set; a stop after ``USED`` (here a measure fault, exit 2) is a line to the owner in the digest and the set is not run
again (no resume, no second ``measure``; ``HISTORY.jsonl`` gains ``measured: false, used: true``).

The USED boundary is read from the codes of item 5: ``measure`` exit 1 (a ``DC-`` refusal) is before USED, exit 2 after.
"""

from __future__ import annotations

import pytest

import w2_172_checks as C
import w2_172_world as W
from w2_172_digest import by_word
from w2_172_world import S171

REVISION = {"checker-1": [{"revise": ["q05"]}]}


def stopped(world, run, step, code, *, used=False):
    assert run.code == 2, run
    assert f"STOPPED {step} {code}" in run.lines, run.out
    assert W.step_names(run)[-1] == step, W.step_names(run)
    counts = world.counts()
    assert counts["stop"] == {"step": step, "exit": code, "used": used}, counts
    assert counts["steps"][-1]["step"] == step and counts["steps"][-1]["exit"] == code, counts["steps"]
    words = by_word(world.digest(), strict=False)
    assert words["STOP"].group(0) == f"STOP {step} exit {code}", world.digest()
    assert run.lines[-12:] == world.digest(), "the digest is printed, line by line"
    return words


@pytest.mark.parametrize("step,code", [("writer-1", 10), ("writer-1", 20), ("writer-1", 21), ("writer-1", 22),
                                       ("checker-1", 20), ("writer-2", 21), ("checker-2", 22)])
def test_s3_a_launch_exit_other_than_0_or_16_stops_the_cycle_with_one_call_and_no_retry(make_world, step, code):
    world = make_world()
    world.plan_launch({**REVISION, step: [{"exit": code}]})
    run = world.go()
    words = stopped(world, run, step, code)
    assert [c["step"] for c in world.stub_calls()].count(step) == 1, "no retry of a code that is not 16"
    assert words["OWNER"]["word"] == "OWNER none", "a stop before USED is no line to the owner"
    assert world.counts()["steps"][-1].get("retried") in (False, None)
    assert world.history() == [], "nothing is appended to HISTORY.jsonl before USED"
    assert not (world.run_dir / "USED").exists() and not (world.run_dir / "DECLARATION.json").exists()
    assert "measure" not in W.step_names(run)


def test_s3_exit_16_then_0_goes_on_with_the_same_command_line(make_world):
    world = make_world()
    world.plan_launch({"writer-1": [{"exit": 16}, {"exit": 0}], "checker-1": [{"exit": 10}]})
    run = world.go()
    stopped(world, run, "checker-1", 10)
    calls = [c for c in world.stub_calls() if c["step"] == "writer-1"]
    assert len(calls) == 2 and calls[0]["argv"] == calls[1]["argv"], calls
    first = [s for s in world.counts()["steps"] if s["step"] == "writer-1"]
    assert first and first[-1]["exit"] == 0 and first[-1]["retried"] is True, world.counts()["steps"]
    assert (world.set_dir / "hidden").is_dir(), "the second call delivered the set; the cycle went on"
    names = W.step_names(run)
    assert [n for i, n in enumerate(names) if i == 0 or names[i - 1] != n] == ["writer-1", "preflight", "checker-1"], names


def test_s3_exit_16_twice_stops_after_exactly_two_calls(make_world):
    world = make_world()
    world.plan_launch({"writer-1": [{"exit": 16}, {"exit": 16}, {"exit": 0}]})
    run = world.go()
    stopped(world, run, "writer-1", 16)
    assert len([c for c in world.stub_calls() if c["step"] == "writer-1"]) == 2
    assert world.counts()["steps"][-1]["retried"] is True
    assert "preflight" not in W.step_names(run)


def test_s3_exit_16_at_a_later_launch_is_retried_too(make_world):
    world = make_world()
    world.plan_launch({"checker-1": [{"exit": 16}, {"exit": 16}]})
    run = world.go()
    stopped(world, run, "checker-1", 16)
    assert len([c for c in world.stub_calls() if c["step"] == "checker-1"]) == 2


# -- the stops that are not a launch's code -----------------------------------------------------------------------------
def test_s3_a_preflight_that_refuses_is_a_stop_at_preflight_with_its_exit_1(make_world):
    world = make_world()
    world.plan_launch({"writer-1": [{"remove": ["q01", "q02", "q03", "q04", "q05"]}]})  # 35 questions: PF-COUNT
    run = world.go()
    stopped(world, run, "preflight", 1)
    assert [c["step"] for c in world.stub_calls()] == ["writer-1"]
    assert not (world.run_dir / "USED").exists() and world.history() == []


def test_s3_a_void_audit_is_a_stop_at_void_with_its_exit_2(make_world):
    world = make_world()
    world.plan_launch({"checker-1": [{"reject": ["q01", "q02", "q03", "q04", "q05"], "revise_n": 0,
                                      "rejected_n": 0}]})  # 35 kept: VOID-COUNT
    run = world.go()
    words = stopped(world, run, "void", 2)
    assert words["OWNER"]["word"] == "OWNER none", "void comes before USED: no line to the owner"
    assert not (world.run_dir / "USED").exists() and world.history() == []


def test_s3_a_measure_refused_before_usd_is_a_stop_before_used(make_world):
    """``measure`` exit 1 (W2-170's ``DC-STORE``: the store's head is not the audit commit) comes before ``declare``
    writes USED: the set stays unmeasured, no line to the owner."""
    world = make_world()
    world.make_link(head="0" * 40)
    world.plan_launch({})
    S171.SCENARIOS["clean"].install(world)
    run = world.go()
    words = stopped(world, run, "measure", 1)
    assert words["OWNER"]["word"] == "OWNER none"
    assert not (world.run_dir / "USED").exists(), "declare refused before USED"
    assert world.history() == []
    assert "judge" not in W.step_names(run)


def fault_twice(gov, docs):
    gov[docs["q12"]["question"]]["by_occ"] = {"1": {"fault": "rerank"}, "2": {"fault": "rerank"}}


def test_s3_a_fault_after_used_is_a_line_to_the_owner_and_the_set_is_not_run_again(make_world):
    """Two degraded attempts: ``measure`` exits 2 after USED (W2-171 item 2). The digest holds the owner line, HISTORY
    gains ``measured: false, used: true``, no later step runs, and a second run on that date (with ``--force`` past the
    5-day refusal) is ``RN-NAME``: the set is never measured twice."""
    world = make_world()
    S171.SCENARIOS["five"].install(world, gov_edit=fault_twice)
    run = world.go(gate=world.gate_stub)
    words = stopped(world, run, "measure", 2, used=True)
    assert words["OWNER"].group(0) == "OWNER stopped after USED at measure exit 2: the set is not run again"
    assert (world.run_dir / "USED").is_file()
    assert [x for x in W.step_names(run)].count("measure") == 1
    assert "judge" not in W.step_names(run) and "auditor" not in [c["step"] for c in world.stub_calls()]
    history = world.history()
    assert len(history) == 1 and history[0]["audit"] == W.AUDIT and history[0]["measured"] is False \
        and history[0]["used"] is True and history[0]["commit"] == world.audit_commit, history
    calls_before = len(world.gov_calls())
    again = world.go(force=True, gate=world.gate_stub)
    assert again.code == 1 and "REFUSED RN-NAME" in again.lines, again
    assert "measure" not in W.step_names(again) and len(world.gov_calls()) == calls_before, "no second measure"
    assert len(world.history()) == 1


# -- F3: a stopped audit's set is never measured later ------------------------------------------------------------------
def test_f3_a_stop_before_used_leaves_the_set_unmeasured_and_the_next_audit_starts_a_new_set(make_world):
    world = make_world()
    world.plan_launch({"writer-1": [{"exit": 10}, {"exit": 0}], "checker-1": [{"exit": 10}]})
    first = world.go()
    stopped(world, first, "writer-1", 10)
    old = world.audit
    assert not (world.sets / "runs" / old / "DECLARATION.json").exists() and not (world.sets / "runs" / old / "USED").exists()
    # the next day: a new set (another name), however the older one was left
    world.set_now("2026-11-11T12:00:00Z")
    world.make_link(world.later_commit)  # the integration store's build is now the later commit
    second = world.go(force=True)
    assert world.audit == "memory-audit-20261111" != old
    assert W.step_names(second)[:1] == ["writer-1"], second.out
    set_names = [c["argv"][c["argv"].index("--set") + 1] for c in world.stub_calls() if "--set" in c["argv"]]
    assert set_names == [old, "memory-audit-20261111"], set_names
    assert not (world.sets / "runs" / old / "DECLARATION.json").exists(), "the stopped set was never measured"
    assert not (world.sets / "runs" / old / "USED").exists()
    assert world.history() == [], "a stop before USED is no line of HISTORY.jsonl"
