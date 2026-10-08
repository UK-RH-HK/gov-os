"""W1-31 after DEC-502: the log forms the third specimen shows (a SessionStart hook that prints plain text and
one that fails, ``gov`` called by a path, a shortened result with the session's ``tool-results`` folder, a call
a hook denies by its answer, a call a permission rule denies, a Stop and a SubagentStop hook that block, the
hook of the event after a failed tool call), and one edge of the cost.

A result is measured or it is refused (DEC-449, DEC-454). Every case writes its own log lines, in the
specimens' forms and with its own texts, in a temporary folder; no case reads a specimen or a log of this
machine. The README maps every case to its KPI line and says which are red against the counter as built.
"""

from __future__ import annotations

import json

import pytest

import w1_31_support as support
from w1_31_support import (EXIT_OK, GOV_PATH, NOT_MEASURED, SESSION_A, SESSION_B, gov_command, pad, tokens)

OUT = pad("MARK-BONGO gov output of the case")
TEXT = pad("MARK-SERVAL hook text of the case")
GOV_ALONE = pad("MARK-OCELOT the ticket is in progress")
NOTHING = dict.fromkeys(support.LOG_SOURCES, 0)
NO_NOTES = {support.LARGER_READING: 0, support.COUNTED_WHOLE: 0}


def printed(run):
    return run.stdout + run.stderr


def one_session(project, sandbox, logs, build):
    """One session of the ticket: a prompt, what ``build`` adds, a last message. Returns the record, which
    the command gives although the ticket has no checkpoint and no close record yet, and the run."""
    log = support.Log(SESSION_A).prompt("MARK-WOMBAT do the work")
    build(log)
    log.say((40, 60, 0, 0), "MARK-GECKO done").write(logs)
    run = support.run_telemetry(project, sandbox, logs, SESSION_A)
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"
    return support.record(run), run


def log_sources(result):
    """The three sources read from the logs, each a count: none of them is named in ``not_measured``."""
    unmeasured = {name: reason for name, reason in support.reasons(result).items() if name in support.LOG_SOURCES}
    assert not unmeasured, f"a form the specimens show is measured: {unmeasured}"
    return {name: result["governance_tokens"][name] for name in support.LOG_SOURCES}


def never_a_number(project, sandbox, logs, build, source):
    """One session with a form no specimen shows: ``source`` is never a number. The command refuses, or the
    record says "not measured" for it, for the measured total and for the measured share and the sum (exit
    code 3) and names the source with a reason. No text of the log is printed."""
    log = support.Log(SESSION_A).prompt("MARK-WOMBAT do the work")
    build(log)
    log.say((40, 60, 0, 0), "MARK-GECKO done").write(logs)
    run = support.run_telemetry(project, sandbox, logs, SESSION_A)
    assert run.returncode not in (EXIT_OK, support.EXIT_USAGE), f"{source} cannot be a number here\n{run.describe()}"
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"
    if run.envelope().get("ok") is False:
        support.refusal(run)
        return
    result = support.record(run)
    assert result["governance_tokens"][source] == NOT_MEASURED, result["governance_tokens"]
    assert result["governance_tokens"]["total"] == NOT_MEASURED, result["governance_tokens"]
    assert support.share(result, "measured") == NOT_MEASURED and support.share(result, "total") == NOT_MEASURED
    assert support.reasons(result).get(source), f"not_measured does not name {source}: {result['not_measured']}"


# --------------------------------------------------------------------------
# Every form of the third specimen in one session: numbers the case computes itself (DEC-502, DEC-507)
# --------------------------------------------------------------------------

