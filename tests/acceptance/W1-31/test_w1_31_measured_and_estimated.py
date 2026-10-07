"""W1-31 after DEC-491 and DEC-495: what the counter reads from the session logs, the labelled estimate, the
three share figures, and the learning metrics read from the commits and from the orchestrator's record.

A result is measured or it is refused (DEC-449, DEC-454): no case here accepts a figure whose source was
absent, unreadable or of a form the specimen does not show. The README maps every case to its KPI line and
says which are red against the counter as built, and why.
"""

from __future__ import annotations

import json
import os
import re

import pytest

import w1_31_support as support
from w1_31_support import (EXIT_NOT_MEASURED, EXIT_OK, NOT_MEASURED, OTHER_TICKET, SESSION_A, SESSION_B,
                           SESSION_NOWHERE, SESSION_OTHER, TICKET, gov_command, pad, tokens)

OUT = pad("MARK-BONGO gov output of the variant")
TEXT = pad("MARK-SERVAL text of the variant")


def run_full(project, sandbox, logs, *sessions, change=None, **how):
    expected = support.full_fixture(project, logs, change=change)
    run = support.run_telemetry(project, sandbox, logs, *(sessions or (SESSION_A, SESSION_B)), **how)
    return expected, run


def printed(run):
    return run.stdout + run.stderr


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b]: the three sources read from the session logs (DEC-495)
# --------------------------------------------------------------------------

def test_sessionstart_packet_is_what_the_sessionstart_hooks_added(project, sandbox, logs, ccusage):
    """The packet is the additional context of the SessionStart hooks of the sessions the caller names,
    counted with W1-24's counter: not the hook's own standard output, and not another session's packet."""
    expected, run = run_full(project, sandbox, logs)
    counted = support.record(run)["governance_tokens"]["sessionstart_packet"]
    assert counted == expected["counts"]["sessionstart_packet"], \
        f"{counted!r}, and the two packets hold {expected['counts']['sessionstart_packet']} tokens"
    only_a = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    assert only_a["governance_tokens"]["sessionstart_packet"] == tokens(support.PACKET_A), \
        "one session named, one packet counted"


def test_hook_output_is_what_the_other_hooks_added(project, sandbox, logs, ccusage):
    """Hook output is the additional context of the hooks that are not SessionStart hooks (the specimen
    shows PostToolUse): after a ``gov`` command and after any other command alike."""
    expected, run = run_full(project, sandbox, logs)
    counted = support.record(run)["governance_tokens"]["hook_output"]
    assert counted == expected["counts"]["hook_output"], \
        f"{counted!r}, and the three texts hold {expected['counts']['hook_output']} tokens"


def test_gov_output_is_the_results_of_the_bash_calls_that_run_gov(project, sandbox, logs, ccusage):
    """``gov`` output is the tool results of the Bash calls whose command runs ``gov``: as the console script
    (an installed project) and as the specimen's ``python3 -m gov.cli.main`` behind an assignment (this
    project). The result of a command that is not ``gov`` is not in it, although its path names ``gov``."""
    expected, run = run_full(project, sandbox, logs)
    counted = support.record(run)["governance_tokens"]["gov_output"]
    assert counted == expected["counts"]["gov_output"], \
        f"{counted!r}, and the three results hold {expected['counts']['gov_output']} tokens " \
        f"(the other command's result holds {tokens(support.OTHER_OUT)})"


def test_a_command_that_only_names_gov_is_not_gov_output(project, sandbox, logs, ccusage):
    """Naming ``gov`` is not running it: an argument, a path, a message, a module of another name, and a tool
    that is not Bash add nothing to the count."""
    def change(first, _second):
        for command in ("echo gov status", "cat src/gov/cli/main.py", "git commit -m 'gov close refuses'",
                        "python3 -m pytest tests/unit/gov -q", "grep -rn gov docs", "tk show gov-0001",
                        "python3 -m gov_tools.report"):
            first.bash(command, support.OTHER_OUT)
        first.tool("Grep", {"pattern": "gov status", "command": "gov status"}, support.OTHER_OUT)
    expected, run = run_full(project, sandbox, logs, change=change)
    counted = support.record(run)["governance_tokens"]["gov_output"]
    assert counted == expected["counts"]["gov_output"], \
        f"{counted!r}: only the three gov commands' results count ({expected['counts']['gov_output']})"


