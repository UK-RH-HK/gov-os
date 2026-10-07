"""W1-31 after DEC-501: the log forms the second specimen shows (hook runs of every event, a hook that blocks
and one that fails, ``gov`` commands in every plain form, a sub-agent's file, a compaction, two totals lines),
what the record says beside its counts, the latency and the agent.

A result is measured or it is refused (DEC-449, DEC-454). Every case writes its own log lines, in the
specimens' forms and with its own texts, in a temporary folder; no case reads a specimen or a log of this
machine. The README maps every case to its KPI line and says which are red against the counter as built.
"""

from __future__ import annotations

import pytest

import w1_31_support as support
from w1_31_support import (EXIT_OK, NOT_MEASURED, SESSION_A, SESSION_B, SESSION_OTHER, gov_command, pad, tokens)

OUT = pad("MARK-BONGO gov output of the case")
TEXT = pad("MARK-SERVAL hook text of the case")
MORE = pad("MARK-CARACAL more hook text of the case, longer than the other")
GOV_ALONE = pad("MARK-OCELOT the ticket is in progress")
SUB_USAGE = ((30, 141, 2000, 0), (30, 4, 300, 2000))


def printed(run):
    return run.stdout + run.stderr


def run_second(project, sandbox, logs, *sessions, change=None, **how):
    expected = support.second_fixture(project, logs, change=change)
    run = support.run_telemetry(project, sandbox, logs, *(sessions or (SESSION_A, SESSION_B)), **how)
    return expected, run


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


def with_subagent(log, *, spaced=False):
    """A sub-agent of ``log`` in the second specimen's form: one ``gov`` command with its hook lines, a first
    message whose two lines differ in usage, a last message of one line, a SubagentStop run."""
    sub = log.subagent(support.AGENT_A)
    log.launch(sub)
    sub.task().call(gov_command("doctor --help", installed=False), support.SUB_GOV, SUB_USAGE[0],
                    pre=support.SUB_PRE, post=support.SUB_POST, fails=support.SUB_FAIL, first_output=14)
    sub.say(SUB_USAGE[1], "MARK-GECKO done", thinking=False).run_only("SubagentStop", support.SUBSTOP_TEXT)
    if spaced:
        sub.spaced = {number for number, line in enumerate(sub.lines)
                      if line.get("type") == "assistant" and line["message"]["id"].endswith("_002")}
    return sub


# --------------------------------------------------------------------------
# Every form of the second specimen in one session: numbers the case computes itself (DEC-501)
# --------------------------------------------------------------------------

def test_every_count_of_a_session_in_the_second_specimens_form_is_the_number_the_case_computes(
        project, sandbox, logs, ccusage):
    """Success lines 1 and 2, failure lines 1 and 2. SessionStart twice around a compaction, PreToolUse and
    PostToolUse context, a blocking hook, failing hooks, Stop and SubagentStop runs, the four ``gov`` forms,
    the sub-agent's file and two totals lines: every measured source, the session tokens (ccusage's, the
    sub-agent's messages among them) and the three share figures are numbers, and the exit code is 0."""
    expected, run = run_second(project, sandbox, logs)
    fresh_in, out, created, read = expected["usage"]
    rows = support.ccusage_sessions(logs, support.cli_support.make_sandbox(project.root.parent / "probe").home)
    assert (fresh_in, out, created, read) == tuple(
        rows[SESSION_A][key] + rows[SESSION_B][key]
        for key in ("inputTokens", "outputTokens", "cacheCreationTokens", "cacheReadTokens")), \
        "the fixture is sound: ccusage counts each message once, the sub-agent's with the session, and takes " \
        "the later of two lines of a message that differ"
    assert created > 0 and read > 0 and rows[SESSION_A]["modelsUsed"] != [support.MODEL]
    result = support.record(run)
    assert (result["tokens_in"], result["tokens_out"], result["cache_creation_tokens"],
            result["cache_read_tokens"]) == (fresh_in, out, created, read), \
        "the session's tokens are ccusage's, the sub-agent's messages among them"
    assert result["cost"] == pytest.approx(rows[SESSION_A]["totalCost"] + rows[SESSION_B]["totalCost"], abs=1e-6)
    measured_total = sum(expected["counts"].values())
    assert result["governance_tokens"] == {**expected["counts"], "total": measured_total}, \
        f"each source is the number the case computes: {expected['counts']}"
    estimated_total = support.estimate(result)["total"]
    assert support.is_count(estimated_total) and estimated_total >= expected["rule"], estimated_total
    denominator = fresh_in + created + out
    assert support.share(result, "measured") == pytest.approx(measured_total / denominator, abs=5e-5), \
        f"measured {measured_total} over {fresh_in} + {created} + {out}"
    assert support.share(result, "estimated") == pytest.approx(estimated_total / denominator, abs=5e-5)
    assert support.share(result, "total") == pytest.approx((measured_total + estimated_total) / denominator, abs=1e-4)
    assert run.returncode == EXIT_OK and result["not_measured"] == [], run.describe()
    assert support.notes(result) == expected["notes"], \
        "five hook texts by the larger reading (one blocking, four failing), one gov result counted whole"
    assert sorted(support.models(result)["session_logs"]) == sorted((support.MODEL, support.OTHER_MODEL)), \
        "the sub-agent's model is a model of the session"


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b]: hook runs (DEC-501)
# --------------------------------------------------------------------------