def test_every_count_of_a_session_in_the_third_specimens_form_is_the_number_the_case_computes(
        project, sandbox, logs, ccusage):
    """Success lines 1 and 2, failure lines 1 and 2. The two SessionStart hooks, ``gov`` by a path and by
    the interpreter with an error result, the context after a failed call, two shortened results with the
    ``tool-results`` folder, ``gov`` by a path through a pipe, a hook's denial, three denials by a rule, a
    blocking Stop hook with its ``system`` line and later runs that succeed, a sub-agent's file with its own
    ``gov`` call and blocking SubagentStop hook, a totals line: every measured source, the two notes, the
    estimate (the two sessions named with their roles), the session tokens and the three share figures are
    numbers the case computes, and the exit code is 0."""
    expected = support.third_fixture(project, logs)
    run = support.run_telemetry(project, sandbox, logs, *support.ROLED)
    fresh_in, out, created, read = expected["usage"]
    rows = support.ccusage_sessions(logs, support.cli_support.make_sandbox(project.root.parent / "probe").home)
    assert (fresh_in, out, created, read) == tuple(
        rows[SESSION_A][key] + rows[SESSION_B][key]
        for key in ("inputTokens", "outputTokens", "cacheCreationTokens", "cacheReadTokens")), \
        "the fixture is sound: ccusage counts each message once, the sub-agent's with the session, beside a " \
        "tool-results folder too"
    assert created > 0 and read > 0 and rows[SESSION_A]["modelsUsed"] != [support.MODEL]
    assert tokens(expected["shortened"]) < 700 < 20000 < tokens(support.GOV3_LONG), \
        "the fixture is sound: the shortened result is far smaller than the full output"
    result = support.record(run)
    assert (result["tokens_in"], result["tokens_out"], result["cache_creation_tokens"],
            result["cache_read_tokens"]) == (fresh_in, out, created, read), \
        "the session's tokens are ccusage's, the sub-agent's messages among them"
    assert result["cost"] == pytest.approx(rows[SESSION_A]["totalCost"] + rows[SESSION_B]["totalCost"], abs=1e-6)
    measured_total = sum(expected["counts"].values())
    assert result["governance_tokens"] == {**expected["counts"], "total": measured_total}, \
        f"each source is the number the case computes: {expected['counts']}"
    assert support.notes(result) == expected["notes"], \
        "five hook texts by the larger reading (the plain SessionStart text, the failing SessionStart hook's, " \
        "the hook's denial, the Stop and the SubagentStop feedback), one gov result counted whole (the pipe's)"
    estimate = support.estimate(result)
    assert (estimate["instruction_files"], estimate["mcp_definitions"], estimate["total"]) == (
        expected["estimate"], 0, expected["estimate"]), estimate
    denominator = fresh_in + created + out
    assert support.share(result, "measured") == pytest.approx(measured_total / denominator, abs=5e-5), \
        f"measured {measured_total} over {fresh_in} + {created} + {out}"
    assert support.share(result, "estimated") == pytest.approx(expected["estimate"] / denominator, abs=5e-5)
    assert support.share(result, "total") == pytest.approx(
        (measured_total + expected["estimate"]) / denominator, abs=1e-4)
    assert run.returncode == EXIT_OK and result["not_measured"] == [], run.describe()
    assert support.latency(result) == expected["latency"]
    assert sorted(support.models(result)["session_logs"]) == sorted((support.MODEL, support.OTHER_MODEL))
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b]: the SessionStart hooks, and plain output of the other events (DEC-502)
# --------------------------------------------------------------------------

def test_a_sessionstart_hooks_plain_output_is_the_packet_by_the_larger_reading(project, sandbox, logs, ccusage):
    """A SessionStart hook prints plain text: its run line carries the text and no added-context line
    follows. The harness gives that text to the session, so it is the packet, counted once (the line holds it
    twice), and the record says that one text was counted by the larger reading."""
    packet = support.plain_text("MARK-SERVAL the packet of the case, printed as plain text")
    result, _run = one_session(project, sandbox, logs, lambda log: log.start_plain(packet))
    assert tokens(packet) == tokens(packet + "\n"), "the fixture is sound: with or without its line end"
    assert log_sources(result) == {"sessionstart_packet": tokens(packet), "hook_output": 0, "gov_output": 0}
    assert support.notes(result) == {support.LARGER_READING: 1, support.COUNTED_WHOLE: 0}


def test_a_failing_sessionstart_hook_is_hook_output_by_the_larger_reading(project, sandbox, logs, ccusage):
    """A SessionStart hook fails without blocking: like a failing hook of any event, what its line holds is
    counted as hook output (not as the packet), and the record says that one text was counted by the larger
    reading. The packet another SessionStart hook added is counted beside it."""
    failed = support.failing_text(TEXT)

    def build(log):
        log.session_start(support.PACKET_A)
        log.start_failing(failed)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == {"sessionstart_packet": tokens(support.PACKET_A), "hook_output": tokens(failed),
                                   "gov_output": 0}
    assert support.notes(result)[support.LARGER_READING] == 1


