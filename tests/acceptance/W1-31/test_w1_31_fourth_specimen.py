"""W1-31 after DEC-655: the session-log reader accepts any Claude Code version whose log it can parse, and the
record names the version that was read. The log forms the fourth specimen shows (a launched worker session of
Claude Code 2.1.292: attachment lines that are no hook's, ``file-history-delta`` lines, messages with several
tool calls, tools that are not Bash, ``gov`` behind a ``cd`` the harness kept, a Stop hook that printed
nothing) are measured; a log the reader cannot parse is "not measured" with its reason, at any version.

A result is measured or it is refused (DEC-449, DEC-454). Every case writes its own log lines, in the
specimens' forms and with its own texts, in a temporary folder; no case reads a specimen or a log of this
machine. The README maps every case to its KPI line and says which are red against the counter as built.
"""

from __future__ import annotations

import pytest

import w1_31_support as support
from w1_31_support import (EXIT_OK, LATER_VERSION, NOT_MEASURED, SESSION_A, SESSION_B, VERSION, VERSION_4,
                           pad, tokens)

OUT = pad("MARK-BONGO gov output of the case")
OUT_2 = pad("MARK-BONGO gov output of the case, the second and longer one")
TEXT = pad("MARK-SERVAL hook text of the case")
PACKET = pad("MARK-SERVAL the packet of the case")
NO_NOTES = {support.LARGER_READING: 0, support.COUNTED_WHOLE: 0}
NON_HOOK_ATTACHMENTS = (*support.ATTACHMENTS_4_START, *support.ATTACHMENTS_4_PROMPT, *support.ATTACHMENTS_4_LATER)


def printed(run):
    return run.stdout + run.stderr


def begun(version):
    """The beginning of one session as the fourth specimen shows it, at ``version``: SessionStart's run and
    the packet it added, then the brief. Its assistant lines carry an effort and a model, as the fourth
    specimen's do."""
    log = support.Log(SESSION_A, version=version)
    log.effort = "high"
    log.hook("SessionStart", PACKET, name="SessionStart:startup",
             command=support.HOOK_COMMAND_4.format("sessionstart.py"))
    return log.brief("MARK-WOMBAT # Brief: do the work")


def one_session(project, sandbox, logs, build, *, version=VERSION_4):
    """One session of the ticket at ``version``: its beginning (``begun``), what ``build`` adds, a last
    message. Returns the record, which the command gives although the ticket has no checkpoint and no close
    record yet, and the run."""
    log = begun(version)
    build(log)
    log.say((2, 60, 0, 0), "MARK-GECKO done", thinking=False).write(logs)
    run = support.run_telemetry(project, sandbox, logs, SESSION_A)
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"
    return support.record(run), run


def log_sources(result):
    """The three sources read from the logs, each a count: none of them is named in ``not_measured``."""
    unmeasured = {name: reason for name, reason in support.reasons(result).items() if name in support.LOG_SOURCES}
    assert not unmeasured, f"a form the specimens show is measured: {unmeasured}"
    return {name: result["governance_tokens"][name] for name in support.LOG_SOURCES}


def counted(packet=0, hook=0, gov=0):
    """What a case expects of the three log sources of a session begun with ``begun`` (its packet is there)."""
    return {"sessionstart_packet": tokens(PACKET) + packet, "hook_output": hook, "gov_output": gov}


def measured_figures(result, run, expected):
    """Every measured source, the two notes, the estimate and the exit code of a fixture that is measured."""
    measured_total = sum(expected["counts"].values())
    assert result["governance_tokens"] == {**expected["counts"], "total": measured_total}, \
        f"each source is the number the case computes: {expected['counts']}\n{run.describe()}"
    assert support.notes(result) == expected["notes"], f"the two notes are {expected['notes']}"
    assert support.estimate(result)["total"] == expected["estimate"]
    assert run.returncode == EXIT_OK and result["not_measured"] == [], run.describe()
    assert all(support.is_number(support.share(result, part)) for part in support.SHARE_PARTS)
    return measured_total


# --------------------------------------------------------------------------
# Every form of the fourth specimen in one session, at its version: numbers the case computes (DEC-655)
# --------------------------------------------------------------------------