def test_a_hook_run_without_added_context_counts_zero(project, sandbox, logs, ccusage):
    """A successful run of any event with no added-context line after it added nothing, whatever its run
    line carries: a Stop run with its plain output and the ``system`` line after it, a SubagentStop run in
    the sub-agent's file, a PostToolUse run that printed nothing. The sources were read and are 0."""
    def build(log):
        log.bash("ls -la", support.OTHER_OUT)
        log.run_only("PostToolUse", name="PostToolUse:Bash")
        sub = log.subagent(support.AGENT_A)
        log.launch(sub)
        sub.task().say((30, 4, 300, 0), "MARK-GECKO done", thinking=False)
        sub.run_only("SubagentStop", support.SUBSTOP_TEXT)
        log.say((20, 30, 0, 0), "MARK-GECKO launched").stop(support.STOP_TEXT)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == dict.fromkeys(support.LOG_SOURCES, 0)
    assert support.notes(result) == {support.LARGER_READING: 0, support.COUNTED_WHOLE: 0}, \
        "nothing was counted by the larger reading and nothing whole"


def test_the_sessionstart_packet_is_counted_each_time_it_is_given(project, sandbox, logs, ccusage):
    """The packet is given at the start and again after a compaction: both are counted. The summary and the
    local command's lines after the boundary are no hook output and no ``gov`` output."""
    def build(log):
        log.session_start(support.PACKET_A)
        log.say((20, 30, 0, 0), "MARK-GECKO first")
        log.compact(support.SUMMARY, support.PRECOMPACT_TEXT, support.PACKET_2, api_duration=3000)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == {"sessionstart_packet": tokens(support.PACKET_A) + tokens(support.PACKET_2),
                                   "hook_output": 0, "gov_output": 0}


def test_added_context_of_any_other_event_is_hook_output(project, sandbox, logs, ccusage):
    """What a hook of another event than SessionStart added is hook output: PreToolUse's like PostToolUse's
    (the second specimen), and an event neither specimen shows, when it adds context in the specimens' form."""
    def build(log):
        log.call("ls -la", support.OTHER_OUT, pre=TEXT, post=support.HOOK_1)
        log.hook("UserPromptSubmit", MORE)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == {"sessionstart_packet": 0, "gov_output": 0,
                                   "hook_output": tokens(TEXT) + tokens(support.HOOK_1) + tokens(MORE)}


