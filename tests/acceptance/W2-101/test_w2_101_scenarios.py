"""W2-101: the scenarios: success-4 and failure-3's commit-order half.

``scenarios.md`` is in W2-11's form (three ``## <n>. <title>`` headings, each with the bullets Situation, Expected and
Pass line); ``gov skilleval`` parses it. The commit-order half reads ``git log`` with ``w2_101_support.commit_order_problem``:
on the real history of the repository the test sits in (**repository-state**), and on planted histories under
``tmp_path`` (the same reading). The records and the summaries arrive after the real ``gov skilleval`` runs, late in the
ticket: their cases are **repository-state** and red until then.
"""
from __future__ import annotations

import re
import shutil

import pytest

import w2_101_support as s

SKILLS = pytest.mark.parametrize("skill", s.SKILLS)
HEADING = re.compile(r"^## (\d+)\.\s+(\S.*?)\s*$")
BULLET = re.compile(r"^- \*\*(Situation|Expected|Pass line):\*\*\s*(.*)$")


def _scenarios(skill):
    """``[{n, title, Situation, Expected, Pass line}]`` read as ``gov skilleval`` reads the file."""
    out, field = [], None
    for line in s.need(s.skill_dir(skill) / s.SCENARIOS_FILE).read_text(encoding="utf-8").splitlines():
        heading, bullet = HEADING.match(line), BULLET.match(line)
        if heading:
            out.append({"n": int(heading.group(1)), "title": heading.group(2)})
            field = None
        elif line.startswith("#"):
            field = None
        elif bullet and out:
            field = bullet.group(1)
            out[-1][field] = bullet.group(2).strip()
        elif field and line[:1].isspace() and line.strip():
            out[-1][field] = f"{out[-1][field]} {line.strip()}".strip()
        else:
            field = None
    return out


# the scenario file's form -------------------------------------------------------------------------------------------------

@SKILLS
def test_the_scenarios_file_holds_three_complete_scenarios_in_the_form_skilleval_reads(skill):
    found = _scenarios(skill)
    assert [item["n"] for item in found] == [1, 2, 3], f"the headings are not '## 1.' to '## 3.': {found}"
    for item in found:
        for field in ("Situation", "Expected", "Pass line"):
            assert item.get(field), f"scenario {item['n']} has no {field} bullet: {item}"
        assert item["title"].strip()


@SKILLS
def test_gov_skilleval_accepts_the_real_scenarios_and_runs_three_sessions(skill, project, stub, tmp_path):
    """The real SKILL.md and scenarios.md copied into a planted project run with the stub model: exit 0, three
    passes, six model calls (a session and a judgement each). The real folder is never written."""
    source = s.skill_dir(skill)
    folder = project / "skills" / skill
    folder.mkdir(parents=True)
    for name in ("SKILL.md", s.SCENARIOS_FILE):
        shutil.copyfile(s.need(source / name), folder / name)
    run = s.skilleval(project, tmp_path / "sandbox", stub, f"skills/{skill}")
    assert run.returncode == 0, run.describe()
    assert run.verdicts() == {1: "pass", 2: "pass", 3: "pass"}, run.describe()
    calls = stub.calls()
    assert [c["role"] for c in calls].count("session") == 3 and [c["role"] for c in calls].count("judge") == 3, \
        f"expected three sessions and three judgements: {[c['role'] for c in calls]}"
    situations = [item["Situation"] for item in _scenarios(skill)]
    sessions = [c["stdin"] for c in calls if c["role"] == "session"]
    assert all(any(situation[:60] in prompt for prompt in sessions) for situation in situations), \
        "a scenario's Situation did not reach a session"


# success-4: scenarios committed no later than the skill text (the real history; repository-state) ----------------------------

@SKILLS
def test_the_real_history_commits_the_scenarios_no_later_than_the_skill_text(skill):
    problem = s.commit_order_problem(s.REPO_ROOT, skill)
    assert problem is None, problem


# failure-3 (the commit-order half): planted histories, the same reading ---------------------------------------------------------