def test_a_log_that_was_read_and_holds_none_counts_zero(project, sandbox, logs, ccusage):
    """Sessions in the specimen's form without a hook and without a command: the three sources were read and
    hold nothing, so each is 0 (a measurement), not "not measured"."""
    support.write_session(logs, SESSION_A, [(1000, 200, 0, 0)])
    counted = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))["governance_tokens"]
    assert {name: counted[name] for name in support.LOG_SOURCES} == dict.fromkeys(support.LOG_SOURCES, 0)


# --------------------------------------------------------------------------
# What the specimen does not show is "not measured", by name, never guessed (DEC-495)
# --------------------------------------------------------------------------

def _failing_hook(log):
    log.bash("ls", support.OTHER_OUT)
    log.hook("PostToolUse", TEXT, name="PostToolUse:Bash", exit_code=2, context=False)


def _unknown_hook_run(log):
    log.hook("PostToolUse", TEXT, name="PostToolUse:Bash", run_type="hook_blocking_error", context=False)


def _unseen_event(log):
    log.hook("UserPromptSubmit", TEXT)


def _context_in_another_form(log):
    log.hook("PostToolUse", TEXT, name="PostToolUse:Bash", content=TEXT)


def _failing_sessionstart(log):
    log.session_start(TEXT, exit_code=2, context=False)


def _gov_in_a_subagent(log):
    log.bash(gov_command("status"), OUT, sidechain=True)


def _gov_without_its_result(log):
    log.bash(gov_command("status"), OUT, result=False)


def _gov_result_in_another_form(log):
    log.bash(gov_command("status"), OUT, result_content=[{"type": "text", "text": OUT}])


def _gov_in_a_compound_command(log):
    log.bash("ls src && " + gov_command("status") + " | head -5", OUT)


@pytest.mark.parametrize("variant, source, named", [
    pytest.param(_failing_hook, "hook_output", None, id="a hook that fails"),
    pytest.param(_unknown_hook_run, "hook_output", None, id="a hook run of another type"),
    pytest.param(_unseen_event, "hook_output", "UserPromptSubmit", id="context added under another hook event"),
    pytest.param(_context_in_another_form, "hook_output", None, id="added context in another form"),
    pytest.param(_failing_sessionstart, "sessionstart_packet", None, id="a SessionStart hook that fails"),
    pytest.param(_gov_in_a_subagent, "gov_output", None, id="gov in a sub-agent's lines"),
    pytest.param(_gov_without_its_result, "gov_output", None, id="gov without its result"),
    pytest.param(_gov_result_in_another_form, "gov_output", None, id="a gov result in another form"),
    pytest.param(_gov_in_a_compound_command, "gov_output", None, id="gov inside a compound command"),
])
def test_a_form_the_specimen_does_not_show_is_not_measured(project, sandbox, logs, tmp_path, ccusage,
                                                           variant, source, named):
    """The same ticket twice: with logs in the specimen's form the source is a count; with one thing more that
    the specimen does not show, it is never a number. Either the record says "not measured" for it, for the
    measured total and for the measured share and the sum (exit code 3) and names the reason, or the command
    refuses. The reason holds no text of the log."""
    expected, run = run_full(project, sandbox, logs)
    assert support.record(run)["governance_tokens"][source] == expected["counts"][source], \
        f"{source} is not counted for logs in the specimen's form\n{run.describe()}"
    varied = tmp_path / "varied-config"
    first, second, other = support.full_logs()
    variant(first)
    for log in (first, second, other):
        log.write(varied)
    run = support.run_telemetry(project, sandbox, varied, SESSION_A, SESSION_B)
    assert run.returncode != EXIT_OK, f"{source} cannot be a number here\n{run.describe()}"
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"
    if run.envelope().get("ok") is False:
        reason = json.dumps(support.refusal(run))
    else:
        result = support.record(run)
        assert result["governance_tokens"][source] == NOT_MEASURED, result["governance_tokens"]
        assert result["governance_tokens"]["total"] == NOT_MEASURED, result["governance_tokens"]
        assert support.share(result, "measured") == NOT_MEASURED and support.share(result, "total") == NOT_MEASURED
        reason = support.reasons(result).get(source)
        assert reason, f"not_measured does not name {source} with its reason: {result['not_measured']}"
    if named:
        assert named in reason, f"the reason does not name {named}: {reason!r}"


