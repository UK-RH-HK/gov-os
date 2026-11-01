"""Review 3's cases for ``gov accept``: the reviewer's findings V1 and V2, given to this suite as described
behaviours (DEC-136) in an addendum (R14, R15) that overrides the design note, review 1's and run 2's addenda where
they differ.

- **R14** The private folder is removed in every path even when a process the run cannot stop (one a test started
  in a session of its own, such as a nested ``gov accept``) changes it meanwhile, or removes it first: an entry
  already gone is passed over, a folder found not empty is emptied again, and no single entry stops the removal of
  the rest. A run stopped by SIGINT, SIGTERM or SIGHUP still ends with 128 plus the signal (R12) whatever the
  clean-up met; a run that was not stopped is reported as its results say, never turned into ``crash`` by an entry
  another process removed. Nothing of the run stays in the caller's ``TMPDIR``.
- **R15** Removing a folder whose thousands of sibling folders sit side by side takes time in proportion to the
  number of entries, not its square: 8,000 empty sibling folders are removed in a few seconds at most.

Every case runs the suite's leak probe (the marker in stdout, stderr, the project, the given ``TMPDIR`` and
``HOME``; the given ``TMPDIR`` empty; the project unchanged); the signal cases search for the marker only, as
review 1's R2 and run 2's R12 do. R14's nested cases are races: each runs several races and fails at the first
that breaks R14. The ``test_premise_*`` cases test the planted pieces themselves, and are green before the
implementation by design.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402

TERM = signal.SIGTERM

# R14: how many races the second form runs in one case (the first runs one per moment of WIND_DOWN_DELAYS_S).
# Review 3 saw run 2's code fail about one race in three with 3,000 files. With MANY_FILES files, run 2's code
# failed 17 races of 40 of the first form and 8 of 8 of the second here, so a red case is nearly certain (see the
# README); a green race costs about 5 s.
BOTH_AT_ONCE_RACES = 3
POLL_S = 0.002           # how often the first form looks for its moment
REMOVAL_WAIT_S = 60.0    # how long the first form waits for the nested pytest to end
# R14, no signal: how many runs the churn case makes (run 2's code failed 11 runs of 12 here; a green run costs
# about 1.5 s).
CHURN_RUNS = 3

# R15: the bounds on the whole run of gov accept (its start, the planted tests, the clean-up and the exit), and on
# its clean-up: from the moment the planted test had made the folders to gov's end. Here a run of this planted
# project without the folders takes about 0.5 s, making the folders about 0.4 s, and a plain recursive removal of
# them 0.14 s, so with a removal that grows with the entries the whole run takes about 1.2 s and the clean-up
# about 0.5 s; run 2's code took 7.1 s to 13.3 s for the whole run and 9.7 s to 12.4 s for the clean-up here, and
# review 3 measured its removal alone at 22.7 s (see the README).
SIBLINGS_RUN_BOUND_S = 10.0
SIBLINGS_CLEAN_UP_BOUND_S = 3.0
PLAIN_REMOVAL_BOUND_S = 2.0   # the premise: a plain recursive removal of the same folders, on this machine


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


def _remove_left(project):
    """What the runs may have left in the given TMPDIRs, removed without recursion."""
    for folder in project.base.glob("given-tmp-*"):
        support.remove_tree(folder)


def _record(started, project, kind, wait_s=support.START_WAIT_S, poll_s=0.05):
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


def _until(delay_s, pid):
    """Back after ``delay_s``, or as soon as ``pid`` no longer runs, whichever comes first."""
    deadline = time.monotonic() + delay_s
    while time.monotonic() < deadline and support.pid_running(pid):
        time.sleep(POLL_S)


def _ended_child(started, pid, wait_s=REMOVAL_WAIT_S):
    """Back once ``pid`` (the nested pytest) no longer runs; an AssertionError if the outer gov ends first or
    ``wait_s`` passes."""
    deadline = time.monotonic() + wait_s
    while support.pid_running(pid):
        assert started.process.poll() is None, "the outer gov ended before the nested pytest did"
        assert time.monotonic() < deadline, f"the nested pytest still ran {wait_s:.0f} s after its test began"
        time.sleep(POLL_S)


# R14, a nested gov accept -----------------------------------------------------------------------------------------

# Each form: the nested planted test's kind, and whether the SIGTERM goes to the outer gov alone while the nested
# gov removes its private folder (its test filled its folder, slept about 1 s and passed, and the nested pytest
# has ended), or to the outer gov and the nested gov at the same moment while the nested test sleeps (as a stop of
# a whole process tree does).
NESTED_FORMS = {
    "SIGTERM-to-gov-while-the-nested-gov-removes": ("fill_then_pass", False),
    "SIGTERM-to-gov-and-the-nested-gov-at-once": ("fill_then_sleep", True),
}

# The first form's moments: seconds after the nested pytest ended, one race per moment. Here the nested gov's
# removal of MANY_FILES files then lasts 0.2 s to 0.4 s, and the outer gov takes about 0.1 s to stop its own child
# and reach its clean-up. The signal goes earlier if the nested gov has ended, so the outer run is always still
# going when it comes; and no pytest of the nested run is left to write in the folders meanwhile.
WIND_DOWN_DELAYS_S = (0.0, 0.03, 0.06, 0.09, 0.12, 0.15, 0.18, 0.21, 0.24, 0.27)


def _nested_race(outer, nested, both, delay_s=0.0):
    """One race of R14's nested form: the problems found, and the run."""
    nested._clear_probe()
    started = outer.start(support.TICKET_ID)
    runner = None
    try:
        runner = _record(started, outer, "nested")
        filled = _record(started, nested, "filled")
        if both:
            os.kill(started.process.pid, TERM)
            os.kill(runner["nested"], TERM)
        else:
            _ended_child(started, filled["pid"])
            _until(delay_s, runner["nested"])
            os.kill(started.process.pid, TERM)
        run = started.finish(support.RUN_TIMEOUT_S, "SIGTERM")
        problems = run.problems(generic=False)   # first, so it is what gov left when it ended
        problems += _ended(run, 128 + int(TERM))
        if not support.pid_gone(runner["pid"]):
            problems.append("the child pytest still runs after gov accept ended")
        if filled.get("made") != support.MANY_FILES or not _under(run, filled["top"]):
            problems.append(f"the nested test did not make its {support.MANY_FILES} files under the given TMPDIR")
        return problems, run
    finally:
        if runner:
            support.kill_quietly(runner["nested"], group=True)
            support.pid_gone(runner["nested"])
        nested.kill_recorded()
        started.stop()
        _remove_left(outer)


