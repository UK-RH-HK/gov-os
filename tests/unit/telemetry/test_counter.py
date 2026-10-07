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
    return {**FULL, "type": "attachment", "attachment": {"type": kind, "hookEvent": event, **fields}}


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
            hook("SessionStart", exitCode=0), context("SessionStart", PACKET),
            {**FULL, "type": "user", "message": {"role": "user", "content": SECRET}},
            *bash(1, "PYTHONPATH=/work/src python3 -m gov.cli.main doctor --help"),
            hook("PostToolUse", exitCode=0), context("PostToolUse", ADDED),
            *assistant(2, {"type": "text", "text": SECRET}),
            {"type": "cost-state", "sessionId": SESSION, "modelUsage": {}}]


def read(tmp_path, lines):
    path = tmp_path / "config" / "projects" / "-work-project" / f"{SESSION}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(line, separators=(",", ":")) + "\n" for line in lines), encoding="utf-8")
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


@pytest.mark.parametrize("text, runs", [
    ("gov status", True), ("A=1 B=2 gov check --json", True), ("python3 -m gov.cli.main doctor", True),
    ("echo gov status", False), ("grep -rn gov docs", False), ("git commit -m 'gov close; refuses'", False),
    ("python3 -m gov_tools.report", False), ("ls src/gov  # a folder", False),
])
def test_a_command_runs_gov_only_in_the_two_known_forms(text, runs):
    assert sessionlog.gov_command(text) is runs


@pytest.mark.parametrize("text", [
    "gov status && gov check", "gov status | head -5", "gov status > out.txt", "gov status 2>&1", "gov status\nls",
    "cd src; gov status", ".venv/bin/gov status", "uv run gov status", "python -m gov.cli.main status",
    "echo $(gov status)", "gov status 'unclosed", "ls src  # it's a comment nobody can split into words",
])
def test_a_gov_command_of_another_form_is_not_measured(tmp_path, text):
    """AD-2, until it is decided: compound, redirected, by a path, through another runner."""
    assert isinstance(sessionlog.gov_command(text), str)
    log = read(tmp_path, [*specimen_form(), *bash(3, text)])
    assert SECRET not in json.dumps(log["missing"]) and list(log["missing"]) == ["gov_output"]


def test_a_gov_result_marked_as_an_error_is_not_measured(tmp_path):
    """AD-2, until it is decided."""
    log = read(tmp_path, [*specimen_form(), *bash(3, "gov close PROJ-aaaa", is_error=True)])
    assert list(log["missing"]) == ["gov_output"] and SECRET not in json.dumps(log["missing"])


@pytest.mark.parametrize("line, sources, named", [
    (hook("PreToolUse", exitCode=0), ["hook_output"], "PreToolUse"),         # AD-6: it added no context
    (context("Stop", ADDED), ["hook_output"], "Stop"),
    (hook(SECRET, exitCode=0), ["hook_output"], ""),                          # an event nobody can name
    (hook("SessionStart", "hook_non_blocking_error"), ["sessionstart_packet"], ""),
    ({**FULL, "type": "attachment", "attachment": {"type": SECRET}}, ["sessionstart_packet", "hook_output"], ""),
    ({**FULL, "type": "system", "subtype": SECRET}, ["sessionstart_packet", "hook_output", "gov_output"], ""),
])
def test_a_line_the_specimen_does_not_show_is_not_measured_for_its_source(tmp_path, line, sources, named):
    log = read(tmp_path, [*specimen_form(), line])
    assert list(log["missing"]) == sources
    assert named in json.dumps(log["missing"]) and SECRET not in json.dumps(log["missing"])


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
