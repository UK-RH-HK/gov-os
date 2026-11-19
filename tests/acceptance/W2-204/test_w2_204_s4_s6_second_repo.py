"""S4, S5, S6 and F4: a second repository is measured by its own file. Its categories key the figures, a subsystem may be
a record key, the control is the file's, and nothing of Gov OS's tables is taken for it."""

from __future__ import annotations

import json
import re

import pytest

import w2_204_stages as ST
import w2_204_support as K
from w2_204_support import HIDDEN, VISIBLE, S171, W171

VERDICT = re.compile(r"FRESH VERDICT hidden right (\d+) of (\d+) \((\d+(?:\.\d+)?) %\): (passes|misses)")
BESIDE = re.compile(r"FRESH BESIDE visible right (\d+) of (\d+)")
CLEAN_SUBSYSTEMS = {"capture-flow": 4, "review-flow": 4, "tide-engine": 4, "none": 28}


def last_two(call: K.Call):
    """The verdict and the beside line: the run's last two lines, each fitting its whole form (counts only)."""
    assert len(call.lines) >= 2, call
    verdict = [m for m in map(VERDICT.fullmatch, call.lines[-2:]) if m]
    beside = [m for m in map(BESIDE.fullmatch, call.lines[-2:]) if m]
    assert len(verdict) == 1 and len(beside) == 1, call
    assert len([x for x in call.lines if x.startswith("FRESH VERDICT")]) == 1, call
    assert len([x for x in call.lines if x.startswith("FRESH BESIDE")]) == 1, call
    return verdict[0], beside[0]


# -- S4 ----------------------------------------------------------------------------------------------------------------
def test_s4_two_delivered_halves_run_to_a_judged_figure_that_passes(stage):
    final = stage("right")["final"]
    assert final.code == 0, final
    verdict, beside = last_two(final)
    assert (verdict[1], verdict[2], verdict[4]) == ("40", "40", "passes"), final
    assert float(verdict[3]) == 100.0 and (beside[1], beside[2]) == ("40", "40"), final


def test_s4_both_halves_figures_are_keyed_by_the_repository_s_categories(stage):
    world = stage("right").world
    for audit in (VISIBLE, HIDDEN):
        path = world.run_dir(audit) / "FIGURES.json"
        assert path.is_file(), f"no FIGURES.json for {audit}: {stage('right')['final']!r}"
        by_category = K.find_key(json.loads(path.read_text(encoding="utf-8")), "by_category")
        assert by_category and all(sorted(found) == sorted(K.CATEGORY_NAMES) for found in by_category), by_category
        assert not any(name in found for found in by_category for name in K.GOV_OS_ONLY_CATEGORIES)


def test_s4_three_wrong_answers_of_forty_say_misses(stage):
    final = stage("misses")["final"]
    assert final.code == 0, final
    verdict, _ = last_two(final)
    assert (verdict[1], verdict[2], verdict[4]) == ("37", "40", "misses") and float(verdict[3]) == 92.5, final


def test_s4_the_verdict_s_n_is_the_kept_hidden_questions(stage):
    run = stage("round2")
    assert run["final"].code == 0, run["final"]
    verdict, _ = last_two(run["final"])
    assert run.world.json_of(HIDDEN, "DROPS.json")["kept"] == 39
    assert (verdict[1], verdict[2], verdict[4]) == ("39", "39", "passes"), run["final"]


# -- S5 ----------------------------------------------------------------------------------------------------------------
def test_s5_questions_are_counted_per_feature_by_their_first_source_s_front_matter(world):
    world.write_half(HIDDEN, K.clean_specs())
    run = world.step("preflight", HIDDEN)
    assert run.code == 0, run
    assert world.json_of(HIDDEN, "PREFLIGHT.json")["subsystems"] == CLEAN_SUBSYSTEMS


def test_s5_a_feature_no_row_holds_and_a_file_without_front_matter_count_none(world):
    """``R-18`` carries ``feature: F09`` (in no row), the scenarios and the code files of ``app/core`` carry no front
    matter: all are ``none``; the path row ``tide-engine`` still counts by path."""
    specs = [s for s in K.clean_specs() if s["id"] in ("q15", "q18", "q21", "q29", "q07")]
    world.write_half(HIDDEN, specs)
    world.step("preflight", HIDDEN)
    found = world.json_of(HIDDEN, "PREFLIGHT.json")["subsystems"]
    assert found == {"capture-flow": 1, "review-flow": 0, "tide-engine": 1, "none": 3}


def test_s5_void_counts_the_kept_questions_per_feature_in_drops_json(world):
    world.write_half(HIDDEN, K.clean_specs())
    assert world.step("preflight", HIDDEN).code == 0
    world.write_notes(HIDDEN, 1, {"q11": ("reject", "R1-WRONG")})   # q11 cites a record of feature F01
    run = world.step("void", HIDDEN)
    assert run.code == 0 and run.last == "DROPS: kept 39 dropped 1", run
    assert world.json_of(HIDDEN, "DROPS.json")["subsystems"] == {**CLEAN_SUBSYSTEMS, "capture-flow": 3}


def test_s5_eleven_of_forty_in_one_feature_are_refused_pf_spread(world):
    world.write_half(HIDDEN, K.heavy_specs())
    run = world.step("preflight", HIDDEN)
    spread = [x for x in run.lines if x.startswith("PF-SPREAD")]
    assert run.code == 1 and len(spread) == 1, run
    assert spread[0].startswith("PF-SPREAD refused") and spread[0].endswith("subsystem capture-flow 11"), run
    assert [x for x in run.lines if x.startswith("PF-") and " refused" in x] == spread, run


