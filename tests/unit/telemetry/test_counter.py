"""Builder tests for ``gov telemetry`` (W1-31). Regression evidence only (DEC-136).

No test reads a real session log, and none reads the specimen: each writes its own lines in the specimen's
form in a temporary folder, ``ccusage`` is a stand-in script there, and ``HOME`` and ``CLAUDE_CONFIG_DIR``
are temporary.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.telemetry import command, counter, sessionlog  # noqa: E402
from gov.telemetry.counter import NOT_MEASURED  # noqa: E402

TICKET, SESSION = "PROJ-aaaa", "11111111-1111-4111-8111-111111111111"
FULL = {"isSidechain": False, "sessionId": SESSION, "version": sessionlog.VERSION}
SECRET = "SECRET-TEXT"  # in every text of a log line: it may reach no reason and no refusal
PACKET, ADDED, OUTPUT = SECRET + " packet.", SECRET + " added by a hook", SECRET + " output of gov..."


def hook(event, kind="hook_success", **fields):
    """A hook line; a run is the specimens' unless ``fields`` say otherwise: exit code 0 and no output."""
    fields = {"content": "", "exitCode": 0, **fields} if kind == "hook_success" else fields
    return {**FULL, "type": "attachment", "attachment": {"type": kind, "hookEvent": event, **fields}}


def failing(event, text=None):
    return hook(event, "hook_non_blocking_error", stderr=text or SECRET + " failed.", stdout="", exitCode=1)


def context(event, text):
    return hook(event, "hook_additional_context", content=[text])


def assistant(number, block, usage=(10, 20, 30, 40)):
    """The two lines of one message of the model, each with the whole usage."""
    message = {"id": f"msg_{number}", "model": "claude-opus-5-5",
               "usage": dict(zip(sessionlog.USAGE, usage))}
    return [{**FULL, "type": "assistant", "requestId": f"req_{number}", "message": {**message, "content": [each]}}
            for each in ({"type": "thinking", "thinking": ""}, block)]


def bash(number, text, output=OUTPUT, is_error=False):
    """A command through the Bash tool and its result."""
    call = {"type": "tool_use", "id": f"toolu_{number}", "name": "Bash", "input": {"command": text}}
    result = {"type": "tool_result", "tool_use_id": f"toolu_{number}", "content": output, "is_error": is_error}
    return [*assistant(number, call), {**FULL, "type": "user", "message": {"role": "user", "content": [result]}}]


def specimen_form():
    """One SessionStart hook with its packet, one ``gov`` command, one PostToolUse hook with its text."""
    return [{"type": "queue-operation", "sessionId": SESSION},
            hook("SessionStart"), context("SessionStart", PACKET),
            {**FULL, "type": "user", "message": {"role": "user", "content": SECRET}},
            *bash(1, "PYTHONPATH=/work/src python3 -m gov.cli.main doctor --help"),
            hook("PostToolUse"), context("PostToolUse", ADDED),
            *assistant(2, {"type": "text", "text": SECRET}),
            {"type": "cost-state", "sessionId": SESSION, "modelUsage": {}}]


def dump(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(line, separators=(",", ":")) + "\n" for line in lines), encoding="utf-8")


def read(tmp_path, lines, subagent=None):
    """Write the session's log, and ``subagent`` as the log of a sub-agent in its place, and read both."""
    folder = tmp_path / "config" / "projects" / "-work-project"
    dump(folder / f"{SESSION}.jsonl", lines)
    if subagent is not None:
        dump(folder / SESSION / "subagents" / "agent-a1b2c3.jsonl", [{**line, "isSidechain": True}
                                                                     for line in subagent])
        (folder / SESSION / "subagents" / "agent-a1b2c3.meta.json").write_text("{}", encoding="utf-8")
    return sessionlog.read(sessionlog.find(tmp_path / "config", SESSION), SESSION)


