"""V1 and V2 through the real command line: ``gov adopt --lite --stage VERDICT`` on the adopted harbour, with the live
``gov doctor`` and ``gov check`` (they are not green on the harbour: README, "The project") [CAP-44.h; DEC-741 F].

What these cases hold is what the command line shows: the three verdicts' exit codes, the record committed (also
when the verdict is NOT_ADOPTED_HEALTHY), the owner's exceptions file, the re-run that supersedes, and that the
command line takes no stand-in for a tool. The session fixtures run the stage once each (``cli_plain``,
``cli_owner``); a case that changes something works on a copy.
"""

from __future__ import annotations

import json

import pytest

import w2_210_support as d1

support = d1.support


def _not_met_names(outcome):
    front, _ = d1.record_at_head(outcome.project)
    return [name for name, state in d1.record_states(front).items() if state == "not met"]


def test_the_command_line_takes_no_stand_in_for_a_tool(adopted):
    """V1: ``tools=`` is the self-tests' seam, never reachable from the command line: the stage is offered and
    ``--tools`` is an unknown argument."""
    run = adopted.gov("adopt", "--lite", "--stage", "VERDICT", "--tools", "stand-in", "--json")
    assert "unrecognized arguments" in run.stderr and "--tools" in run.stderr, run.describe()
    run = adopted.gov("adopt", "--help")
    assert "--tools" not in run.stdout and "stand-in" not in run.stdout.lower(), run.stdout


def test_a_verdict_that_is_not_adopted_healthy_is_committed_and_the_command_exits_non_zero(cli_plain):
    """V2: the live tools are not green on the harbour: NOT_ADOPTED_HEALTHY is committed as a record (one commit,
    the stage's subject, that record alone, a clean tree) and the command refuses with ``ADOPT_NOT_ADOPTED``, the
    conditions not met named."""
    outcome = d1.taken(cli_plain)
    error = d1.assert_refused(outcome, "ADOPT_NOT_ADOPTED")
    front, _ = d1.record_at_head(outcome.project)
    assert front["verdict"] == "NOT_ADOPTED_HEALTHY"
    names = _not_met_names(outcome)
    assert {d1.RELEASE, d1.DOCTOR} <= set(names) <= set(d1.TOOL_CONDITIONS), names
    for name in names:
        assert name in json.dumps(error), f"the refusal does not name {name!r}: {error}"
    assert d1.head_subject(outcome.project).startswith("gov adopt --lite VERDICT:"), d1.head_subject(outcome.project)
    assert d1.head_files(outcome.project) == [d1.VERDICT_REL]
    assert outcome.after.porcelain == "", outcome.after.porcelain
    assert d1.git_parent(outcome.project) == outcome.before.state["head"], "one commit: the record's"


def test_every_condition_a_record_gives_is_met_but_the_live_tools_ones_on_the_harbour(cli_plain):
    """V1: with no stand-in, the conditions read from records and git are ``met`` on the adopted harbour (A0 to A8,
    the A5 review, the native layout, both gates, the closed ticket); the others are the live tools'."""
    d1.taken(cli_plain)
    front, _ = d1.record_at_head(cli_plain.project)
    assert list(d1.record_states(front)) == list(d1.CONDITIONS)
    not_tools = {n: s for n, s in d1.record_states(front).items() if n not in d1.TOOL_CONDITIONS}
    assert set(not_tools.values()) == {"met"}, not_tools


def test_the_live_tools_conditions_name_the_commands_run_and_their_exit_codes(cli_plain):
    """V1: the command run and its exit code are the evidence of a tool's condition (``gov doctor`` exits 3 on the
    harbour: its path_compliance and framework_lock parts fail)."""
    d1.taken(cli_plain)
    front, _ = d1.record_at_head(cli_plain.project)
    by_name = {item["name"]: item for item in front["conditions"]}
    assert "gov doctor" in by_name[d1.DOCTOR]["evidence"]["command"] and by_name[d1.DOCTOR]["evidence"]["exit"] == 3
    assert by_name[d1.DOCTOR]["state"] == "not met" and by_name[d1.RELEASE]["state"] == "not met"
    assert "gov check" in by_name[d1.CHECK]["evidence"]["command"]


