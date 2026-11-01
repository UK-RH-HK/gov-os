"""Review 4's cases for ``gov accept``: the reviewer's finding W1, given to this suite as a described behaviour
(DEC-136) in an addendum (R16, DEC-987) that overrides the design note and the addenda R1 to R15 where they differ.

- **R16** No process of the run outlives ``gov``, and nothing of the run appears in the caller's ``TMPDIR``
  afterwards. Before its clean-up, in every path (a pass, a failure, a stop by SIGINT, SIGTERM or SIGHUP), ``gov
  accept`` stops every process the run started, whatever its session or process group (processes a test started
  in a session of its own, and their own children, included), and waits until none is left; only then does it
  remove its private folder. Once ``gov`` has ended, no process of the run is alive, and nothing of the run (no
  folder, no file, no name) appears in the caller's ``TMPDIR`` later. The exit codes, the envelope, the signals
  held during the clean-up and the marker rules stay as before.

Both cases take review 4's form: the outer planted test runs ``gov accept`` on a nested planted project, in a
session of its own, with as ``TMPDIR`` a new folder of its own ``tmp_path`` (the form in which this suite's harness
runs every planted run), and an environment carrying a token of the case's own; the nested test records that it
sleeps, sleeps ``R16_SLEEP_S`` and passes, and its pytest then writes its report. The case finds the processes of
the run by that token (in their environment or command line) and by the process ids the planted tests recorded,
never by a name. Each case is a race: it runs ``RACES`` races and fails at the first that breaks R16. The
``test_premise_*`` case tests the token search itself, and is green before the implementation by design.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402

TERM = signal.SIGTERM

# R16: how many races each case runs. On the head each race is red at its first check of the processes (the nested
# gov and its pytest still run when gov ends) and again at the later look at the given TMPDIR; a green race costs
# about R16_SLEEP_S + SETTLE_S plus two starts of gov (10 s to 15 s here).
RACES = 2
# How long after the nested test's sleep would have ended the case looks at the given TMPDIR again: the nested
# pytest then tears down, writes its report (that write makes the missing folders anew) and ends, and the nested
# gov parses it and removes its own folder. Review 4 saw the head's leftovers appear 2.4 s to 3.4 s after gov
# ended, its nested test sleeping 1 s to 3 s. The case also waits until no process of the run is left (up to
# GONE_LATER_S), since once none is left nothing more can appear.
SETTLE_S = 4.0
GONE_LATER_S = 60.0


def _outcome_problems(run, expected, code):
    """``assert_outcome``'s finding as a list (empty when the result and the exit code are the expected ones)."""
    try:
        support.assert_outcome(run, expected, code)
    except AssertionError as error:
        return [str(error).split("\ncommand: ", 1)[0]]
    return []


def _ended(run, expected):
    """How gov ended, against the ordinary exit with code ``expected`` (R12)."""
    if run.returncode == expected:
        return []
    how = f"was killed by signal {-run.returncode}" if run.returncode < 0 else f"exited with code {run.returncode}"
    return [f"gov {how}, expected an ordinary exit with code {expected} (128 plus the signal)"]


def _under(run, path):
    """Whether ``path`` is below the TMPDIR the run was given."""
    return run.tmpdir.resolve() in Path(path).resolve().parents


def _record(started, project, kind, wait_s=support.START_WAIT_S, poll_s=0.01):
    """The first probe record of ``kind`` in ``project``'s probe folder, while the started run of gov accept goes
    on; an AssertionError if gov ends first or ``wait_s`` passes."""
    deadline = time.monotonic() + wait_s
    while time.monotonic() < deadline:
        records = project.records(kind)
        if records:
            return records[0]
        if started.process.poll() is not None:
            stdout, stderr = started.process.communicate()
            raise AssertionError(f"gov accept ended (exit code {started.process.returncode}) before a planted test "
                                 f"recorded {kind!r}\nstdout: {stdout[-2000:]}\nstderr: {stderr[-2000:]}")
        time.sleep(poll_s)
    raise AssertionError(f"no planted test recorded {kind!r} within {wait_s:.0f} s")