def test_a_log_of_another_claude_code_version_is_refused_by_its_version(project, sandbox, logs, ccusage):
    """The log form is the specimen's (Claude Code 2.1.288) and nothing else. A session whose log another
    version wrote is refused, the refusal says which version, and no figure is given for the ticket."""
    first, second, other = support.full_logs()
    second.version = "2.1.999"
    for line in second.lines:
        line["version"] = "2.1.999"
    for log in (first, second, other):
        log.write(logs)
    run = support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_B)
    error = support.refusal(run)
    assert "2.1.999" in json.dumps(error), f"the refusal does not say which version the log is from: {error}"
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"


# --------------------------------------------------------------------------
# Counts only, never content (DEC-495)
# --------------------------------------------------------------------------

def test_the_counter_prints_counts_only_never_content(project, sandbox, logs, tmp_path, ccusage):
    """No text of a log (a packet, a hook's text or command, a command line, a tool result, a prompt, an
    answer) is in anything the command prints: with and without ``--json``, where it succeeds, where a
    source is not measured and where it refuses."""
    _expected, run = run_full(project, sandbox, logs)
    plain = support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_B, as_json=False)
    varied = tmp_path / "varied-config"
    first, second, other = support.full_logs()
    _unseen_event(first)
    _gov_in_a_compound_command(second)
    for log in (first, second, other):
        log.write(varied)
    not_measured = support.run_telemetry(project, sandbox, varied, SESSION_A, SESSION_B)
    refused = support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_NOWHERE)
    assert run.returncode == EXIT_OK, f"the full fixture is measured\n{run.describe()}"
    assert not_measured.returncode != EXIT_OK and refused.returncode != EXIT_OK
    for each in (run, plain, not_measured, refused):
        assert support.MARK not in printed(each), f"text of the log is printed\n{each.describe()}"


# --------------------------------------------------------------------------
# The estimate: instruction files and governance MCP definitions, on a line of their own (DEC-495)
# --------------------------------------------------------------------------

def test_the_estimate_is_a_line_of_its_own_labelled_estimated(project, sandbox, logs, ccusage):
    """The line carries its label, how it was formed, the files it stands on, a count for each of the two
    sources and their sum. Nothing of it is inside ``governance_tokens``, whose total is the measured one."""
    expected, run = run_full(project, sandbox, logs)
    result = support.record(run)
    estimate = support.estimate(result)
    assert sorted(estimate) == sorted(support.ESTIMATE_KEYS), f"the estimate's line is {estimate!r}"
    assert estimate["label"] == support.ESTIMATED
    assert isinstance(estimate["method"], str) and estimate["method"].strip(), "it names how it was formed"
    assert isinstance(estimate["files"], list) and "CLAUDE.md" in estimate["files"], \
        f"it stands on the root rule Claude Code is given (W1-38): {estimate['files']!r}"
    assert all((project.root / rel).is_file() for rel in estimate["files"]), estimate["files"]
    assert support.is_count(estimate["instruction_files"]) and estimate["instruction_files"] >= expected["rule"], \
        f"instruction_files is {estimate['instruction_files']!r}; CLAUDE.md alone holds {expected['rule']}"
    assert support.is_count(estimate["mcp_definitions"]), estimate
    assert estimate["total"] == estimate["instruction_files"] + estimate["mcp_definitions"]
    counted = result["governance_tokens"]
    assert counted["total"] == sum(expected["counts"].values()) == sum(counted[name] for name in support.SOURCES), \
        "the measured total is the sum of the five measured sources and of nothing else"


def test_the_estimate_follows_the_instruction_file(project, sandbox, logs, ccusage):
    """A longer instruction file is a larger estimate, and the measured sources do not move."""
    _expected, run = run_full(project, sandbox, logs)
    before = support.record(run)
    project.add_instructions(more="One more rule. " * 80)   # 1,200 characters more: 300 tokens
    after = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_B))
    grown = support.estimate(after)["instruction_files"]
    assert support.is_count(grown) and grown >= support.estimate(before)["instruction_files"] + 300, \
        f"{before['estimated_governance_tokens']['instruction_files']!r} -> {grown!r}"
    assert after["governance_tokens"] == before["governance_tokens"]
    assert support.share(after, "measured") == support.share(before, "measured")
    assert support.share(after, "estimated") > support.share(before, "estimated")


