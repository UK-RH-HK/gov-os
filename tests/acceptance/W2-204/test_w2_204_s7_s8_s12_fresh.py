"""S7, S8 and S12: ``gov memaudit fresh`` follows the design's cycle from what is delivered, on a pinned snapshot it
builds, and closes with the transcript scan. The planted runs are built once (``w2_204_stages``) and read here."""

from __future__ import annotations

import os
import re

import pytest

import w2_204_stages as ST
import w2_204_support as K
from w2_204_support import HIDDEN, VISIBLE

BOTH = (VISIBLE, HIDDEN)


def waiting(call: K.Call) -> list[tuple[str, str]]:
    return [(m[1], m[2]) for m in (re.fullmatch(r"WAITING (\S+) (\S+)", x) for x in call.lines) if m]


def stopped(call: K.Call) -> list[tuple[str, str]]:
    return [(m[1], m[2]) for m in (re.fullmatch(r"STOPPED (\S+) (\S+)(?: \S+)?", x) for x in call.lines) if m]


def has(call: K.Call, prefix: str) -> list[str]:
    return [x for x in call.lines if x.startswith(prefix)]


# -- S7 (a): a thin domain in round 1 -------------------------------------------------------------------------------
def test_s7a_a_refused_first_pre_flight_is_recorded_and_the_run_waits_for_the_checker(stage):
    run = stage("round2")
    first = run["r1"]
    assert first.code == 5 and (HIDDEN, "checker-1") in waiting(first), first
    assert not stopped(first) and f"STEP {HIDDEN} preflight-1 refused" in first.lines, first
    recorded = run.record["preflight_1"]
    assert recorded and recorded["ok"] is False and recorded["codes"]["PF-SPREAD"]["ok"] is False, recorded


def test_s7a_after_the_notes_the_writer_s_round_2_is_asked_though_every_line_accepts(stage):
    call = stage("round2")["notes1"]
    assert call.code == 5 and (HIDDEN, "writer-2") in waiting(call) and not stopped(call), call


def test_s7a_after_a_repaired_round_2_the_checker_s_round_2_is_asked(stage):
    call = stage("round2")["r2"]
    assert call.code == 5 and (HIDDEN, "checker-2") in waiting(call) and not stopped(call), call


def test_s7a_with_the_second_notes_the_run_goes_on_to_the_judged_figure(stage):
    run = stage("round2")
    final, world = run["final"], run.world
    assert final.code == 0 and f"STEP {HIDDEN} preflight-final ok" in final.lines, final
    assert not waiting(final) and not stopped(final) and has(final, "FRESH VERDICT hidden right 39 of 39"), final
    assert (world.run_dir(HIDDEN) / "USED").exists() and (world.run_dir(HIDDEN) / "FIGURES.json").is_file()
    assert world.json_of(HIDDEN, "DROPS.json")["notes_round"] == 2


def test_s7a_the_first_pre_flight_ran_once_for_the_half(stage):
    run = stage("round2")
    assert run["final"].code == 0, run["final"]
    events = [e["event"] for e in run.world.ledger(HIDDEN)]
    assert events.count("preflight") == 2 and events.count("drop") == 1, events   # the first and the final one


# -- S7 (b): all accepted, the first pre-flight ok ------------------------------------------------------------------
def test_s7b_nothing_delivered_waits_for_the_writer_s_round_1(stage):
    plan = stage("right")["plan"]
    assert plan.code == 5 and waiting(plan) and waiting(plan)[-1][1] == "writer-1", plan
    assert waiting(plan)[-1][0] in BOTH and not stopped(plan), plan


def test_s7b_a_delivered_half_without_notes_waits_for_the_checker(stage):
    call = stage("right")["delivered"]
    assert call.code == 5 and waiting(call) and waiting(call)[-1][1] == "checker-1" and not stopped(call), call


def test_s7b_no_round_2_is_asked_when_every_line_accepts_and_the_first_pre_flight_is_ok(stage):
    run = stage("right")
    assert run["final"].code == 0, run["final"]
    for call in run.fresh_calls:
        assert not [w for w in waiting(call) if w[1] in ("writer-2", "checker-2")], call
    for audit in BOTH:
        assert not (run.world.set_dir(audit) / "XCHECK-r2.md").exists()
        assert run.world.json_of(audit, "DROPS.json")["notes_round"] == 1
        assert [e["event"] for e in run.world.ledger(audit)].count("preflight") == 2


