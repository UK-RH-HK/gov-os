"""W1-31: the governance share counter, ``gov telemetry <ticket>`` (DEC-086, DEC-106, DEC-170).

The README maps every case to its KPI line and says what each fails on today. Every case but the first
depends on the fixture ``built``, which fails with "gov telemetry is not built" while the command module is
absent; an assertion failure of a case's own is a behaviour failure.
"""

from __future__ import annotations

import os
import shutil
import stat

import pytest
import yaml

import w1_31_support as support
from w1_31_support import (EXIT_GOV_ERROR, EXIT_NOT_MEASURED, EXIT_OK, EXIT_USAGE, NOT_MEASURED, OTHER_TICKET,
                           SESSION_A, SESSION_B, SESSION_NOWHERE, SESSION_OTHER, SOURCES, TICKET)

# (input, output, cache creation, cache read) of each message of the model, in sessions without hooks and
# without commands. The cases of the sources read from the logs, of the estimate and of the three share
# figures are in ``test_w1_31_measured_and_estimated.py``.
TURNS_A = [(1000, 200, 0, 50000), (500, 300, 0, 70000)]
TURNS_B = [(400, 100, 0, 0)]
TURNS_OTHER = [(9000, 900, 0, 0)]
IN_AB, OUT_AB, READ_AB = 1900, 600, 120000


def write_logs(logs, turns_a=TURNS_A):
    support.write_session(logs, SESSION_A, turns_a)
    support.write_session(logs, SESSION_B, TURNS_B)
    support.write_session(logs, SESSION_OTHER, TURNS_OTHER, cwd="/work/other")
    return logs


def measured(project, sandbox, logs, *sessions):
    return support.record(support.run_telemetry(project, sandbox, logs, *(sessions or (SESSION_A, SESSION_B))))


# --------------------------------------------------------------------------
# The command exists (the one case that does not depend on ``built``)
# --------------------------------------------------------------------------

def test_the_counter_is_a_command_of_gov(tmp_path, sandbox):
    """``gov telemetry`` is a command: an unknown ticket is a governance error in the envelope, not a usage error."""
    project = support.Project(tmp_path / "project")
    run = support.run_telemetry(project, sandbox, None, ticket="NO-SUCH-TICKET")
    assert run.returncode != EXIT_USAGE, f"gov telemetry is not built: no command module\n{run.describe()}"
    envelope = run.envelope()
    assert run.returncode == EXIT_GOV_ERROR and envelope["ok"] is False and envelope["command"] == "telemetry", \
        run.describe()
    assert envelope["error"]["code"], run.describe()


# --------------------------------------------------------------------------
# Success line 1 [CAP-04.b]: governance tokens per ticket, joined with ccusage's fresh input and output
# --------------------------------------------------------------------------

def test_joins_ccusage_input_and_output_of_the_tickets_sessions(project, sandbox, logs, ccusage):
    """The tokens in and out are ccusage's, summed over the ticket's sessions and over no other session."""
    write_logs(logs)
    result = measured(project, sandbox, logs)
    rows = support.ccusage_sessions(logs, sandbox.home)
    assert result["tokens_in"] == rows[SESSION_A]["inputTokens"] + rows[SESSION_B]["inputTokens"] == IN_AB
    assert result["tokens_out"] == rows[SESSION_A]["outputTokens"] + rows[SESSION_B]["outputTokens"] == OUT_AB
    only_a = measured(project, sandbox, logs, SESSION_A)
    assert (only_a["tokens_in"], only_a["tokens_out"]) == (1500, 500), "one session named, one session counted"


def test_names_each_of_the_seven_sources_of_governance_tokens(project, sandbox, logs, ccusage):
    """Each DEC-086 source has its own figure, a count or "not measured": the five measured ones in
    ``governance_tokens`` with their total, the two estimated ones on a line of their own (DEC-495)."""
    write_logs(logs)
    result = measured(project, sandbox, logs)
    counted = result["governance_tokens"]
    assert sorted(counted) == sorted((*SOURCES, "total")), f"the measured sources named: {sorted(counted)}"
    estimate = support.estimate(result)
    for name, value in [(name, counted[name]) for name in (*SOURCES, "total")] + \
                       [(name, estimate[name]) for name in (*support.ESTIMATED_SOURCES, "total")]:
        assert support.is_count(value) or value == NOT_MEASURED, \
            f"{name} is {value!r}: neither a count nor 'not measured'"