def test_every_count_of_a_session_in_the_fourth_specimens_form_is_the_number_the_case_computes(
        project, sandbox, logs, ccusage):
    """Success lines 1, 2 and 3, failure lines 1 and 2. A launched worker session as Claude Code 2.1.292
    wrote it: SessionStart's packet; attachment lines that are no hook's, the lines between turns and
    ``file-history-delta`` lines, each by its type; messages of one line and of several tool calls, each
    result right after its call; Read, Grep, Write and Edit beside Bash; four ``gov`` commands behind a
    ``cd`` the harness kept, beside other commands; commands behind a ``cd`` that do not run ``gov``; a call
    a hook denies by its answer; a Stop hook that printed nothing; a totals line that names a model no
    assistant line carries. Every measured source, the two notes, the estimate, the session tokens and the
    three share figures are numbers the case computes, the exit code is 0, **and the record names the
    version that was read**: the named sessions', not that of another session's log beside them."""
    expected = support.fourth_fixture(project, logs)
    run = support.run_telemetry(project, sandbox, logs, *support.ROLED)
    fresh_in, out, created, read = expected["usage"]
    rows = support.ccusage_sessions(logs, support.cli_support.make_sandbox(project.root.parent / "probe").home)
    assert (fresh_in, out, created, read) == tuple(
        rows[SESSION_A][key] + rows[SESSION_B][key]
        for key in ("inputTokens", "outputTokens", "cacheCreationTokens", "cacheReadTokens")), \
        "the fixture is sound: ccusage counts each message once, however many calls it holds"
    assert created > 0 and read > 0 and rows[SESSION_A]["modelsUsed"] == [support.MODEL]
    result = support.record(run)
    assert (result["tokens_in"], result["tokens_out"], result["cache_creation_tokens"],
            result["cache_read_tokens"]) == (fresh_in, out, created, read), "the session's tokens are ccusage's"
    assert result["cost"] == pytest.approx(rows[SESSION_A]["totalCost"] + rows[SESSION_B]["totalCost"], abs=1e-6)
    measured_total = measured_figures(result, run, expected)
    estimate = support.estimate(result)
    assert (estimate["instruction_files"], estimate["mcp_definitions"]) == (expected["estimate"], 0), estimate
    denominator = fresh_in + created + out
    assert support.share(result, "measured") == pytest.approx(measured_total / denominator, abs=5e-5), \
        f"measured {measured_total} over {fresh_in} + {created} + {out}"
    assert support.share(result, "estimated") == pytest.approx(expected["estimate"] / denominator, abs=5e-5)
    assert support.share(result, "total") == pytest.approx(
        (measured_total + expected["estimate"]) / denominator, abs=1e-4)
    assert support.latency(result) == expected["latency"]
    assert support.models(result)["session_logs"] == [support.MODEL], \
        "the models are the assistant lines': the totals line names one more, which no assistant line carries"
    assert support.agent(result) == VERSION_4, \
        f"the record names the version that was read, {VERSION_4}: {result['agent']!r}"
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"


@pytest.mark.parametrize("version", [LATER_VERSION, VERSION, "2.2.0"],
                         ids=["a later version", "the earlier specimens' version", "a later minor version"])
def test_the_fourth_specimens_forms_are_measured_at_any_version(project, sandbox, logs, ccusage, version):
    """The same forms as another version wrote them, later or earlier: measured likewise, and each record
    names its own version. The version alone never refuses a log; no version is pinned."""
    expected = support.fourth_fixture(project, logs, version=version)
    run = support.run_telemetry(project, sandbox, logs, *support.ROLED)
    result = support.record(run)
    measured_figures(result, run, expected)
    assert support.agent(result) == version, f"the record names the version that was read: {result['agent']!r}"


@pytest.mark.parametrize("fixture, version", [
    pytest.param("second", VERSION_4, id="the second specimen's forms at 2.1.292"),
    pytest.param("third", LATER_VERSION, id="the third specimen's forms at 2.1.296"),
])
def test_the_earlier_specimens_forms_are_measured_at_any_version(project, sandbox, logs, ccusage, fixture, version):
    """The forms of the earlier specimens (hooks of six events, a compaction, sub-agents' files, denials,
    shortened results) as a later version wrote them, the sub-agents' files too: every count is the number
    it is at 2.1.288, and the record names the version that was read."""
    def change(first, second):
        first.at(version)
        second.at(version)
    build = support.second_fixture if fixture == "second" else support.third_fixture
    expected = build(project, logs, change=change)
    run = support.run_telemetry(project, sandbox, logs, *support.ROLED)
    result = support.record(run)
    measured_figures(result, run, expected)
    assert support.agent(result) == version, f"the record names the version that was read: {result['agent']!r}"
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b]: lines the fourth specimen holds by their type count nothing (DEC-655)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("full", [False, True], ids=["as the specimens hold them", "with a full line's fields"])
def test_attachment_lines_that_are_no_hooks_count_nothing(project, sandbox, logs, ccusage, full):
    """The fifteen attachment types of the specimens that are no hook's (three of them shown by the fourth
    specimen only): such a line is no hook's run and no added context, so it counts nothing, and the
    sources beside it stay measured. The specimens hold these lines by their type alone; whether the
    harness's line carries the fields of a full line (a ``version`` among them) they do not show, so both
    are measured alike."""
    def build(log):
        log.mark(*NON_HOOK_ATTACHMENTS, full=full)
        log.turn((2, 20, 0, 0), [support.bash_step("gov status", OUT)])
        log.mark("environment", "silent_turn_reminder", full=full)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == counted(gov=tokens(OUT))
    assert support.notes(result) == NO_NOTES
    assert support.agent(result) == VERSION_4