def test_plain_output_of_a_hook_of_any_other_event_counts_zero(project, sandbox, logs, ccusage):
    """For every event but SessionStart, a run that succeeded with plain output and no added-context line
    added nothing: 0, and the sources stay measured. PreToolUse and PostToolUse here, beside the Stop and
    SubagentStop runs the specimens show."""
    def build(log):
        tool_id, called = log._call("Bash", {"command": "ls -la", "description": "run the command"}, (10, 20, 0, 0))
        log.run_only("PreToolUse", "MARK-SERVAL the guard looked at the command", name="PreToolUse:Bash",
                     tool_use_id=tool_id)
        log.result(tool_id, called, support.OTHER_OUT)
        log.run_only("PostToolUse", "MARK-SERVAL the guard recorded the command", name="PostToolUse:Bash",
                     tool_use_id=tool_id)
        log.say((20, 30, 0, 0), "MARK-GECKO listed").stop(support.STOP_TEXT_3)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == NOTHING
    assert support.notes(result) == NO_NOTES


def test_added_context_after_a_failed_tool_call_is_hook_output(project, sandbox, logs, ccusage):
    """A command fails; the hook of the event after a failed tool call adds context: hook output, like any
    event's. The failed ``gov`` command's result, marked as an error, is ``gov`` output."""
    refused = support.error_text("MARK-BONGO gov: error: argument <command>: invalid choice")
    result, _run = one_session(project, sandbox, logs, lambda log: log.call(
        gov_command("nosuchcommand", installed=False), refused, error=True, failure=TEXT))
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": tokens(TEXT),
                                   "gov_output": tokens(refused)}
    assert support.notes(result) == NO_NOTES


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b]: gov by a path; gov through another runner (DEC-502)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("command, whole", [
    pytest.param(f"{GOV_PATH} status", 0, id="an absolute path"),
    pytest.param(".venv/bin/gov status", 0, id="a relative path"),
    pytest.param("./gov status", 0, id="a path in the working directory"),
    pytest.param(f"GOV_ROLE=engineer {GOV_PATH} status", 0, id="a path after an assignment"),
    pytest.param(f"{GOV_PATH} doctor --help 2>&1 | head -3", 1, id="a path, through a pipe"),
])
def test_gov_called_by_a_path_is_gov_output(project, sandbox, logs, ccusage, command, whole):
    """A command word whose last path component is ``gov`` runs ``gov``: its result is ``gov`` output, whole
    and noted where ``gov`` did not run alone. A command that only holds such a path as an argument does
    not run it."""
    def build(log):
        log.call(command, OUT)
        log.call(f"ls -la {GOV_PATH}", support.OTHER_OUT)
        log.call(f"{GOV_PATH}-tools report", support.OTHER_OUT)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": 0, "gov_output": tokens(OUT)}
    assert support.notes(result)[support.COUNTED_WHOLE] == whole


def test_a_gov_result_by_a_path_marked_as_an_error_is_counted(project, sandbox, logs, ccusage):
    """A refusal of ``gov`` called by a path is ``gov`` output like any other result."""
    refused = support.error_text("MARK-BONGO gov: error: the ticket is not in progress", 1)
    result, _run = one_session(project, sandbox, logs,
                               lambda log: log.call(f"{GOV_PATH} close PROJ-aaaa", refused, error=True))
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": 0, "gov_output": tokens(refused)}


@pytest.mark.parametrize("command", [
    pytest.param("uv run gov status", id="uv run gov"),
    pytest.param("uv run python3 -m gov.cli.main status", id="uv run python3 -m gov.cli.main"),
    pytest.param(f"poetry run {GOV_PATH} status", id="poetry run, gov by a path"),
])
def test_gov_through_another_runner_is_not_measured_by_name(project, sandbox, logs, ccusage, command):
    """``gov`` behind a program that runs another program is a form no specimen shows: ``gov`` output is "not
    measured", by name, never a count that leaves the result out."""
    def build(log):
        log.call(gov_command("status"), GOV_ALONE)
        log.call(command, OUT)
    never_a_number(project, sandbox, logs, build, "gov_output")


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b], failure line 1: what else a session's folder holds (DEC-502)
# --------------------------------------------------------------------------

