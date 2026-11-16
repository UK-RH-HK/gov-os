"""W2-60b, KPI success-2, success-3, success-4 and failure-2 -- the record's values: from the harness's own record,
with their source; not measured when not given, never 0; counts only, never content; the window and the compactions.

success-2 [DEC-655, DEC-495]: "Each value comes from the harness's own record of that session (its session log, through
W1-31's reader, and the result line when the session ran with --output-format json), with its source named; a value
those forms do not give is not measured, with the reason, never zero or a guess." Verify: a planted session log: each
value in the record names its source; a value the log does not give is "not measured" with its reason and is never 0.

success-3 [DEC-495]: "Counts only, never content: no text of the session's log reaches the record, the Claude Code
version excepted." Verify: a planted log holding one unique sentence: a grep of the record for it finds 0 hits; the
Claude Code version is present.

success-4 [DEC-838 items 1 and 2]: "The window recorded is the one the session ran with, as its log states it (1M for
Opus 5.5), and each compaction is counted." Verify: a planted log of a 1M-window session with three compactions: the
record states the 1M window and 3 compactions.

failure-2: "A value the log does not hold reported as measured; a zero for not measured; log text in a record." Verify:
planted logs with no cost value and with a log sentence: the record shows not measured (no 0 for it) and holds 0 hits of
the sentence.

The window: no line of the harness's session log states it (the lead's search of real 2.1.31x-2.1.32x logs; W1-31's
specimens; model ids carry no ``[1m]``). The harness's result line of a ``--output-format json`` run does:
``modelUsage.<model>.contextWindow`` (``docs/assessment/2026-10/F-models-context.md`` F5, F8, F9: 200000 for
``claude-opus-4-6``). So the window case runs the session with ``-p --output-format json`` and a result line stating
1,000,000; a plain run's window is not measured (see the README's open question).
"""

from __future__ import annotations

import pytest

import w2_60b_support as t

b = t.b
ENG = t.ENGINEER
T = b.T
JSON_RUN = ("-p", "--output-format", "json", "work on the planted ticket")


def _run(cli, launch, project, log, *cli_args, result=None):
    t.set_plan(cli, log=log, result=result)
    run = launch(ENG, T.tk, *cli_args)
    assert run.run.returncode == 0 and len(run.calls) == 1, run.describe()
    sid = run.calls[0]["session_id"]
    record = t.session_record(project, sid)
    t.assert_form(record)
    return run, sid, record


def _given(run, name):
    return b.option_values(run.calls[0]["args"], name)[0]


def _one_million(value):
    return value == t.ONE_MILLION or (isinstance(value, str) and value.strip().lower() in ("1m", "1000000", "1000k"))


def test_s2_each_value_the_log_gives_is_recorded_with_its_source(cli, launch, project):
    log = t.rich_log()
    run, _, record = _run(cli, launch, project, log)
    assert t.measured(record, "model") == _given(run, "--model"), "the model is not the log's"
    assert t.measured(record, "effort") == _given(run, "--effort"), "the effort is not the log's perTurnEffort"
    got = tuple(t.measured(record, key) for key in t.TOKENS)
    assert got == log.usage(), (
        f"the four token counts {dict(zip(t.TOKENS, got))} are not the log's sums "
        f"{dict(zip(t.TOKENS, log.usage()))} (input, output, cache creation, cache read)")
    assert t.measured(record, "compactions") == 3
    assert len(t.measured(record, "rate_limit_events")) == 2
    assert t.LOG_VERSION in str(t.measured(record, "claude_code_version"))


def test_s2_a_json_run_s_result_line_gives_the_cost_with_its_source(cli, launch, project):
    _, _, record = _run(cli, launch, project, t.rich_log(), *JSON_RUN, result=t.result_line(cost=0.4321))
    assert t.measured(record, "cost_usd") == pytest.approx(0.4321), (
        "the cost is not the result line's total_cost_usd (the log holds no cost)")
    for key in ("turns", "minutes"):
        value = t.measured(record, key)
        assert isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0, (
            f"the result line gives {key}, recorded as {value!r}")


def test_f2_a_log_with_no_cost_value_records_the_cost_not_measured_never_0(cli, launch, project):
    """No totals line, no result line: the cost is given nowhere; nor is the window."""
    _, _, record = _run(cli, launch, project, t.rich_log(cost=False))
    t.not_measured(record, "cost_usd")
    t.not_measured(record, "window")


def test_f2_a_session_with_no_log_records_every_log_value_not_measured_never_0(cli, launch, project):
    _, _, record = _run(cli, launch, project, None)
    for key in ("model", "effort", "window", *t.TOKENS, "cost_usd", "turns", "compactions", "subagents",
                "rate_limit_events", "claude_code_version"):
        t.not_measured(record, key)


def test_s3_no_text_of_the_session_s_log_reaches_the_record(cli, launch, project):
    _, sid, _ = _run(cli, launch, project, t.rich_log(subagents=(("a1b2c3", t.HAIKU5),)))
    text = t.text_of(project, sid)
    for word in (t.SENTENCE, "marmoset", t.ERROR_WORD, "Work on the planted ticket", "Done with this step"):
        assert text.count(word) == 0, f"the record holds {word!r}, text of the session's log ({text.count(word)} hits)"


def test_s3_no_text_of_a_json_run_s_result_reaches_the_record(cli, launch, project):
    _, sid, _ = _run(cli, launch, project, t.rich_log(), *JSON_RUN, result=t.result_line())
    text = t.text_of(project, sid)
    for word in (t.SENTENCE, t.RESULT_WORD):
        assert text.count(word) == 0, f"the record holds {word!r} ({text.count(word)} hits)"


def test_s3_the_claude_code_version_is_recorded(cli, launch, project):
    _, _, record = _run(cli, launch, project, t.rich_log())
    assert t.LOG_VERSION in str(t.measured(record, "claude_code_version")), (
        f"the record's claude_code_version is not the log's {t.LOG_VERSION}")


def test_s4_three_compactions_are_counted_3(cli, launch, project):
    _, _, record = _run(cli, launch, project, t.rich_log(compactions=3))
    assert t.measured(record, "compactions") == 3


def test_s4_no_compaction_is_counted_0(cli, launch, project):
    _, _, record = _run(cli, launch, project, t.rich_log(compactions=0))
    assert t.measured(record, "compactions") == 0, "a log with no compact_boundary line counts 0 compactions"


def test_s4_the_window_the_session_ran_with_is_recorded_as_its_harness_record_states_it(cli, launch, project):
    """A 1M-window session (its result line's ``contextWindow`` 1,000,000) with three compactions."""
    _, _, record = _run(cli, launch, project, t.rich_log(compactions=3), *JSON_RUN,
                        result=t.result_line(window=t.ONE_MILLION))
    window = t.measured(record, "window")
    assert _one_million(window), f"the record's window is {window!r}, not the 1M the session ran with"
    assert t.measured(record, "compactions") == 3
