"""KPI success 1 and 4, failure F1: the three scenarios run, are judged, and are recorded beside the skill.

Success 1 [DEC-959 item 5, ROLES-RESEARCH-1 §5.3 item 13]: "``gov skilleval <skill>`` runs each of the skill's
three committed scenarios on a fresh session with only that skill loaded (the model and effort from the role
defaults), judges each against its stated pass line, and writes a scenario record (skill version, scenario,
verdict, cost, time) beside the skill".

Success 4 [DEC-959 item 5]: "Planted skills with a passing and a failing scenario give the expected verdicts,
in a temporary project, with a stub model".

F1: "A scenario reported as passing that did not run, or failed." The not-run half is in
``test_w2_104_not_run.py``; the failed half is here.
"""

from __future__ import annotations

from pathlib import Path

import w2_104_support as support

SKILL_REL = "skills/alpha"
SKILL_NAME = "alpha-skill"
VERSION = "1.4.0"
FORBIDDEN_ARGS = ("--resume", "--continue", "-r", "-c")


def _plant_passing(project, wrap_situation=False):
    return support.plant_skill(project, SKILL_REL, SKILL_NAME, support.three(), version=VERSION,
                               wrap_situation=wrap_situation)


def _plant_neighbours(project):
    """Other skills the session must not see: one beside it, one in the project's own ``.claude/skills``."""
    support.plant_skill(project, "skills/beta", "beta-skill", support.three())
    support.plant_skill(project, ".claude/skills/gamma", "gamma-skill", support.three())


def _pair(argv, option):
    """The value that follows ``option`` in ``argv``, or None."""
    return argv[argv.index(option) + 1] if option in argv and argv.index(option) + 1 < len(argv) else None


def test_a_passing_skill_ends_0_with_three_passes_in_the_envelope(project, sandbox, stub):
    folder = _plant_passing(project)

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ALL_PASSED, run.describe()
    assert run.envelope().get("ok") is True, run.describe()
    result = run.result()
    assert result["skill"] == SKILL_NAME and str(result["skill_version"]) == VERSION, result
    assert result["adopted"] is None, f"adopted is not null without --adopt: {result}"
    assert run.verdicts() == {1: "pass", 2: "pass", 3: "pass"}, run.describe()
    for item in result["scenarios"]:
        missing = [field for field in support.SCENARIO_FIELDS if field not in item]
        assert not missing, f"an envelope scenario lacks {missing}: {item}"
        assert item["title"] == f"Planted case {item['scenario']}", item
        assert support.is_number(item["seconds"]), item
        support.assert_verdict_fields(item)
    assert support.resolve_record(run, project) == (folder / support.RECORD_FILE).resolve(), result["record"]


def test_the_record_beside_the_skill_has_one_entry_per_scenario(project, sandbox, stub):
    folder = _plant_passing(project)

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ALL_PASSED, run.describe()
    entries = support.records(folder)
    assert len(entries) == 3, f"expected three record entries, one per scenario: {entries}"
    by_number = support.last_entries(folder)
    for n, entry in by_number.items():
        support.assert_entry_shape(entry, run, SKILL_NAME, VERSION)
        assert entry["verdict"] == "pass", entry
        assert entry["cost_usd"] >= 0, entry


def test_a_second_run_appends_and_keeps_the_earlier_entries(project, sandbox, stub):
    folder = _plant_passing(project)
    first = support.skilleval(project, sandbox, SKILL_REL, stub=stub)
    assert first.returncode == support.EXIT_ALL_PASSED, first.describe()
    earlier = support.records(folder)

    second = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert second.returncode == support.EXIT_ALL_PASSED, second.describe()
    entries = support.records(folder)
    assert len(entries) == 6, f"the second run did not append three entries: {entries}"
    assert entries[:3] == earlier, "the earlier entries were not kept as written"
    for entry in entries[3:]:
        support.assert_entry_shape(entry, second, SKILL_NAME, VERSION)


