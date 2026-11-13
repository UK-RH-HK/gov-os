"""S1 and failure line 1: a brief's ``effort`` passed to the session as ``--effort <value>`` and recorded in
``WALL.json`` and ``counts.json``; a value outside the five refuses 10 before anything is built (DEC-1120 (2)-(3),
DEC-1101 (2)).

Readings (the ticket does not spell these out; the lead's brief settles the first three):
- the counts gain one top-level field ``effort``, a string or null, on every result line (null when the brief names
  none, and on a refusal before the brief is read or when its value is refused: a refused value is never recorded);
- ``WALL.json`` records it under the key ``effort``, null when the brief names none;
- the session's argv carries ``--effort`` and the value as two items; whether the canary's call carries it too is not
  settled, so only the real session's call is held to it (and, with no ``effort`` line, no call carries it);
- "a value outside the five" includes another case of a word (``High``), a number, a list and the empty string.
"""

from __future__ import annotations

import json

import pytest

import w2_173_support as s
from w2_173_support import sa, support
from w2_149_support import assert_good_launch, assert_nothing_built, assert_refused


def plant_for(world, flow, half):
    """What a set-up A flow reads from its half before it builds (nothing for the writers): W2-149's planting."""
    if flow in ("labeller", "labeller-2", "overlap-auditor"):
        sa.plant_half(world, half, n_actions=48, n_cases=12)
    if flow == "overlap-auditor":
        sa.plant_labels(world, half)


def manifest(world, line):
    return json.loads((world.wall(line) / "WALL.json").read_text())


# -- the counts schema -----------------------------------------------------------------------------------------------

def test_s1_the_counts_schema_gains_effort_a_closed_string_or_null():
    schema = s.counts_schema()
    prop = schema.get("properties", {}).get("effort")
    assert isinstance(prop, dict), "indep-counts.schema.json has no top-level property effort"
    types = prop.get("type") if isinstance(prop.get("type"), list) else [prop.get("type")]
    assert set(types) == {"string", "null"}, prop
    assert set(prop.get("enum", [])) == set(s.EFFORTS) | {None}, prop
    assert "effort" in schema.get("required", []), "effort is not on every result line (required)"
    assert support.schema_holes(schema) == [], "the counts schema lets free text or an unnamed key through"


# -- recorded --------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("value", s.EFFORTS)
def test_s1_each_of_the_five_values_is_recorded_in_wall_json_and_counts(world, value):
    run = world.launch(*world.args("writer", brief=s.EFFORT_BRIEF[value], seed=17, dry=True))
    assert run.code == 0, run.why()
    line = run.line
    assert line["status"] == "dry", line
    assert manifest(world, line).get("effort") == value, "WALL.json does not record the brief's effort"
    assert line.get("effort") == value, "the result line does not record the brief's effort"
    assert s.counts_file(world, line).get("effort") == value, "counts.json does not record the brief's effort"
    assert s.schema_errors(line) == [], s.schema_errors(line)
    assert world.calls() == [], "a --dry build started claude"


def test_s1_a_brief_with_no_effort_line_records_effort_null(world):
    run = world.launch(*world.args("writer", seed=17, dry=True))
    assert run.code == 0, run.why()
    line = run.line
    m = manifest(world, line)
    assert "effort" in m and m["effort"] is None, "WALL.json does not record effort: null"
    assert "effort" in line and line["effort"] is None, line
    assert s.counts_file(world, line).get("effort", "absent") is None
    assert s.schema_errors(line) == [], s.schema_errors(line)


# -- passed to the session -------------------------------------------------------------------------------------------

