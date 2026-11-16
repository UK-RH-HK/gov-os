"""W2-60b S2, S4: the result line of a session run with ``--output-format json``.

When the CLI arguments hold ``--output-format json``, the launcher starts the CLI with its stdout on a pipe, relays
every byte unchanged and in order to its own stdout, and keeps the last complete line that parses as a JSON object of
``"type": "result"`` for the session record. In every other mode stdout is inherited as before. A relay failure keeps
the session's exit code and says one stderr line.

These cases start real processes (a stand-in CLI written in Python), never the real CLI or a model."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests" / "unit" / "launch"))
sys.path.insert(0, str(REPO / "tests" / "unit" / "telemetry"))

from gov.launch import launcher  # noqa: E402
import test_session_record_launch as base  # noqa: E402
from test_session_record_launch import TICKET, Session, project  # noqa: E402,F401
from test_sessionlog_w2_60b import SECRET  # noqa: E402

REAL_POPEN = subprocess.Popen  # taken before the fixture puts the stand-in in its place
RESULT = {"type": "result", "subtype": "success", "is_error": False, "num_turns": 4, "duration_ms": 90000,
          "session_id": "x", "total_cost_usd": 1.75, "result": SECRET,
          "modelUsage": {"claude-opus-5-5": {"costUSD": 1.75, "contextWindow": 1000000}}}


# -- which runs are relayed -----------------------------------------------------------------------------------------

@pytest.mark.parametrize("args, relayed", (
    (["-p", "hi", "--output-format", "json"], True),
    (["--output-format=json", "-p", "hi"], True),
    (["--output-format", "text", "--output-format", "json"], True),
    (["--output-format", "json", "--output-format", "text"], False),
    (["--output-format", "stream-json"], False),
    (["--output-format=text"], False),
    (["-p", "--output-format json"], False),
    (["--output-format"], False),
    ([], False),
))
def test_only_a_json_run_is_relayed(args, relayed):
    assert launcher._json_output(args) is relayed


def _options_seen(monkeypatch):
    seen = []

    class Seen(Session):
        def __init__(self, argv, cwd, env, **options):
            seen.append(options)
            super().__init__(argv, cwd, env, **options)

    monkeypatch.setattr(launcher.subprocess, "Popen", Seen)
    return seen


def test_an_interactive_run_inherits_stdout_as_before(project, monkeypatch):
    seen = _options_seen(monkeypatch)
    assert launcher.launch(project, "engineer", TICKET, []) == 0
    assert "stdout" not in seen[0]


def test_a_json_run_puts_the_session_s_stdout_on_a_pipe(project, monkeypatch):
    seen = _options_seen(monkeypatch)
    assert launcher.launch(project, "engineer", TICKET, ["-p", "hi", "--output-format", "json"]) == 0
    assert seen[0].get("stdout") == subprocess.PIPE


# -- the relay itself -----------------------------------------------------------------------------------------------

def _child(code: str):
    return REAL_POPEN([sys.executable, "-c", textwrap.dedent(code)], stdout=subprocess.PIPE)


def _relay_into(child, out: int, said: list):
    relay = launcher._Relay(child.stdout.fileno(), out=out, say=said.append)
    relay.pump(lambda: child.poll() is None)
    code = child.wait()
    relay.drain(5)
    relay.close()
    child.stdout.close()
    return relay, code


def _relay_to_file(tmp_path, code: str):
    said: list = []
    target = tmp_path / "out.bin"
    with open(target, "wb") as handle:
        relay, exit_code = _relay_into(_child(code), handle.fileno(), said)
    return relay, exit_code, target.read_bytes(), said


def test_the_bytes_are_relayed_unchanged_with_a_partial_last_line(tmp_path):
    code = """
        import os, json
        data = bytes(range(256)) * 3 + b"\\r\\n\\x00line two\\n" + json.dumps({"type": "result", "a": 1}).encode() \\
            + b"\\n" + b"a partial last line, no newline"
        os.write(1, data)
        raise SystemExit(7)
    """
    relay, exit_code, out, said = _relay_to_file(tmp_path, code)
    expected = (bytes(range(256)) * 3 + b"\r\n\x00line two\n" + json.dumps({"type": "result", "a": 1}).encode()
                + b"\n" + b"a partial last line, no newline")
    assert out == expected and exit_code == 7 and said == []
    assert relay.result == {"type": "result", "a": 1}


def test_a_large_output_is_relayed_whole_and_in_order(tmp_path):
    code = """
        import os, json, random
        random.seed(5)
        chunk = bytes(random.getrandbits(8) for _ in range(65536)).replace(b"\\n", b".")
        for i in range(80):
            os.write(1, b"%05d:" % i + chunk + b"\\n")
        os.write(1, json.dumps({"type": "result", "total_cost_usd": 2.0}).encode() + b"\\n")
    """
    relay, exit_code, out, said = _relay_to_file(tmp_path, code)
    lines = out.split(b"\n")
    assert len(out) == 80 * (6 + 65536 + 1) + len(json.dumps({"type": "result", "total_cost_usd": 2.0})) + 1
    assert [line[:6] for line in lines[:80]] == [b"%05d:" % i for i in range(80)]
    assert exit_code == 0 and relay.result == {"type": "result", "total_cost_usd": 2.0} and said == []


def test_the_last_result_line_is_kept_and_other_lines_are_not(tmp_path):
    code = """
        import json
        print(json.dumps({"type": "result", "n": 1}))
        print(json.dumps({"type": "assistant", "n": 2}))
        print(json.dumps({"type": "result", "n": 3}))
        print("[1, 2]")
        print("{not json")
    """
    relay, _code, _out, _said = _relay_to_file(tmp_path, code)
    assert relay.result == {"type": "result", "n": 3}


def test_a_truncated_last_line_is_not_a_result(tmp_path):
    code = """
        import os
        os.write(1, b'{"type": "result", "n": 1}\\n{"type": "result", "n"')
    """
    relay, _code, out, _said = _relay_to_file(tmp_path, code)
    assert relay.result == {"type": "result", "n": 1} and out.endswith(b'"n"')


def test_a_line_nested_too_deep_to_parse_is_relayed_and_is_no_result(tmp_path):
    """json.loads raises RecursionError (not ValueError) on deep nesting: the relay goes on, the code is kept."""
    code = """
        import os, json
        os.write(1, json.dumps({"type": "result", "n": 1}).encode() + b"\\n")
        os.write(1, b'{"type": "result", "x": ' + b"[" * 200000 + b"]" * 200000 + b"}\\nafter\\n")
        raise SystemExit(4)
    """
    relay, exit_code, out, said = _relay_to_file(tmp_path, code)
    assert exit_code == 4 and out.endswith(b"}\nafter\n") and len(out) > 400000
    assert relay.result == {"type": "result", "n": 1} and said == []


def test_no_output_gives_no_result(tmp_path):
    relay, exit_code, out, said = _relay_to_file(tmp_path, "raise SystemExit(3)")
    assert out == b"" and relay.result is None and exit_code == 3 and said == []


def test_a_stdout_that_cannot_be_written_keeps_the_code_says_one_line_and_still_reads_the_result(tmp_path):
    read_end, write_end = os.pipe()
    os.close(read_end)  # nobody reads the launcher's stdout: every write fails (EPIPE)
    said: list = []
    child = _child("""
        import json
        for i in range(2000):
            print("x" * 100)
        print(json.dumps({"type": "result", "total_cost_usd": 0.5}))
        raise SystemExit(9)
    """)
    try:
        relay, exit_code = _relay_into(child, write_end, said)
    finally:
        os.close(write_end)
    assert exit_code == 9  # the session was never blocked on a full pipe, and its code is its own
    assert len(said) == 1 and said[0].count("\n") == 1 and "stdout" in said[0]
    assert relay.result == {"type": "result", "total_cost_usd": 0.5}


# -- through the launcher, with a real process ----------------------------------------------------------------------

def _stand_in_cli(project, body: str) -> None:
    cli = Path(os.environ["HOME"]) / launcher.CLI_REL
    cli.write_text(f"#!{sys.executable}\n" + textwrap.dedent(body), encoding="utf-8")
    cli.chmod(0o755)


@pytest.fixture
def started(project, monkeypatch):
    monkeypatch.setattr(launcher.subprocess, "Popen", REAL_POPEN)
    return project


def test_a_json_launch_relays_the_bytes_keeps_the_code_and_records_the_result_line(started, capfdbinary):
    _stand_in_cli(started, f"""
        import json, os, sys
        os.write(1, b"first\\n\\x00\\xff binary\\n")
        os.write(1, json.dumps({RESULT!r}).encode() + b"\\n")
        raise SystemExit(3)
    """)
    assert launcher.launch(started, "engineer", TICKET, ["-p", "hi", "--output-format", "json"]) == 3
    assert capfdbinary.readouterr().out == b"first\n\x00\xff binary\n" + json.dumps(RESULT).encode() + b"\n"
    record = base._record(started)
    assert record["exit_code"] == 3
    assert record["cost_usd"] == {"value": 1.75, "source": record["cost_usd"]["source"]}
    assert "result line" in record["cost_usd"]["source"] and record["window"]["value"] == 1000000
    assert record["turns"]["value"] == 4 and record["minutes"]["value"] == 1.5
    assert SECRET not in base._records(started)[0].read_text(encoding="utf-8")


def test_a_json_launch_relays_exact_bytes(started, tmp_path):
    """The launcher's stdout byte for byte: ``gov launch`` run as its own process, its stdout read as bytes."""
    payload = bytes(range(256)) + b"\n" + json.dumps(RESULT).encode() + b"\ntail without newline"
    (tmp_path / "payload.bin").write_bytes(payload)
    _stand_in_cli(started, f"""
        import os
        os.write(1, open({str(tmp_path / 'payload.bin')!r}, 'rb').read())
    """)
    script = textwrap.dedent(f"""
        import sys
        sys.path.insert(0, {str(REPO / 'tests' / 'unit' / 'launch')!r})
        from gov.launch import launcher
        launcher._check_repository_settings = lambda *a: None
        sys.exit(launcher.launch({str(started)!r}, "engineer", {TICKET!r}, ["-p", "x", "--output-format=json"]))
    """)
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    done = REAL_POPEN([sys.executable, "-c", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out, err = done.communicate(timeout=60)
    assert done.returncode == 0, err
    assert out == payload
    assert base._record(started)["cost_usd"]["value"] == 1.75


def test_a_signal_mid_run_keeps_relaying_to_the_end_and_gives_the_interrupt_exit(started, capfd):
    """DEC-392: the session asks its launcher to end (SIGINT) after a first part; the launcher asks the session's group
    to end (SIGTERM), and the session writes its last part, the result line, on the way out: all of it is relayed."""
    _stand_in_cli(started, f"""
        import json, os, signal, sys, time
        def bye(*_):
            os.write(1, b"second part\\n" + json.dumps({RESULT!r}).encode() + b"\\n")
            os._exit(0)
        signal.signal(signal.SIGTERM, bye)
        os.write(1, b"first part\\n")
        os.kill(os.getppid(), signal.SIGINT)
        time.sleep(30)
    """)
    assert launcher.launch(started, "engineer", TICKET, ["-p", "hi", "--output-format", "json"]) == \
        launcher.INTERRUPT_EXIT
    out = capfd.readouterr().out
    assert out == "first part\nsecond part\n" + json.dumps(RESULT) + "\n"
    record = base._record(started)
    assert record["exit_code"] == launcher.INTERRUPT_EXIT and record["cost_usd"]["value"] == 1.75


def test_an_interactive_launch_with_a_started_process_inherits_stdout(started, capfd):
    _stand_in_cli(started, """
        import os
        os.write(1, b"straight through\\n")
    """)
    assert launcher.launch(started, "engineer", TICKET, []) == 0
    assert capfd.readouterr().out == "straight through\n"
    assert base._record(started)["cost_usd"]["value"] is None


def test_a_lead_launch_is_never_relayed():
    """Only a worker session has a record to read a result line into; a lead's stdout stays inherited (S7)."""
    assert launcher._relays(None, ["--output-format", "json"]) is False
    assert launcher._relays({"any": "plan"}, ["--output-format", "json"]) is True