def _pids(*records):
    """The process ids the planted tests recorded: each test's own, and the nested gov's."""
    return {int(record[key]) for record in records if record for key in ("pid", "nested") if record.get(key)}


def _alive(token, recorded):
    """The processes of the run still running: those carrying the token, and those the planted tests recorded."""
    return sorted(set(support.processes_carrying(token)) | {pid for pid in recorded if support.pid_running(pid)})


def _alive_problems(token, recorded):
    alive = _alive(token, recorded)
    if not alive:
        return []
    return [f"{len(alive)} processes of the run still run once gov accept ended: "
            + "; ".join(f"{pid} {support.command_line(pid)}" for pid in alive)]


def _later_problems(run, token, recorded, sleeping, ended):
    """What appeared in the given TMPDIR after gov ended: looked at once the nested test's sleep would have ended
    and SETTLE_S more have passed, and no process of the run is left (up to GONE_LATER_S)."""
    if sleeping:
        time.sleep(max(0.0, sleeping["at"] + support.R16_SLEEP_S + SETTLE_S - time.monotonic()))
    deadline = time.monotonic() + GONE_LATER_S
    while _alive(token, recorded) and time.monotonic() < deadline:
        time.sleep(0.1)
    left = support.everything_under(run.tmpdir)
    found = []
    if left:
        found.append(f"the given TMPDIR holds {len(left)} entries {time.monotonic() - ended:.1f} s after gov "
                     f"accept ended (it held none when gov ended): {left[:8]}")
    if any(support.MARKER in rel.lower() for rel in left):
        found.append("a name left in the given TMPDIR after gov ended holds the marker")
    for path in support.files_holding_marker(run.tmpdir / rel for rel in left):
        found.append(f"a file left in the given TMPDIR after gov ended holds the marker: {path}")
    return found


def _premise_problems(run, sleeping):
    if not sleeping or not _under(run, sleeping.get("tempdir", "/")):
        return [f"the nested test did not run with its temporary folder under the given TMPDIR: {sleeping}"]
    return []


def _kill_run(token, recorded, started=None):
    """Whatever is left of the run killed, so a red race leaves no orphan: every process carrying the token, every
    recorded one (and the nested gov's session), and the outer gov's group."""
    if started is not None:
        started.stop()
    for _ in range(3):
        for pid in set(support.processes_carrying(token)) | set(recorded):
            support.kill_quietly(pid, group=True)
            support.kill_quietly(pid)
        for pid in set(support.processes_carrying(token)) | set(recorded):
            support.pid_gone(pid)


def _remove_left(project):
    """What the runs may have left in the given TMPDIRs, removed without recursion."""
    for folder in project.base.glob("given-tmp-*"):
        support.remove_tree(folder)


def _projects(tmp_path, kind, name, token):
    nested = support.Project(tmp_path / "nested", support.R16_NESTED_FILES, support.R16_NESTED_README)
    outer = support.Project(tmp_path / "outer",
                            support.second_file(kind, name, extra=support.run_nested_r16_extra(nested, token)),
                            support.SECOND_README)
    return outer, nested


# R16, the stopped run --------------------------------------------------------------------------------------------

def _stopped_race(outer, nested, token):
    """One race of the stopped run: the problems found, and the run."""
    nested._clear_probe()
    started = outer.start(support.TICKET_ID)
    recorded = set()
    try:
        runner = _record(started, outer, "nested")
        recorded |= _pids(runner)
        sleeping = _record(started, nested, "nested_sleeping")
        recorded |= _pids(sleeping)
        problems = []
        if not support.pid_running(sleeping["pid"]):
            problems.append("premise: the nested pytest had ended before the stop came")
        os.kill(started.process.pid, TERM)
        run = started.finish(support.RUN_TIMEOUT_S, "SIGTERM")
        ended = time.monotonic()
        problems += run.problems(generic=False)   # first, so it is what gov left when it ended
        problems += _alive_problems(token, recorded)
        problems += _ended(run, 128 + int(TERM))
        problems += _premise_problems(run, sleeping)
        problems += _later_problems(run, token, recorded, sleeping, ended)
        return problems, run
    finally:
        _kill_run(token, recorded | _pids(*outer.records(), *nested.records()), started)
        _remove_left(outer)