@pytest.mark.parametrize("state", ["absent", "unreadable"])
def test_the_estimate_is_not_measured_without_its_instruction_file(project, sandbox, logs, ccusage, state):
    """``CLAUDE.md`` is not there, or is there and cannot be read: the estimate of the instruction files is
    "not measured", and so are the estimate's sum, the estimated share and the sum of the shares (exit code
    3). What was measured stays a number."""
    expected = support.full_fixture(project, logs)
    (project.root / "CLAUDE.md").unlink()
    if state == "unreadable":
        os.symlink(project.root / "no-such-file", project.root / "CLAUDE.md")
    run = support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_B)
    result = support.record(run)
    estimate = support.estimate(result)
    assert estimate["instruction_files"] == NOT_MEASURED and estimate["total"] == NOT_MEASURED, estimate
    assert support.share(result, "estimated") == NOT_MEASURED and support.share(result, "total") == NOT_MEASURED
    assert run.returncode == EXIT_NOT_MEASURED, run.describe()
    assert "instruction_files" in support.reasons(result)
    assert result["governance_tokens"]["total"] == sum(expected["counts"].values())
    assert support.is_number(support.share(result, "measured")), result["governance_share"]


# --------------------------------------------------------------------------
# Success lines 1, 2 and 5; failure line 1: the three share figures (DEC-495)
# --------------------------------------------------------------------------

def test_the_three_share_figures_are_the_numbers_the_case_computes(project, sandbox, logs, ccusage):
    """Every source measured or estimated: the measured part, the estimated part and their sum are numbers,
    each over fresh input plus cache creation plus output (ccusage's), and the exit code is 0."""
    expected, run = run_full(project, sandbox, logs)
    result = support.record(run)
    fresh_in, out, created, read = expected["usage"]
    rows = support.ccusage_sessions(logs, support.cli_support.make_sandbox(project.root.parent / "probe").home)
    assert (fresh_in, out, created, read) == tuple(
        rows[SESSION_A][key] + rows[SESSION_B][key]
        for key in ("inputTokens", "outputTokens", "cacheCreationTokens", "cacheReadTokens")), \
        "the fixture is sound: ccusage counts each message of the logs once"
    assert (result["tokens_in"], result["tokens_out"], result["cache_creation_tokens"],
            result["cache_read_tokens"]) == (fresh_in, out, created, read)
    measured_total = sum(expected["counts"].values())
    assert result["governance_tokens"] == {**expected["counts"], "total": measured_total}
    estimated_total = support.estimate(result)["total"]
    assert support.is_count(estimated_total) and estimated_total >= expected["rule"], estimated_total
    denominator = fresh_in + created + out
    assert created > 0 and read > 0
    assert support.share(result, "measured") == pytest.approx(measured_total / denominator, abs=5e-5), \
        f"measured {measured_total} over {fresh_in} + {created} + {out}"
    assert support.share(result, "estimated") == pytest.approx(estimated_total / denominator, abs=5e-5)
    assert support.share(result, "total") == pytest.approx((measured_total + estimated_total) / denominator, abs=1e-4)
    assert support.share(result, "measured") != pytest.approx(measured_total / (fresh_in + out), abs=5e-5), \
        "cache creation is in the denominator"
    assert run.returncode == EXIT_OK and result["not_measured"] == [], run.describe()
    assert result["learning_metrics"]["governance_share"] == result["governance_share"]