def test_the_lines_between_turns_and_the_file_history_lines_count_nothing(project, sandbox, logs, ccusage):
    """``last-prompt``, ``ai-title``, ``atis-latch``, ``file-history-snapshot`` and, shown by the fourth
    specimen only, ``file-history-delta``: the harness's own lines, held by their type. None is a hook's
    line or a tool's result: each counts nothing, and the sources beside them stay measured."""
    def build(log):
        log.bare("file-history-snapshot", sessionId=None)
        log.marks().file_history()
        log.turn((2, 20, 0, 0), [support.write_step("/work/project/docs/a.md", support.WRITTEN_4),
                                 support.bash_step("gov status", OUT)])
        log.marks().file_history(4)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == counted(gov=tokens(OUT))
    assert support.notes(result) == NO_NOTES


def test_tools_that_are_not_bash_count_nothing(project, sandbox, logs, ccusage):
    """Read, Grep, Write and Edit, as the fourth specimen shows them: a result block without ``is_error``
    and a ``toolUseResult`` of the tool's own form. None runs ``gov``, whatever its input names (a
    governance file read, a pattern that holds ``gov status``, a path that ends in ``gov``): nothing is
    counted for them and the three sources stay measured."""
    def build(log):
        log.turn((2, 30, 0, 0), [
            support.read_step("/work/project/governance/kernel/skills/discovery/SKILL.md", support.FILE_4),
            support.read_step("/work/project/.venv/bin/gov", support.FILE_4),
            support.grep_step("gov status", support.FOUND_4)])
        log.turn((2, 30, 0, 100), [
            support.write_step("/work/project/docs/gov.md", support.WRITTEN_4),
            support.edit_step("/work/project/docs/gov.md", "gap_ticket: null", "gap_ticket: MARK-1",
                              support.WRITTEN_4)], thinking=False)
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == counted()
    assert support.notes(result) == NO_NOTES


def test_several_calls_of_one_message_are_each_counted_and_the_message_once(project, sandbox, logs, ccusage):
    """One message of the model with a ``thinking`` line and four tool calls, each call's result line right
    after its call and before the next call's line: every ``gov`` result among them is counted, the other
    results are not, and the message's tokens are counted once, although five lines carry its usage."""
    def build(log):
        log.turn((7, 300, 900, 1100), [
            support.read_step("/work/project/README.md", support.FILE_4),
            support.bash_step("gov status", OUT),
            support.bash_step("ls -la src/gov", support.OTHER_OUT),
            support.bash_step("gov doctor --json", OUT_2)])
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == counted(gov=tokens(OUT) + tokens(OUT_2))
    assert support.notes(result) == NO_NOTES
    assert (result["tokens_in"], result["tokens_out"], result["cache_creation_tokens"],
            result["cache_read_tokens"]) == (7 + 2, 300 + 60, 900, 1100), \
        "the message of five lines is counted once, and the last message beside it"


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b]: ``gov`` behind a ``cd`` the harness kept (DEC-501, DEC-502, DEC-655)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("command", [*support.GOV4_COMMANDS, f"cd {support.ROOT_4} && gov status"], ids=[
    "cd; gov through a pipe; other commands", "cd; gov through a pipe; lists", "cd; gov through a pipe",
    "cd; gov; echo; another program; echo", "cd && gov"])
def test_gov_behind_a_cd_the_harness_kept_is_counted_whole(project, sandbox, logs, ccusage, command):
    """The fourth specimen's sessions call ``gov`` behind ``cd <the project's folder>;``, and the harness
    logged the command with the ``cd`` (the second specimen's was logged without it). ``gov`` is the
    command word of one of the command's simple commands, so the command runs ``gov``; it runs beside
    other commands, so the whole result is counted and the record says that one was counted whole."""
    result, _run = one_session(project, sandbox, logs, lambda log: log.turn(
        (2, 20, 0, 0), [support.bash_step(command, OUT)]))
    assert log_sources(result) == counted(gov=tokens(OUT))
    assert support.notes(result) == {support.LARGER_READING: 0, support.COUNTED_WHOLE: 1}