def test_r16_a_sigterm_to_gov_alone_while_a_nested_run_sleeps_leaves_no_process_and_nothing_later(tmp_path):
    """A planted test runs gov accept on a nested planted project, in a session of its own, with its TMPDIR inside
    the test's own tmp_path; SIGTERM goes to the outer gov alone while the nested test sleeps. Each race: exit code
    143, the given TMPDIR empty and no marker when gov ends, no process of the run still running, and the given
    TMPDIR still empty once the nested test's sleep would have ended. The case fails at the first race that breaks
    R16."""
    token = f"qzv96leak-r16-{uuid.uuid4().hex}"
    outer, nested = _projects(tmp_path, "r16_nested_waits", "test_qzv96leak_r16_waits", token)
    for race in range(1, RACES + 1):
        problems, run = _stopped_race(outer, nested, token)
        assert not problems, (f"race {race} of {RACES} (SIGTERM to gov alone while the nested test sleeps):\n"
                              + "\n".join(problems) + "\n" + run.describe())


# R16, the run that does not wait ---------------------------------------------------------------------------------

def test_r16_a_test_that_leaves_a_nested_run_going_passes_and_leaves_no_process_and_nothing_later(tmp_path):
    """A passing planted test starts gov accept on a nested planted project, in a session of its own, with its
    TMPDIR inside the test's own tmp_path, and returns once the nested test sleeps, without waiting for it; no
    signal. Each race: both lines pass, exit code 0, the given TMPDIR empty and no marker when gov ends, no process
    of the run still running, and the given TMPDIR still empty once the nested test's sleep would have ended. The
    case fails at the first race that breaks R16."""
    token = f"qzv96leak-r16-{uuid.uuid4().hex}"
    outer, nested = _projects(tmp_path, "r16_nested_returns", "test_qzv96leak_r16_returns", token)
    for race in range(1, RACES + 1):
        nested._clear_probe()
        recorded = set()
        try:
            run = outer.run(support.TICKET_ID)
            ended = time.monotonic()
            runner = (outer.records("nested") or [None])[0]
            sleeping = (nested.records("nested_sleeping") or [None])[0]
            recorded |= _pids(runner, sleeping)
            problems = run.problems()   # first, so it is what gov left when it ended
            problems += _alive_problems(token, recorded)
            problems += _outcome_problems(run, support.SECOND_PASSES_EXPECTED, support.EXIT_PASS)
            problems += _premise_problems(run, sleeping)
            problems += _later_problems(run, token, recorded, sleeping, ended)
            assert not problems, (f"race {race} of {RACES} (the planted test did not wait for its nested run):\n"
                                  + "\n".join(problems) + "\n" + run.describe())
        finally:
            _kill_run(token, recorded | _pids(*outer.records(), *nested.records()))
            _remove_left(outer)


# Premise: the token search finds what the cases rely on (green before the implementation, by design) ------------

def test_premise_r16_the_token_search_finds_a_process_of_its_own_session_and_its_child_and_not_once_gone(tmp_path):
    token = f"qzv96leak-r16-{uuid.uuid4().hex}"
    child = "import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); " \
            "time.sleep(60)"
    parent = subprocess.Popen([sys.executable, "-c", child], env={**os.environ, support.R16_TOKEN_KEY: token},
                              stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              start_new_session=True)
    try:
        deadline = time.monotonic() + 60
        while len(support.processes_carrying(token)) < 2:
            assert time.monotonic() < deadline and parent.poll() is None, \
                f"the search did not find the process and its child: {support.processes_carrying(token)}"
            time.sleep(0.05)
        assert parent.pid in support.processes_carrying(token)
        assert not support.processes_carrying(f"qzv96leak-r16-{uuid.uuid4().hex}"), "another token finds nothing"
        found = support.processes_carrying(token)
        support.kill_quietly(parent.pid, group=True)
        parent.wait(timeout=30)
        assert all(support.pid_gone(pid) for pid in found)
        assert not support.processes_carrying(token), "the search still finds processes once they are gone"
    finally:
        support.kill_quietly(parent.pid, group=True)
        parent.wait(timeout=30)