def test_a_part_that_is_not_measured_gives_no_sum_and_exit_code_3(project, sandbox, logs, ccusage):
    """A checkpoint record that is there and cannot be read: its source, the measured total, the measured
    share and the sum of the shares say "not measured", the record names the source with a reason, and the
    exit code is 3. The estimated part and the sessions' tokens were measured and are still given."""
    expected = support.full_fixture(project, logs)
    folder = project.root / "docs" / "checkpoints" / TICKET
    os.symlink(folder / "no-such-file", folder / f"CP-{TICKET}-0002.md")
    run = support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_B)
    result = support.record(run)
    assert run.returncode == EXIT_NOT_MEASURED, run.describe()
    assert result["governance_tokens"]["checkpoint_records"] == NOT_MEASURED, result["governance_tokens"]
    assert result["governance_tokens"]["total"] == NOT_MEASURED
    assert support.share(result, "measured") == NOT_MEASURED and support.share(result, "total") == NOT_MEASURED
    assert support.is_number(support.share(result, "estimated")), result["governance_share"]
    assert "checkpoint_records" in support.reasons(result)
    assert (result["tokens_in"], result["tokens_out"]) == expected["usage"][:2]


def test_the_record_states_no_verdict_and_no_threshold(project, sandbox, logs, ccusage):
    """The counter measures; the verdict on the 15 % is the owner's at the Wave 1 exit (DEC-495). Nothing
    printed says whether a budget is met, and no threshold is in it."""
    _expected, run = run_full(project, sandbox, logs)
    plain = support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_B, as_json=False)
    assert run.returncode == EXIT_OK, run.describe()
    judging = re.compile(r"verdict|threshold|budget|ceiling|exceed|within|complian|breach"
                         r"|(?<![\d.])15(?:\.0+)? ?%|(?<![\d.])0\.150*(?!\d)", re.IGNORECASE)
    for each in (run, plain):
        found = judging.findall(printed(each))
        assert not found, f"the output judges or names a threshold: {found}\n{each.describe()}"


# --------------------------------------------------------------------------
# Failure line 1: ccusage against the log
# --------------------------------------------------------------------------

def test_ccusage_figures_that_differ_from_the_logs_give_no_figure(project, sandbox, logs):
    """A complete row from ccusage whose tokens are not those of the session's own assistant lines (each
    message once): the session was not measured, and no share, token count or cost is a number."""
    expected = support.full_fixture(project, logs)
    fresh_in, out, created, read = expected["logs"][0].usage()
    row = {"sessionId": SESSION_A, "projectPath": "-work-project", "inputTokens": fresh_in - 500,
           "outputTokens": out, "cacheCreationTokens": created, "cacheReadTokens": read, "totalCost": 0.5,
           "totalTokens": fresh_in - 500 + out + created + read, "modelsUsed": [support.MODEL],
           "modelBreakdowns": [{"modelName": support.MODEL, "inputTokens": fresh_in - 500, "outputTokens": out,
                                "cacheCreationTokens": created, "cacheReadTokens": read, "cost": 0.5}],
           "firstActivity": "2026-10-07T10:00:00.000Z", "lastActivity": "2026-10-07T10:10:00.000Z"}
    path = support.fake_ccusage(sandbox, f"#!/bin/sh\ncat <<'REPORT'\n{json.dumps({'sessions': [row]})}\nREPORT\n")
    support.assert_no_figure(support.run_telemetry(project, sandbox, logs, SESSION_A, path=path))


def test_a_line_ccusage_passes_over_gives_no_figure(project, sandbox, logs, ccusage):
    """ccusage 20.0.26 passes over a line it cannot parse and still prints a row for the session (run 1). Its
    row is then smaller than the log, and the counter, which reads the log itself, gives no figure."""
    project.add_checkpoint(1)
    log = support.Log(SESSION_A).session_start(support.PACKET_A).prompt()
    log.say((1000, 200, 0, 0)).say((700, 300, 0, 0))
    log.spaced = {number for number, line in enumerate(log.lines)
                  if line.get("type") == "assistant" and line["message"]["id"].endswith("_002")}
    log.write(logs)
    row = support.ccusage_sessions(logs, sandbox.home)[SESSION_A]
    assert (row["inputTokens"], log.usage()[0]) == (1000, 1700), \
        "the fixture is sound: ccusage prints a row and leaves the second message out"
    support.assert_no_figure(support.run_telemetry(project, sandbox, logs, SESSION_A))


# --------------------------------------------------------------------------
# Success line 5 [CAP-40.c]: rewritten acceptance tests and KPI disputes (DEC-491)
# --------------------------------------------------------------------------