def test_the_text_of_a_blocking_hook_is_hook_output_by_the_larger_reading(project, sandbox, logs, ccusage):
    """A PreToolUse hook blocks a call: its text reaches the session as that call's result, marked as an
    error, and that result is counted as hook output. The record says that one text was counted by the
    larger reading, and holds nothing of it."""
    blocked = support.blocked_text(TEXT)
    result, _run = one_session(project, sandbox, logs, lambda log: log.blocked("echo MARK-DUGONG", blocked))
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": tokens(blocked), "gov_output": 0}
    assert support.notes(result)[support.LARGER_READING] == 1


def test_the_text_of_a_failing_hook_is_hook_output_by_the_larger_reading(project, sandbox, logs, ccusage):
    """A hook fails without blocking: whether its text reaches the model is not shown, and the larger reading
    is taken. What its line holds as ``stderr`` is counted as hook output, beside what the other hook added,
    and the record says that one text was counted by the larger reading."""
    failed = support.failing_text(TEXT)
    result, _run = one_session(project, sandbox, logs,
                               lambda log: log.call("ls -la", support.OTHER_OUT, post=MORE, fails=failed))
    assert log_sources(result) == {"sessionstart_packet": 0, "gov_output": 0,
                                   "hook_output": tokens(MORE) + tokens(failed)}
    assert support.notes(result)[support.LARGER_READING] == 1


def test_a_blocked_gov_command_is_counted_once_as_hook_output(project, sandbox, logs, ccusage):
    """A hook blocks a command that runs ``gov``: the command never ran, and its result is the hook's text.
    It is counted once, as hook output, and is neither ``gov`` output nor dropped."""
    blocked = support.blocked_text(TEXT)
    result, _run = one_session(project, sandbox, logs,
                               lambda log: log.blocked(gov_command(f"close {support.TICKET}"), blocked))
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": tokens(blocked), "gov_output": 0}


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b]: gov commands (DEC-501)
# --------------------------------------------------------------------------

def test_a_gov_result_marked_as_an_error_is_counted(project, sandbox, logs, ccusage):
    """Every refusal of ``gov`` is a result marked as an error: it is ``gov`` output like any other."""
    refused = support.error_text("MARK-BONGO gov: error: argument <command>: invalid choice")
    result, _run = one_session(project, sandbox, logs, lambda log: log.call(
        gov_command("nosuchcommand", installed=False), refused, error=True))
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": 0, "gov_output": tokens(refused)}
    assert support.notes(result)[support.COUNTED_WHOLE] == 0, "gov ran alone here"


@pytest.mark.parametrize("command", [
    pytest.param("ls src && " + gov_command("status"), id="beside another command, &&"),
    pytest.param(gov_command("status") + "; ls src", id="beside another command, ;"),
    pytest.param(gov_command("doctor --help", installed=False) + " | head -3", id="through a pipe"),
    pytest.param(gov_command("check --json") + " 2>/dev/null", id="with a redirection"),
])
def test_gov_beside_other_commands_is_counted_whole_and_the_record_says_so(project, sandbox, logs, ccusage,
                                                                           command):
    """The one result of such a command cannot be told apart: all of it is counted as ``gov`` output, which
    over-counts, and the record says how many results were counted whole. A ``gov`` command that ran alone
    in the same session is counted and is not among them."""
    def build(log):
        log.call(gov_command("status"), GOV_ALONE)
        log.call(command, OUT)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == {"sessionstart_packet": 0, "hook_output": 0,
                                   "gov_output": tokens(GOV_ALONE) + tokens(OUT)}
    assert support.notes(result)[support.COUNTED_WHOLE] == 1


# --------------------------------------------------------------------------
# Success lines 1 and 2, failure line 1: a sub-agent's file (DEC-501)
# --------------------------------------------------------------------------

