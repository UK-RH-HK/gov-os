"""W2-187 I1-I9 at unit scale (S1, S2, S5, S7, S8, S9): the standing set's record, its declaration, the week rule, the
check against fitting, the cadences, the repair and the state per repository. Planted under ``tmp_path``; no search, no
model call, never the real sets root or runs folder."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from gov.memaudit import declare, layout, pool, schedule, standing
from gov.memaudit.common import UsageError

from .conftest import AUDIT, git_env, run

SET = "memory-standing-20261111"
WEEK = "2026-W47"
T0 = datetime(2026, 11, 16, 21, 0, tzinfo=timezone.utc)  # a Monday


@pytest.fixture
def stand(plant, monkeypatch):
    """A plant with the standing set's files (a copy of the plant's 40), the delivered writer and checker, and the
    runs folder named by ``GOV_INDEP_RUNS_DIR``."""
    monkeypatch.setenv("GOV_INDEP_RUNS_DIR", str(plant.runs))
    monkeypatch.delenv("GOV_MEMAUDIT_STATE", raising=False)
    shutil.copytree(plant.hidden, plant.root / "fixtures/evaluation" / SET / "hidden")
    plant.state = schedule.state_dir(plant.runs, plant.repo["path"])
    for kind, sha in (("writer", "w" * 64), ("checker", "c" * 64)):
        folder = plant.runs / "indep" / kind / "r1"
        folder.mkdir(parents=True)
        (folder / "counts.json").write_text(json.dumps(
            {"status": "delivered", "set": SET, "brief_sha256": sha, "commit": plant.repo["head"]}))
    return plant


def declared(plant, name=SET, **kw):
    return standing.declare(str(plant.root), name, repo=plant.repo["path"], runs_dir=plant.runs, **kw)


def plant_misses(plant, text, folder="memory-audit-20260101"):
    run_dir = plant.root / "runs" / folder
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "misses.jsonl", "a") as f:
        f.write(json.dumps({"id": "x", "question": text}) + "\n")


def rows(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines()] if Path(path).exists() else []


# ---- S1: standing declare

def test_a_new_standing_set_is_recorded_with_each_field(stand):
    word, counts = declared(stand)
    assert word == "ok"
    line = rows(stand.state / "STANDING.jsonl")
    assert len(line) == 1 and line[0] == counts
    assert line[0]["event"] == "declared" and line[0]["set"] == SET and line[0]["n"] == 40 and line[0]["n_apart"] == 1
    assert line[0]["set_digest"] == declare.set_digest(stand.root / "fixtures/evaluation" / SET / "hidden")
    assert (line[0]["writer_brief_sha256"], line[0]["checker_brief_sha256"]) == ("w" * 64, "c" * 64)
    assert line[0]["written_commit"] == stand.repo["head"] and line[0]["wave0"] is False and line[0]["at"]
    assert standing.lines(word, counts) == [
        f"STANDING DECLARED {SET}: n 40 apart 1 digest {line[0]['set_digest'][:12]} written at {stand.repo['head'][:12]}"]


def test_a_set_whose_question_was_written_to_a_misses_file_is_refused_spent_with_a_count_never_an_id(stand):
    plant_misses(stand, stand.questions["q03"]["question"])
    plant_misses(stand, stand.questions["q09"]["question"])
    word, counts = declared(stand)
    assert (word, counts) == ("refused", {"code": "STANDING_SPENT 2"})
    assert not (stand.state / "STANDING.jsonl").exists()  # nothing written


def test_an_auditor_run_in_the_log_or_a_class_file_spends_a_set(stand):
    (stand.runs / "indep" / "AUDITS.log").write_text(json.dumps({"commit": "a" * 40, "audit": SET}) + "\n")
    assert declared(stand)[1] == {"code": "STANDING_SPENT 0"}
    (stand.runs / "indep" / "AUDITS.log").unlink()
    (stand.root / "runs" / SET / "x").mkdir(parents=True)
    (stand.root / "runs" / SET / "x" / "miss-classes.json").write_text("{}")
    assert declared(stand)[1] == {"code": "STANDING_SPENT 0"}


def wave0(plant, *, record=True, base=None):
    run_dir = plant.root / "runs" / AUDIT
    run_dir.mkdir(parents=True)
    (run_dir / "USED").write_text("x")
    (run_dir / "DECLARATION.json").write_text(json.dumps({"audit_commit": plant.repo["head"]}))
    if record:
        (run_dir / "FIGURES.json").write_text("{}")
    (run_dir / "misses.jsonl").write_text(json.dumps({"question": plant.questions["q01"]["question"]}) + "\n")
    (run_dir / "miss-classes.json").write_text("{}")
    state_log = plant.state / "indep" / "AUDITS.log"
    state_log.parent.mkdir(parents=True, exist_ok=True)
    state_log.write_text(json.dumps({"commit": base or plant.repo["head"], "audit": "baseline"}) + "\n")
    for kind in ("writer", "checker"):
        (plant.runs / "indep" / kind / "r1" / "counts.json").write_text(json.dumps(
            {"status": "delivered", "set": AUDIT, "brief_sha256": kind[0] * 64, "commit": plant.repo["head"]}))


def test_a_wave0_verdict_set_with_used_and_its_record_is_accepted_its_own_misses_do_not_spend_it(stand):
    wave0(stand)
    word, counts = declared(stand, AUDIT)
    assert word == "ok" and counts["wave0"] is True


def test_a_used_set_without_its_result_record_or_at_another_commit_is_spent(stand):
    wave0(stand, record=False)
    assert declared(stand, AUDIT)[1]["code"].startswith("STANDING_SPENT")  # its own misses now count against it
    (stand.root / "runs" / AUDIT / "FIGURES.json").write_text("{}")
    (stand.state / "indep" / "AUDITS.log").write_text(json.dumps({"commit": "b" * 40}) + "\n")
    assert declared(stand, AUDIT)[1]["code"].startswith("STANDING_SPENT")  # not the baseline's commit: not Wave 0


def test_a_second_live_set_is_refused_until_the_first_is_retired_or_replaced_when_thin(stand):
    assert declared(stand)[0] == "ok"
    other = "memory-standing-20261118"
    shutil.copytree(stand.root / "fixtures/evaluation" / SET, stand.root / "fixtures/evaluation" / other)
    for kind in ("writer", "checker"):
        (stand.runs / "indep" / kind / "r2").mkdir()
        (stand.runs / "indep" / kind / "r2" / "counts.json").write_text(json.dumps(
            {"status": "delivered", "set": other, "brief_sha256": "d" * 64, "commit": stand.repo["head"]}))
    assert declared(stand, other)[1] == {"code": f"STANDING_LIVE {SET}"}
    assert declared(stand, other, replaces=SET)[1] == {"code": f"STANDING_LIVE {SET}"}  # not thin
    standing.append(stand.state, "HISTORY.jsonl", {"kind": "standing", "set": SET, "week": WEEK, "measured": True,
                                                   "word": "pass", "flags": ["STANDING_THIN 69"]})
    word, _ = declared(stand, other, replaces=SET)
    assert word == "ok"
    assert [r["event"] for r in rows(stand.state / "STANDING.jsonl")] == ["declared", "retired", "declared"]
    assert rows(stand.state / "STANDING.jsonl")[1]["reason"] == "thin"
    assert standing.live(stand.state)["set"] == other


def test_a_set_with_no_delivered_briefs_or_a_bad_form_is_refused(stand):
    (stand.runs / "indep" / "checker" / "r1" / "counts.json").write_text(json.dumps({"status": "refused", "set": SET}))
    assert declared(stand)[1] == {"code": "STANDING_BRIEFS"}
    (stand.runs / "indep" / "checker" / "r1" / "counts.json").write_text(json.dumps(
        {"status": "delivered", "set": SET, "brief_sha256": "c" * 64}))
    hidden = stand.root / "fixtures/evaluation" / SET / "hidden"
    (hidden / "q01.yaml").write_text("id: q01\n")
    assert declared(stand)[1] == {"code": "STANDING_FORM"}
    shutil.copy(stand.hidden / "q01.yaml", hidden / "q01.yaml")
    for i in range(30, 41):
        (hidden / f"q{i:02d}.yaml").unlink()
    assert declared(stand)[1] == {"code": "STANDING_FORM"}  # fewer than 36
    assert not (stand.state / "STANDING.jsonl").exists()


# ---- S5: the bar at 95 %

def test_the_bar_is_95_percent_for_40_79_and_80():
    assert [declare.bar(n)["need_right"] for n in (40, 79, 80)] == [38, 76, 76]
    assert [declare.bar(n)["max_wrong"] for n in (40, 79, 80)] == [2, 3, 4]
    assert all(declare.bar(n)["target_right"] == declare.bar(n)["need_right"] for n in (40, 79, 80))
    assert "ceil(95 n / 100)" in declare.ROUNDING and "standing and fresh runs alike" in declare.ROUNDING


# ---- S2: the week rule

def week_paths(plant):
    return layout.paths(str(plant.root), SET, WEEK)


def test_the_week_rule_by_the_markers_in_the_week_folder(stand):
    p = week_paths(stand)
    assert standing.week_state(p) == "go"  # no folder
    layout.make_run(p)
    assert standing.week_state(p) == "go"  # a folder without USED is re-used
    (p["run"] / "USED").write_text("x")
    assert standing.week_state(p) == "used"  # USED with no STOPPED
    (p["run"] / "STOPPED").write_text("fault")
    assert standing.week_state(p) == "restart"  # stopped before its reader run began
    (p["run"] / "reader").mkdir()
    assert standing.week_state(p) == "used"  # the reader run began: never again
    (p["run"] / "reader").rmdir()
    standing.restart(p)
    assert not p["run"].exists() and (p["run"].parent / f"{WEEK}.stopped").is_dir()
    layout.make_run(p)
    (p["run"] / "USED").write_text("x")
    (p["run"] / "STOPPED").write_text("fault")
    assert standing.week_state(p) == "used"  # the one restart has been made


def test_a_verdict_in_the_week_folder_is_final(stand):
    p = week_paths(stand)
    layout.make_run(p)
    (p["run"] / "USED").write_text("x")
    (p["run"] / "FIGURES.json").write_text("{}")
    assert standing.week_state(p) == "used"
    assert str(p["run"]).endswith(f"runs/{SET}/{WEEK}") and oct(p["run"].stat().st_mode & 0o777) == "0o700"
    assert oct(p["run"].parent.stat().st_mode & 0o777) == "0o700"  # the set's own run folder: mode 700 too


def test_the_week_is_the_iso_year_and_week_of_the_clock():
    assert standing.week_of(T0) == WEEK
    assert standing.week_of(datetime(2027, 1, 3, tzinfo=timezone.utc)) == "2026-W53"
    with pytest.raises(UsageError):
        layout.paths("/", SET, "2026-46")


# ---- S7: the check against fitting

def history(state, *rows_):
    standing.append(state, "HISTORY.jsonl", *rows_)


def lines_at(pcts, name=SET):
    return [{"kind": "standing", "set": name, "week": f"2026-W{40 + i}", "measured": True, "n": 100, "right": p,
             "pct": float(p), "word": "pass" if p >= 95 else "miss", "passes": p >= 95} for i, p in enumerate(pcts)]


def fresh_fig(right, n=100):
    return {"n": n, "verdict": {"right": right}}


def set_live(plant):
    assert declared(plant)[0] == "ok"


def test_a_fresh_run_five_points_below_the_standing_mean_retires_the_set(stand):
    set_live(stand)
    history(stand.state, *lines_at([96, 96, 96, 96]))
    got = standing.drift(stand.state, fresh_fig(90))
    assert got["word"] == "STANDING_FITTED" and (got["S"], got["F"]) == (96.0, 90.0)
    assert standing.live(stand.state) is None
    assert rows(stand.state / "HISTORY.jsonl")[-1] == {"kind": "drift", "word": "STANDING_FITTED", "S": 96.0, "F": 90.0,
                                                       "set": SET}
    assert rows(stand.state / "STANDING.jsonl")[-1]["reason"] == "fitted"
    assert standing.is_standing(str(stand.root), SET, stand.repo["path"], by_name=False)


def test_a_fresh_run_five_points_above_the_standing_mean_asks_for_the_staleness_pass(stand):
    set_live(stand)
    history(stand.state, *lines_at([90, 90, 90, 90]))
    got = standing.drift(stand.state, fresh_fig(96))
    assert got["word"] == "STANDING_STALE" and standing.live(stand.state)["set"] == SET  # nothing retired
    assert rows(stand.state / "HISTORY.jsonl")[-1]["word"] == "STANDING_STALE"


def test_a_gap_under_five_points_prints_no_flag_and_writes_nothing(stand):
    set_live(stand)
    history(stand.state, *lines_at([95, 95, 95, 95]))
    before = (stand.state / "HISTORY.jsonl").read_text()
    got = standing.drift(stand.state, fresh_fig(92))
    assert got["word"] == "none" and (stand.state / "HISTORY.jsonl").read_text() == before
    assert standing.live(stand.state)


def test_fewer_than_four_weekly_figures_is_not_yet_and_only_the_last_four_count(stand):
    set_live(stand)
    history(stand.state, *lines_at([96, 96]))
    got = standing.drift(stand.state, fresh_fig(90))
    assert got["word"] is None and got["k"] == 2
    from gov.memaudit import digest
    assert digest.drift_line(got) == "DRIFT not yet (2 of 4)"
    history(stand.state, *lines_at([60, 60, 96, 96, 96, 96]))
    assert standing.drift(stand.state, fresh_fig(96))["S"] == 96.0  # the earlier 60s are not in the last four


def test_a_fresh_run_with_no_live_set_writes_nothing(stand):
    assert standing.drift(stand.state, fresh_fig(50))["word"] is None
    assert not (stand.state / "HISTORY.jsonl").exists()


# ---- S8: the cadences, the miss and the repair

def test_the_fresh_set_is_due_on_the_first_monday_28_days_after_the_last_fresh_run():
    def starts(days_ago):
        return [{"at": schedule.stamp(T0 - timedelta(days=days_ago)), "kind": "fresh"}]
    assert schedule.fresh_due([], None, T0)["reason"] == "first"
    assert schedule.fresh_due(starts(27), None, T0) == {"due": False, "reason": "wait", "next": "2026-11-23"}
    assert schedule.fresh_due(starts(28), None, T0)["reason"] == "28d"
    assert schedule.fresh_due(starts(35), None, T0)["due"] is True


def test_a_standing_miss_makes_the_fresh_set_due_until_one_starts_in_the_week():
    miss = {"kind": "standing", "measured": True, "passes": False, "word": "miss"}
    fresh = [{"at": schedule.stamp(T0 - timedelta(days=10)), "kind": "fresh"}]
    assert schedule.fresh_due(fresh, miss, T0)["reason"] == "miss"
    again = fresh + [{"at": schedule.stamp(T0 - timedelta(hours=1)), "kind": "fresh"}]
    got = schedule.fresh_due(again, miss, T0 + timedelta(days=1))
    assert got["due"] is False and got["next"] == "2026-11-23"  # the next Monday
    assert schedule.fresh_due(again, {**miss, "passes": True, "word": "pass"}, T0 + timedelta(days=1))["due"] is False


def repair_rows(state):
    return [r for r in rows(state / "HISTORY.jsonl") if r["kind"] == "repair"]


def run_standing(state, pcts, name=SET):
    for i, p in enumerate(pcts):
        history(state, *lines_at([p], name))
        standing.repair_after(state, name, f"2026-W{40 + i}")


def test_a_pass_then_two_misses_opens_the_repair_and_a_later_pass_closes_it(tmp_path):
    # pass, miss, miss with the first miss under 5 points below the pass: only the second miss opens it
    run_standing(tmp_path, [96, 92])
    assert repair_rows(tmp_path) == []
    run_standing(tmp_path, [92])
    assert [r["word"] for r in repair_rows(tmp_path)] == ["MEMORY_REPAIR open"]
    run_standing(tmp_path, [92])  # a third miss opens nothing more
    assert len(repair_rows(tmp_path)) == 1
    run_standing(tmp_path, [96])
    assert [r["word"] for r in repair_rows(tmp_path)] == ["MEMORY_REPAIR open", "MEMORY_REPAIR closed"]


def test_a_miss_five_points_below_the_last_pass_opens_the_repair_at_once(tmp_path):
    run_standing(tmp_path, [96])
    history(tmp_path, *lines_at([90]))
    standing.repair_after(tmp_path, SET, "2026-W41")
    assert [(r["word"], r["week"]) for r in repair_rows(tmp_path)] == [("MEMORY_REPAIR open", "2026-W41")]


def test_a_miss_less_than_five_points_below_the_last_pass_does_not(tmp_path):
    run_standing(tmp_path, [96, 92])
    assert repair_rows(tmp_path) == []


def status_repair(plant, *extra):
    done = subprocess.run([sys.executable, "-m", "gov.memaudit", "status", "--sets-root", str(plant.root), "--repo",
                           str(plant.repo["path"]), "--repair", *extra], capture_output=True, text=True,
                          env=dict(plant.env(), GOV_INDEP_RUNS_DIR=str(plant.runs)), cwd=plant.tmp)
    return done


def test_status_repair_exits_1_while_open_then_0_after_a_pass_or_the_owners_decision(stand):
    assert status_repair(stand).stdout == "REPAIR none\n"
    run_standing(stand.state, [96, 92, 92])
    done = status_repair(stand)
    assert (done.returncode, done.stdout) == (1, "REPAIR open since 2026-W42\n")
    # a planted pass closes it without a repair line of ours
    history(stand.state, *lines_at([97]))
    assert (status_repair(stand).returncode, status_repair(stand).stdout) == (0, "REPAIR none\n")
    run_standing(stand.state, [90, 90])
    assert status_repair(stand).returncode == 1
    done = status_repair(stand, "--residual", "DEC-1")
    assert (done.returncode, done.stdout) == (0, "REPAIR residual DEC-1\n")
    assert status_repair(stand).returncode == 0
    assert rows(stand.state / "HISTORY.jsonl")[-1] == {"kind": "repair", "word": "MEMORY_REPAIR residual",
                                                       "decision": "DEC-1"}
    assert status_repair(stand, "--residual", "decision-1").returncode == 4


def test_status_without_repair_still_needs_since(stand):
    done = subprocess.run([sys.executable, "-m", "gov.memaudit", "status", "--sets-root", str(stand.root)],
                          capture_output=True, text=True, env=stand.env(), cwd=stand.tmp)
    assert done.returncode == 4


# ---- S9: state per repository, the retrieval change per repository

def test_the_state_folder_is_keyed_by_the_directory_name_and_the_hash_of_its_real_path(tmp_path):
    a, b = tmp_path / "x" / "app", tmp_path / "y" / "app"
    a.mkdir(parents=True)
    b.mkdir(parents=True)
    ka, kb = schedule.state_dir(tmp_path, a), schedule.state_dir(tmp_path, b)
    assert ka != kb and ka.parent == kb.parent == tmp_path / "indep" / "memaudit"
    import hashlib
    assert ka.name == "app-" + hashlib.sha256(os.path.realpath(a).encode()).hexdigest()[:8]
    link = tmp_path / "lnk"
    link.symlink_to(a)
    assert schedule.state_dir(tmp_path, link).name.endswith(ka.name[-8:])  # the real path, not the one given


def test_two_repositories_on_one_runs_folder_never_read_each_others_history(tmp_path):
    runs, a, b = tmp_path, tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    history(schedule.state_dir(runs, a), {"commit": "c" * 40, "measured": True})
    assert schedule.last_audit_commit(schedule.state_dir(runs, a)) == "c" * 40
    assert schedule.last_audit_commit(schedule.state_dir(runs, b)) is None


def gitrepo(tmp_path, name):
    r = tmp_path / name
    env = git_env(tmp_path)
    run("git", "init", "-q", "-b", "main", str(r), env=env)
    (r / "a.md").write_text("one\n")
    run("git", "add", "-A", cwd=r, env=env)
    run("git", "commit", "-q", "-m", "one", cwd=r, env=env)
    return r, env


def test_a_pin_change_is_a_retrieval_change_and_a_change_under_the_gov_code_is_not_for_an_adopted_repo(tmp_path,
                                                                                                    monkeypatch):
    monkeypatch.setenv("GOV_INDEP_RUNS_DIR", str(tmp_path / "runs"))
    repo, env = gitrepo(tmp_path, "adopted")
    first = run("git", "rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()
    (repo / "docs").mkdir()
    (repo / "docs" / "n.md").write_text("two\n")
    run("git", "add", "-A", cwd=repo, env=env)
    run("git", "commit", "-q", "-m", "two", cwd=repo, env=env)
    head = run("git", "rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()
    pin_a = tmp_path / "share/pin-aaaaaaaaaaaa/bin"
    pin_b = tmp_path / "share/pin-bbbbbbbbbbbb/bin"
    for pin in (pin_a, pin_b):
        pin.mkdir(parents=True)
        (pin / "gov").write_text("#!/bin/sh\n")
    gov = tmp_path / "gov"
    gov.symlink_to(pin_a / "gov")
    history(schedule.state_dir(tmp_path / "runs", repo), {"commit": first, "measured": True, "gov_pin": "pin-aaaaaaaaaaaa"})
    assert schedule.retrieval_changed(repo, first, head, gov) == []  # the same pin, no retrieval path changed
    gov.unlink()
    gov.symlink_to(pin_b / "gov")
    assert schedule.retrieval_changed(repo, first, head, gov) == ["gov-pin"]
    # a line without the field (W2-172's planted lines) is no trigger
    (schedule.state_dir(tmp_path / "runs", repo) / "HISTORY.jsonl").write_text(json.dumps({"commit": first}) + "\n")
    assert schedule.retrieval_changed(repo, first, head, gov) == []


def test_a_change_of_the_retrieval_yaml_or_the_path_map_is_a_retrieval_change_for_any_repository(tmp_path, monkeypatch):
    monkeypatch.setenv("GOV_INDEP_RUNS_DIR", str(tmp_path / "runs"))
    repo, env = gitrepo(tmp_path, "adopted")
    first = run("git", "rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()
    (repo / "governance/project").mkdir(parents=True)
    (repo / "governance/project/retrieval.yaml").write_text("pool: {}\n")
    (repo / "src/gov/retrieval").mkdir(parents=True)
    (repo / "src/gov/retrieval/x.py").write_text("x = 1\n")
    run("git", "add", "-A", cwd=repo, env=env)
    run("git", "commit", "-q", "-m", "two", cwd=repo, env=env)
    head = run("git", "rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()
    assert sorted(schedule.retrieval_changed(repo, first, head)) == ["governance/project/retrieval.yaml",
                                                                    "src/gov/retrieval/x.py"]


def test_pool_import_sets_imports_exactly_those_sets_once_and_refuses_a_standing_set(stand):
    said = []
    root = stand.root / "fixtures/evaluation"
    for name in ("alpha", "beta", "gamma"):
        shutil.copytree(stand.hidden, root / name / "hidden")
    assert pool.importing(str(stand.root), emit=said.append, sets=["alpha", "beta"]) == "ok"
    names = sorted(e.name for e in (root / "memory-pool/hidden").iterdir())
    assert len(names) == 78 and all(n.startswith(("alpha-", "beta-")) for n in names)  # the apart question left out
    assert said == ["IMPORTED 78 from 2 sets"]
    assert (stand.root / "runs/memory-pool/IMPORTED-alpha.json").is_file()
    said.clear()
    assert pool.importing(str(stand.root), emit=said.append, sets=["alpha", "gamma"]) == "refused" and said == ["MS-IMPORTED"]
    assert not any(e.name.startswith("gamma-") for e in (root / "memory-pool/hidden").iterdir())
    said.clear()
    assert pool.importing(str(stand.root), emit=said.append, sets=[SET]) == "refused" and said == ["MS-STANDING"]


def test_classes_and_pool_refuse_a_standing_set_name(stand):
    for sub in ("classes", "pool"):
        done = subprocess.run([sys.executable, "-m", "gov.memaudit", sub, "--sets-root", str(stand.root), "--audit", SET],
                              capture_output=True, text=True, env=dict(stand.env(), GOV_INDEP_RUNS_DIR=str(stand.runs)),
                              cwd=stand.tmp)
        assert (done.returncode, done.stdout) == (1, "MS-STANDING\n"), sub


def test_measure_kept_on_a_standing_set_prints_used_exits_3_and_writes_nothing(stand):
    layout.make_run(week_paths(stand))
    before = sorted(str(p) for p in stand.root.rglob("*"))
    done = subprocess.run([sys.executable, "-m", "gov.memaudit", "measure", "--sets-root", str(stand.root), "--audit", SET,
                           "--repo", str(stand.repo["path"]), "--kept", "1"], capture_output=True, text=True,
                          env=dict(stand.env(), GOV_INDEP_RUNS_DIR=str(stand.runs)), cwd=stand.tmp)
    assert (done.returncode, done.stdout) == (3, "USED\n")
    assert sorted(str(p) for p in stand.root.rglob("*")) == before


def test_the_standing_run_has_no_decision_force_or_data_flag(stand):
    for flag in (["--decision", "DEC-1"], ["--force"], ["--set", "x"], ["--baseline", "x"]):
        done = subprocess.run([sys.executable, "-m", "gov.memaudit", "standing", "run", "--sets-root", str(stand.root),
                               *flag], capture_output=True, text=True, env=stand.env(), cwd=stand.tmp)
        assert done.returncode == 4, flag


def test_standing_live_prints_the_key_then_the_live_set_and_writes_nothing(stand):
    def live():
        return subprocess.run([sys.executable, "-m", "gov.memaudit", "standing", "live", "--sets-root", str(stand.root),
                               "--repo", str(stand.repo["path"])], capture_output=True, text=True,
                              env=dict(stand.env(), GOV_INDEP_RUNS_DIR=str(stand.runs)), cwd=stand.tmp)
    done = live()
    assert (done.returncode, done.stdout) == (1, f"KEY {stand.state.name}\nLIVE none\n")
    assert not stand.state.exists()
    set_live(stand)
    done = live()
    assert (done.returncode, done.stdout) == (0, f"KEY {stand.state.name}\nLIVE {SET}\n")


# ---- S6, S8: the thin set in the digest; due and due --fresh by the command line

def test_fewer_than_70_live_questions_prints_standing_thin_in_the_block_and_70_does_not():
    from gov.memaudit import digest
    st = {"audit": SET, "week": WEEK, "commit": "a" * 40, "figures": None, "stop": None, "next": "2026-11-23",
          "next_mode": "weekly", "next_fresh": "2026-12-14", "repair": None}
    thin = digest.standing_lines({**st, "live": {"n": 69, "n_set": 80, "dropped": 11}})
    assert "QUESTIONS live 69 of 80; dropped 11" in thin and "STANDING_THIN 69" in thin
    assert not [x for x in digest.standing_lines({**st, "live": {"n": 70, "n_set": 80, "dropped": 10}})
                if x.startswith("STANDING_THIN")]
    assert thin[0] == f"STANDING {SET} week {WEEK} commit aaaaaaaaaaaa" and thin[-2:] == ["STOP none", "OWNER none"]
    assert "VERDICT not reached" in thin and "P1 none" in thin and "MAINTAIN none" in thin and "REPAIR none" in thin


def due_cli(plant, *extra):
    done = subprocess.run([sys.executable, "-m", "gov.memaudit", "due", "--sets-root", str(plant.root), "--repo",
                           str(plant.repo["path"]), "--store-link", str(plant.repo["path"]), *extra],
                          capture_output=True, text=True, cwd=plant.tmp,
                          env=dict(plant.env(), GOV_INDEP_RUNS_DIR=str(plant.runs), GOV_MEMAUDIT_NOW=schedule.stamp(T0)))
    return done.returncode, done.stdout.splitlines()


def test_due_answers_for_the_live_set_and_due_fresh_for_the_fresh_one(stand):
    assert due_cli(stand)[0] == 0  # no live set: as W2-172's due, and a first fresh start is due
    assert due_cli(stand, "--fresh") == due_cli(stand)  # with no live set --fresh answers as due
    set_live(stand)
    code, out = due_cli(stand)
    assert (code, out[0], out[2]) == (0, "MODE weekly", "REASON start")  # no standing start yet
    code, out = due_cli(stand, "--fresh")
    assert (code, out) == (0, ["MODE fresh", f"DUE yes next {T0:%Y-%m-%d}", "REASON first"])
    standing.append(stand.state, "STARTS.log", {"audit": SET, "at": schedule.stamp(T0 - timedelta(hours=1)),
                                                "kind": "standing"},
                    {"audit": "memory-audit-20261110", "at": schedule.stamp(T0 - timedelta(days=27)), "kind": "fresh"})
    code, out = due_cli(stand)
    assert (code, out[1]) == (1, "DUE no next 2026-11-22")  # the standing set's weekly cadence: six days
    code, out = due_cli(stand, "--fresh")
    assert (code, out) == (1, ["MODE fresh", "DUE no next 2026-11-23", "REASON wait"])  # 27 days: the next Monday
    standing.append(stand.state, "STARTS.log", {"audit": "memory-audit-20261109", "at": schedule.stamp(T0 - timedelta(days=28)),
                                                "kind": "fresh"})
    (stand.state / "STARTS.log").write_text("".join(json.dumps(x) + "\n" for x in (
        {"audit": SET, "at": schedule.stamp(T0 - timedelta(hours=1)), "kind": "standing"},
        {"audit": "memory-audit-20261109", "at": schedule.stamp(T0 - timedelta(days=28)), "kind": "fresh"})))
    assert due_cli(stand, "--fresh")[1] == ["MODE fresh", f"DUE yes next {T0:%Y-%m-%d}", "REASON 28d"]
    # one standing miss: the fresh set is due at once, and the P1 reason is a word in the line
    history(stand.state, {"kind": "standing", "set": SET, "week": WEEK, "measured": True, "passes": False, "word": "miss",
                          "n": 40, "right": 30, "pct": 75.0, "at": schedule.stamp(T0)})
    (stand.state / "STARTS.log").write_text(json.dumps({"audit": "f", "at": schedule.stamp(T0 - timedelta(days=10)),
                                                        "kind": "fresh"}) + "\n")
    assert due_cli(stand, "--fresh")[1][2] == "REASON miss"
