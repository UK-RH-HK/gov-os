"""W2-100, the three scenarios of each skill: success-4, failure-4 (the history and the failing-scenario halves) and
failure-2 (the harness half).

``scenarios.md`` is in ``gov skilleval``'s form (W2-104): exactly three scenarios, each ``## <n>. <title>`` and the
bullets Situation, Expected and Pass line. The real skills' scenario files, their commit order (``git log`` on the
repository the test sits in) and, once the lead's real runs have landed, the records and summaries are
repository-state cases. The harness is run only with a stub ``claude`` written in ``tmp_path``: no model, no network.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

import w2_100_support as s

BULLETS = ["Situation", "Expected", "Pass line"]


def _scenarios(skill):
    return s.need(s.skill_dir(skill) / "scenarios.md").read_text(encoding="utf-8")


# the real scenarios -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("skill", s.SKILLS)
def test_scenarios_md_holds_exactly_three_scenarios_each_with_its_three_bullets(skill):
    blocks = s.scenario_blocks(_scenarios(skill))
    assert [b[0] for b in blocks] == [1, 2, 3], f"the scenario headings are numbered {[b[0] for b in blocks]}, not 1, 2, 3"
    for n, title, bullets, order in blocks:
        assert title.strip(), f"scenario {n} has no title"
        assert order == BULLETS, f"scenario {n}: the bullets are {order}, expected {BULLETS}"
        assert all(bullets[label].strip() for label in BULLETS), f"scenario {n} has an empty bullet: {bullets}"


@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_real_scenarios_are_evaluable_by_the_harness(skill, project, base, stub):
    """The skill's SKILL.md and scenarios.md (two named files) in a temporary project, the stub as the model:
    ``gov skilleval`` reads three scenarios and runs them (exit 0), not 5 (cannot be evaluated)."""
    folder = s.need(s.skill_dir(skill) / "scenarios.md").parent
    target = project / "skills" / skill
    target.mkdir(parents=True)
    for name in ("SKILL.md", "scenarios.md"):
        shutil.copyfile(s.need(folder / name), target / name)
    run = s.run_skilleval(project, base, f"skills/{skill}", stub=stub)
    assert run.returncode == 0, run.describe()
    assert run.verdicts() == {1: "pass", 2: "pass", 3: "pass"}, run.describe()


def test_a_security_scenario_holds_a_finding_whose_pass_line_wants_p1():
    blocks = s.scenario_blocks(_scenarios("security"))
    hits = [n for n, _t, b, _o in blocks if "finding" in b["Situation"].lower() and "P1" in b["Pass line"]]
    assert hits, "no security scenario has a finding in its Situation and P1 in its Pass line"
    for n, _t, b, _o in blocks:
        if n in hits:
            assert "P2" not in b["Pass line"] and "P3" not in b["Pass line"] or "not" in b["Pass line"].lower(), (
                f"scenario {n}'s pass line accepts a route below P1: {b['Pass line']}")


# failure-4 / success-4: scenarios committed no later than the skill text ---------------------------------------------

@pytest.mark.parametrize("skill", s.SKILLS)
def test_git_log_shows_every_scenarios_file_no_later_than_the_skill_text(skill):
    problems = s.order_problems(s.REPO_ROOT, skill)
    assert not problems, f"{problems}"


@pytest.mark.parametrize("shape", ["scenarios-first", "same-commit"])
def test_a_planted_history_with_the_scenarios_first_is_accepted(tmp_path, shape):
    repo = s.plant_history(tmp_path, "backend", shape)
    assert s.order_problems(repo, "backend") == []


@pytest.mark.parametrize("shape, file_named", [("skill-first", "scenarios.md"), ("copy-late", ".rulesync/skills/backend/scenarios.md")])
def test_a_planted_history_with_the_skill_text_first_is_refused_naming_the_skill(tmp_path, shape, file_named):
    repo = s.plant_history(tmp_path, "backend", shape)
    problems = s.order_problems(repo, "backend")
    assert problems, f"the history {shape} is accepted"
    assert all(p.startswith("backend:") for p in problems), f"the refusal does not name the skill: {problems}"
    assert any(file_named in p for p in problems), f"the refusal does not name {file_named}: {problems}"


def test_a_planted_history_naming_another_skill_is_refused_for_the_missing_skill(tmp_path):
    repo = s.plant_history(tmp_path, "backend", "scenarios-first")
    problems = s.order_problems(repo, "api")
    assert problems and all(p.startswith("api:") for p in problems), f"{problems}"


# failure-4 (the failing-scenario half) and success-4 on the harness --------------------------------------------------

def _plant(project, name, judge_fail_on=(), finding=False, skill_text=None):
    return s.plant_skill(project, f"skills/{name}", name, s.planted_scenarios(name, finding, judge_fail_on), skill_text)


def test_a_skill_with_a_failing_scenario_ends_3_names_the_skill_and_is_recorded_as_failed(project, base, stub):
    _plant(project, "backend", judge_fail_on=(2,))
    s.write_imports(project, [s.import_entry("backend", adopted=False)])
    run = s.run_skilleval(project, base, "skills/backend", stub=stub)
    assert run.returncode == 3, run.describe()
    assert run.result()["skill"] == "backend", run.describe()
    assert run.verdicts() == {1: "pass", 2: "fail", 3: "pass"}, run.describe()
    records = s.load_yaml(project / "skills/backend/scenario-records.yaml")["records"]
    assert [(r["scenario"], r["verdict"]) for r in records] == [(1, "pass"), (2, "fail"), (3, "pass")], records
    assert s.read_imports(project)["backend"]["adopted"] is False, "a failing skill was adopted"


def test_the_same_skill_with_three_passing_scenarios_ends_0(project, base, stub):
    """The control of the case above: only the failing scenario differs."""
    _plant(project, "backend")
    run = s.run_skilleval(project, base, "skills/backend", stub=stub)
    assert run.returncode == 0 and run.verdicts() == {1: "pass", 2: "pass", 3: "pass"}, run.describe()


# failure-2 (the harness half): a security finding routed P2 fails the scenario ----------------------------------------

def test_a_security_scenario_with_a_finding_passes_when_the_skill_routes_it_p1(project, base, stub):
    _plant(project, "security", finding=True, skill_text=s.build_skill("security"))
    run = s.run_skilleval(project, base, "skills/security", stub=stub)
    assert run.returncode == 0 and run.verdicts() == {1: "pass", 2: "pass", 3: "pass"}, run.describe()


def test_a_planted_security_copy_that_routes_the_finding_p2_fails_the_scenario_and_ends_3(project, base, stub):
    bad = s.insert_line(s.build_skill("security"), "- A finding of low impact is a P2.", "body")
    _plant(project, "security", finding=True, skill_text=bad)
    run = s.run_skilleval(project, base, "skills/security", stub=stub)
    assert run.returncode == 3, run.describe()
    assert run.verdicts()[2] == "fail", run.describe()
    assert run.result()["skill"] == "security", run.describe()


# success-4: the records and the summaries (the lead's real runs) -------------------------------------------------------

@pytest.mark.parametrize("skill", s.SKILLS)
def test_each_scenarios_last_record_passes_and_the_summaries_hold_its_entry(skill):
    """Waits for the lead's real ``gov skilleval`` runs (records) and the hand-written summaries beside them."""
    folder = s.need(s.skill_dir(skill) / "SKILL.md").parent
    problems = s.record_problems(folder, skill)
    assert not problems, f"{problems}"