@pytest.mark.parametrize("form", list(NESTED_FORMS))
def test_r14_a_sigterm_while_a_nested_gov_accept_removes_its_folder_ends_with_143_and_leaves_nothing(tmp_path, form):
    """A planted test runs gov accept on a nested planted project, in a session of its own, with its own temporary
    folder (inside the outer run's private folder) as TMPDIR; the nested test leaves MANY_FILES small files in a
    folder of its temporary folder. SIGTERM goes to the outer gov alone while the nested gov removes its folder,
    its pytest ended (once per moment of WIND_DOWN_DELAYS_S), or to both gov processes at once while the nested
    test sleeps (BOTH_AT_ONCE_RACES times). Each race: exit code 143, the given TMPDIR empty, no marker anywhere,
    the child gone. The case fails at the first race that breaks R14."""
    kind, both = NESTED_FORMS[form]
    nested = support.Project(tmp_path / "nested", support.nested_files(kind), support.NESTED_README)
    outer = support.Project(tmp_path / "outer",
                            support.second_file("run_nested", "test_qzv96leak_nested_runner",
                                                extra=support.run_nested_extra(nested)),
                            support.SECOND_README)
    delays = (0.0,) * BOTH_AT_ONCE_RACES if both else WIND_DOWN_DELAYS_S
    for race, delay_s in enumerate(delays, 1):
        problems, run = _nested_race(outer, nested, both, delay_s)
        when = "to both at once" if both else f"{delay_s:.2f} s after the nested pytest ended"
        assert not problems, (f"race {race} of {len(delays)} (SIGTERM {when}):\n" + "\n".join(problems) + "\n"
                              + run.describe())


# R14, a churning process, no signal ------------------------------------------------------------------------------

def test_r14_processes_of_their_own_session_churning_in_the_temporary_folder_leave_the_result_as_the_tests_gave_it(
        tmp_path):
    """A passing planted test starts CHURNERS processes in sessions of their own, each making and removing files in
    a new folder of its temporary folder until the clean-up removes its canary file; the run ends with no signal.
    The result is the tests' (both lines pass, exit code 0), never a crash; the given TMPDIR is empty when gov
    ends, and every churner has stopped. The run is made CHURN_RUNS times; the case fails at the first bad one."""
    project = support.Project(tmp_path, support.second_file("churn_pass", "test_qzv96leak_churner",
                                                            extra=support.CHURN), support.SECOND_README)
    for number in range(1, CHURN_RUNS + 1):
        try:
            run = project.run(support.TICKET_ID)
            problems = run.problems()   # first, so it is what gov left when it ended
            problems += _outcome_problems(run, support.SECOND_PASSES_EXPECTED, support.EXIT_PASS)
            churning = project.records("churning")
            if len(churning) != support.CHURNERS or not all(_under(run, record["folder"]) for record in churning):
                problems.append(f"the planted test did not start its {support.CHURNERS} churners under the given "
                                f"TMPDIR: {churning}")
            deadline = time.monotonic() + support.GONE_WAIT_S
            still = [record["folder"] for record in churning
                     if not support.pid_gone(record["pid"], max(0.0, deadline - time.monotonic()))]
            if still:
                problems.append(f"churners still run after gov accept ended, their folders left: {still}")
            assert not problems, (f"run {number} of {CHURN_RUNS}:\n" + "\n".join(problems) + "\n"
                                  + run.describe())
        finally:
            project.kill_recorded()
            _remove_left(project)