# -- S6 ----------------------------------------------------------------------------------------------------------------
def _trial(tmp_path, **control) -> dict:
    doc = K.config_doc()
    doc["control"] = "none" if control.get("none") else {**doc["control"], **control}
    path = tmp_path / "trial-memory-audit.yaml"
    path.write_text(K.config_text(doc), encoding="utf-8")
    return {"GOV_MEMAUDIT_CONFIG": str(path)}


def test_s6_a_control_at_the_file_s_baseline_is_in_range(world, tmp_path):
    env = _trial(tmp_path, baseline=20)
    world.prepare(env=env)
    world.install_plans(control_hits=20)
    run = world.step("measure", HIDDEN, env=env)
    control = [x for x in run.lines if x.startswith("CONTROL")]
    assert run.code == 0 and len(control) == 1, run
    assert "hit@5 20 of 24" in control[0] and "last 20" in control[0] and control[0].endswith("in range"), run
    assert any(x.startswith("RETRIEVAL attempt 1: hit@5 39 of 39") for x in run.lines), run


def test_s6_a_control_outside_the_file_s_spread_stops_the_audit(world, tmp_path):
    env = _trial(tmp_path, baseline=20)
    world.prepare(env=env)
    world.install_plans(control_hits=24)
    run = world.step("measure", HIDDEN, env=env)
    assert run.code == 2 and "STOPPED control" in run.lines, run
    assert any(x.startswith("CONTROL") and "hit@5 24 of 24" in x and "out of range" in x for x in run.lines), run
    assert not (world.run_dir(HIDDEN) / "attempt-1").exists()


def test_s6_baseline_first_passes_and_its_figure_is_the_next_audit_s_last(stage):
    """The planted run's file says ``baseline: first``: the visible half's control (17 of 24) cannot be out of range,
    and the hidden half, the next audit, compares with it."""
    run = stage("right")
    assert run["final"].code == 0, run["final"]
    visible, hidden = (run.world.json_of(a, "FIGURES.json")["control"] for a in (VISIBLE, HIDDEN))
    assert (visible["hit5"], visible["of"]) == (17, 24), visible
    assert (hidden["hit5"], hidden["of"], hidden["last"], hidden["last_audit"]) == (17, 24, 17, VISIBLE), hidden


def test_s6_control_none_makes_no_control_search_and_the_figures_hold_null(world, tmp_path):
    env = _trial(tmp_path, none=True)
    world.prepare(env=env)
    world.install_plans()
    run = world.step("measure", HIDDEN, env=env)
    assert run.code == 0 and not [x for x in run.lines if x.startswith("CONTROL")], run
    asked = {call.get("q") for call in world.gov_calls()}
    assert W171.PROBE in asked and not asked & {K.control_text(k) for k in range(1, K.CONTROL_N + 1)}
    assert not list(world.run_dir(HIDDEN).glob("control-*"))
    run = world.step("judge", HIDDEN, env=env)
    assert run.code == 0, run
    assert world.json_of(HIDDEN, "FIGURES.json")["control"] is None


def test_s6_gov_os_s_own_control_is_still_34_within_2(stage):
    measure = stage("govos")["module:measure"]
    assert measure.code == 0 and "CONTROL control-1: hit@5 34 of 40; last 34; in range" in measure.lines, measure


def test_s6_gov_os_s_control_three_away_is_out_of_range(tmp_path):
    W171.build(tmp_path / "g")
    gov_os = W171.World(tmp_path / "g")
    gov_os.write_set(W171.clean_specs())
    gov_os.write_notes(1)
    S171.Scenario("far", control_hits=37).install(gov_os)
    flags = ST.gov_os_flags(gov_os)
    for step in ("preflight", "void"):
        run = ST.gov_os_call(gov_os, "module", step, flags[step])
        assert run.code == 0, (step, run)
    run = ST.gov_os_call(gov_os, "module", "measure", flags["measure"])
    assert run.code == 2 and "STOPPED control" in run.lines, run
    assert "CONTROL control-1: hit@5 37 of 40; last 34; control out of range" in run.lines, run


# -- F4 ----------------------------------------------------------------------------------------------------------------
def test_f4_a_question_labelled_with_a_gov_os_category_is_pf_form(world):
    specs = K.clean_specs()
    specs[6]["category"] = "kernel-template"   # q07
    world.write_half(HIDDEN, specs)
    run = world.step("preflight", HIDDEN)
    form = [x for x in run.lines if x.startswith("PF-FORM")]
    assert run.code == 1 and len(form) == 1 and form[0].split() == ["PF-FORM", "refused", "1", "q07"], run


def test_f4_a_half_with_no_register_question_is_not_thin_for_a_gov_os_domain(world):
    world.write_half(HIDDEN, K.clean_specs())
    run = world.step("preflight", HIDDEN)
    assert run.code == 0 and "PF-SPREAD ok" in run.lines and "PF-QUOTA ok" in run.lines, run
    record = world.json_of(HIDDEN, "PREFLIGHT.json")
    assert sorted(record["domains"]) == sorted([*K.DOMAIN_NAMES, "none"])
    assert not set(record["domains"]) & set(K.GOV_OS_ONLY_DOMAINS)
    assert sorted(record["categories"]) == sorted(K.CATEGORY_NAMES)
    assert record["domains"] == {"decisions": 8, "harbour-tasks": 4, "berth-specs": 7, "pilot-reports": 6, "code": 15,
                                 "none": 0}


def test_f4_void_never_calls_a_gov_os_domain_thin(world):
    world.prepare()
    drops = world.json_of(HIDDEN, "DROPS.json")
    assert drops["void"] is None and sorted(drops["domains"]) == sorted([*K.DOMAIN_NAMES, "none"]), drops
    assert not set(drops.get("thin_domains", [])) & set(K.GOV_OS_ONLY_DOMAINS)