def test_a_shortened_result_is_counted_as_logged_and_tool_results_is_passed_over(project, sandbox, logs, ccusage):
    """An over-long output: the harness keeps the full text in a file of the session's ``tool-results``
    folder, and the log's result line holds a shortened form with a preview. The session is measured, with
    that folder beside its file; for a ``gov`` command the count is that of the result line's text (what
    reached the session), not of the full text. The shortened result of another command counts nothing."""
    made = {}

    def build(log):
        made["gov"] = log.long_call(f"{GOV_PATH} status --all", support.GOV3_LONG, logs)
        made["other"] = log.long_call("python3 -c \"print('MARK-DUGONG ' * 6000)\"", support.OTHER_LONG, logs)
        made["log"] = log
    result, run = one_session(project, sandbox, logs, build)
    kept = sorted(path.name for path in (made["log"].folder(logs) / SESSION_A / "tool-results").iterdir())
    assert len(kept) == 2 and all(name in made["gov"] + made["other"] for name in kept), \
        "the fixture is sound: the folder holds the two full texts, and each result line names its file"
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": 0, "gov_output": tokens(made["gov"])}
    assert tokens(made["gov"]) < 700 < 20000 < tokens(support.GOV3_LONG), "not the full text's count"
    assert support.notes(result) == NO_NOTES, "the result is one command's, counted as logged"
    row = support.ccusage_sessions(logs, sandbox.home)[SESSION_A]
    assert (result["tokens_in"], result["tokens_out"]) == (row["inputTokens"], row["outputTokens"]), run.describe()


@pytest.mark.parametrize("entry", ["notes.txt", "memory/notes.txt"], ids=["a file", "a folder"])
def test_any_other_content_of_a_sessions_folder_gives_no_figure(project, sandbox, logs, ccusage, entry):
    """Beside ``subagents`` and ``tool-results`` the session's folder holds something no specimen shows:
    nobody read it, and the session is not measured. No share, token count or cost is a number."""
    project.add_checkpoint(1)
    log = support.Log(SESSION_A).prompt()
    log.long_call(f"{GOV_PATH} status --all", support.GOV3_LONG, logs)
    sub = log.subagent(support.AGENT_A)
    log.launch(sub)
    sub.task().say((1, 4, 300, 0), "MARK-GECKO done", thinking=False)
    log.say((40, 60, 0, 0))
    log.tool_results[f"../{entry}"] = TEXT
    log.write(logs)
    assert sorted(path.name for path in (log.folder(logs) / SESSION_A).iterdir()) == sorted(
        ("subagents", "tool-results", entry.split("/")[0])), "the fixture is sound"
    run = support.run_telemetry(project, sandbox, logs, SESSION_A)
    support.assert_no_figure(run)
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b]: denials (DEC-502)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("command", ["echo MARK-DUGONG", gov_command("close PROJ-aaaa"), f"{GOV_PATH} pause"],
                         ids=["a command that is not gov", "gov", "gov by a path"])
def test_a_call_a_hook_denies_by_its_answer_is_hook_output(project, sandbox, logs, ccusage, command):
    """A PreToolUse hook denies a call by its answer: the hook's reason reaches the session as that call's
    result, marked as an error. Like the result of a call a hook blocked, it is hook output, counted whole
    and once, and the record notes one text counted by the larger reading. Also when the denied command
    would run ``gov``: it never ran, and its result is not ``gov`` output."""
    denied = support.hook_denial_text("MARK-SERVAL the guard denies this command")
    result, _run = one_session(project, sandbox, logs, lambda log: log.denied(command, denied))
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": tokens(denied), "gov_output": 0}
    assert support.notes(result) == {support.LARGER_READING: 1, support.COUNTED_WHOLE: 0}


@pytest.mark.parametrize("command", ["echo MARK-DUGONG now", gov_command("close PROJ-aaaa"), f"{GOV_PATH} pause",
                                     gov_command("status", installed=False) + " | head -3"],
                         ids=["a command that is not gov", "gov", "gov by a path", "gov through a pipe"])