def test_a_command_behind_a_cd_that_does_not_run_gov_counts_nothing(project, sandbox, logs, ccusage):
    """The fourth specimen's other commands: a list of commands, a loop behind a ``cd`` over files whose
    paths name ``gov``, a program behind ``cd`` and ``&&`` whose text holds ``gov status``, a commit whose
    message names ``gov`` (the harness notes the commit beside the result). None has ``gov`` as the command
    word of a simple command: their results are not ``gov`` output, and nothing is noted."""
    def build(log):
        for number, command in enumerate(support.OTHER4_COMMANDS):
            log.turn((2, 20, 0, 0), [support.bash_step(command, support.OTHER_OUT,
                                                       committed="11308f8" if number == 4 else None)])
    result, _run = one_session(project, sandbox, logs, build)
    assert log_sources(result) == counted()
    assert support.notes(result) == NO_NOTES


# --------------------------------------------------------------------------
# Success lines 1 and 3: a Stop hook that printed nothing; the totals line's models (DEC-501, DEC-655)
# --------------------------------------------------------------------------

def test_a_stop_hook_that_printed_nothing_counts_zero(project, sandbox, logs, ccusage):
    """The Stop hook ran and printed nothing: the log holds no run line for it, only the ``system`` line
    after the Stop hooks, which names the hook, holds no error and no added context and says that there
    was no output. Nothing was added: 0, and the sources stay measured."""
    result, _run = one_session(project, sandbox, logs, lambda log: log.say(
        (2, 30, 0, 0), "MARK-GECKO the work is done", thinking=False).quiet_stop())
    assert log_sources(result) == counted()
    assert support.notes(result) == NO_NOTES


def test_the_models_are_the_assistant_lines_whatever_the_totals_line_names(project, sandbox, logs, ccusage):
    """The fourth specimen's totals line names two models, and only one of them is on an assistant line (the
    other's calls are not in the log as assistant lines). The record's models are the assistant lines';
    the latency is the totals line's API duration."""
    def build(log):
        log.totals_model = support.OTHER_MODEL
        log.api_duration = support.API_DURATION_4
    result, _run = one_session(project, sandbox, logs, build)
    assert support.models(result)["session_logs"] == [support.MODEL]
    assert support.latency(result) == support.API_DURATION_4


# --------------------------------------------------------------------------
# A log the reader cannot parse is "not measured" with its reason, at any version (DEC-655, DEC-449, DEC-454)
# --------------------------------------------------------------------------

def _line_of_another_type(log):
    log.bare("turn-ledger-unseen", content="MARK-SERVAL what such a line may hold")


def _attachment_of_another_type(log):
    log.mark("tool_guidance_unseen")


def _system_line_of_another_subtype(log):
    log.add({"type": "system", "subtype": "hook_digest_unseen", "content": TEXT, "level": "info"})


def _user_line_not_of_its_form(log):
    log.add({"promptId": "prompt-unseen", "type": "user", "message": {"role": "user", "content": {"text": TEXT}}})


def _line_that_is_no_object(log):
    log.lines.append([TEXT])


def _last_line_cut_off(log):
    log.unfinished = '{"parentUuid":null,"isSidechain":false,"type":"user","message":{"role":"user","content":"MARK-SER'


def _hook_run_of_another_type(log):
    log.hook("PostToolUse", TEXT, name="PostToolUse:Bash", run_type="hook_blocking_error", context=False)


def _sessionstart_run_with_another_exit_code(log):
    log.session_start(TEXT, exit_code=2, context=False)


ALL_THREE = support.LOG_SOURCES