def test_s1_a_brief_naming_high_starts_the_session_with_effort_high(world):
    """Failure line 1: a session started without the effort its brief names."""
    run = world.deliver("writer", brief=s.EFFORT_BRIEF["high"])
    sessions = s.session_argvs(world)
    assert len(sessions) == 1, f"one real session expected: {run.why()}"
    assert s.efforts_in(sessions[0]) == ["high"], f"the session's argv: {sessions[0]}"
    i = sessions[0].index("--effort") if "--effort" in sessions[0] else None
    assert i is not None and sessions[0][i + 1] == "high", "--effort and its value are not two argv items"
    assert run.code == 0, run.why()
    assert run.line.get("effort") == "high" and s.counts_file(world, run.line).get("effort") == "high"
    assert s.schema_errors(run.line) == [], s.schema_errors(run.line)


def test_s1_a_checker_brief_naming_high_starts_its_session_with_effort_high(world):
    s.plant_audit_set(world)
    run = world.deliver("checker", brief=s.CHECKER_HIGH, set_=s.AUDIT_SET, out=s.checker_out())
    sessions = s.session_argvs(world)
    assert len(sessions) == 1, f"one real session expected: {run.why()}"
    assert s.efforts_in(sessions[0]) == ["high"], f"the session's argv: {sessions[0]}"
    assert run.line.get("effort") == "high", run.line


def test_s1_a_brief_with_no_effort_line_passes_no_effort_flag(world):
    """Green today: a brief with no effort runs as today, no --effort in any call (canary or session)."""
    run = world.deliver("writer")
    assert run.code == 0, run.why()
    raw = s.raw_calls(world)
    assert len(s.session_argvs(world)) == 1 and len(raw) >= 2, f"a canary and a session expected: {raw}"
    assert all(s.efforts_in(r["argv"]) == [] for r in raw), [r["argv"] for r in raw]


# -- a value outside the five ----------------------------------------------------------------------------------------

@pytest.mark.parametrize("bad", sorted(s.BAD_EFFORT))
def test_s1_an_effort_outside_the_five_refuses_10_before_anything_is_built(world, bad):
    """Failure line 1: an invalid effort that builds a wall. A real launch (no --dry): exit 10 (reason brief), the
    walls folder under the planted sets root unchanged entry for entry, no tree, no seed line, no claude call; the
    result line still validates and records effort null; a good launch of the same kind builds afterwards."""
    walls_before = s.snapshot(world.walls)
    before = world.built_state("writer")
    world.write_stub(session={"out": support.good_out("writer")})
    run = world.launch(*world.args("writer", brief=s.BAD_BRIEF[bad]))
    assert_refused(world, run, 10)
    assert s.snapshot(world.walls) == walls_before, "the walls folder changed"
    assert_nothing_built(world, "writer", before)
    assert s.raw_calls(world) == [], "claude was started"
    assert s.schema_errors(run.line) == [], s.schema_errors(run.line)
    assert "effort" in run.line and run.line["effort"] is None, run.line
    assert_good_launch(world, "writer")


# -- set-up A's five briefs (no effort) ------------------------------------------------------------------------------

@pytest.mark.parametrize("flow", sorted(sa.FLOW))
def test_s1_the_five_set_up_a_briefs_still_pass_stage_10_and_build_dry_walls(world, flow):
    """Green today: the five approved set-up A briefs name no effort and still build dry walls."""
    half = "held-out" if flow == "writer-heldout" else "tuning"
    plant_for(world, flow, half)
    run = sa.dry(world, flow, half, seed=5150)
    assert run.code == 0, run.why()
    assert run.line["status"] == "dry", run.line
    assert (world.wall(run.line) / "WALL.json").is_file()
    assert world.calls() == [], "a --dry build started claude"


@pytest.mark.parametrize("flow", sorted(sa.FLOW))
def test_s1_the_five_set_up_a_dry_walls_record_effort_null(world, flow):
    half = "held-out" if flow == "writer-heldout" else "tuning"
    plant_for(world, flow, half)
    run = sa.dry(world, flow, half, seed=5150)
    assert run.code == 0, run.why()
    m = manifest(world, run.line)
    assert "effort" in m and m["effort"] is None, "WALL.json does not record effort: null"
    assert "effort" in run.line and run.line["effort"] is None, run.line
    assert s.schema_errors(run.line) == [], s.schema_errors(run.line)