def row(**changes):
    """ccusage's row of the session of ``specimen_form``: two messages, each counted once."""
    return {"sessionId": SESSION, "inputTokens": 20, "outputTokens": 40, "cacheCreationTokens": 60,
            "cacheReadTokens": 80, "totalCost": 0.02, "modelsUsed": ["claude-opus-5-5"],
            "modelBreakdowns": [{"modelName": "claude-opus-5-5", "cost": 0.02}], **changes}


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A project with one ticket, the session's log in the specimen's form, and a stand-in ccusage that
    prints ``report.json``."""
    root = tmp_path / "project"
    (root / ".tickets").mkdir(parents=True)
    (root / ".tickets" / f"{TICKET}.md").write_text(f"---\nid: {TICKET}\nprofile: LITE\n---\n# t\n", encoding="utf-8")
    (tmp_path / "bin").mkdir()
    stand_in = tmp_path / "bin" / "ccusage"
    stand_in.write_text(f"#!/bin/sh\ncat '{tmp_path}/report.json'\n", encoding="utf-8")
    stand_in.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}/bin:/usr/bin:/bin")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "config"))
    read(tmp_path, specimen_form())
    return root


def report(project, *rows):
    (project.parent / "report.json").write_text(json.dumps({"sessions": list(rows)}), encoding="utf-8")


def test_the_share_is_a_number_only_when_every_part_was_measured():
    assert counter.share(250, 2500) == 0.1
    assert counter.share(NOT_MEASURED, 2500) == NOT_MEASURED
    assert counter.share(250, 0) == NOT_MEASURED, "no tokens in the sessions is no denominator"


def test_a_log_in_the_specimens_form_is_counted_each_message_once(tmp_path):
    log = read(tmp_path, specimen_form())
    assert log["usage"] == (20, 40, 60, 80) and log["models"] == ["claude-opus-5-5"] and log["missing"] == {}
    assert log["counts"] == {"sessionstart_packet": 5, "hook_output": 7, "gov_output": 7}
    assert log["notes"] == dict.fromkeys(sessionlog.NOTES, 0) and log["versioned"]
    assert log["duration"] is None, "its totals line names no API duration"


ALONE, BESIDE, NOT_GOV = (True, False), (True, True), (False, False)


@pytest.mark.parametrize("text, told", [
    ("gov status", ALONE), ("A=1 B=2 gov check --json", ALONE), ("python3 -m gov.cli.main doctor", ALONE),
    ("gov status && gov check", BESIDE), ("gov status | head -5", BESIDE), ("gov status > out.txt", BESIDE),
    ("gov status 2>&1", BESIDE), ("gov status\nls", BESIDE), ("cd src; gov status", BESIDE),
    ("echo gov status", NOT_GOV), ("grep -rn gov docs", NOT_GOV), ("git commit -m 'gov close; refuses'", NOT_GOV),
    ("python3 -m gov_tools.report", NOT_GOV), ("ls src/gov  # a folder", NOT_GOV),
])
def test_a_command_runs_gov_in_the_two_known_forms_alone_or_beside_others(text, told):
    assert sessionlog.gov_command(text) == told


@pytest.mark.parametrize("text", [
    ".venv/bin/gov status", "uv run gov status", "python -m gov.cli.main status", "ls && ./gov status",
    "gov status 'unclosed", "ls src  # it's a comment nobody can split into words",
])
def test_a_gov_command_by_a_path_or_through_a_runner_is_not_measured(tmp_path, text):
    """AD-2, until it is decided; and a command whose words cannot be told apart."""
    assert isinstance(sessionlog.gov_command(text), str)
    log = read(tmp_path, [*specimen_form(), *bash(3, text)])
    assert SECRET not in json.dumps(log["missing"]) and list(log["missing"]) == ["gov_output"]


def test_the_second_specimens_forms_are_counted_and_the_larger_readings_noted(tmp_path):
    """DEC-501: an error result, context of another event, a failing hook, a blocked call, runs that add
    nothing, a compaction, the packet again, two totals lines; and a sub-agent's file with the session."""
    blocked = "PreToolUse:Bash hook error: [hook]: " + SECRET
    call = {"type": "tool_use", "id": "toolu_4", "name": "Bash", "input": {"command": "gov status"}}
    result = {"type": "tool_result", "tool_use_id": "toolu_4", "content": blocked, "is_error": True}
    summary = {"hookErrors": [], "hookAdditionalContext": [], "preventedContinuation": False}
    lines = [*specimen_form(), *bash(3, "gov close PROJ-aaaa", is_error=True),
             hook("PreToolUse"), context("PreToolUse", ADDED), failing("PostToolUse"), *assistant(4, call),
             {**FULL, "type": "user", "toolDenialKind": "permission-rule",
              "message": {"role": "user", "content": [result]}},
             hook("Stop", content=SECRET), {**FULL, "type": "system", "subtype": "stop_hook_summary", **summary},
             {"type": "mode", "sessionId": SESSION}, {**FULL, "type": "system", "subtype": "compact_boundary"},
             {**FULL, "type": "user", "message": {"role": "user", "content": "<local-command-stdout>" + SECRET}},
             hook("SessionStart"), context("SessionStart", PACKET),
             {"type": "cost-state", "sessionId": SESSION, "totalAPIDuration": 700}]
    early, late = assistant(6, {"type": "text", "text": SECRET}, usage=(1, 141, 3, 4))
    early["message"]["usage"] = {**late["message"]["usage"], "output_tokens": 14}
    log = read(tmp_path, lines, subagent=[*bash(5, "gov status | head -1"), failing("PostToolUse"), early, late,
                                          hook("SubagentStop", content=SECRET)])
    assert log["missing"] == {}
    assert log["counts"] == {"sessionstart_packet": 5 + 5, "hook_output": 7 + 7 + 5 + 12 + 5, "gov_output": 7 + 7 + 7}
    assert log["notes"] == {"larger_reading_hook_texts": 3, "gov_results_counted_whole": 1}
    assert log["usage"] == (51, 241, 153, 204), "the sub-agent's messages too, the first by its later line"
    assert log["duration"] == 700, "the last totals line of the session's own file"