@pytest.mark.parametrize("variant, sources, version", [
    pytest.param(_line_of_another_type, ALL_THREE, VERSION_4, id="a line of a type no specimen shows"),
    pytest.param(_line_of_another_type, ALL_THREE, LATER_VERSION,
                 id="a line of a type no specimen shows, at a later version"),
    pytest.param(_attachment_of_another_type, ("sessionstart_packet", "hook_output"), VERSION_4,
                 id="an attachment of a type no specimen shows"),
    pytest.param(_system_line_of_another_subtype, ALL_THREE, VERSION_4,
                 id="a system line of a subtype no specimen shows"),
    pytest.param(_user_line_not_of_its_form, ALL_THREE, VERSION_4, id="a user line that is not of its form"),
    pytest.param(_line_that_is_no_object, ALL_THREE, VERSION_4, id="a line that is no object"),
    pytest.param(_last_line_cut_off, ALL_THREE, VERSION_4, id="a last line cut off before its end"),
    pytest.param(_hook_run_of_another_type, ("hook_output",), VERSION_4, id="a hook run of a type no specimen shows"),
    pytest.param(_hook_run_of_another_type, ("hook_output",), LATER_VERSION,
                 id="a hook run of a type no specimen shows, at a later version"),
    pytest.param(_sessionstart_run_with_another_exit_code, ("sessionstart_packet",), LATER_VERSION,
                 id="a SessionStart run line with another exit code, at a later version"),
])
def test_a_log_the_reader_cannot_parse_is_not_measured_at_any_version(project, sandbox, tmp_path, ccusage,
                                                                      variant, sources, version):
    """The same session twice, as a version other than the first specimens' wrote it. In the specimens'
    forms it is measured and the record names its version: the version is no reason to refuse. With one
    line more that the reader cannot parse, each source that line could belong to is never a number:
    either the record says "not measured" for it, for the measured total and for the measured share and
    the sum (exit code 3) and names it with its reason, or the command refuses with its reason. No share
    figure is given, and no text of the log is printed."""
    def session(name, more):
        folder = tmp_path / name
        log = begun(version)
        log.turn((2, 20, 0, 0), [support.bash_step("gov status", OUT)])
        more(log)
        log.say((2, 60, 0, 0), "MARK-GECKO done", thinking=False).write(folder)
        return support.run_telemetry(project, sandbox, folder, SESSION_A)
    control = session("control-config", lambda log: None)
    result = support.record(control)
    assert log_sources(result) == counted(gov=tokens(OUT)), control.describe()
    assert support.agent(result) == version, f"the record names the version that was read: {result['agent']!r}"
    run = session("varied-config", variant)
    assert run.returncode not in (EXIT_OK, support.EXIT_USAGE), \
        f"{', '.join(sources)} cannot be a number here\n{run.describe()}"
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"
    if run.envelope().get("ok") is False:
        error = support.refusal(run)
        assert isinstance(error.get("message"), str) and error["message"].strip(), \
            f"a refusal gives its reason: {error!r}"
        return
    result = support.record(run)
    for source in sources:
        assert result["governance_tokens"][source] == NOT_MEASURED, result["governance_tokens"]
        assert support.reasons(result).get(source), \
            f"not_measured does not name {source} with its reason: {result['not_measured']}"
    assert result["governance_tokens"]["total"] == NOT_MEASURED, result["governance_tokens"]
    assert support.share(result, "measured") == NOT_MEASURED and support.share(result, "total") == NOT_MEASURED


def test_a_log_in_which_no_line_carries_a_version_is_not_measured(project, sandbox, tmp_path, ccusage):
    """Every full line of every specimen carries a version (the prompt's, the model's, a tool result's, a
    hook's, the ``system`` line's). A log none of whose lines carries one is in a form no specimen shows,
    and there is no version to record: it is "not measured" with its reason, never measured with a
    version that is empty, absent or assumed. The same log with its versions is measured."""
    def session(name, version):
        folder = tmp_path / name
        log = begun(version)
        log.turn((2, 20, 0, 0), [support.bash_step("gov status", OUT)])
        log.say((2, 60, 0, 0), "MARK-GECKO done", thinking=False).write(folder)
        return support.run_telemetry(project, sandbox, folder, SESSION_A)
    control = session("control-config", VERSION_4)
    result = support.record(control)
    assert log_sources(result) == counted(gov=tokens(OUT)), control.describe()
    assert support.agent(result) == VERSION_4
    run = session("versionless-config", None)
    assert run.returncode not in (EXIT_OK, support.EXIT_USAGE), f"no version was read\n{run.describe()}"
    assert support.MARK not in printed(run), f"text of the log is printed\n{run.describe()}"
    if run.envelope().get("ok") is False:
        error = support.refusal(run)
        assert isinstance(error.get("message"), str) and error["message"].strip(), \
            f"a refusal gives its reason: {error!r}"
        return
    result = support.record(run)
    said = result.get("agent")
    assert said == NOT_MEASURED or support.agent(result) == NOT_MEASURED, \
        f"no version was read, and the record must say so: {said!r}"
    for source in support.LOG_SOURCES:
        assert result["governance_tokens"][source] == NOT_MEASURED, result["governance_tokens"]
        assert support.reasons(result).get(source), \
            f"not_measured does not name {source} with its reason: {result['not_measured']}"
    assert support.share(result, "measured") == NOT_MEASURED and support.share(result, "total") == NOT_MEASURED