def test_a_subagents_lines_and_tokens_belong_to_the_named_session(project, sandbox, logs, tmp_path, ccusage):
    """The same session with and without its sub-agent's file. With it, the sub-agent's hook context, failing
    hook text and ``gov`` result are counted with the session, and the session's tokens are ccusage's row,
    which holds the sub-agent's messages: the first of them, whose two lines differ, with its later usage."""
    def write(folder, with_file):
        log = support.Log(SESSION_A).prompt("MARK-WOMBAT do the work")
        log.call(gov_command("status"), GOV_ALONE, (500, 100, 0, 0))
        with_subagent(log)
        if not with_file:
            log.subagents.clear()
        log.say((40, 60, 0, 0), "MARK-GECKO done").write(folder)
        return log
    log = write(logs, True)
    alone = write(tmp_path / "alone-config", False)
    row = support.ccusage_sessions(logs, sandbox.home)[SESSION_A]
    lone = support.ccusage_sessions(tmp_path / "alone-config", sandbox.home)[SESSION_A]
    usage = log.usage(subagents=True)
    assert usage == (row["inputTokens"], row["outputTokens"], row["cacheCreationTokens"], row["cacheReadTokens"]) \
        and usage[1] == alone.usage()[1] + 141 + 4 and lone["outputTokens"] == alone.usage()[1], \
        "the fixture is sound: ccusage's row holds the sub-agent's two messages, the first with 141 output, " \
        "and without the file the session's own messages only"
    run = support.run_telemetry(project, sandbox, logs, SESSION_A)
    result = support.record(run)
    assert (result["tokens_in"], result["tokens_out"], result["cache_creation_tokens"],
            result["cache_read_tokens"]) == usage, run.describe()
    assert log_sources(result) == {
        "sessionstart_packet": 0,
        "hook_output": tokens(support.SUB_PRE) + tokens(support.SUB_POST) + tokens(support.SUB_FAIL),
        "gov_output": tokens(GOV_ALONE) + tokens(support.SUB_GOV)}
    assert support.OTHER_MODEL in support.models(result)["session_logs"], "the sub-agent's model is the session's"
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"
    without = support.record(support.run_telemetry(project, sandbox, tmp_path / "alone-config", SESSION_A))
    assert log_sources(without) == {"sessionstart_packet": 0, "hook_output": 0, "gov_output": tokens(GOV_ALONE)}
    assert (without["tokens_in"], without["tokens_out"]) == alone.usage()[:2]


def test_a_subagents_file_that_ccusage_reads_otherwise_gives_no_figure(project, sandbox, logs, ccusage):
    """The cross-check of ccusage against the log's own lines covers the sub-agent's file. ccusage passes
    over a line of that file: its row is smaller than the session's lines and the sub-agent's together, and
    no share, token count or cost is a number."""
    project.add_checkpoint(1)
    log = support.Log(SESSION_A).prompt()
    log.call(gov_command("status"), GOV_ALONE, (500, 100, 0, 0))
    with_subagent(log, spaced=True)
    log.say((40, 60, 0, 0)).write(logs)
    row = support.ccusage_sessions(logs, sandbox.home)[SESSION_A]
    assert row["outputTokens"] == log.usage(subagents=True)[1] - 4 and row["modelsUsed"] != [support.MODEL], \
        "the fixture is sound: ccusage prints a row and leaves the sub-agent's last message out"
    run = support.run_telemetry(project, sandbox, logs, SESSION_A)
    support.assert_no_figure(run)
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"


def test_a_subagent_of_a_session_that_was_not_named_is_never_counted(project, sandbox, logs, ccusage):
    """Two sessions in the same project folder, each with a sub-agent's file. Only one is named: the other
    session's sub-agent adds nothing to the counts and nothing to the tokens."""
    log = support.Log(SESSION_A).prompt()
    log.call(gov_command("status"), GOV_ALONE, (500, 100, 0, 0))
    with_subagent(log)
    log.say((40, 60, 0, 0)).write(logs)
    other = support.Log(SESSION_OTHER).prompt()
    stray = other.subagent(support.AGENT_OTHER)
    other.launch(stray)
    stray.task().call(gov_command("status"), support.GOV_OTHER, (7000, 700, 0, 0), pre=support.HOOK_OTHER,
                      post=support.HOOK_OTHER, fails=support.failing_text(support.HOOK_OTHER))
    stray.say((10, 10, 0, 0), thinking=False)
    other.say((10, 10, 0, 0)).write(logs)
    result = support.record(support.run_telemetry(project, sandbox, logs, SESSION_A))
    assert log_sources(result) == {
        "sessionstart_packet": 0,
        "hook_output": tokens(support.SUB_PRE) + tokens(support.SUB_POST) + tokens(support.SUB_FAIL),
        "gov_output": tokens(GOV_ALONE) + tokens(support.SUB_GOV)}
    assert (result["tokens_in"], result["tokens_out"]) == log.usage(subagents=True)[:2]