def test_counts_the_tickets_checkpoint_records(project, sandbox, logs, ccusage):
    """The ticket's checkpoint records are counted with W1-24's counter; another ticket's are not."""
    write_logs(logs)
    expected = project.add_checkpoint(1) + project.add_checkpoint(2, filler="after the second step")
    project.add_checkpoint(1, ticket=OTHER_TICKET, filler="x" * 400)
    assert measured(project, sandbox, logs)["governance_tokens"]["checkpoint_records"] == expected
    expected += project.add_checkpoint(3, filler="y" * 200)
    assert measured(project, sandbox, logs)["governance_tokens"]["checkpoint_records"] == expected, \
        "a further record changes the count: the figure is counted, not constant"


def test_automatic_checkpoints_are_checkpoint_records(project, sandbox, logs, ccusage):
    """A checkpoint the hooks wrote to the ignored scratch folder (DEC-444) is a checkpoint record too."""
    write_logs(logs)
    expected = project.add_checkpoint(1) + project.add_checkpoint(2, automatic=True, filler="z" * 40)
    assert measured(project, sandbox, logs)["governance_tokens"]["checkpoint_records"] == expected


def test_counts_the_tickets_close_record(project, sandbox, logs, ccusage):
    """A close record of the ticket that exists is counted; another ticket's is not."""
    write_logs(logs)
    text = f"---\nid: CL-{TICKET}\ntype: close\nstatus: ACTIVE\ntask: {TICKET}\n---\n\n# CL-{TICKET}\n\n\n"
    text += "\n" * (-len(text) % 4)
    project.write(f"docs/close/{TICKET}/CL-{TICKET}.md", text)
    project.write(f"docs/close/{OTHER_TICKET}/CL-{OTHER_TICKET}.md", text + "more\n" * 40)
    assert measured(project, sandbox, logs)["governance_tokens"]["close_records"] == support.tokens(text)


# --------------------------------------------------------------------------
# Success line 2: the share and the P1 fields, in a form a close record can carry; cache reads apart
# --------------------------------------------------------------------------

def test_record_names_every_p1_field_and_invents_none(project, sandbox, logs, ccusage):
    """Every Contract v3 P1 field of the KPI line is in the record, with a value or with "not measured"."""
    write_logs(logs)
    result = measured(project, sandbox, logs)
    absent = [name for name in (*support.P1_FIELDS, "governance_share") if name not in result]
    assert not absent, f"the record lacks {absent}"
    empty = [name for name in support.P1_FIELDS if result[name] is None or result[name] == ""]
    assert not empty, f"{empty} are empty: a field is measured or says 'not measured'"
    assert result["ticket"] == TICKET


def test_sessions_carry_what_ccusage_measured_for_each(project, sandbox, logs, ccusage):
    """One entry per session of the ticket: its id, its model, its tokens, its cache reads and its cost."""
    write_logs(logs)
    result = measured(project, sandbox, logs)
    rows = support.ccusage_sessions(logs, sandbox.home)
    by_id = {entry["session"]: entry for entry in result["sessions"]}
    assert sorted(by_id) == sorted((SESSION_A, SESSION_B)), f"the sessions listed: {sorted(by_id)}"
    for session, entry in by_id.items():
        row = rows[session]
        assert (entry["tokens_in"], entry["tokens_out"]) == (row["inputTokens"], row["outputTokens"]), entry
        assert entry["cache_read_tokens"] == row["cacheReadTokens"], entry
        assert entry["cost"] == pytest.approx(row["totalCost"], abs=1e-6), entry
        assert entry["model"] not in (None, "", []), entry


def test_cost_is_ccusages(project, sandbox, logs, ccusage):
    write_logs(logs)
    rows = support.ccusage_sessions(logs, sandbox.home)
    expected = rows[SESSION_A]["totalCost"] + rows[SESSION_B]["totalCost"]
    assert expected > 0, "the fixture's model has a price in ccusage's built-in table"
    assert measured(project, sandbox, logs)["cost"] == pytest.approx(expected, abs=1e-6)


def test_cache_reads_and_cache_creation_are_figures_of_their_own(project, sandbox, logs, ccusage):
    """Cache reads are reported separately, as ccusage gives them; so is cache creation."""
    write_logs(logs, turns_a=[(1000, 200, 3000, 50000), (500, 300, 0, 70000)])
    result = measured(project, sandbox, logs)
    assert result["cache_read_tokens"] == READ_AB
    assert result["cache_creation_tokens"] == 3000
    assert result["tokens_out"] == OUT_AB, "neither is inside the output tokens"