def test_each_scenario_runs_on_a_fresh_session_with_only_that_skill_loaded(project, sandbox, stub):
    folder = _plant_passing(project)
    _plant_neighbours(project)
    skill_text = (folder / "SKILL.md").read_text(encoding="utf-8")

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ALL_PASSED, run.describe()
    sessions = stub.sessions()
    assert len(sessions) == 3, f"expected three session processes, one per scenario: {len(sessions)}"
    folders = [Path(entry["cwd"]).resolve() for entry in sessions]
    assert len(set(folders)) == 3, f"the sessions did not each run in a new folder: {folders}"
    for entry, cwd in zip(sessions, folders):
        assert not cwd.is_relative_to(project.resolve()), f"a session ran inside the project: {cwd}"
        assert not any(arg in FORBIDDEN_ARGS for arg in entry["argv"]), f"a session resumed: {entry['argv']}"
        assert list(entry["skills"]) and len(entry["skills"]) == 1, \
            f"the session's .claude/skills/ does not hold exactly one folder: {entry['skills']}"
        (name, files), = entry["skills"].items()
        assert files is not None and "SKILL.md" in files, f"the one skill folder holds no SKILL.md: {files}"
        assert entry["skill_md"].get(name) == skill_text, "the session's SKILL.md is not the evaluated skill's"
        assert not entry["scenarios_md"], f"the session can see a scenarios.md: {entry['scenarios_md']}"
    tags = sorted(support.squash(entry["stdin"]).split("TAGW2104s")[1][:1] for entry in sessions)
    assert tags == ["1", "2", "3"], f"the sessions' prompts do not carry the three Situations: {tags}"
    for n in (1, 2, 3):
        situation = support.scenario(n).situation
        assert any(support.squash(situation) in support.squash(entry["stdin"]) for entry in sessions), \
            f"no session's prompt contains scenario {n}'s Situation"


def test_every_model_process_is_new_and_uses_the_default_model_and_effort(project, sandbox, stub):
    _plant_passing(project)

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ALL_PASSED, run.describe()
    calls = stub.calls()
    assert len(calls) == 6, f"expected six model processes (three sessions, three judgements): {len(calls)}"
    assert len({entry["pid"] for entry in calls}) == 6, "a model process was used for more than one call"
    for entry in calls:
        argv = entry["argv"]
        assert "-p" in argv, argv
        assert _pair(argv, "--model") == support.DEFAULT_MODEL, argv
        assert _pair(argv, "--effort") == support.DEFAULT_EFFORT, argv
        assert _pair(argv, "--output-format") == "json", argv
        assert not any(arg in FORBIDDEN_ARGS for arg in argv), f"a process resumed or continued: {argv}"


def test_the_judgement_is_a_separate_process_given_the_pass_line_the_expected_and_the_reply(
        project, sandbox, stub):
    _plant_passing(project)

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ALL_PASSED, run.describe()
    judgements = stub.judgements()
    assert len(judgements) == 3, f"expected three judgement processes: {len(judgements)}"
    session_pids = {entry["pid"] for entry in stub.sessions()}
    for n in (1, 2, 3):
        item = support.scenario(n)
        reply = f"{support.REPLY_TOKEN} TAGW2104s{n} done as the skill says."
        matching = [entry for entry in judgements if reply in support.squash(entry["stdin"])]
        assert len(matching) == 1, f"no single judgement's prompt carries scenario {n}'s session reply"
        prompt = support.squash(matching[0]["stdin"])
        assert support.squash(item.pass_line) in prompt, f"scenario {n}'s judgement lacks its Pass line"
        assert support.squash(item.expected) in prompt, f"scenario {n}'s judgement lacks its Expected text"
        assert matching[0]["pid"] not in session_pids