def test_a_call_a_permission_rule_denies_counts_nothing(project, sandbox, logs, ccusage, command):
    """A permission rule denies a call: the result is the harness's own sentence. It is no hook's and no
    ``gov`` output, also when the command would run ``gov``: nothing is counted, nothing is noted, and the
    three sources stay measured. The hook's denial in the same session is counted beside it."""
    denied = support.hook_denial_text("MARK-SERVAL the guard denies this command")

    def build(log):
        log.denied(command, support.rule_denial_text(command))
        log.denied("echo MARK-DUGONG", denied)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": tokens(denied), "gov_output": 0}
    assert support.notes(result) == {support.LARGER_READING: 1, support.COUNTED_WHOLE: 0}


def _denial_with_another_text(log):
    log.denied("echo MARK-DUGONG", pad("MARK-SERVAL the call was not allowed, in words no specimen shows"))


def _denial_of_another_kind(log):
    tool_id, called = log._call("Bash", {"command": "echo MARK-DUGONG", "description": "run the command"},
                                (10, 20, 0, 0))
    log.result(tool_id, called, support.rule_denial_text("echo MARK-DUGONG"), error=True, denial="MARK-other-kind")


def _denial_that_is_not_marked_as_an_error(log):
    tool_id, called = log._call("Bash", {"command": "echo MARK-DUGONG", "description": "run the command"},
                                (10, 20, 0, 0))
    log.result(tool_id, called, support.hook_denial_text(TEXT), denial="permission-rule")


@pytest.mark.parametrize("variant", [
    pytest.param(_denial_with_another_text, id="a denial with a text of neither form"),
    pytest.param(_denial_of_another_kind, id="a denial of another kind"),
    pytest.param(_denial_that_is_not_marked_as_an_error, id="a denial that is not marked as an error"),
])
def test_a_denial_in_a_form_no_specimen_shows_is_not_measured(project, sandbox, logs, ccusage, variant):
    """The specimens show three denials: a hook's block, a hook's answer and a rule's, each an error result
    whose line carries the same denial kind and whose text begins in its own way. A denied call in any other
    form is not known to be a hook's or nobody's: hook output is "not measured", by name."""
    never_a_number(project, sandbox, logs, variant, "hook_output")


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b]: Stop and SubagentStop hooks that block (DEC-502)
# --------------------------------------------------------------------------

def test_the_feedback_of_a_blocking_stop_hook_is_hook_output_counted_once(project, sandbox, logs, ccusage):
    """A Stop hook blocks: the session is given a line of feedback, and the ``system`` line after it holds
    the same text again. It is hook output, counted once (the feedback line's text), never twice; the record
    notes one text counted by the larger reading. The later runs that succeed with plain output count 0."""
    feedback = support.feedback_text("MARK-SERVAL write the record first, then stop")

    def build(log):
        log.say((20, 30, 0, 0), "MARK-GECKO first").feedback(feedback)
        log.say((20, 30, 0, 0), "MARK-GECKO second").stop(support.STOP_TEXT_3)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": tokens(feedback), "gov_output": 0}, \
        f"the feedback holds {tokens(feedback)} tokens; counted with the system line's copy it would be " \
        f"{tokens(feedback) + tokens(feedback[len('Stop hook feedback:') + 1:])}"
    assert support.notes(result) == {support.LARGER_READING: 1, support.COUNTED_WHOLE: 0}


def test_the_feedback_of_a_blocking_subagentstop_hook_is_counted_once_with_the_session(project, sandbox, logs,
                                                                                       ccusage):
    """A SubagentStop hook blocks: the feedback line is in the sub-agent's file (under the same heading as
    a Stop hook's, and with no ``system`` line after it). It is hook output of the named session, counted
    once; the sub-agent's later run that succeeds counts 0, and so do the session's own lines about the
    sub-agent (its start and the notice of its end)."""
    feedback = support.feedback_text("MARK-SERVAL answer in one word", "SubagentStop")

    def build(log):
        sub = log.subagent(support.AGENT_A)
        log.launch(sub)
        sub.task().say((1, 4, 300, 0), "MARK-GECKO done", thinking=False).feedback(feedback)
        sub.say((2, 4, 60, 300), "MARK-GECKO done", thinking=False).run_only(
            "SubagentStop", support.SUBSTOP_TEXT_3, command=support.HOOK_COMMAND_3)
        log.say((20, 30, 0, 0), "MARK-GECKO launched").stop(support.STOP_TEXT_3)
        log.notice(support.NOTICE)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": tokens(feedback), "gov_output": 0}
    assert support.notes(result) == {support.LARGER_READING: 1, support.COUNTED_WHOLE: 0}