def test_record_is_plain_data_a_close_record_can_carry(project, sandbox, logs, ccusage):
    """The record survives the YAML frontmatter ``gov close`` writes: maps, lists, strings and numbers only."""
    write_logs(logs)
    project.add_checkpoint(1)
    result = measured(project, sandbox, logs)
    assert yaml.safe_load(yaml.safe_dump(result, sort_keys=False, allow_unicode=True)) == result


def test_the_counter_writes_nothing(project, sandbox, logs, ccusage):
    """Measuring is reading: the project is as it was. Writing the close record is ``gov close``'s work."""
    write_logs(logs)
    project.add_checkpoint(1)

    def snapshot():
        return sorted((str(path.relative_to(project.root)), path.read_bytes() if path.is_file() else None)
                      for path in project.root.rglob("*") if ".git/" not in f"{path.relative_to(project.root)}/")
    before = snapshot()
    measured(project, sandbox, logs)
    assert snapshot() == before


# --------------------------------------------------------------------------
# Failure line 2: cache reads are counted in the share
# --------------------------------------------------------------------------

def test_cache_reads_change_neither_share_nor_tokens(project, sandbox, logs, tmp_path, ccusage):
    """Two tickets' worth of logs that differ only in cache reads give the same share, total, tokens in and out."""
    project.add_checkpoint(1)
    write_logs(logs)
    heavy = tmp_path / "heavy-config"
    write_logs(heavy, turns_a=[(1000, 200, 0, 5_000_000), (500, 300, 0, 7_000_000)])
    light_result, heavy_result = measured(project, sandbox, logs), measured(project, sandbox, heavy)
    assert heavy_result["cache_read_tokens"] == 12_000_000 and light_result["cache_read_tokens"] == READ_AB
    for name in ("governance_share", "governance_tokens", "tokens_in", "tokens_out"):
        assert heavy_result[name] == light_result[name], \
            f"{name} moved with the cache reads: {light_result[name]!r} -> {heavy_result[name]!r}"
    assert heavy_result["learning_metrics"]["governance_share"] == light_result["governance_share"]


# --------------------------------------------------------------------------
# Success line 3 [CAP-40.a]: agent, provider, latency and files read
# --------------------------------------------------------------------------

def test_record_names_agent_provider_latency_and_files_read(project, sandbox, logs, ccusage):
    """Each is in the record with what the session log gave, or with "not measured"; none is empty."""
    write_logs(logs)
    result = measured(project, sandbox, logs)
    absent = [name for name in support.LOG_FIELDS if name not in result]
    assert not absent, f"the record lacks {absent}"
    empty = [name for name in support.LOG_FIELDS if result[name] is None or result[name] == ""]
    assert not empty, f"{empty} are empty: a field is measured or says 'not measured'"


# --------------------------------------------------------------------------
# Success line 4 [CAP-53.c]: the share is reported per profile
# --------------------------------------------------------------------------

@pytest.mark.parametrize("profile", ["LITE", "STANDARD", "FULL"])
def test_record_names_the_tickets_profile_beside_the_share(make_project, sandbox, logs, ccusage, profile):
    """The profile is the one the ticket file declares, so the share can be judged against that ceremony."""
    write_logs(logs)
    result = measured(make_project(profile), sandbox, logs)
    assert result["profile"] == profile
    assert "governance_share" in result


# --------------------------------------------------------------------------
# Success line 5 [CAP-40.c]: the three Wave 1 learning metrics
# --------------------------------------------------------------------------

def test_record_carries_the_three_learning_metrics(project, sandbox, logs, ccusage):
    """KPI disputes, rewritten acceptance tests and the governance share, the last the same figure as the
    record's own. The first two are a count, a list (one entry per dispute or rewrite) or "not measured"."""
    write_logs(logs)
    result = measured(project, sandbox, logs)
    metrics = result["learning_metrics"]
    assert sorted(metrics) == sorted(support.LEARNING_METRICS), f"the metrics named: {sorted(metrics)}"
    assert metrics["governance_share"] == result["governance_share"]
    for name in ("kpi_disputes", "acceptance_tests_rewritten"):
        value = metrics[name]
        assert value == NOT_MEASURED or support.is_count(value) or isinstance(value, list), \
            f"{name} is {value!r}"