def test_the_same_conditions_come_from_the_stood_in_tools_and_from_the_live_ones(cli_plain, copy_of, tmp_path):
    """V1: "the same planted failure with the checks of the live tools stood in gives the same answer": on a copy of
    the project before the stage, ``compute`` with the tools stood in as the harbour's live ones answer gives, for the
    conditions that are not the tools', the states the command line recorded."""
    d1.taken(cli_plain)
    front, _ = d1.record_at_head(cli_plain.project)
    ad = copy_of(cli_plain, tmp_path)
    d1.git_reset_back(ad.project, 1)
    result = d1.compute(ad.project, tools=d1.healthy_tools(
        doctor=d1.doctor(lock="MISSING", exit_code=3, failing_part="path_compliance"),
        check=d1.check(red=("security",))))
    assert {n: s for n, s in d1.states(result).items() if n not in d1.TOOL_CONDITIONS} == \
        {n: s for n, s in d1.record_states(front).items() if n not in d1.TOOL_CONDITIONS}


def test_a_planted_a7_failure_through_the_command_line_makes_that_condition_not_met_beside_the_tools_ones(
        adopted, tmp_path):
    """V1/V2: A7's record with ``result: fail``: the command line records NOT_ADOPTED_HEALTHY with the lite A7 gate
    ``not met`` beside the live tools' conditions, and the others as they were."""
    d1.set_result(adopted.project, "A7", "fail")
    outcome = d1.taken(d1.run_stage(adopted))
    error = d1.assert_refused(outcome, "ADOPT_NOT_ADOPTED")
    names = _not_met_names(outcome)
    assert d1.LITE_A7 in names and set(names) - {d1.LITE_A7} <= set(d1.TOOL_CONDITIONS), names
    assert d1.LITE_A7 in json.dumps(error)
    assert d1.head_files(outcome.project) == [d1.VERDICT_REL]


def test_a_planted_removed_stage_record_through_the_command_line_is_named(adopted):
    """V1: a stage record removed (A2): the command line records A2 ``not met`` and names it, never skips it."""
    d1.remove_record(adopted.project, d1.RECORD["A2"])
    outcome = d1.taken(d1.run_stage(adopted))
    error = d1.assert_refused(outcome, "ADOPT_NOT_ADOPTED")
    assert "A2" in _not_met_names(outcome) and "A2" in json.dumps(error)


def test_an_owner_exceptions_file_gives_adopted_with_accepted_exceptions_and_the_command_exits_0(cli_owner):
    """V2: the owner's file (last commit ``Role: owner`` alone) naming each condition not met: the verdict is
    ADOPTED_WITH_ACCEPTED_EXCEPTIONS, exit 0; each condition accepted is recorded ``accepted`` with its
    ``owner_entry``."""
    outcome = d1.taken(cli_owner)
    done = d1.envelope(outcome)
    assert done["ok"] is True and outcome.run.returncode == 0, outcome.run.describe()
    front, _ = d1.record_at_head(outcome.project)
    assert front["verdict"] == "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    by_name = {item["name"]: item for item in front["conditions"]}
    assert outcome.names, "the first run found nothing not met"
    for name in outcome.names:
        assert by_name[name]["state"] == "accepted" and by_name[name]["owner_entry"] == d1.OWNER_DECISION, by_name[name]
    assert {n for n, i in by_name.items() if i["state"] != "accepted"} == set(d1.CONDITIONS) - set(outcome.names)
    assert outcome.after.porcelain == ""


def test_the_stage_run_again_after_the_owners_commit_replaces_the_earlier_record(cli_plain, cli_owner):
    """V2: the re-run replaces the earlier record: ``supersedes`` names the sha256 of the record it replaces; git
    keeps the old one."""
    d1.taken(cli_owner)
    front, _ = d1.record_at_head(cli_owner.project)
    old_commit = d1.last_commit(cli_plain.project, d1.VERDICT_REL)
    old = support.at_head(cli_plain.project, d1.VERDICT_REL)
    assert front.get("supersedes") == d1.hashlib.sha256(old).hexdigest()
    kept = support.git(cli_owner.project, "show", f"{old_commit}:{d1.VERDICT_REL}")
    assert kept.encode("utf-8") == old, "git keeps the earlier record"
    assert d1.head_files(cli_owner.project) == [d1.VERDICT_REL]
    assert d1.head_subject(cli_owner.project).startswith("gov adopt --lite VERDICT:")


def test_an_exceptions_file_committed_by_the_owner_for_a_condition_that_is_met_changes_nothing(adopted):
    """V2: through the command line, an owner's file that names only A0 (met) and a condition that does not exist
    leaves the verdict where the live tools put it (NOT_ADOPTED_HEALTHY): nothing is accepted."""
    d1.write_exceptions(adopted.project, d1.accept("A0", "no such condition"), "owner")
    outcome = d1.taken(d1.run_stage(adopted))
    d1.assert_refused(outcome, "ADOPT_NOT_ADOPTED")
    front, _ = d1.record_at_head(outcome.project)
    assert front["verdict"] == "NOT_ADOPTED_HEALTHY"
    assert "accepted" not in d1.record_states(front).values()
