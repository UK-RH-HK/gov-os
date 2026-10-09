"""KPI success 1 (DEC-392, amending DEC-386): the launcher's temp folder when a signal arrives or the removal fails.

"gov launch keeps the session's exit code and names the folder on stderr when
its temp folder cannot be removed; SIGTERM and SIGHUP end the session and
remove the folder as an interrupt does; the exit code after an interrupt is
130."

W1-28 left these three open (its README, residuals; ``bootstrap.md``, "W1-28
residuals"): a failed removal was a traceback and lost the session's exit
code; on SIGTERM and SIGHUP the session lived on and the folder stayed; the
exit code after an interrupt was not decided.

Each case starts its own stand-in session program in a temporary folder and
sends a signal to the launcher process it started, and to nothing else. Nothing
is timed: a case waits for the session's report, then for the launcher's end.
"""

from __future__ import annotations

import os
import signal

import pytest

import w1_32_launch_support as support

SIGNALS = (signal.SIGTERM, signal.SIGHUP)
EVERY_SIGNAL = (signal.SIGINT, *SIGNALS)


def _name(number):
    return signal.Signals(number).name


# --------------------------------------------------------------------------
# The removal fails
# --------------------------------------------------------------------------

@pytest.fixture()
def stuck(launch_project, sandbox, cli):
    """``stuck(code)``: a launch whose session ends with ``code`` and leaves a folder that cannot be removed."""
    if os.geteuid() == 0:
        pytest.skip("a read-only folder does not stop the removal for the superuser")

    def _stuck(code):
        support.plan(cli, files=support.LEFT, sealed=("sealed",), exit_code=code)
        return support.launch(launch_project, sandbox, cli)

    yield _stuck
    support.unseal(sandbox.tmpdir)


@pytest.mark.parametrize("code", (0, 7))
def test_a_failed_removal_keeps_the_sessions_exit_code(stuck, code):
    """DEC-332 holds when the folder stays: the launcher ends with the session's exit code, 0 included."""
    result = stuck(code)
    folder = support.w28.temp_folder(result)
    assert (folder / "sealed" / "kept.txt").is_file(), "the fixture's folder was removed: the removal did not fail"
    assert result.run.returncode == code, (
        f"the session ended with exit code {code}, its temp folder could not be removed, and gov launch ended with "
        f"{result.run.returncode}\n{result.describe()}"
    )


@pytest.mark.parametrize("code", (0, 7))
def test_a_failed_removal_writes_one_line_to_stderr_that_names_the_folder(stuck, code):
    result = stuck(code)
    folder = support.w28.temp_folder(result)
    assert os.path.lexists(folder), "the fixture's folder was removed: the removal did not fail"
    lines = [line for line in result.run.stderr.splitlines() if line.strip()]
    assert "Traceback" not in result.run.stderr, f"a failed removal ends as a traceback\n{result.describe()}"
    assert len(lines) == 1, f"stderr holds {len(lines)} lines after a failed removal, not one\n{result.describe()}"
    assert str(folder) in lines[0], f"the line on stderr does not name the folder that stayed, {folder}: {lines[0]!r}"


def test_a_failed_removal_prints_no_envelope(stuck, interface):
    """The launcher did not refuse: the session ran. DEC-332: a refusal prints the envelope, a session's end none."""
    result = stuck(7)
    assert "LAUNCH_REFUSED" not in result.run.stdout + result.run.stderr, result.describe()
    assert not result.run.stdout.strip(), f"gov launch printed to stdout after a failed removal\n{result.describe()}"
    assert len(result.sessions) == 1, f"not exactly one session was started\n{result.describe()}"


# --------------------------------------------------------------------------
# SIGTERM and SIGHUP are handled as an interrupt is
# --------------------------------------------------------------------------

@pytest.mark.parametrize("number", SIGNALS, ids=_name)
def test_the_signal_ends_the_session(launch_project, sandbox, cli, number):
    """The session does not live on once its launcher has ended."""
    result = support.signalled_launch(launch_project, sandbox, cli, number)
    assert result.session_ended, (
        f"{result.signal} ended gov launch and its session still ran {support.SESSION_END_S:.0f} s later\n"
        f"{result.describe()}"
    )


@pytest.mark.parametrize("number", SIGNALS, ids=_name)
def test_the_signal_removes_the_temp_folder(launch_project, sandbox, cli, number):
    result = support.signalled_launch(launch_project, sandbox, cli, number)
    support.w28.assert_removed(result.folder, f"after {result.signal} to the launcher")
    assert result.after == result.before, (
        f"after {result.signal} the temp directory holds {result.after}, not {result.before}"
    )


def test_an_interrupt_of_the_launcher_alone_ends_the_session(launch_project, sandbox, cli):
    """What the two signals are held to: ``kill -INT <launcher>`` ends the session and removes the folder."""
    result = support.signalled_launch(launch_project, sandbox, cli, signal.SIGINT)
    assert result.session_ended, f"SIGINT ended gov launch and its session still ran\n{result.describe()}"
    support.w28.assert_removed(result.folder, "after SIGINT to the launcher")


# --------------------------------------------------------------------------
# The exit code after an interrupt
# --------------------------------------------------------------------------

@pytest.mark.parametrize("number", EVERY_SIGNAL, ids=_name)
def test_the_exit_code_after_the_signal_is_130(launch_project, sandbox, cli, number):
    """130 as an exit code of the launcher's own: not the death by signal a shell would report as 128 + n."""
    result = support.signalled_launch(launch_project, sandbox, cli, number)
    assert result.returncode == support.INTERRUPT_EXIT, (
        f"gov launch ended with {result.returncode} after {result.signal}, not {support.INTERRUPT_EXIT}\n"
        f"{result.describe()}"
    )