def _summary_with_an_error_and_no_feedback_line(log):
    log.say((20, 30, 0, 0), "MARK-GECKO first")
    log.stop_summary(errors=[support.feedback_errors(TEXT)], command=f"{support.HOOK_COMMAND_3} Stop")


def _summary_that_prevented_continuation(log):
    log.say((20, 30, 0, 0), "MARK-GECKO first").feedback(support.feedback_text(TEXT), prevented=True)


def _summary_whose_error_is_not_the_feedback(log):
    log.say((20, 30, 0, 0), "MARK-GECKO first").feedback(support.feedback_text(TEXT), summary=False)
    log.stop_summary(errors=[support.feedback_errors("MARK-CARACAL another text than the feedback line's")],
                     command=f"{support.HOOK_COMMAND_3} Stop")


@pytest.mark.parametrize("variant", [
    pytest.param(_summary_with_an_error_and_no_feedback_line, id="an error in the system line and no feedback line"),
    pytest.param(_summary_that_prevented_continuation, id="a system line that prevented continuation"),
    pytest.param(_summary_whose_error_is_not_the_feedback, id="an error in the system line that is not the feedback"),
])
def test_a_stop_hooks_block_in_a_form_no_specimen_shows_is_not_measured(project, sandbox, logs, ccusage, variant):
    """The third specimen shows one form of a blocking Stop hook: the feedback line, then a ``system`` line
    that holds the same text and did not prevent continuation. Another form may hold hook text nobody
    counted: hook output is "not measured", by name."""
    never_a_number(project, sandbox, logs, variant, "hook_output")


# --------------------------------------------------------------------------
# Success line 2: the cost of a session whose model has no price (DEC-449)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("mixed", [False, True], ids=["no model of the session has a price",
                                                      "one model of the session has no price"])
def test_the_cost_of_a_model_without_a_price_is_not_measured(project, sandbox, logs, ccusage, mixed):
    """ccusage 20.0.26 prints a cost of 0 for a model it has no price for, and marks that model's part of
    the row. Such a session's cost is "not measured", never 0 and never the priced part alone, and so is the
    ticket's (never the other session's alone). The tokens were measured and are given."""
    unpriced = support.Log(SESSION_A, model="claude-nosuchmodel-9-9").prompt()
    if mixed:
        unpriced.say((500, 100, 0, 0), model=support.MODEL)
    unpriced.say((1000, 200, 300, 4000)).write(logs)
    support.write_session(logs, SESSION_B, [(400, 100, 0, 0)])
    rows = support.ccusage_sessions(logs, sandbox.home)
    marked = [each.get("missingPricing") for each in rows[SESSION_A]["modelBreakdowns"]]
    assert True in marked and rows[SESSION_B]["totalCost"] > 0 and (rows[SESSION_A]["totalCost"] > 0) is mixed, \
        f"the fixture is sound: ccusage marks the model without a price: {json.dumps(rows[SESSION_A])}"
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_B))
    by_id = {entry["session"]: entry["cost"] for entry in result["sessions"]}
    assert by_id[SESSION_A] == NOT_MEASURED, f"the cost of the session is {by_id[SESSION_A]!r}"
    assert by_id[SESSION_B] == pytest.approx(rows[SESSION_B]["totalCost"], abs=1e-6)
    assert result["cost"] == NOT_MEASURED, f"the ticket's cost is {result['cost']!r}"
    assert (result["tokens_in"], result["tokens_out"]) == (
        rows[SESSION_A]["inputTokens"] + rows[SESSION_B]["inputTokens"],
        rows[SESSION_A]["outputTokens"] + rows[SESSION_B]["outputTokens"])
