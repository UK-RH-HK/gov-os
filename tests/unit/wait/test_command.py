"""`gov wait` unit cases beyond the acceptance suite: usage errors, the exit-file forms, the tail."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from gov.cli.main import main


def wait(capsys, monkeypatch, *argv, every="0.05"):
    monkeypatch.setenv("GOV_WAIT_EVERY", every)
    code = main(["wait", *argv])
    out = capsys.readouterr()
    return code, out.out, out.err


def test_no_exit_file_is_usage_exit_2(capsys, monkeypatch):
    code, out, err = wait(capsys, monkeypatch)
    assert code == 2 and "invalid choice" not in err and "exit-file" in err


def test_max_s_not_a_number_is_exit_2(tmp_path, capsys, monkeypatch):
    code, out, err = wait(capsys, monkeypatch, str(tmp_path / "j.exit"), "soon")
    assert code == 2 and "not a number" in err and "invalid choice" not in err


def test_code_is_taken_modulo_256_and_the_first_line_only(tmp_path, capsys, monkeypatch):
    exit_file = tmp_path / "j.exit"
    exit_file.write_text(" 300 \r\nignored\n")
    code, out, err = wait(capsys, monkeypatch, str(exit_file), "1")
    assert code == 300 % 256 and f"wait: DONE exit 300 ({exit_file})" in out


def test_a_blank_exit_file_is_exit_2(tmp_path, capsys, monkeypatch):
    exit_file = tmp_path / "j.exit"
    exit_file.write_text("\n")
    code, out, err = wait(capsys, monkeypatch, str(exit_file), "1")
    assert code == 2 and "holds no exit code: ''" in out


def test_a_cap_above_570_is_said_on_stderr(tmp_path, capsys, monkeypatch):
    exit_file = tmp_path / "j.exit"
    exit_file.write_text("0\n")
    code, out, err = wait(capsys, monkeypatch, str(exit_file), "9999")
    assert code == 0 and "wait: <max-s> 9999 capped at 570" in err


def test_json_log_tail_and_summary(tmp_path, capsys, monkeypatch):
    exit_file = tmp_path / "j.exit"
    exit_file.write_text("0\n")
    (tmp_path / "j.json").write_text('launcher line\n{"result": "all done", "session_id": "s1", "is_error": false, '
                                     '"num_turns": 3}\n')
    (tmp_path / "j.summary").write_text("summary text\n")
    code, out, err = wait(capsys, monkeypatch, str(exit_file), "1")
    assert "session_id=s1 is_error=False turns=3" in out and "all done" in out and "summary text" in out


def test_gov_wait_log_overrides_and_lines_limit(tmp_path, capsys, monkeypatch):
    exit_file = tmp_path / "j.exit"
    exit_file.write_text("0\n")
    log = tmp_path / "other.txt"
    log.write_text("\n".join(f"line {n}" for n in range(10)) + "\n")
    monkeypatch.setenv("GOV_WAIT_LOG", str(log))
    monkeypatch.setenv("GOV_WAIT_LINES", "2")
    code, out, err = wait(capsys, monkeypatch, str(exit_file), "1")
    assert "line 9" in out and "line 8" in out and "line 7" not in out


def test_a_dead_pid_ends_the_wait_with_125_within_a_poll(tmp_path, capsys, monkeypatch):
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    (tmp_path / "j.pid").write_text(f"{child.pid}\n")
    code, out, err = wait(capsys, monkeypatch, str(tmp_path / "j.exit"), "30")
    assert code == 125 and "wait: GONE" in out and str(child.pid) in out


def test_the_exit_file_written_as_the_job_ends_wins_over_gone(tmp_path, capsys, monkeypatch):
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    (tmp_path / "j.pid").write_text(f"{child.pid}\n")
    (tmp_path / "j.exit").write_text("7\n")
    code, out, err = wait(capsys, monkeypatch, str(tmp_path / "j.exit"), "30")
    assert code == 7


def test_running_at_the_bound_is_124(tmp_path, capsys, monkeypatch):
    (tmp_path / "j.pid").write_text(f"{os.getpid()}\n")
    code, out, err = wait(capsys, monkeypatch, str(tmp_path / "j.exit"), "0")
    assert code == 124 and "wait: RUNNING after 0s" in out