# -- S7 (c) and (d): a round 2 the final pre-flight refuses ---------------------------------------------------------
@pytest.fixture(params=["stopped-thin", "stopped-heavy"])
def stopped_run(request, stage) -> ST.Stage:
    return stage(request.param)


def test_s7c_a_refused_first_pre_flight_asks_round_2(stopped_run):
    call = stopped_run["r1"]
    assert call.code == 5 and waiting(call) and waiting(call)[-1][1] == "writer-2" and not stopped(call), call


def test_s7c_a_round_2_the_final_pre_flight_refuses_stops_the_run_with_exit_2(stopped_run):
    call = stopped_run["r2"]
    assert call.code == 2 and len(stopped(call)) == 1, call
    audit, step = stopped(call)[0]
    assert audit in BOTH and step == "preflight-final" and not has(call, "FRESH VERDICT"), call


def test_s7c_nothing_is_spent_at_a_stop_no_used_no_measure(stopped_run):
    world = stopped_run.world
    assert stopped_run["r2"].code == 2 and stopped(stopped_run["r2"]), stopped_run["r2"]
    assert world.gov_calls() == [] and world.claude_calls() == []
    for audit in BOTH:
        folder = world.run_dir(audit)
        assert not (folder / "USED").exists() and not (folder / "DECLARATION.json").exists()
        assert not list(folder.glob("attempt-*")) and not list(folder.glob("control-*"))
    assert not list(world.runs.rglob("q*.yaml")), "a half was released before its measure"


def test_s7d_a_second_call_after_a_stop_repeats_no_recorded_step(stopped_run):
    first, again, world = stopped_run["r2"], stopped_run["again"], stopped_run.world
    assert first.code == 2 and again.code == 2 and stopped(first) and stopped(again) == stopped(first), (first, again)
    audit = stopped(first)[0][0]
    at_stop = stopped_run.record["events_at_stop"][audit]
    now = [e["event"] for e in world.ledger(audit)]
    assert now.count("preflight") == at_stop.count("preflight") == 2, (at_stop, now)   # one first, one final
    assert now.count("drop") == at_stop.count("drop") == 1, (at_stop, now)


# -- S8 -----------------------------------------------------------------------------------------------------------------
def test_s8_the_two_halves_are_named_from_the_tag(stage):
    run = stage("right")
    line = f"FRESH plan: visible {VISIBLE} hidden {HIDDEN} at {run.world.audit_commit[:12]}"
    assert (VISIBLE, HIDDEN) == ("memory-audit-26111901", "memory-audit-26111902")
    assert run["plan"].lines and run["plan"].lines[0] == line, run["plan"]


@pytest.mark.parametrize("entry", ["module", "cli"])
def test_s8_a_letter_of_the_tag_names_the_next_pair(world, entry):
    run = world.fresh(entry=entry, tag="20261119c")
    line = f"FRESH plan: visible memory-audit-26111905 hidden memory-audit-26111906 at {world.audit_commit[:12]}"
    assert run.code == 5 and line in run.lines, run
    assert waiting(run) and waiting(run)[-1] in (("memory-audit-26111905", "writer-1"),
                                                 ("memory-audit-26111906", "writer-1")), run


def test_s8_the_repository_s_store_tree_and_index_are_not_touched(stage):
    run = stage("right")
    assert run["final"].code == 0, run["final"]
    assert run.record["after"] == run.record["before"]
    assert run.record["before"]["status"] == "A  notes/staged.txt\n M records/late.md\n"


def test_s8_the_snapshot_is_a_detached_clean_clone_at_the_commit_without_hard_links(stage):
    run = stage("right")
    world = run.world
    assert (world.clone / ".git").is_dir(), run["final"]
    assert world.git_out(world.clone, "rev-parse", "HEAD").stdout.strip() == world.audit_commit
    assert world.git_status(world.clone) == ""
    assert world.git_out(world.clone, "symbolic-ref", "-q", "HEAD").returncode != 0, "the clone is on a branch"
    linked = [name for folder, _, names in os.walk(world.clone / ".git" / "objects") for name in names
              if os.stat(os.path.join(folder, name)).st_nlink != 1]
    assert not linked, "the clone shares objects with the repository by hard links"
    assert os.path.realpath(world.fresh_dir).startswith(os.path.realpath(world.runs) + os.sep)
    assert not os.path.realpath(world.fresh_dir).startswith(os.path.realpath(world.sets) + os.sep)