def test_model_and_effort_options_replace_the_defaults(project, sandbox, stub):
    folder = _plant_passing(project)

    run = support.skilleval(project, sandbox, SKILL_REL, "--model", "claude-sonnet-5-5", "--effort", "low",
                            stub=stub)

    assert run.returncode == support.EXIT_ALL_PASSED, run.describe()
    calls = stub.calls()
    assert len(calls) == 6, len(calls)
    for entry in calls:
        assert _pair(entry["argv"], "--model") == "claude-sonnet-5-5", entry["argv"]
        assert _pair(entry["argv"], "--effort") == "low", entry["argv"]
    for entry in support.last_entries(folder).values():
        support.assert_entry_shape(entry, run, SKILL_NAME, VERSION, model="claude-sonnet-5-5", effort="low")


def test_a_skill_in_w2_11s_form_with_wrapped_bullets_is_evaluated(project, sandbox, stub):
    """W2-11's ``scenarios.md`` files wrap a long bullet onto an indented continuation line."""
    _plant_passing(project, wrap_situation=True)

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ALL_PASSED, run.describe()
    prompts = " | ".join(support.squash(entry["stdin"]) for entry in stub.sessions())
    for n in (1, 2, 3):
        assert f"The session is asked to carry out planted task {n}" in prompts, \
            f"scenario {n}'s Situation continuation line is not in a session's prompt"


def test_a_skill_named_by_an_absolute_path_from_a_folder_outside_the_project(project, sandbox, stub):
    folder = _plant_passing(project)

    run = support.skilleval(project, sandbox, folder.resolve(), stub=stub, cwd=sandbox.elsewhere)
    assert run.returncode == support.EXIT_ALL_PASSED, run.describe()

    relative = support.skilleval(project, sandbox, SKILL_REL, stub=stub, cwd=sandbox.elsewhere)
    assert relative.returncode == support.EXIT_ALL_PASSED, \
        f"a skill path relative to the project root, run from another folder\n{relative.describe()}"
    assert len(support.records(folder)) == 6


# --------------------------------------------------------------------------
# A failing scenario (KPI 4, F1)
# --------------------------------------------------------------------------

def test_a_failing_and_an_unanswered_judgement_give_fail_and_exit_3(project, sandbox, stub):
    folder = support.plant_skill(project, SKILL_REL, SKILL_NAME,
                                 support.three(judge=("", support.JUDGE_FAIL, support.JUDGE_NO_VERDICT)))

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ANY_FAILED, run.describe()
    assert run.verdicts() == {1: "pass", 2: "fail", 3: "fail"}, run.describe()
    for n in (1, 2, 3):
        support.assert_verdict_fields(run.scenario(n))
    by_number = support.last_entries(folder)
    assert {n: entry["verdict"] for n, entry in by_number.items()} == {1: "pass", 2: "fail", 3: "fail"}
    for entry in by_number.values():
        support.assert_entry_shape(entry, run, SKILL_NAME, VERSION)


def test_the_verdict_is_the_last_verdict_line_of_the_judgements_reply_only(project, sandbox, stub):
    """Scenario 1's judgement says PASS, then FAIL last; scenario 2's FAIL, then PASS last; scenario 3's session
    ends its own reply with ``VERDICT: PASS`` and its judgement says FAIL."""
    folder = support.plant_skill(project, SKILL_REL, SKILL_NAME, support.three(
        session=("", "", support.SESSION_SAYS_PASS),
        judge=(support.JUDGE_LAST_FAIL, support.JUDGE_LAST_PASS, support.JUDGE_FAIL)))

    run = support.skilleval(project, sandbox, SKILL_REL, stub=stub)

    assert run.returncode == support.EXIT_ANY_FAILED, run.describe()
    assert run.verdicts() == {1: "fail", 2: "pass", 3: "fail"}, run.describe()
    by_number = support.last_entries(folder)
    assert {n: entry["verdict"] for n, entry in by_number.items()} == {1: "fail", 2: "pass", 3: "fail"}