SUMMARY_WITH_CONTEXT = {**FULL, "type": "system", "subtype": "stop_hook_summary", "hookErrors": [],
                        "hookAdditionalContext": [SECRET], "preventedContinuation": False}
DENIED_OTHERWISE = {**FULL, "type": "user", "toolDenialKind": "permission-rule", "message": {
    "role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_9", "content": SECRET, "is_error": True}]}}
PACKET_AND_HOOKS = ["sessionstart_packet", "hook_output"]


@pytest.mark.parametrize("line, sources", [
    (failing("SessionStart"), PACKET_AND_HOOKS),                       # AD-8, until it is decided
    (hook("PostToolUse", exitCode=2), ["hook_output"]),
    (hook("PostToolUse", content=SECRET), ["hook_output"]),            # a run with output, of no Stop event
    (hook("PostToolUse", "hook_blocking_error"), ["hook_output"]),
    (failing("PostToolUse", [SECRET]), ["hook_output"]),
    (SUMMARY_WITH_CONTEXT, ["hook_output"]),
    (DENIED_OTHERWISE, ["hook_output"]),                               # a denial that is not a hook's
    ({**FULL, "type": "attachment", "attachment": {"type": SECRET}}, PACKET_AND_HOOKS),
    ({**FULL, "type": "system", "subtype": SECRET}, list(sessionlog.LOG_SOURCES)),
    ({**FULL, "type": SECRET}, list(sessionlog.LOG_SOURCES)),
    ({**hook("PostToolUse"), "isSidechain": True}, list(sessionlog.LOG_SOURCES)),  # a side-chain line, own file
])
def test_a_line_neither_specimen_shows_is_not_measured_for_its_source(tmp_path, line, sources):
    log = read(tmp_path, [*specimen_form(), line])
    assert list(log["missing"]) == sources and SECRET not in json.dumps(log["missing"])


def test_a_subagents_file_in_another_form_or_a_folder_nobody_read_refuses(tmp_path):
    folder = tmp_path / "config" / "projects" / "-work-project" / SESSION
    log = read(tmp_path, specimen_form(), subagent=[hook("PostToolUse", "hook_blocking_error")])
    assert list(log["missing"]) == ["hook_output"], "an unseen line of a sub-agent leaves no clean figure"
    (folder / "subagents" / "agent-a1b2c3.jsonl").write_text(SECRET + "\n", encoding="utf-8")
    (folder / "subagents" / "agent-d4e5f6.jsonl").mkdir()
    (folder / "tool-results").mkdir()
    for code, remove in (("SESSION_LOG_FORM", folder / "tool-results"),               # a folder nobody read
                         ("SESSION_LOG_FORM", folder / "subagents" / "agent-a1b2c3.jsonl"),  # no JSON
                         ("SESSION_LOG_UNREADABLE", folder / "subagents" / "agent-d4e5f6.jsonl")):
        with pytest.raises(GovError) as refusal:
            sessionlog.read(sessionlog.find(tmp_path / "config", SESSION), SESSION)
        assert refusal.value.code == code
        assert SECRET not in refusal.value.message + json.dumps(refusal.value.details)
        remove.rmdir() if remove.is_dir() else remove.unlink()