def test_s8_the_rebuild_command_ran_once_in_the_clone_only(stage):
    run = stage("right")
    world = run.world
    assert world.rebuilds() == [{"cwd": os.path.realpath(world.clone), "head": world.audit_commit,
                                 "argv": [str(world.rebuild_log)]}], run["final"]
    built = {x for call in run.fresh_calls for x in call.lines if x.startswith("SNAPSHOT")}
    assert built == {f"SNAPSHOT {world.audit_commit[:12]} store built"}, built


def test_s8_each_half_is_declared_on_the_clone_s_own_store(stage):
    run = stage("right")
    world = run.world
    assert run["final"].code == 0, run["final"]
    store = world.clone / ".gov-runtime" / "store.db"
    for audit in BOTH:
        declared = world.json_of(audit, "DECLARATION.json")
        assert declared["store_commit"] == declared["audit_commit"] == world.audit_commit
        assert declared["store_sha256"] == K.sha_file(store) != run.record["before"]["store"]


def test_s8_the_visible_half_is_released_after_its_measure_and_the_hidden_half_is_not(stage):
    run = stage("right")
    world = run.world
    assert run["final"].code == 0, run["final"]
    released = {p.name: p.read_bytes() for p in (world.fresh_dir / "visible").rglob("q*.yaml")}
    assert released == {p.name: p.read_bytes() for p in world.hidden(VISIBLE).glob("q*.yaml")} and len(released) == 40
    assert K.files_holding(world.runs, K.planted_words("h")) == []


def test_s8_the_run_s_state_is_counts_json_in_its_folder(stage):
    import json
    run = stage("right")
    state = run.world.fresh_dir / "COUNTS.json"
    assert state.is_file(), run["plan"]
    assert isinstance(json.loads(state.read_text(encoding="utf-8")), dict)


@pytest.mark.parametrize("entry", ["module", "cli"])
def test_s8_a_tag_whose_run_folder_holds_another_commit_is_refused(world, entry):
    assert world.fresh(entry=entry).code == 5
    run = world.fresh(entry=entry, commit=world.later_commit)
    assert run.code == 1 and has(run, "FR-NAME") and not has(run, "FRESH VERDICT"), run


def test_s8_a_tag_whose_audit_names_exist_without_its_run_folder_is_refused(world):
    world.write_half(HIDDEN, K.clean_specs())
    before = K.W171.snapshot(world.sets)
    run = world.fresh()
    assert run.code == 1 and has(run, "FR-NAME"), run
    assert K.W171.snapshot(world.sets) == before and world.rebuilds() == []


def test_s8_a_run_folder_inside_the_sets_root_is_refused(world):
    run = world.fresh(runs=world.sets / "inside")
    assert run.code in (1, 4) and not (world.sets / "inside").exists(), run


# -- S12 ----------------------------------------------------------------------------------------------------------------
def scans(call: K.Call) -> list[str]:
    return sorted(x for x in call.lines if x.startswith("SCAN "))


def test_s12_transcripts_that_name_no_id_give_two_clean_lines_and_the_verdict(stage):
    final = stage("misses")["final"]
    assert final.code == 0 and scans(final) == [f"SCAN {VISIBLE} clean", f"SCAN {HIDDEN} clean"], final
    assert has(final, "FRESH VERDICT") and not has(final, "MEASURE VOID"), final


def test_s12_a_transcript_that_names_a_question_id_voids_the_measure(stage):
    run = stage("void")
    final = run["final"]
    void = [re.fullmatch(r"MEASURE VOID (\S+)", x) for x in has(final, "MEASURE VOID")]
    assert final.code == 2 and void and all(m and m[1] in BOTH for m in void), final
    assert not has(final, "FRESH VERDICT") and not has(final, "FRESH BESIDE"), final
    assert all((run.world.run_dir(a) / "FIGURES.json").is_file() for a in BOTH), "the scan ran before both were judged"


def test_s12_the_same_transcript_allowed_by_its_session_is_clean(stage):
    final = stage("right")["final"]
    assert "--allow-session" in final.argv and ST.LEAK_SESSION in final.argv
    assert final.code == 0 and scans(final) == [f"SCAN {VISIBLE} clean", f"SCAN {HIDDEN} clean"], final
    assert has(final, "FRESH VERDICT") and not has(final, "MEASURE VOID"), final


def test_s12_the_window_opens_at_the_half_s_first_brief_event(stage):
    """The scan's window is told from the ledger: each half's first ``brief`` event is there before any step's."""
    run = stage("right")
    assert run["final"].code == 0, run["final"]
    for audit in BOTH:
        events = [e["event"] for e in run.world.ledger(audit)]
        assert "brief" in events and events.index("brief") < events.index("preflight"), events
