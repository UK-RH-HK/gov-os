"""S2 (and F1's 125): a job gone without its exit file ends the wait at once, by its pid alone; usage errors are exit 2."""

from __future__ import annotations

import pytest

import w2_160_support as support

BOUND = 20  # the <max-s> given: a wait that waits for it is far outside the assertions below
QUICK = 6.0  # one poll period (0.2 s) plus the command's start-up and a generous slack


def test_s2_a_job_killed_before_writing_its_exit_file_is_gone_exit_125_within_a_poll_period(wait, procs):
    base = wait.base()
    pid = procs.dead()
    wait.write(base, ".pid", f"{pid}\n")
    result = wait.run(base + ".exit", BOUND)
    assert result.code == 125, result
    assert "GONE" in result.out, result
    assert str(pid) in result.out, f"the line names the pid:\n{result}"
    assert result.elapsed < QUICK, f"ends at once, not at the bound ({BOUND} s):\n{result}"


def test_s2_a_second_process_of_the_same_command_line_does_not_keep_the_wait_alive(wait, procs):
    base = wait.base()
    first, second = procs.sleeper(), procs.sleeper()  # the same command line, the same name
    wait.write(base, ".pid", f"{first.pid}\n")
    first.kill()
    first.wait(timeout=10)
    assert second.poll() is None, "the second stand-in is left running"
    result = wait.run(base + ".exit", BOUND)
    assert result.code == 125 and "GONE" in result.out, result
    assert result.elapsed < QUICK, result


def test_s2_a_zombie_job_counts_as_gone(wait, procs):
    pid = procs.zombie()
    if pid is None:
        pytest.skip("a zombie cannot be arranged here")
    base = wait.base()
    wait.write(base, ".pid", f"{pid}\n")
    result = wait.run(base + ".exit", BOUND)
    assert result.code == 125 and "GONE" in result.out, result
    assert result.elapsed < QUICK, result


def test_s2_a_live_job_without_its_exit_file_is_running_not_gone(wait, procs):
    base = wait.base()
    wait.write(base, ".pid", f"{procs.sleeper().pid}\n")
    result = wait.run(base + ".exit", 1)
    assert result.code == 124 and "RUNNING" in result.out, result
    assert "GONE" not in result.out, result


def test_s2_a_job_that_wrote_its_exit_file_and_then_exited_is_done_not_gone(wait, procs):
    base = wait.base()
    wait.write(base, ".pid", f"{procs.dead()}\n")
    wait.write(base, ".exit", "5\n")
    result = wait.run(base + ".exit", BOUND)
    assert result.code == 5, result
    assert "DONE exit 5" in result.out and "GONE" not in result.out, result


def test_s2_a_live_pid_does_not_hold_back_a_written_exit_file(wait, procs):
    base = wait.base()
    wait.write(base, ".pid", f"{procs.sleeper().pid}\n")
    wait.write(base, ".exit", "0\n")
    result = wait.run(base + ".exit", BOUND)
    assert result.code == 0 and "DONE exit 0" in result.out, result
    assert result.elapsed < QUICK, result


def test_s2_an_exit_file_holding_no_number_is_exit_2(wait):
    base = wait.base()
    wait.write(base, ".exit", "abc\n")
    result = wait.run(base + ".exit", 5)
    assert result.code == 2, result
    assert "abc" in result.out + result.err, f"the text found is named:\n{result}"


def test_s2_a_max_s_that_is_not_a_number_is_exit_2(wait):
    result = wait.run(wait.base() + ".exit", "x")
    assert result.code == 2, result
    assert "invalid choice" not in result.err, f"exit 2 from a command that exists (not from an unknown command):\n{result}"
    assert result.elapsed < QUICK, f"a usage error does not wait:\n{result}"


def test_s2_no_arguments_is_exit_2(wait):
    result = wait.run()
    assert result.code == 2, result
    assert "invalid choice" not in result.err, f"exit 2 from a command that exists (not from an unknown command):\n{result}"
    assert result.elapsed < QUICK, result