# --------------------------------------------------------------------------
# Success line 6 [CAP-40.d]: the sandbox's added system-prompt tokens, a line apart
# --------------------------------------------------------------------------

def test_sandbox_tokens_are_a_line_apart_and_never_assumed(project, sandbox, logs, ccusage):
    """The line is in the record, outside the governance tokens, their estimate and every share figure. No
    measurement is recorded yet (DEC-491: it is made once, in the Wave 1 exit run), so it says "not measured":
    the 3,250 of EXP-001 is a past measurement, not a value, and appears nowhere in what is printed."""
    support.full_fixture(project, logs)
    run = support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_B)
    result = support.record(run)
    assert support.SANDBOX_LINE in result, f"the record has no {support.SANDBOX_LINE}"
    assert result[support.SANDBOX_LINE] == NOT_MEASURED, f"it is {result[support.SANDBOX_LINE]!r}"
    assert sorted(result["governance_tokens"]) == sorted((*SOURCES, "total")), \
        "the sandbox's tokens are not a source of the governance share"
    assert "sandbox" not in " ".join(support.estimate(result)).lower()
    assert sorted(result["governance_share"]) == sorted(support.SHARE_PARTS), result["governance_share"]
    assert "3250" not in run.stdout.replace(",", ""), "the constant of EXP-001 is in the output"


# --------------------------------------------------------------------------
# Failure line 1: no share figure. A figure is measured, or the command does not succeed.
# --------------------------------------------------------------------------

def test_no_session_of_the_ticket_gives_no_figure(project, sandbox, logs, ccusage):
    """No session is named for the ticket: there is no denominator, and logs of other work are not taken."""
    write_logs(logs)
    project.add_checkpoint(1)
    support.assert_no_figure(support.run_telemetry(project, sandbox, logs))


def test_named_session_without_a_log_gives_no_figure(project, sandbox, logs, ccusage):
    """ccusage answers an unknown session with nothing and exit code 0: that is not a session of zero tokens."""
    write_logs(logs)
    support.assert_no_figure(support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_NOWHERE))


def test_absent_log_folder_gives_no_figure(project, sandbox, tmp_path, ccusage):
    support.assert_no_figure(support.run_telemetry(project, sandbox, tmp_path / "no-such-config", SESSION_A))


def test_empty_log_folder_gives_no_figure(project, sandbox, logs, ccusage):
    """ccusage prints totals of zero for a folder without logs: zero is not what was measured."""
    support.assert_no_figure(support.run_telemetry(project, sandbox, logs, SESSION_A))


def test_absent_ccusage_refuses(project, sandbox, logs):
    """Without ccusage the counter refuses and says so; it reports no zero."""
    if shutil.which("ccusage", path=support.SYSTEM_PATH):
        pytest.skip("ccusage is installed in a system folder here: its absence cannot be staged")
    write_logs(logs)
    project.add_checkpoint(1)
    run = support.run_telemetry(project, sandbox, logs, SESSION_A, SESSION_B, path=support.SYSTEM_PATH)
    envelope = run.envelope()
    assert envelope["ok"] is False and run.returncode in (EXIT_GOV_ERROR, EXIT_NOT_MEASURED), run.describe()
    assert not envelope["result"], run.describe()
    assert "ccusage" in (envelope["error"]["message"] + str(envelope["error"]["details"])).lower(), run.describe()


@pytest.mark.parametrize("script", [
    pytest.param("#!/bin/sh\necho 'ccusage: cannot read' >&2\nexit 1\n", id="exit code 1"),
    pytest.param("#!/bin/sh\necho 'not a report'\nexit 0\n", id="no report"),
    pytest.param("#!/bin/sh\necho '{\"sessions\": [{\"sessionId\": \"" + SESSION_A + "\"}]}'\nexit 0\n",
                 id="a row without its figures"),
])
def test_ccusage_that_cannot_be_read_gives_no_figure(project, sandbox, logs, script):
    """A ccusage that fails, or whose answer is not its report, is a source that could not be read."""
    write_logs(logs)
    fake = sandbox.bin / "ccusage"
    fake.write_text(script, encoding="utf-8")
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    run = support.run_telemetry(project, sandbox, logs, SESSION_A, path=f"{sandbox.bin}:{support.SYSTEM_PATH}")
    support.assert_no_figure(run)