def _planted_records(folder, last_verdict=None, run_ats=("2026-11-14T10:00:01Z", "2026-11-14T10:00:02Z", "2026-11-14T10:00:03Z")):
    entries = [{"skill": "backend", "skill_version": "1.0.0", "scenario": 2, "title": "Second", "verdict": "fail",
                "cause": "the reply missed the pass line", "cost_usd": 0.3, "seconds": 9.0, "model": "m", "effort": "high",
                "run_at": "2026-11-14T09:00:00Z"}]
    for n, run_at in zip((1, 2, 3), run_ats):
        verdict = last_verdict.get(n, "pass") if last_verdict else "pass"
        entries.append({"skill": "backend", "skill_version": "1.0.0", "scenario": n, "title": f"Title {n}" if n != 2 else "Second",
                        "verdict": verdict, "cause": None if verdict == "pass" else "x", "cost_usd": 0.3, "seconds": 9.0,
                        "model": "m", "effort": "high", "run_at": run_at})
    (folder / s.RECORD_FILE).write_text(yaml.safe_dump({"records": entries}, sort_keys=False), encoding="utf-8")


def _entry(n, title, verdict="pass", run_at=None, lines=("one", "two", "three")):
    run_at = run_at or f"2026-11-14T10:00:0{n}Z"
    body = "\n".join(f"  {line}" for line in lines)
    return f"## Scenario {n}: {title}\n- verdict: {verdict}\n- run_at: {run_at}\n- summary:\n{body}\n"


def _planted_summaries(folder, skip=(), changes=None):
    titles = {1: "Title 1", 2: "Second", 3: "Title 3"}
    parts = ["# Scenario summaries\n", _entry(2, "Second", "fail", "2026-11-14T09:00:00Z")]
    parts += [_entry(n, titles[n], **(changes or {}).get(n, {})) for n in (1, 2, 3) if n not in skip]
    (folder / s.SUMMARY_FILE).write_text("\n".join(parts), encoding="utf-8")


def _folder(tmp_path):
    folder = tmp_path / "backend"
    folder.mkdir()
    return folder


def test_the_records_reader_accepts_a_good_planted_pair_with_an_older_failed_run(tmp_path):
    folder = _folder(tmp_path)
    _planted_records(folder)
    _planted_summaries(folder)
    assert s.record_problems(folder, "backend") == []


@pytest.mark.parametrize("defect", ["last-record-fails", "summary-missing-3", "summary-run-at-differs",
                                    "summary-verdict-fail", "summary-two-lines", "no-summary-file", "no-records-file",
                                    "wrong-skill"])
def test_the_records_reader_refuses_a_planted_pair_with_one_defect(tmp_path, defect):
    folder = _folder(tmp_path)
    _planted_records(folder, last_verdict={3: "fail"} if defect == "last-record-fails" else None)
    if defect == "summary-missing-3":
        _planted_summaries(folder, skip=(3,))
    elif defect == "summary-run-at-differs":
        _planted_summaries(folder, changes={2: {"run_at": "2026-11-14T10:00:09Z"}})
    elif defect == "summary-verdict-fail":
        _planted_summaries(folder, changes={1: {"verdict": "fail"}})
    elif defect == "summary-two-lines":
        _planted_summaries(folder, changes={3: {"lines": ("one", "two")}})
    elif defect != "no-summary-file":
        _planted_summaries(folder)
    if defect == "no-records-file":
        (folder / s.RECORD_FILE).unlink()
    problems = s.record_problems(folder, "api" if defect == "wrong-skill" else "backend")
    assert problems, f"the planted pair with the defect {defect} is accepted"