def _listed(entries, key):
    assert isinstance(entries, list) and all(isinstance(entry, dict) for entry in entries), f"it is {entries!r}"
    return entries, [entry.get(key) for entry in entries]


def _is_commit(named, full):
    return isinstance(named, str) and len(named) >= 7 and full.startswith(named)


def test_rewrites_are_the_designers_commits_after_the_first_engineer_commit(project, sandbox, logs, ccusage):
    """One entry per commit of the test designer for the ticket after the ticket's first engineer commit, with
    the reason its ``Rewrite-Reason:`` trailer gives. A rewrite without the trailer is listed with "reason not
    recorded". The designer's commit before implementation began, another role's and another ticket's are not
    rewrites."""
    support.write_session(logs, SESSION_A, [(1000, 200, 0, 0)])
    assert support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))[
        "learning_metrics"]["acceptance_tests_rewritten"] == [], "the commits were read and hold no rewrite"
    acceptance = f"tests/acceptance/{support.WBS}/test_it.py"
    project.write(acceptance, "def test_it():\n    assert 1 == 1\n")
    with_reason = project.commit("tests brought to the decision", f"Task: {TICKET}",
                                 "Role: independent-test-designer", "Implements: CAP-00.a",
                                 "Rewrite-Reason: test_it, DEC-900 changed the bound")
    project.write("src/example/a.py", "VALUE = 2\n")
    project.commit("the work again", f"Task: {TICKET}", "Role: engineer", "Implements: CAP-00.a")
    project.write(acceptance, "def test_it():\n    assert 2 == 2\n")
    without_reason = project.commit("tests changed", f"Task: {TICKET}", "Role: independent-test-designer",
                                    "Implements: CAP-00.a")
    project.write("tests/acceptance/T-02/test_other.py", "def test_other():\n    assert True\n")
    project.commit("another ticket's tests", f"Task: {OTHER_TICKET}", "Role: independent-test-designer",
                   "Rewrite-Reason: not of this ticket")
    project.write("docs/note.md", "a note\n")
    project.commit("a note", f"Task: {TICKET}", "Role: orchestrator")
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    entries, commits = _listed(result["learning_metrics"]["acceptance_tests_rewritten"], "commit")
    assert len(entries) == 2, f"two rewrites, and {len(entries)} listed: {entries}"
    by_reason = {entry.get("reason"): entry.get("commit") for entry in entries}
    assert sorted(by_reason) == sorted(("test_it, DEC-900 changed the bound", support.REASON_NOT_RECORDED)), entries
    assert _is_commit(by_reason["test_it, DEC-900 changed the bound"], with_reason), entries
    assert _is_commit(by_reason[support.REASON_NOT_RECORDED], without_reason), \
        f"the rewrite without a reason is listed, never left out: {commits}"


def test_commits_that_cannot_be_read_are_not_measured(project, sandbox, logs, ccusage):
    """Where the project's commits cannot be read, the rewrites and the commits' models are "not measured":
    never an empty list, which would say that no test was rewritten."""
    support.write_session(logs, SESSION_A, [(1000, 200, 0, 0)])
    (project.root / ".git").rename(project.root / "git-taken-away")
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    assert result["learning_metrics"]["acceptance_tests_rewritten"] == NOT_MEASURED
    assert support.models(result)["commits"] == NOT_MEASURED


def test_kpi_disputes_are_read_from_the_orchestrators_record(project, sandbox, logs, ccusage):
    """One entry per line of the ticket's disputes record, each with the decision that settled it; a record
    that is there and empty is no dispute. (The place and the form of the record are proposed: README, PR-1.)"""
    support.write_session(logs, SESSION_A, [(1000, 200, 0, 0)])
    project.add_disputes("DEC-900: whether the bound counts the header", "DEC-901: what fresh input means")
    project.add_disputes("DEC-902: another ticket's dispute", ticket=OTHER_TICKET)
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    _entries, decisions = _listed(result["learning_metrics"]["kpi_disputes"], "decision")
    assert decisions == ["DEC-900", "DEC-901"], decisions
    project.add_disputes()
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    assert result["learning_metrics"]["kpi_disputes"] == [], "the record was read and holds no dispute"


