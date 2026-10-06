"""Command-level tests: ``gov context`` through its ``--json`` envelope (API-0002, DEC-317).

Red reason: ``src/gov/context/command.py`` does not exist (the command module is not built).
"""

from __future__ import annotations

import json

import w1_24_support as S


def test_gov_context_prints_the_api_0002_envelope(cli, project):
    """``gov context --json --root <project> <ticket>`` prints a JSON envelope with the API-0002 fields."""
    run = cli.command(project, S.TK_NORMAL)
    envelope = run.envelope()
    assert isinstance(envelope, dict)
    assert "ok" in envelope and "command" in envelope and "result" in envelope and "session" in envelope, \
        f"the envelope lacks a required field: {sorted(envelope)}"
    assert isinstance(envelope["ok"], bool)
    assert isinstance(envelope["command"], str)
    assert isinstance(envelope["session"], str)


def test_the_envelope_result_is_the_packet(cli, project):
    """The envelope's ``result`` is the context packet (a map with mandatory, authority, hash, budget)."""
    packet = cli.command(project, S.TK_NORMAL).packet()
    S.check_packet(packet)
    found_ids = {item[S.M_ID] for item in packet[S.K_MANDATORY]}
    for source_id in S.ALL_NORMAL_SOURCES:
        assert source_id in found_ids, f"{source_id} is missing from the command's packet"


def test_a_missing_input_gives_the_blocked_error(cli, project):
    """``gov context`` with a ticket that names a missing source gives exit code 1 and error code BLOCKED."""
    run = cli.command(project, S.TK_BLOCKED)
    assert run.returncode != 0, f"the command succeeded with a missing mandatory input\n{run.describe()}"
    envelope = run.envelope()
    assert envelope["ok"] is False, f"ok is true with a missing mandatory input\n{run.describe()}"
    error = envelope.get("error", {})
    assert error.get("code") == S.BLOCKED, \
        f"expected error code {S.BLOCKED!r}, got {error.get('code')!r}\n{run.describe()}"


def test_repeated_runs_print_the_same_bytes(cli, project):
    """Two runs with the same arguments produce the same standard output (deterministic, CAP-38.b)."""
    out1 = cli.command(project, S.TK_NORMAL).stdout
    out2 = cli.command(project, S.TK_NORMAL).stdout
    env1 = json.loads(out1)
    env2 = json.loads(out2)
    env1.pop("session", None)
    env2.pop("session", None)
    assert env1 == env2, "two runs with the same arguments produced different envelopes (ignoring session)"


def test_brief_prints_the_path_and_summary(cli, project):
    """``gov context --json --brief <ticket>`` returns a result with a path and a summary."""
    run = cli.command(project, "--brief", S.TK_BRIEF)
    assert run.returncode == 0, f"--brief failed\n{run.describe()}"
    result = run.packet()
    assert isinstance(result.get("path"), str) and result["path"], "the brief result has no path"
    assert isinstance(result.get("summary"), str) and result["summary"], "the brief result has no summary"
