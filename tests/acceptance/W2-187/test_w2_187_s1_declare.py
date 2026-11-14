"""S1 (and F1's spent check): ``python3 -m gov.memaudit standing declare --sets-root R --set <name> [--repo D] [--runs-dir DIR]
[--replaces <old>]`` (Interface I3).

It records one standing set for the repository: one ``STANDING.jsonl`` line (event, set, set_digest, n, n_apart, the two
brief hashes, the writer's commit, wave0, at) in the repository's key folder, and prints ``STANDING DECLARED <set>: n <n>
apart <k> digest <12 hex> written at <12 hex>``. Refusals, in this order and with nothing written (exit 1): ``STANDING_SPENT
<k>``, ``STANDING_LIVE <set>``, ``STANDING_BRIEFS``, ``STANDING_FORM``. A Wave 0 verdict set (``memory-audit-<date>``) with its
``USED`` marker and counts-only result record is accepted.

Readings (the Interface leaves them to the test): ``n`` counts every kept question (80 here) and ``n_apart`` the nonexistent-id
questions among them (1); the retired line of a replaced set may or may not carry ``set`` (the suite reads the reason, and the
set where it is given).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime

import pytest

import w2_187_world as W
from w2_187_world import W171

GOOD_AT = "2026-11-08"
OTHER = "memory-standing-20261108"
WAVE0 = "memory-audit-20261001"


def world_with_briefs(make_world, name=W.STD):
    world = make_world()
    world.plant_briefs(name)
    return world


def state(world):
    return W.tree_state(world.sets, world.runs_env)


def copy_set(world, name):
    shutil.copytree(world.std_set_dir, world.sets / "fixtures" / "evaluation" / name)


def test_s1_a_new_set_is_recorded_with_each_field_and_prints_its_line(make_world):
    world = world_with_briefs(make_world)
    digest = world.std_digest()
    run = world.standing_declare()
    assert run.code == 0, run
    assert run.lines == [f"STANDING DECLARED {W.STD}: n 80 apart 1 digest {digest[:12]} written at {world.base_commit[:12]}"], run
    (line,) = world.standing_lines()
    assert set(line) == {"event", "set", "set_digest", "n", "n_apart", "writer_brief_sha256", "checker_brief_sha256",
                         "written_commit", "wave0", "at"}, line
    assert (line["event"], line["set"], line["n"], line["n_apart"], line["wave0"]) == ("declared", W.STD, 80, 1, False)
    assert line["set_digest"] == digest
    assert line["writer_brief_sha256"] == W.WRITER_SHA and line["checker_brief_sha256"] == W.CHECKER_SHA
    assert line["written_commit"] == world.base_commit
    assert datetime.fromisoformat(line["at"].replace("Z", "+00:00"))
    assert world.std_digest() == digest, "the set is read, never edited"


def test_s1_the_digest_is_sha256sum_of_the_yaml_files_under_the_c_locale(make_world):
    world = world_with_briefs(make_world)
    assert world.standing_declare().code == 0
    shell = subprocess.run("LC_ALL=C sha256sum *.yaml | sha256sum", shell=True, cwd=world.std_hidden, text=True,
                           capture_output=True, check=True).stdout.split()[0]
    assert world.standing_lines()[0]["set_digest"] == shell


def test_s1_the_runs_folder_defaults_to_the_environments_and_the_key_folders_briefs_count_too(make_world):
    world = make_world()
    world.plant_briefs(runs=world.mem)  # <key folder>/indep/{writer,checker}/*/
    run = world.drive("standing", "declare", "--sets-root", str(world.sets), "--set", W.STD, "--repo", str(world.repo))
    assert run.code == 0, run
    assert [x["event"] for x in world.standing_lines()] == ["declared"]


def test_s1_a_set_whose_question_is_in_a_misses_file_is_spent_and_the_count_is_never_an_id(make_world):
    world = world_with_briefs(make_world)
    docs = world.std_docs()
    folder = world.sets / "runs" / "memory-audit-20260920"
    folder.mkdir(parents=True)
    rows = [{"id": f"zz{k}", "question": docs[f"q0{k}"]["question"], "gold_answer": "x", "gold_sources": [], "answer": "y",
             "outcome": "wrong", "evidence_in_bundle": False} for k in (5, 6)]
    rows.append({"id": "zz9", "question": "a question that is in no standing set", "gold_answer": "x", "gold_sources": [],
                 "answer": "y", "outcome": "wrong", "evidence_in_bundle": False})
    (folder / "misses.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    before = state(world)
    run = world.standing_declare()
    assert run.code == 1 and run.lines == ["STANDING_SPENT 2"], run
    assert state(world) == before and world.standing_lines() == []
    assert not [x for x in run.lines if "q05" in x or "q06" in x]


def test_s1_a_misses_file_of_other_questions_does_not_spend_the_set(make_world):
    world = world_with_briefs(make_world)
    folder = world.sets / "runs" / "memory-audit-20260920"
    folder.mkdir(parents=True)
    (folder / "misses.jsonl").write_text(json.dumps({"id": "q05", "question": "an entirely different question",
                                                      "gold_answer": "x"}) + "\n", encoding="utf-8")
    run = world.standing_declare()
    assert run.code == 0, "matched by question text, never by id: " + repr(run)


@pytest.mark.parametrize("where", ["classes-file", "audits-log-key-folder", "audits-log-runs-folder"])
def test_s1_a_set_an_auditor_read_is_spent(make_world, where):
    world = world_with_briefs(make_world)
    baseline = {"time": "2026-11-02T00:00:00Z", "commit": world.base_commit, "run": "baseline", "audit": "baseline"}
    audited = {"time": "2026-11-03T00:00:00Z", "commit": world.base_commit, "run": "auditor-1", "audit": W.STD}
    if where == "classes-file":
        folder = world.std_runs / "2026-W44"
        folder.mkdir(parents=True)
        (folder / "miss-classes.json").write_text("{}", encoding="utf-8")
    elif where == "audits-log-key-folder":
        world.plant_audits(baseline, audited)
    else:
        log = world.runs_env / "indep" / "AUDITS.log"
        log.write_text(json.dumps(audited) + "\n", encoding="utf-8")
    before = state(world)
    run = world.standing_declare()
    assert run.code == 1 and len(run.lines) == 1 and run.lines[0].startswith("STANDING_SPENT"), run
    assert state(world) == before and world.standing_lines() == []


def wave0_world(make_world, *, used=True, record=True, commit=None, own_misses=True):
    world = make_world()
    copy_set(world, WAVE0)
    world.plant_briefs(WAVE0)
    world.plant_audits({"time": "2026-10-01T00:00:00Z", "commit": world.base_commit, "run": "baseline", "audit": "baseline"})
    run = world.sets / "runs" / WAVE0
    run.mkdir(parents=True, mode=0o700)
    if used:
        (run / "USED").write_text("2026-10-01T10:00:00Z " + WAVE0 + " 00\n", encoding="utf-8")
    (run / "DECLARATION.json").write_text(json.dumps({"audit": WAVE0, "audit_commit": commit or world.base_commit, "n": 80}),
                                          encoding="utf-8")
    if record:
        (run / "FIGURES.json").write_text(json.dumps({"audit": WAVE0, "n": 80, "verdict": {"right": 78, "wrong": 1}}),
                                          encoding="utf-8")
    if own_misses:  # the Wave 0 run's own misses file and classes: they do not spend it (the CTO's U1)
        questions = [d["question"] for d in world.std_docs().values()][:3]
        (run / "misses.jsonl").write_text("".join(json.dumps({"id": f"w{k}", "question": text}) + "\n"
                                                  for k, text in enumerate(questions)), encoding="utf-8")
        (run / "miss-classes.json").write_text("{}", encoding="utf-8")
    return world


def test_s1_a_wave_0_verdict_set_with_its_used_marker_and_result_record_is_accepted(make_world):
    world = wave0_world(make_world)
    run = world.standing_declare(WAVE0)
    assert run.code == 0, run
    (line,) = world.standing_lines()
    assert (line["event"], line["set"], line["wave0"]) == ("declared", WAVE0, True), line
    assert run.lines[0].startswith(f"STANDING DECLARED {WAVE0}: n 80 apart 1 digest "), run


@pytest.mark.parametrize("flaw", ["no-record", "other-commit"])
def test_s1_a_wave_0_set_without_its_record_or_at_another_commit_is_spent_with_zero(make_world, flaw):
    world = wave0_world(make_world, record=flaw != "no-record", commit="1" * 40 if flaw == "other-commit" else None)
    run = world.standing_declare(WAVE0)
    assert run.code == 1 and run.lines == ["STANDING_SPENT 0"], run
    assert world.standing_lines() == []


def test_s1_a_second_live_set_is_refused_until_the_first_is_retired(make_world):
    world = world_with_briefs(make_world, OTHER)
    copy_set(world, OTHER)
    world.plant_standing()
    before = state(world)
    run = world.standing_declare(OTHER)
    assert run.code == 1 and run.lines == [f"STANDING_LIVE {W.STD}"], run
    assert state(world) == before
    world.plant_standing(world.standing_record(), {"event": "retired", "set": W.STD, "reason": "fitted", "at": GOOD_AT})
    again = world.standing_declare(OTHER)
    assert again.code == 0, again
    assert [x["event"] for x in world.standing_lines()][-1] == "declared" and world.standing_lines()[-1]["set"] == OTHER


def test_s1_replaces_lifts_the_live_check_only_for_the_live_set_that_is_thin(copy_std, make_world):
    thin = copy_std("thin69")
    copy_set(thin, OTHER)
    thin.plant_briefs(OTHER)
    wrong = thin.standing_declare(OTHER, extra=("--replaces", "memory-standing-20250101"))
    assert wrong.code == 1 and wrong.lines == [f"STANDING_LIVE {W.STD}"], "only the live set can be replaced"
    run = thin.standing_declare(OTHER, extra=("--replaces", W.STD))
    assert run.code == 0, run
    retired = [x for x in thin.standing_lines() if x["event"] == "retired"]
    assert len(retired) == 1 and retired[0]["reason"] == "thin" and retired[0].get("set", W.STD) == W.STD, retired
    assert thin.standing_lines()[-1]["event"] == "declared" and thin.standing_lines()[-1]["set"] == OTHER
    live = thin.standing_live()
    assert live.code == 0 and live.lines[-1] == f"LIVE {OTHER}", live
    fine = make_world()
    copy_set(fine, OTHER)
    fine.plant_briefs(OTHER)
    fine.plant_standing()
    refused = fine.standing_declare(OTHER, extra=("--replaces", W.STD))
    assert refused.code == 1 and refused.lines == [f"STANDING_LIVE {W.STD}"], "a set that is not thin is not replaced"


@pytest.mark.parametrize("case", ["none", "writer-only", "checker-only", "rejected", "other-set"])
def test_s1_without_a_delivered_writer_and_checker_for_the_set_it_is_refused(make_world, case):
    world = make_world()
    kinds = {"writer-only": ("writer",), "checker-only": ("checker",)}.get(case, ("writer", "checker"))
    if case != "none":
        world.plant_briefs(kinds=kinds, status="rejected" if case == "rejected" else "delivered",
                           set_name="memory-standing-20250101" if case == "other-set" else None)
    before = state(world)
    run = world.standing_declare()
    assert run.code == 1 and run.lines == ["STANDING_BRIEFS"], run
    assert state(world) == before and world.standing_lines() == []


def test_s1_a_file_that_fails_the_form_is_refused(make_world):
    world = world_with_briefs(make_world)
    path = world.std_hidden / "q07.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("gold_answer:", "gold:"), encoding="utf-8")
    before = state(world)
    run = world.standing_declare()
    assert run.code == 1 and run.lines == ["STANDING_FORM"], run
    assert state(world) == before and world.standing_lines() == []


def test_s1_a_set_of_36_files_is_accepted_and_35_is_not(make_world):
    keep = {35: [f"q{k:02d}" for k in range(1, 35)] + [W.APART], 36: [f"q{k:02d}" for k in range(1, 36)] + [W.APART]}
    outcomes = {}
    for count, ids in keep.items():
        world = world_with_briefs(make_world)
        for path in world.std_hidden.glob("*.yaml"):
            if path.stem not in ids:
                path.unlink()
        run = world.standing_declare()
        outcomes[count] = (run.code, run.lines[0].split(" digest")[0] if run.lines else None)
    assert outcomes[35] == (1, "STANDING_FORM"), outcomes
    assert outcomes[36] == (0, f"STANDING DECLARED {W.STD}: n 36 apart 1"), outcomes


@pytest.mark.parametrize("flaws,first", [(("spent", "live"), "STANDING_SPENT"), (("live", "briefs"), "STANDING_LIVE"),
                                         (("briefs", "form"), "STANDING_BRIEFS")])
def test_s1_the_refusals_come_in_the_order_spent_live_briefs_form(make_world, flaws, first):
    world = make_world()
    if "briefs" not in flaws:
        world.plant_briefs()
    if "form" in flaws:
        path = world.std_hidden / "q07.yaml"
        path.write_text(path.read_text(encoding="utf-8").replace("gold_answer:", "gold:"), encoding="utf-8")
    if "live" in flaws:
        world.plant_standing()
    if "spent" in flaws:
        folder = world.sets / "runs" / "memory-audit-20260920"
        folder.mkdir(parents=True)
        (folder / "misses.jsonl").write_text(json.dumps({"question": world.std_docs()["q05"]["question"]}) + "\n",
                                             encoding="utf-8")
    run = world.standing_declare()
    assert run.code == 1 and run.lines[0].startswith(first), run


@pytest.mark.parametrize("bad", ["memory-standing-2026", "standing-20261101", "memory-fresh-20261101", "../x"])
def test_s1_a_set_name_that_is_not_of_the_forms_is_usage_exit_4(make_world, bad):
    world = world_with_briefs(make_world)
    assert world.drive("standing", "declare", "--help").code == 0, "the subcommand exists"
    run = world.standing_declare(bad)
    assert run.code == 4, run
    assert world.standing_lines() == []


def test_s1_the_sets_root_is_required(make_world):
    world = world_with_briefs(make_world)
    run = world.drive("standing", "declare", "--set", W.STD, "--repo", str(world.repo))
    assert run.code == 4, run
    assert world.drive("standing", "declare", "--help").code == 0, "the subcommand exists"