@pytest.mark.parametrize("state", ["no record", "a line without its decision", "unreadable"])
def test_kpi_disputes_are_not_measured_without_a_readable_record(project, sandbox, logs, ccusage, state):
    """Without the record nobody counted the disputes: "not measured", never 0 and never an empty list. The
    same for a record that cannot be read and for one with a line that names no decision."""
    support.write_session(logs, SESSION_A, [(1000, 200, 0, 0)])
    if state == "a line without its decision":
        project.add_disputes("DEC-900: whether the bound counts the header", "the designer disputed line 3")
    elif state == "unreadable":
        folder = project.root / "docs" / "close" / TICKET
        folder.mkdir(parents=True)
        os.symlink(folder / "no-such-file", folder / support.DISPUTES_NAME)
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    assert result["learning_metrics"]["kpi_disputes"] == NOT_MEASURED, result["learning_metrics"]


# --------------------------------------------------------------------------
# The smaller points of DEC-491
# --------------------------------------------------------------------------

def test_a_ticket_without_a_profile_is_not_measured_for_the_profile(make_project, sandbox, logs, ccusage):
    """Success line 4 [CAP-53.c]: the counter does not assume STANDARD."""
    support.write_session(logs, SESSION_A, [(1000, 200, 0, 0)])
    result = support.record(support.run_telemetry(make_project(None), sandbox, logs, SESSION_A))
    assert result["profile"] == NOT_MEASURED, f"the profile is {result['profile']!r}"


def test_an_empty_checkpoint_folder_counts_zero_and_an_absent_one_is_not_measured(project, sandbox, logs, ccusage):
    """A ticket without a folder of checkpoints (deliberate or automatic) was never checkpointed as far as
    anyone can read: "not measured". A folder of the ticket that is there and holds no record was read: 0."""
    support.write_session(logs, SESSION_A, [(1000, 200, 0, 0)])
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    assert result["governance_tokens"]["checkpoint_records"] == NOT_MEASURED
    assert "checkpoint_records" in support.reasons(result)
    (project.root / "docs" / "checkpoints" / TICKET).mkdir(parents=True)
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    assert result["governance_tokens"]["checkpoint_records"] == 0
    assert "checkpoint_records" not in support.reasons(result)


def test_the_close_record_is_not_measured_before_the_close(project, sandbox, logs, ccusage):
    """The close record's own tokens are counted by a measure after the close. Before it exists the source is
    "not measured", also when the ticket's close folder is there and holds something else."""
    support.write_session(logs, SESSION_A, [(1000, 200, 0, 0)])
    project.add_disputes()
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    assert result["governance_tokens"]["close_records"] == NOT_MEASURED
    assert "close_records" in support.reasons(result)
    expected = project.add_close()
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    assert result["governance_tokens"]["close_records"] == expected


def test_the_model_is_reported_from_the_logs_and_from_the_commits(project, sandbox, logs, ccusage):
    """Success line 2: both places, each named. The session logs' models are those of the named sessions'
    assistant lines; the commits' are the ``Co-Authored-By`` lines of the ticket's commits, as read, and "not
    measured" for a commit without one (DEC-470)."""
    _expected, run = run_full(project, sandbox, logs)
    model = support.models(support.record(run))
    assert sorted(model["session_logs"]) == sorted((support.MODEL, support.OTHER_MODEL)), model["session_logs"]
    entries, _commits = _listed(model["commits"], "commit")
    assert len(entries) == 2, f"the ticket has two commits, and {len(entries)} are listed: {entries}"
    read = {full: entry.get("model") for entry in entries for full in (project.tests, project.work)
            if _is_commit(entry.get("commit"), full)}
    assert read == {project.tests: NOT_MEASURED, project.work: support.CO_AUTHOR}, entries


# --------------------------------------------------------------------------
# Success line 3 [CAP-40.a]: what the specimen shows no source for stays "not measured"
# --------------------------------------------------------------------------

def test_provider_and_files_read_have_no_source_in_the_specimen(project, sandbox, logs, ccusage):
    """The specimen names no provider and holds no call that reads a file: the two say "not measured"."""
    _expected, run = run_full(project, sandbox, logs)
    result = support.record(run)
    assert (result["provider"], result["files_read"]) == (NOT_MEASURED, NOT_MEASURED)