@pytest.mark.parametrize("version, named", [("2.1.999", "2.1.999"), (SECRET, "names no version"), (None, "no version")])
def test_a_log_of_another_version_is_refused_and_only_a_version_is_named(tmp_path, version, named):
    lines = specimen_form()
    lines[2] = {**lines[2], "version": version}
    with pytest.raises(GovError) as refusal:
        read(tmp_path, lines)
    assert refusal.value.code == "SESSION_LOG_VERSION"
    assert named in refusal.value.message and SECRET not in refusal.value.message + json.dumps(refusal.value.details)


def test_the_record_of_a_bare_project_and_the_commands_exit_code(project):
    report(project, row())
    args = argparse.Namespace(ticket=TICKET, ticket_session=[SESSION, SESSION])
    record, code = command.run(project, args, {})
    assert code == command.EXIT_NOT_MEASURED == 3
    assert record["governance_tokens"] == {"sessionstart_packet": 5, "hook_output": 7, "gov_output": 7,
                                           "checkpoint_records": NOT_MEASURED, "close_records": NOT_MEASURED,
                                           "total": NOT_MEASURED}
    assert [entry["name"] for entry in record["not_measured"]] == [
        "checkpoint_records", "close_records", "instruction_files", "mcp_definitions"]
    assert record["governance_share"] == dict.fromkeys(("measured", "estimated", "total"), NOT_MEASURED)
    assert record["estimated_governance_tokens"]["files"] == NOT_MEASURED, "it stands on no file that was read"
    assert (record["tokens_in"], record["tokens_out"], record["profile"]) == (20, 40, "LITE"), "named once"
    assert record["sandbox_system_prompt_tokens"] == NOT_MEASURED and SECRET not in json.dumps(record)
    assert record["counting_notes"] == {"larger_reading_hook_texts": 0, "gov_results_counted_whole": 0}
    assert record["known_gaps"][0]["name"] == "precompact_hook_output", "named in every record, compacted or not"
    assert record["latency"] == {"harness_api_duration_ms": NOT_MEASURED}, "no totals line with an API duration"
    assert record["sessions"][0]["harness_api_duration_ms"] == NOT_MEASURED
    assert record["agent"] == {"harness": "Claude Code", "version": "2.1.288"}
    assert record["model"]["commits"] == NOT_MEASURED == record["learning_metrics"]["acceptance_tests_rewritten"]


def test_the_estimate_counts_no_mcp_server_it_cannot_class(project):
    """AD-1, until it is decided: a count only where the file was read and defines no server."""
    report(project, row())
    (project / "CLAUDE.md").write_text("rule" * 25, encoding="utf-8")
    mcp = project / ".mcp.json"
    for text, expected in (('{"mcpServers": {}}', 0), ('{"mcpServers": {"gov": {"command": "x"}}}', NOT_MEASURED),
                           ("{}", NOT_MEASURED), ("not JSON", NOT_MEASURED)):
        mcp.write_text(text, encoding="utf-8")
        estimate = counter.measure(project, TICKET, [SESSION])["estimated_governance_tokens"]
        assert (estimate["instruction_files"], estimate["mcp_definitions"]) == (25, expected), text
        assert estimate["total"] == (25 if expected == 0 else NOT_MEASURED)


def test_a_cost_without_a_price_for_every_model_is_not_measured(project):
    report(project, row(modelBreakdowns=[{"modelName": "a", "cost": 0.02},
                                         {"modelName": "b", "cost": 0.0, "missingPricing": True}]))
    record = counter.measure(project, TICKET, [SESSION])
    assert record["cost"] == NOT_MEASURED == record["sessions"][0]["cost"]
    assert record["cache_read_tokens"] == 80


@pytest.mark.parametrize("rows", [[], [row(), row()], [row(outputTokens=None)], [row(inputTokens=True)],
                                  [row(inputTokens=10)], [row(cacheReadTokens=0)]],
                         ids=["no row", "two rows", "a figure absent", "a figure that is no count",
                              "a line passed over", "cache reads that differ"])
def test_a_session_ccusage_did_not_measure_as_its_log_reads_refuses(project, rows):
    report(project, *rows)
    with pytest.raises(GovError) as refusal:
        counter.measure(project, TICKET, [SESSION])
    assert refusal.value.code == "SESSIONS_NOT_MEASURED"
