"""S1: the control runs first (Interface 5, 12; S1's Verify: a planted fake ``gov`` returning a control at 34, 33 and 31:
the first two proceed, the third stops before the audit set's first search).

The control is ``memory-retrieval --part visible`` (40 questions), run on ``--repo`` as the attempts are, after
``declare`` (W2-170: ``DECLARATION.json``, then ``USED``) and before the audit set's first search. ``last`` is the
latest earlier ``memory-audit-<date>`` run folder's ``FIGURES.json`` ``control.hit5`` (34 when none); in range is
``abs(hit5 - last) <= 2``. Out of range: exit 2, ``STOPPED control``, ``USED`` as W2-170 wrote it, no attempt folder.
"""

from __future__ import annotations

import os
import shutil

import pytest

import w2_171_scenario as S
import w2_171_world as W


def _scenario(hits: int) -> S.Scenario:
    return S.Scenario("control", control_hits=hits)


@pytest.mark.parametrize("hits", [34, 33])
def test_s1_a_control_at_34_or_33_goes_on_to_the_attempt(world, hits):
    _scenario(hits).install(world)
    run = world.measure()
    assert run.code == 0, run
    events = world.events("control")
    assert len(events) == 1, events
    assert (events[0]["k"], events[0]["hit5"], events[0]["of"], events[0]["last"], events[0]["ok"]) == \
        (1, hits, 40, 34, True), events
    assert "last_audit" in events[0]
    control = world.run_dir / "control-1"
    assert (control / "measure.txt").is_file() and (control / "kept").is_dir()
    lines = world.question_lines(control)
    assert len(lines) == 40 and all(part == "visible" for _, part, *_ in lines), lines[:2]
    assert any(x.startswith("families:") for x in (control / "measure.txt").read_text().splitlines())
    assert (world.run_dir / "attempt-1" / "DONE").is_file()
    assert (world.run_dir / "COUNTS").read_text().strip() == "attempt-1"


def test_s1_a_control_at_31_stops_before_the_audit_set_s_first_search(world):
    _scenario(31).install(world)
    run = world.measure()
    assert run.code == 2, run
    assert "STOPPED control" in run.lines, run
    assert (world.run_dir / "STOPPED").read_text().strip() == "control"
    # USED as W2-170 wrote it: one line naming the audit and the declaration's sha256
    used = (world.run_dir / "USED").read_text().splitlines()
    assert len(used) == 1 and used[0].split()[1:] == [W.AUDIT, W.sha_file(world.run_dir / "DECLARATION.json")], used
    assert [p.name for p in world.run_dir.glob("attempt-*")] == []
    assert not (world.run_dir / "COUNTS").exists()
    assert not [e for e in world.events("search") if e.get("phase") == "attempt"]
    asked = {c["q"] for c in world.gov_calls()}
    audit_texts = {d["question"] for d in world.docs().values()}
    assert not (asked & audit_texts), "the audit set's questions were searched after a control out of range"
    control = world.events("control")
    assert len(control) == 1 and control[0]["hit5"] == 31 and control[0]["ok"] is False, control
    assert world.events("stopped")[0]["cause"] == "control"
    assert not world.events("attempt")


@pytest.mark.parametrize("hits,goes_on", [(31, True), (28, True), (33, False), (27, False)])
def test_s1_last_is_the_latest_earlier_audit_s_control_hit5(world, hits, goes_on):
    """Earlier audits: 20261015 (control 20), 20261101 (control 30: the latest earlier that has a FIGURES.json),
    20261105 (a run folder without one) and 20261201 (a later audit, control 99: not earlier, never read)."""
    world.plant_earlier("memory-audit-20261015", control_hit5=20)
    world.plant_earlier("memory-audit-20261101", control_hit5=30)
    (world.sets / "runs" / "memory-audit-20261105").mkdir(parents=True)
    world.plant_earlier("memory-audit-20261201", control_hit5=99)
    _scenario(hits).install(world)
    run = world.measure()
    assert world.events("control"), run
    event = world.events("control")[0]
    assert event["last"] == 30 and event["last_audit"] == "memory-audit-20261101", event
    assert event["hit5"] == hits and event["ok"] is goes_on, event
    assert run.code == (0 if goes_on else 2), run
    if not goes_on:
        assert "STOPPED control" in run.lines, run


def test_s1_the_control_is_searched_as_the_attempts_are_whatever_the_callers_environment(world):
    """Item 5 and 12: batch 10, bundle 6,000, ``GOV_ROLE=orchestrator``, ``GOV_STORE`` and ``GOV_TICKET`` unset, on
    ``--repo``; the probe is the one search ``gov retrieve "what decides a close" --json`` before the control."""
    _scenario(34).install(world)
    run = world.measure(env={"GOV_ROLE": "engineer", "GOV_STORE": "/nonexistent/store.db", "GOV_TICKET": "DAEO-0000"})
    assert run.code == 0, run
    calls = [c for c in world.gov_calls() if c["argv"][:1] == ["retrieve"]]
    assert calls and calls[0]["q"] == W.PROBE and "--json" in calls[0]["argv"], calls[:1]
    assert os.path.realpath(calls[0]["cwd"]) == os.path.realpath(world.repo)
    measured = [c for c in calls if c["q"] != W.PROBE]     # the probe's own environment is not stated
    assert len(measured) >= 80
    for call in measured:
        assert call["env"] == {"GOV_ROLE": "orchestrator", "GOV_STORE": None, "GOV_TICKET": None}, call
    for call in measured:
        argv = call["argv"]
        assert argv[argv.index("--batch-size") + 1] == "10" and argv[argv.index("--bundle-budget") + 1] == "6000", argv
        assert argv[-1] == "--json"
    first_control = next(i for i, c in enumerate(calls) if c["q"] == W.control_text(1))
    first_audit = next(i for i, c in enumerate(calls) if c["q"] in {d["question"] for d in world.docs().values()})
    assert 0 < first_control < first_audit, "probe, then control, then the audit set"


def test_s1_a_control_search_not_answered_as_declared_is_notready_not_control(world):
    def edit(gov, docs):
        gov[W.control_text(3)]["fault"] = "rerank"
    _scenario(34).install(world, gov_edit=edit)
    run = world.measure()
    assert run.code == 2 and "STOPPED notready" in run.lines, run
    assert (world.run_dir / "STOPPED").read_text().strip() == "notready"
    assert [p.name for p in world.run_dir.glob("attempt-*")] == []
    assert not (set(c["q"] for c in world.gov_calls()) & {d["question"] for d in world.docs().values()})


def test_s1_a_missing_control_set_ends_the_ready_check(world):
    """The CTO's ruling 9: no session opens the sets root to confirm the control's set; a missing set is
    ``STOPPED notready`` and the first live run shows it."""
    _scenario(34).install(world)
    shutil.rmtree(world.sets / "fixtures" / "evaluation" / "memory-retrieval" / "visible")
    run = world.measure()
    assert run.code == 2 and "STOPPED notready" in run.lines, run
    assert (world.run_dir / "STOPPED").read_text().strip() == "notready"
    assert [p.name for p in world.run_dir.glob("attempt-*")] == []