# --------------------------------------------------------------------------
# Success line 3 [CAP-40.a]: latency and agent (DEC-501)
# --------------------------------------------------------------------------

def test_latency_is_the_api_duration_of_each_sessions_last_totals_line(project, sandbox, logs, ccusage):
    """Latency is the harness's summed API duration, named as such: for a session the ``totalAPIDuration`` of
    its last totals line (the earlier one, before the compaction, is not the figure, and neither are the
    line's other durations); for the ticket, the sum over its sessions."""
    expected, run = run_second(project, sandbox, logs)
    result = support.record(run)
    by_id = {entry["session"]: entry.get(support.API_DURATION) for entry in result["sessions"]}
    assert by_id == {SESSION_A: support.API_DURATION_A, SESSION_B: support.API_DURATION_B}, \
        f"each session's entry carries its own: {by_id}"
    assert support.latency(result) == expected["latency"] == 47000


def test_a_session_without_a_totals_line_has_no_latency(project, sandbox, logs, ccusage):
    """A named session whose log holds no totals line: its latency is "not measured", and so is the
    ticket's; never 0 and never the other session's alone. The share does not stand on it: the three
    figures are numbers and the exit code is 0."""
    def change(_first, second):
        second.api_duration = None
    _expected, run = run_second(project, sandbox, logs, change=change)
    result = support.record(run)
    by_id = {entry["session"]: entry.get(support.API_DURATION) for entry in result["sessions"]}
    assert by_id == {SESSION_A: support.API_DURATION_A, SESSION_B: NOT_MEASURED}, by_id
    assert support.latency(result) == NOT_MEASURED
    assert run.returncode == EXIT_OK and all(
        support.is_number(support.share(result, part)) for part in support.SHARE_PARTS), run.describe()


def test_the_agent_is_the_harness_and_its_version(project, sandbox, logs, ccusage):
    """The agent is the harness whose logs these are and its version, as the log's lines give it."""
    _expected, run = run_second(project, sandbox, logs)
    assert support.record(run)["agent"] == {"harness": support.HARNESS, "version": support.VERSION}


# --------------------------------------------------------------------------
# Failure line 1: what the record says beside its counts does not stand in the way of a figure (DEC-501)
# --------------------------------------------------------------------------

def test_the_precompact_gap_is_named_and_is_no_entry_of_not_measured(project, sandbox, logs, tmp_path, ccusage):
    """The output of a PreCompact hook cannot be counted: the record names that as a known gap, with a
    reason, for a session with a compaction and for one without. It is no entry of ``not_measured``, and
    neither it nor the two counting notes keeps the exit code from 0. The reason holds no text of the log."""
    _expected, run = run_second(project, sandbox, logs)
    result = support.record(run)
    known = support.gaps(result)
    assert support.PRECOMPACT_GAP in known, f"the known gaps are {sorted(known)}"
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"
    assert result["not_measured"] == [] and run.returncode == EXIT_OK, run.describe()
    assert support.notes(result)[support.LARGER_READING] > 0 and support.notes(result)[support.COUNTED_WHOLE] > 0
    plain = tmp_path / "plain-config"
    support.write_session(plain, SESSION_A, [(1000, 200, 0, 0)])
    result = support.record(support.run_telemetry(project, sandbox, plain, SESSION_A))
    assert support.PRECOMPACT_GAP in support.gaps(result)
    assert support.PRECOMPACT_GAP not in support.reasons(result)