# R15 ----------------------------------------------------------------------------------------------------------

def test_r15_eight_thousand_empty_sibling_folders_are_removed_within_the_bound(tmp_path):
    """A passing planted test leaves SIBLINGS empty folders side by side in a new folder of its temporary folder:
    both lines pass, exit code 0, the given TMPDIR empty; the whole run of gov accept ends within
    SIBLINGS_RUN_BOUND_S, and its clean-up (from the moment the folders were made to gov's end) within
    SIBLINGS_CLEAN_UP_BOUND_S."""
    project = support.Project(tmp_path, support.second_file("siblings_pass", "test_qzv96leak_siblings",
                                                            extra=support.SIBLING_FOLDERS), support.SECOND_README)
    try:
        run = project.run(support.TICKET_ID)
        ended = time.monotonic()
        problems = run.problems()   # first, so it is what gov left when it ended
        problems += _outcome_problems(run, support.SECOND_PASSES_EXPECTED, support.EXIT_PASS)
        siblings = project.records("siblings")
        if not siblings or siblings[0].get("made") != support.SIBLINGS or not _under(run, siblings[0]["top"]):
            problems.append(f"the planted test did not make its {support.SIBLINGS} folders under the given TMPDIR")
            clean_up = None
        else:
            clean_up = ended - siblings[0]["at"]
        if run.elapsed > SIBLINGS_RUN_BOUND_S:
            problems.append(f"the run took {run.elapsed:.1f} s, more than {SIBLINGS_RUN_BOUND_S:.0f} s for "
                            f"{support.SIBLINGS} empty sibling folders")
        if clean_up is not None and clean_up > SIBLINGS_CLEAN_UP_BOUND_S:
            problems.append(f"the clean-up took {clean_up:.1f} s from the folders' making to gov's end, more than "
                            f"{SIBLINGS_CLEAN_UP_BOUND_S:.0f} s for {support.SIBLINGS} empty sibling folders")
        assert not problems, "\n".join(problems) + f"\nelapsed: {run.elapsed:.1f} s\n" + run.describe()
    finally:
        _remove_left(project)


# Premises: the planted pieces do what the cases above rely on (green before the implementation, by design) -----

def test_premise_r14_a_churner_stops_once_its_canary_is_gone_and_its_folder_then_stays_still(tmp_path):
    folder, probe = tmp_path / "churn", tmp_path / "probe"
    folder.mkdir()
    probe.mkdir()
    churner = subprocess.Popen([sys.executable, "-c", support.CHURNER, str(folder), str(probe),
                                str(support.CHURN_BATCH)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        deadline = time.monotonic() + 60
        while len(os.listdir(folder)) < 2:
            assert time.monotonic() < deadline and churner.poll() is None, "the churner never began"
            time.sleep(0.01)
        time.sleep(0.2)
        assert churner.poll() is None, "the churner stopped on its own before its canary went"
        os.unlink(folder / support.CANARY)
        assert churner.wait(timeout=support.GONE_WAIT_S) == 0, "the churner did not end once its canary went"
        left = sorted(os.listdir(folder))
        time.sleep(0.3)
        assert sorted(os.listdir(folder)) == left, "the churner's folder still changed after it stopped"
        shutil.rmtree(folder)
        assert not folder.exists()
    finally:
        support.kill_quietly(churner.pid, group=True)
        churner.wait(timeout=30)


def test_premise_r15_a_plain_recursive_removal_takes_the_sibling_folders_away_in_a_few_seconds(tmp_path):
    top = tmp_path / "siblings"
    top.mkdir()
    for index in range(support.SIBLINGS):
        (top / f"qzv96leak-{index}").mkdir()
    assert len(os.listdir(top)) == support.SIBLINGS
    started = time.monotonic()
    shutil.rmtree(top)
    took = time.monotonic() - started
    assert not top.exists()
    assert took < PLAIN_REMOVAL_BOUND_S, f"a plain recursive removal took {took:.1f} s here"