@SKILLS
def test_a_planted_history_with_the_skill_text_first_is_refused_naming_the_skill(skill, tmp_path):
    repo = s.plant_history(tmp_path, skill, "skill-first")
    problem = s.commit_order_problem(repo, skill)
    assert problem is not None and skill in problem, f"the reading does not refuse and name {skill}: {problem!r}"


@SKILLS
@pytest.mark.parametrize("order", ["scenarios-first", "same"])
def test_a_planted_history_with_the_scenarios_first_or_beside_the_text_is_accepted(skill, order, tmp_path):
    repo = s.plant_history(tmp_path, skill, order)
    assert s.commit_order_problem(repo, skill) is None


def test_the_reading_names_a_missing_file_and_a_shallow_history(tmp_path):
    repo = s.plant_history(tmp_path, "frontend", "same")
    gone = s.commit_order_problem(repo, "devops")
    assert gone is not None and "devops" in gone, f"an absent skill is not named: {gone!r}"
    # the planted history made shallow (a .git/shallow file naming its head): its history cannot show the order
    head = s.git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / ".git" / "shallow").write_text(head + "\n", encoding="utf-8")
    problem = s.commit_order_problem(repo, "frontend")
    assert problem is not None and "shallow" in problem, f"a shallow history is not named: {problem!r}"


# success-4: the scenario record and the summaries (repository-state: red until the real runs) -----------------------------------

def _last_three(skill):
    records = s.records_of(skill)
    assert len(records) >= 3, f"{skill}'s {s.RECORD_FILE} holds {len(records)} entries, expected the three of one run"
    last = records[-3:]
    assert [r.get("scenario") for r in last] == [1, 2, 3], f"the last three entries are not scenarios 1, 2, 3: {last}"
    return last


@SKILLS
def test_the_scenario_record_holds_three_passing_entries_of_this_skill(skill):
    version = s.split_frontmatter(s.read_skill(skill))[0].get("version")
    for entry in _last_three(skill):
        assert entry.get("skill") == skill, f"an entry is for another skill: {entry}"
        assert entry.get("verdict") == "pass", f"scenario {entry.get('scenario')} did not pass: {entry}"
        assert str(entry.get("run_at") or "").strip(), f"an entry has no run_at: {entry}"
        assert str(entry.get("skill_version")) == str(version), \
            f"the entry was run on version {entry.get('skill_version')}, the skill is at {version}: {entry}"


@SKILLS
def test_the_summaries_hold_an_entry_with_a_three_line_summary_for_each_recorded_run(skill):
    """``scenario-summaries.md`` beside the record: for each of the last three entries its ``run_at`` stands in the
    file, with the scenario's number, the verdict ``pass`` and a summary of at least three lines within the entry
    (read as the window of lines around the ``run_at`` line, up to six before and eight after, cut at the next
    entry's ``run_at``)."""
    text = s.need(s.skill_dir(skill) / s.SUMMARY_FILE).read_text(encoding="utf-8")
    lines = text.splitlines()
    entries = _last_three(skill)
    at = {}
    for entry in entries:
        run_at = str(entry["run_at"])
        hits = [i for i, line in enumerate(lines) if run_at in line]
        assert hits, f"{s.SUMMARY_FILE} does not hold run_at {run_at} of scenario {entry['scenario']}"
        at[entry["scenario"]] = hits[0]
    stops = sorted(at.values())
    for entry in entries:
        n, here = entry["scenario"], at[entry["scenario"]]
        later = [i for i in stops if i > here]
        window = lines[max(0, here - 6):min(later[0] if later else len(lines), here + 9)]
        block = "\n".join(window)
        for other in entries:
            block = block.replace(str(other["run_at"]), "")
        assert re.search(rf"(?<![\d.])0?{n}(?![\d:-])", block), f"the entry at run_at {entry['run_at']} does not name scenario {n}"
        assert re.search(r"\bpass(ed)?\b", block, re.I), f"the entry for scenario {n} does not state the verdict pass"
        assert sum(1 for line in window if line.strip()) >= 4, \
            f"the entry for scenario {n} holds no three-line summary beside its fields: {window}"
