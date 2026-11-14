"""W2-187 I4, I6 at run scale (S2, S3, S4, S5, S6, F1, F2): ``standing run`` on a planted repository with a fake ``gov`` and a
fake ``claude`` (never a real search, a real model call or the real sets root)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

from gov.memaudit import judge, layout, matcher, prompts, schedule, standing

from .conftest import git_env, run
from .fakes import FakeClaude, FakeGov, plant_audit, plant_control
from .test_measure import snapshot

SET = "memory-standing-20261111"
UNIQUE_IDS = ("q03", "q07", "q10", "q12", "q15")


class Standing:
    """A plant with a standing set (a copy of the plant's 40, five questions in unique words), a store link, the fake
    ``gov`` and ``claude``, and the set declared."""

    def __init__(self, plant, monkeypatch, broken=()):
        self.plant = plant
        monkeypatch.setenv("GOV_INDEP_RUNS_DIR", str(plant.runs))
        monkeypatch.delenv("GOV_MEMAUDIT_STATE", raising=False)
        self.planted = []
        shutil.copytree(plant.hidden, plant.root / "fixtures/evaluation" / SET / "hidden")
        self.hidden = plant.root / "fixtures/evaluation" / SET / "hidden"
        for qid in UNIQUE_IDS:
            q = plant.questions[qid]
            q["question"], q["gold_answer"] = f"uniqq{qid}zephyr?", f"uniqgold{qid}marmot"
            self.rewrite(qid, q)
            self.planted += [q["question"], q["gold_answer"], f"uniqans{qid}narwhal"]
        for qid in broken:  # a gold anchor that no longer resolves at the audit commit
            q = dict(plant.questions[qid])
            q["sources"] = [{"path": "docs/gone/missing.md", "lines": [1, 2]}]
            self.rewrite(qid, q)
        self.head, self.repo = plant.repo["head"], plant.repo["path"]
        self.link = plant.tmp / "link"
        run("git", "clone", "-q", str(self.repo), str(self.link), env=plant.repo["env"])
        (self.link / ".gov-runtime").mkdir()
        shutil.copy(plant.store, self.link / ".gov-runtime/store.db")
        self.fake = FakeGov(plant)
        plant_control(plant, self.fake)
        plant_audit(plant, self.fake)
        self.fake.plan["store_commit"] = self.head
        self.fake.save()
        self.claude = FakeClaude(plant)
        for qid in UNIQUE_IDS:
            self.claude.plan["readers"][plant.questions[qid]["question"]] = {"steps": [
                self.claude.answer(qid, f"RIGHT uniqans{qid}narwhal")]}
        self.claude.save()
        ct = int(run("git", "show", "-s", "--format=%ct", self.head, cwd=self.repo, env=plant.repo["env"]).stdout)
        self.now = datetime.fromtimestamp(ct, timezone.utc) + timedelta(hours=1)
        self.week = standing.week_of(self.now)
        self.state = schedule.state_dir(plant.runs, self.repo)
        for kind in ("writer", "checker"):
            folder = plant.runs / "indep" / kind / "r1"
            folder.mkdir(parents=True)
            (folder / "counts.json").write_text(json.dumps(
                {"status": "delivered", "set": SET, "brief_sha256": kind[0] * 64, "commit": self.head}))
        assert standing.declare(str(plant.root), SET, repo=self.repo, runs_dir=plant.runs)[0] == "ok"
        self.run_dir = plant.root / "runs" / SET / self.week

    def rewrite(self, qid, q):
        (self.hidden / f"{qid}.yaml").write_text(yaml.safe_dump(q, sort_keys=False), encoding="utf-8")

    def env(self, **more):
        return dict(self.plant.env(), GOV_INDEP_RUNS_DIR=str(self.plant.runs),
                    GOV_MEMAUDIT_NOW=self.now.strftime("%Y-%m-%dT%H:%M:%SZ"), **more)

    def standing_run(self, *extra):
        return subprocess.run(
            [sys.executable, "-m", "gov.memaudit", "standing", "run", "--sets-root", str(self.plant.root), "--repo",
             str(self.repo), "--store-link", str(self.link), "--gov", str(self.plant.gov), "--claude",
             str(self.claude.exe), *extra], capture_output=True, text=True, env=self.env(), cwd=self.plant.tmp)

    def history(self):
        path = self.state / "HISTORY.jsonl"
        return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

    def tree(self):
        return {**{f"sets/{k}": v for k, v in snapshot(self.plant.root).items()},
                **{f"runs/{k}": v for k, v in snapshot(self.plant.runs).items()}}


@pytest.fixture
def stand(plant, monkeypatch):
    return Standing(plant, monkeypatch)


def test_a_standing_run_judges_the_live_set_once_and_prints_the_digest_and_the_last_line(stand):
    done = stand.standing_run()
    assert done.returncode == 0, done.stdout + done.stderr
    out = done.stdout.splitlines()
    assert out[-1] == f"STANDING {stand.week} right 40 of 40: passes"
    block = [x for x in out if x.startswith(("STANDING ", "VERDICT right", "MISSES ", "QUESTIONS ", "BESIDE hit5", "MAINTAIN",
                                             "P1 ", "REPAIR ", "NEXT ", "STOP ", "OWNER "))]
    assert block[0] == f"STANDING {SET} week {stand.week} commit {stand.head[:12]}"
    assert "VERDICT right 40 of 40; wrong 0; not found 1; bar 38 right: passes" in out
    assert "QUESTIONS live 40 of 40; dropped 0" in out and "STANDING_THIN 40" in out  # under 70: asks a replacement
    assert "P1 none" in out and "REPAIR none" in out and "STOP none" in out and "OWNER none" in out
    assert any(x.startswith("NEXT standing ") and "; fresh " in x for x in out)
    digest = (stand.state / "standing" / SET / stand.week / "DIGEST.txt").read_text().splitlines()
    assert digest and all(x in out for x in digest)  # the block as written is the block printed
    line = stand.history()[-1]
    assert line["kind"] == "standing" and line["set"] == SET and line["week"] == stand.week and line["audit"] == SET
    assert (line["n"], line["right"], line["wrong"], line["dropped"], line["pct"], line["word"]) == (40, 40, 0, 0, 100.0,
                                                                                                    "pass")
    assert line["measured"] is True and line["used"] is True and line["passes"] is True
    assert line["flags"] == ["STANDING_THIN 40"] and line["gov_pin"] == "pin-0123456789ab"
    assert line["retrieval_yaml_sha256"] and line["path_map_sha256"] and line["pool_regression"] is False
    starts = [json.loads(x) for x in (stand.state / "STARTS.log").read_text().splitlines()]
    assert starts[-1]["kind"] == "standing" and starts[-1]["week"] == stand.week


def test_the_declaration_comes_before_used_before_the_first_search(stand):
    assert stand.standing_run().returncode == 0
    from gov.memaudit import ledger
    events = [e["event"] for e in ledger.read(stand.run_dir)]
    assert events.index("declaration") < events.index("used") < events.index("search")
    assert (stand.run_dir / "DECLARATION.json").stat().st_mtime_ns < (stand.run_dir / "USED").stat().st_mtime_ns
    decl = json.loads((stand.run_dir / "DECLARATION.json").read_text())
    assert decl["standing"] is True and decl["n"] == 40 and decl["n_set"] == 40 and decl["dropped"] == 0
    assert decl["bar"] == {"need_right": 38, "max_wrong": 2, "target_right": 38}
    assert oct(stand.run_dir.stat().st_mode & 0o777) == "0o700" and oct(stand.run_dir.parent.stat().st_mode & 0o777) == "0o700"


def test_a_second_run_in_the_same_week_exits_3_and_writes_nothing(stand):
    assert stand.standing_run().returncode == 0
    before = stand.tree()
    done = stand.standing_run()
    assert (done.returncode, done.stdout) == (3, "USED\n")
    assert stand.tree() == before
    assert len(stand.history()) == 1


def test_five_planted_misses_leave_only_counts_in_every_line_and_file_outside_the_run_folder(plant, monkeypatch):
    kinds = {"q03": "wrong", "q07": "wrong", "q10": "notfound", "q12": "notfound", "q15": "uncited"}
    s = Standing(plant, monkeypatch)
    for qid, kind in kinds.items():
        s.claude.plan["readers"][plant.questions[qid]["question"]] = {"steps": [
            s.claude.answer(qid, f"WRONG uniqans{qid}narwhal") if kind == "wrong" else
            {"verdict": "not_found", "answer": "", "citations": [], "search": ""} if kind == "notfound" else
            s.claude.answer(qid, f"RIGHT uniqans{qid}narwhal", gold=False)]}
    s.claude.save()
    done = s.standing_run()
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.splitlines()[-1] == f"STANDING {s.week} right 35 of 40: misses"
    seen = done.stdout + done.stderr
    ours = plant.root / "runs" / SET
    for root in (plant.runs, plant.root):
        for f in sorted(root.rglob("*")):
            if f.is_file() and ours not in f.parents and "fixtures" not in f.relative_to(root).parts:
                seen += f.read_text(errors="replace")
    assert not [x for x in s.planted + list(kinds) if x in seen], [x for x in s.planted + list(kinds) if x in seen]
    figures = json.loads((s.run_dir / "FIGURES.json").read_text())
    assert figures["verdict"]["right"] == 35 and figures["misses"]["total"] == 5
    assert not list(plant.root.rglob("misses.jsonl")) and not list(plant.root.rglob("miss-classes.json"))
    out = done.stdout.splitlines()
    assert "P1 memory below 95 %: wrong 2 incomplete 1 not_found 2" in out
    assert any(x.startswith("MISSES outcome wrong ") and "; rank 1-5 " in x and " absent " in x for x in out)
    line = s.history()[-1]
    assert (line["word"], line["passes"], line["right"], line["n"]) == ("miss", False, 35, 40)


@pytest.mark.parametrize("wrong,word", [(2, "pass"), (3, "miss")])
def test_right_at_the_need_right_passes_and_one_under_it_misses(plant, monkeypatch, wrong, word):
    s = Standing(plant, monkeypatch)
    for qid in ("q01", "q02", "q04")[:wrong]:
        s.claude.script(qid, "notfound")
    s.claude.save()
    done = s.standing_run()
    assert done.returncode == 0, done.stdout + done.stderr  # a miss is data, not a failure
    need = 38
    right = 40 - wrong
    assert done.stdout.splitlines()[-1] == f"STANDING {s.week} right {right} of 40: " + ("passes" if word == "pass" else "misses")
    assert (right >= need) == (word == "pass")
    assert s.history()[-1]["word"] == word


def test_three_broken_anchors_are_dropped_by_count_and_the_set_is_never_edited(plant, monkeypatch):
    s = Standing(plant, monkeypatch, broken=("q21", "q22", "q23"))
    digest = declare_digest(s)
    done = s.standing_run()
    assert done.returncode == 0, done.stdout + done.stderr
    out = done.stdout.splitlines()
    assert "QUESTIONS live 37 of 40; dropped 3" in out and "STANDING_THIN 37" in out
    pre = json.loads((s.run_dir / "PREFLIGHT.json").read_text())
    assert (pre["n"], pre["n_set"], pre["dropped"], len(pre["dropped_ids"])) == (37, 40, 3, 3)
    assert sorted(pre["dropped_ids"]) == ["q21", "q22", "q23"]
    assert not [x for x in out if any(i in x for i in pre["dropped_ids"])]  # no id is printed
    assert declare_digest(s) == digest  # nothing in the set is edited
    assert s.history()[-1]["n"] == 37 and s.history()[-1]["dropped"] == 3
    assert json.loads((s.run_dir / "DECLARATION.json").read_text())["n"] == 37


def declare_digest(s):
    from gov.memaudit.common import set_digest
    return set_digest(s.hidden)


def test_an_edited_set_is_refused_before_any_search_and_the_week_is_not_spent(stand):
    q = yaml.safe_load((stand.hidden / "q01.yaml").read_text())
    q["gold_answer"] = "edited after the record"
    stand.rewrite("q01", q)
    before = stand.tree()
    done = stand.standing_run()
    assert (done.returncode, done.stdout) == (1, "STANDING_DIGEST\n")
    assert stand.tree() == before and stand.fake.calls() == []
    assert not stand.run_dir.exists()


def test_a_result_from_another_store_commit_makes_the_attempt_a_fault_and_one_restart_goes_on(stand):
    question = stand.plant.questions["q05"]["question"]
    stand.fake.override(question, 1, store_commit="f" * 40)
    stand.fake.save()
    done = stand.standing_run()
    assert done.returncode == 0, done.stdout + done.stderr
    said = (stand.state / "standing" / SET / stand.week / "measure.out").read_text().splitlines()
    assert any(x.startswith("FAULT attempt-1: store_commit") for x in said)  # a child's lines are its step file's
    assert done.stdout.splitlines()[-1].endswith("right 40 of 40: passes")
    assert (stand.run_dir / "attempt-1" / "FAULT").read_text().strip() == "store_commit"
    assert (stand.run_dir / "COUNTS").read_text().strip() == "attempt-2"


def test_a_stop_before_the_reader_run_allows_one_restart_in_the_week_and_a_second_is_refused(stand):
    question = stand.plant.questions["q05"]["question"]
    for nth in (1, 2):
        stand.fake.override(question, nth, store_commit="f" * 40)
    stand.fake.save()
    first = stand.standing_run()
    assert first.returncode == 2 and "STOPPED measure 2" in first.stdout.splitlines(), first.stdout
    assert "STOPPED fault" in (stand.state / "standing" / SET / stand.week / "measure.out").read_text().splitlines()
    assert "OWNER stopped after USED at measure exit 2: the set is not run again" in first.stdout.splitlines()
    assert (stand.run_dir / "STOPPED").is_file() and not (stand.run_dir / "reader").exists()
    assert stand.history()[-1]["measured"] is False
    again = stand.standing_run()  # the fake's later answers are from the declared store: the restart runs through
    assert again.returncode == 0, again.stdout + again.stderr
    assert (stand.run_dir.parent / f"{stand.week}.stopped").is_dir() and (stand.run_dir / "reader").is_dir()
    third = stand.standing_run()
    assert (third.returncode, third.stdout) == (3, "USED\n")


def test_a_gate_that_stays_shut_stops_before_measure_and_the_week_is_not_spent(stand):
    shut = stand.plant.tmp / "shut.sh"
    shut.write_text("#!/bin/sh\nexit 1\n")
    shut.chmod(0o755)
    done = subprocess.run(
        [sys.executable, "-m", "gov.memaudit", "standing", "run", "--sets-root", str(stand.plant.root), "--repo",
         str(stand.repo), "--store-link", str(stand.link), "--gov", str(stand.plant.gov), "--claude", str(stand.claude.exe),
         "--gate-cmd", str(shut)], capture_output=True, text=True, cwd=stand.plant.tmp,
        env=stand.env(GOV_MEMAUDIT_GATE_MAX_S="1", GOV_MEMAUDIT_GATE_POLL_S="1"))
    assert done.returncode == 2 and "STOPPED measure gate busy" in done.stdout.splitlines()
    assert not (stand.run_dir / "USED").exists() and not stand.history()
    assert stand.standing_run().returncode == 0  # the week was not spent


def test_a_run_with_no_live_set_is_refused_with_its_code_and_writes_nothing(plant, monkeypatch):
    monkeypatch.setenv("GOV_INDEP_RUNS_DIR", str(plant.runs))
    ct = datetime.now(timezone.utc)
    done = subprocess.run(
        [sys.executable, "-m", "gov.memaudit", "standing", "run", "--sets-root", str(plant.root), "--repo",
         str(plant.repo["path"]), "--store-link", str(plant.repo["path"])], capture_output=True, text=True,
        env=dict(plant.env(), GOV_INDEP_RUNS_DIR=str(plant.runs), GOV_MEMAUDIT_NOW=ct.strftime("%Y-%m-%dT%H:%M:%SZ")),
        cwd=plant.tmp)
    assert (done.returncode, done.stdout) == (1, "STANDING_NONE\n")
    assert not schedule.state_dir(plant.runs, plant.repo["path"]).exists()


def test_the_judged_path_is_the_fresh_audits_one_a_spy_sees_the_same_functions_called(stand, monkeypatch):
    """One path, two modes: a standing week is judged by ``_Judge.one``, ``prompts.prompt_of`` and ``matcher.cited``."""
    monkeypatch.setenv("GOV_ROLE", "orchestrator")
    calls = []
    for owner, name in ((judge._Judge, "one"), (judge._Judge, "grade"), (prompts, "prompt_of"), (matcher, "cited")):
        real = getattr(owner, name)

        def spy(*a, _real=real, _name=name, **kw):
            calls.append(_name)
            return _real(*a, **kw)
        monkeypatch.setattr(owner, name, spy)
    p = layout.paths(str(stand.plant.root), SET, stand.week)
    for sub in (["preflight", "--repo", str(stand.repo), "--commit", stand.head],
                ["measure", "--repo", str(stand.repo), "--commit", stand.head, "--store",
                 str(stand.link / ".gov-runtime/store.db"), "--gov", str(stand.plant.gov)]):
        done = subprocess.run([sys.executable, "-m", "gov.memaudit", sub[0], "--sets-root", str(stand.plant.root), "--audit", SET,
                               "--week", stand.week, *sub[1:]], capture_output=True, text=True, env=stand.env(),
                              cwd=stand.plant.tmp)
        assert done.returncode == 0, done.stdout + done.stderr
    said = []
    assert judge.run(str(stand.plant.root), SET, repo=stand.repo, gov=str(stand.plant.gov), claude=str(stand.claude.exe),
                     emit=said.append, week=stand.week) == "ok"
    assert {"one", "grade", "prompt_of", "cited"} <= set(calls) and p["run"] == stand.run_dir
    assert not (stand.run_dir / "misses.jsonl").exists()
    assert not [x for x in said if any(s in x for s in stand.planted)]
