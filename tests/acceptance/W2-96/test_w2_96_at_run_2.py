"""Run 2's cases for ``gov accept`` (DEC-970): PKG-1 (a) and review 2's N2, N5, N7 and N8, given to this suite as
described behaviours (DEC-136) in an addendum that overrides the design note and review 1's addendum where they
differ.

- **R8** Any collected case that failed or errored, mapped or not, fails the run: ``outcome: fail``, exit code 3.
  A case the README never names is still only counted under ``unmapped``, never named; skipped cases never fail
  the run. This replaces "unmapped cases never change the exit code".
- **R9** A SIGINT that arrives while the clean-up runs (stopping the child, restoring permissions, removing the
  private folder) is held back as SIGTERM and SIGHUP are: the clean-up finishes, nothing stays in the given
  ``TMPDIR``, and only then does ``gov`` end. More signals of the three kinds during the clean-up change nothing.
- **R10** The private folder is removed whatever its depth: a chain of more than 1,100 nested folders (the deepest
  without permissions) does not turn a finished run into a ``crash``.
- **R11** A signal among SIGHUP, SIGTERM and SIGINT that ``gov accept`` was started with set to "ignore" (as
  ``nohup`` does for SIGHUP) stays ignored for the whole run: it stops neither the run nor its child.
- **R12** Whenever a SIGINT, SIGTERM or SIGHUP ends the run, ``gov`` ends by an ordinary exit with code 128 plus
  the signal's number (130, 143, 129), never by death by the signal (-2, -15, -1 to ``subprocess``).

Every case runs the suite's leak probe (the marker in stdout, stderr, the project, the given ``TMPDIR`` and
``HOME``; the given ``TMPDIR`` empty; the project unchanged); the signal cases search for the marker only, as the
interrupt case and review 1's R2 do. The ``test_premise_*`` cases test the planted projects themselves, and are
green before the implementation by design.
"""

from __future__ import annotations

import os
import re
import signal
import stat
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402

line, counts = support.line, support.counts
INT, TERM, HUP = signal.SIGINT, signal.SIGTERM, signal.SIGHUP

ALPHA_RAW = {key: value for key, value in support.COMMON_RAW.items() if "alpha" in key}

# R11: how long after the ignored signal the case looks whether gov and its child still run.
IGNORED_WAIT_S = 1.5


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


def _remove_left(project):
    """What the run may have left in the given TMPDIRs and the planted chains, removed without recursion."""
    for record in project.records("deep"):
        support.remove_tree(record["top"])
    for folder in project.base.glob("given-tmp-*"):
        support.remove_tree(folder)


# R8 -----------------------------------------------------------------------------------------------------------

UNMAPPED_FAILURES = {"assertion": "fail", "setup-error": "setup_error", "teardown-error": "teardown_error"}


@pytest.mark.parametrize("kind", list(UNMAPPED_FAILURES))
def test_r8_a_failed_case_the_readme_never_names_fails_the_run_while_every_mapped_line_passes(tmp_path, kind):
    """The README maps ALPHA's three passing cases; the second file's one case, which no item names, fails its
    assertion, errors in setup or errors in teardown: the line still passes, the run fails, the case is counted
    under unmapped and never named."""
    files = support.second_file(UNMAPPED_FAILURES[kind], "test_qzv96leak_second_unnamed")
    project = support.Project(tmp_path, files, support.SIMPLE_README)
    run = project.run(support.TICKET_ID)
    expected = support.result("fail", [line("success-1", "pass", 3)], unmapped=counts(0, 1), totals=counts(3, 1))
    support.assert_outcome(run, expected, support.EXIT_FAIL)
    support.assert_clean(run)


def test_r8_a_skipped_case_the_readme_never_names_leaves_a_passing_run_passing(tmp_path):
    """The README maps ALPHA's three passing cases; the second file's one case, which no item names, is skipped."""
    project = support.Project(tmp_path, support.second_file("skip", "test_qzv96leak_second_skipped"),
                              support.SIMPLE_README)
    run = project.run(support.TICKET_ID)
    expected = support.result("pass", [line("success-1", "pass", 3)], unmapped=counts(0, 0, 1),
                              totals=counts(3, 0, 1))
    support.assert_outcome(run, expected, support.EXIT_PASS)
    support.assert_clean(run)


def _w1_30_problems(run):
    """W1-30's form: whether the row with no header row or the Case table maps its item is not judged; the run
    must fail (ok true, exit code 3) with success 1 passing and the failing case counted as failed once."""
    envelope = run.envelope()
    problems = []
    if run.returncode != support.EXIT_FAIL:
        problems.append(f"exit code {run.returncode}, expected 3: a failing case outside the readable map")
    if envelope["ok"] is not True:
        problems.append("ok is not true for a run that ended in a result")
    got = support.projection(envelope.get("result"))
    if not isinstance(got, dict):
        return problems + [f"the result is no object: {got!r}"]
    if got["outcome"] != "fail" or got["error_kind"] is not None:
        problems.append(f"outcome {got['outcome']!r} with error kind {got['error_kind']!r}, expected fail")
    lines = got["lines"] if isinstance(got["lines"], list) else []
    if not lines or lines[0] != line("success-1", "pass", 3):
        problems.append(f"success 1 is not reported first, passing with its 3 cases: {lines}")
    extra = lines[1:]
    if len(extra) > 1 or any(item.get("kpi") != "failure-1" or item.get("outcome") != "fail" for item in extra):
        problems.append(f"a line beyond success 1 other than a failing failure 1: {extra}")
    if got["totals"] != counts(3, 1):
        problems.append(f"totals {got['totals']}, expected {counts(3, 1)}")
    unmapped = got["unmapped"] if isinstance(got["unmapped"], dict) else {}
    failed = (unmapped.get("failed") or 0) + sum(item.get("failed") or 0 for item in extra)
    if failed != 1:
        problems.append(f"the failing case is counted as failed {failed} times, under unmapped or failure 1")
    return problems


@pytest.mark.parametrize("form", list(support.W1_30_FORMS))
def test_r8_a_failing_case_outside_the_readable_map_in_w1_30s_form_fails_the_run(tmp_path, form):
    """A readable heading-form table maps the passing cases under ``### S1``; the failing case sits in a one-row
    table with no header row under ``### F1: …``, or in a ``Case | Clause`` table under ``### Failure 1: …``,
    as review 2 planted W1-30's README: exit code 3, never 0."""
    project = support.Project(tmp_path, support.SECOND_FAILS, support.W1_30_FORMS[form])
    run = project.run(support.TICKET_ID)
    problems = _w1_30_problems(run)
    assert not problems, "\n".join(problems) + "\n" + run.describe()
    support.assert_clean(run)


# R9 -----------------------------------------------------------------------------------------------------------

# The presses to gov alone, each ``(seconds after the one before, signal)``; the first ends the run while the
# planted test sleeps, the others arrive while gov cleans up its 20,000 files (removing them alone takes about
# 0.4 s on this machine). The run ends as the first press's interrupt: exit code 130 (R12).
# P-W2-96-R9-PREMISE (a) revised review 2's form, a second press 0.2 s after the first: a clean-up that ended within
# 0.2 s left the case's premise (a second press) unmet. Its second press now goes once the planted files begin to
# disappear (``ON_REMOVAL``), so it comes while gov removes them, however fast the removal is.
ON_REMOVAL = "once the planted files begin to disappear"
CLEAN_UP_PRESSES = {
    "a-second-press-once-the-removal-began": [(0, INT), (ON_REMOVAL, INT)],
    "spaced-presses": [(0, INT)] + [(0.1, INT)] * 15,
    "mixed-kinds": [(0, INT)] + [(0.1, TERM), (0.1, HUP), (0.1, INT)] * 5,
}
REMOVAL_WAIT_S = 60.0   # how long the revised form waits, after the first press, for the removal to begin
POLL_S = 0.001          # how often it looks


def _folder_marks(folders):
    """Each folder's modification time, or None once it is gone: an entry removed from it changes its mark."""
    found = []
    for folder in folders:
        try:
            found.append(os.stat(folder).st_mtime_ns)
        except OSError:
            found.append(None)
    return found


def _press_on_removal(started, schedule, sleeping):
    """``Started.send_all``, with ``ON_REMOVAL`` as a delay: that press goes as soon as an entry of the planted
    test's temporary folder or of one of its MANY_FOLDERS folders is removed (or the folder is gone), while gov
    still runs. ``run.sent`` lists the signals sent."""
    base = Path(sleeping["tmp_path"])
    folders = [base] + [base / f"qzv96leak-many-{index}" for index in range(support.MANY_FOLDERS)]
    first = _folder_marks(folders)
    sent = []
    for delay, signum in schedule:
        if delay == ON_REMOVAL:
            deadline = time.monotonic() + REMOVAL_WAIT_S
            while (started.process.poll() is None and time.monotonic() < deadline
                   and _folder_marks(folders) == first):
                time.sleep(POLL_S)
        elif delay:
            time.sleep(delay)
        if started.process.poll() is not None:
            break
        os.kill(started.process.pid, signum)
        sent.append(int(signum))
    run = started.finish(60.0, f"signals {sent}")
    run.sent = sent
    return run


@pytest.mark.parametrize("presses", list(CLEAN_UP_PRESSES))
def test_r9_a_ctrl_c_during_the_clean_up_is_held_back_until_the_clean_up_ends(tmp_path, presses):
    """A planted test leaves 20,000 files in its temporary folder, then sleeps. SIGINT to gov alone ends the run;
    further presses (SIGINT, or SIGTERM, SIGHUP and SIGINT in turn) arrive during the clean-up, the revised form's
    second once the planted files begin to disappear. When gov ends, the given TMPDIR is empty, no marker
    anywhere, the child gone, and the exit code is 130."""
    files = support.second_file("many_sleep", "test_qzv96leak_many", extra=support.MANY)
    project = support.Project(tmp_path, files, support.SECOND_README)
    started = project.start(support.TICKET_ID)
    try:
        sleeping = started.wait_for("sleeping", support.START_WAIT_S)
        schedule = CLEAN_UP_PRESSES[presses]
        if any(delay == ON_REMOVAL for delay, _ in schedule):
            run = _press_on_removal(started, schedule, sleeping)
        else:
            run = started.send_all(schedule)
        problems = run.problems(generic=False)   # first, so it is what gov left when it ended
        problems += _ended(run, 128 + int(INT))
        if len(run.sent) < 2:
            problems.append(f"the case's premise failed: gov ended before a second press (sent {run.sent})")
        if not support.pid_gone(sleeping["pid"]):
            problems.append("the child pytest still runs after gov accept ended")
        given = run.tmpdir.resolve()
        if sleeping.get("made") != support.MANY_FILES or given not in Path(sleeping["tmp_path"]).resolve().parents:
            problems.append(f"the planted test did not make its {support.MANY_FILES} files under the given TMPDIR")
        assert not problems, "\n".join(problems) + f"\nsignals sent: {run.sent}\n" + run.describe()
    finally:
        started.stop()
        _remove_left(project)


# R10 ----------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind, expected, code", [
    ("deep_pass", support.SECOND_PASSES_EXPECTED, support.EXIT_PASS),
    ("deep_fail", support.SECOND_FAILS_EXPECTED, support.EXIT_FAIL),
], ids=["passes", "fails"])
def test_r10_a_chain_of_nested_folders_deeper_than_a_recursive_removal_leaves_the_result_as_the_tests_gave_it(
        tmp_path, kind, expected, code):
    """A planted test leaves, in its temporary folder, a chain of 1,200 nested folders, the deepest three without
    write, read or any permission, then passes (exit code 0) or fails (exit code 3): never an error."""
    files = support.second_file(kind, "test_qzv96leak_deep", extra=support.DEEP)
    project = support.Project(tmp_path, files, support.SECOND_README)
    try:
        run = project.run(support.TICKET_ID)
        problems = run.problems()   # first, so it is what gov left when it ended
        problems += _outcome_problems(run, expected, code)
        deep = project.records("deep")
        given = run.tmpdir.resolve()
        if not deep or deep[0].get("depth") != support.CHAIN_DEPTH:
            problems.append(f"the planted test did not make its chain of {support.CHAIN_DEPTH} folders")
        elif given not in Path(deep[0]["top"]).resolve().parents:
            problems.append(f"the planted chain {deep[0]['top']} was made outside the given TMPDIR {given}")
        assert not problems, "\n".join(problems) + "\n" + run.describe()
    finally:
        _remove_left(project)


# R11 ----------------------------------------------------------------------------------------------------------

# The signal gov is started ignoring, and whether it is sent to gov's process group (as a hang-up reaches the
# foreground job) rather than to gov alone.
IGNORED = {
    "SIGHUP-to-gov": (HUP, False),
    "SIGHUP-to-its-process-group": (HUP, True),
    "SIGTERM-to-gov": (TERM, False),
    "SIGINT-to-gov": (INT, False),
}


@pytest.mark.parametrize("case", list(IGNORED))
def test_r11_a_signal_gov_was_started_ignoring_stays_ignored_and_the_run_completes(tmp_path, case):
    """gov accept is started with the signal set to "ignore", as nohup does; while a planted test waits, the signal
    is sent. 1.5 s later gov and its child still run; the planted test is then let go: the run completes and
    reports as usual (both lines pass, exit code 0)."""
    signum, group = IGNORED[case]
    project = support.Project(tmp_path, support.second_file("wait_for_go", "test_qzv96leak_waiter"),
                              support.SECOND_README)
    started = project.start(support.TICKET_ID, ignore=(signum,))
    try:
        waiting = started.wait_for("waiting", support.START_WAIT_S)
        if group:
            os.killpg(started.process.pid, signum)
        else:
            os.kill(started.process.pid, signum)
        time.sleep(IGNORED_WAIT_S)
        problems = []
        if started.process.poll() is not None:
            problems.append(f"gov accept ended (exit code {started.process.returncode}) on signal {int(signum)}, "
                            "which it was started ignoring")
        if not support.pid_running(waiting["pid"]):
            problems.append(f"the child pytest was stopped by signal {int(signum)}, which gov was started ignoring")
        project.go()
        run = started.finish()
        problems += _outcome_problems(run, support.SECOND_PASSES_EXPECTED, support.EXIT_PASS)
        if not project.records("went"):
            problems.append("the planted test never went on after the signal")
        problems += run.problems()
        assert not problems, "\n".join(problems) + "\n" + run.describe()
    finally:
        started.stop()


# R12 ----------------------------------------------------------------------------------------------------------

# The signals sent to gov alone while the planted test (and the grandchild it started) sleeps, each
# ``(seconds after the one before, signal)``, and the exit code gov must end with.
EXIT_AFTER = {
    "SIGTERM-twice-5-ms-apart": ([(0, TERM), (0.005, TERM)], 128 + int(TERM)),
    "SIGHUP-twice-5-ms-apart": ([(0, HUP), (0.005, HUP)], 128 + int(HUP)),
    "SIGINT": ([(0, INT)], 128 + int(INT)),
}


@pytest.mark.parametrize("case", list(EXIT_AFTER))
def test_r12_a_signal_that_ends_the_run_ends_gov_by_an_ordinary_exit_with_128_plus_the_signal(tmp_path, case):
    """SIGTERM twice a few milliseconds apart, SIGHUP the same, or one SIGINT, while the child runs: the return
    code is 143, 129 or 130, never a negative one; the given TMPDIR is empty and the child and grandchild gone."""
    schedule, expected = EXIT_AFTER[case]
    project = support.Project(tmp_path, support.second_file("sleep", "test_qzv96leak_sleeper"),
                              support.SECOND_README)
    started = project.start(support.TICKET_ID)
    try:
        sleeping = started.wait_for("sleeping", support.START_WAIT_S)
        run = started.send_all(schedule)
        problems = run.problems(generic=False)   # first, so it is what gov left when it ended
        problems += _ended(run, expected)
        if not support.pid_gone(sleeping["pid"]):
            problems.append("the child pytest still runs after gov accept ended")
        if not support.pid_gone(sleeping["grandchild"]):
            problems.append("a process the child started still runs after gov accept ended")
        assert not problems, "\n".join(problems) + f"\nsignals sent: {run.sent}\n" + run.describe()
    finally:
        started.stop()


# Premises: the planted projects do what the cases above rely on (green before the implementation, by design) ---

def test_premise_r8_w1_30s_forms_map_the_passing_cases_and_hold_the_failing_one_in_no_test_or_file_table():
    for form, text in support.W1_30_FORMS.items():
        tables = support.markdown_tables(text)
        mapping = [(header, body) for header, body in tables
                   if any(cell.lower().startswith(("test", "file")) for cell in header)]
        assert len(mapping) == 1, f"{form}: one table with a Test or File column under a header row"
        header, body = mapping[0]
        assert not any(cell.lower().startswith("kpi") for cell in header), f"{form}: the heading form"
        items = {item for row in body for item in re.findall(r"`([^`]+)`", row[0])}
        assert items == {"test_qzv96leak_alpha_one", "test_qzv96leak_alpha_param"}, f"{form}: {items}"
        assert "`test_qzv96leak_second_fails`" in text, f"{form}: the failing case is in the README"
        assert not any("test_qzv96leak_second_fails" in " ".join(row) for row in body), form
        headings = re.findall(r"^#{2,6}\s+(.*)$", text, re.MULTILINE)
        assert [support.line_names(heading) for heading in headings] == [["success-1"], ["failure-1"]], form
    assert len(support.markdown_tables(support.W1_30_FORMS["a-row-with-no-header-under-f1"])) == 1, \
        "the row under F1 has no header row: it is no table of its own"


def test_premise_r10_raw_pytest_leaves_a_chain_deeper_than_1100_and_the_recursion_limit_its_bottom_locked(
        tmp_path):
    project = support.Project(tmp_path, support.second_file("deep_pass", "test_qzv96leak_deep", extra=support.DEEP),
                              support.SECOND_README)
    try:
        done, outcomes = project.raw_pytest()
        assert outcomes == {**ALPHA_RAW, "test_qzv96leak_second::test_qzv96leak_deep": "passed"}, \
            f"raw pytest: {outcomes}\n{done.stdout[-3000:]}"
        records = project.records("deep")
        assert len(records) == 1, f"the planted test made one chain: {records}"
        assert records[0]["depth"] == support.CHAIN_DEPTH > max(1100, sys.getrecursionlimit()), records[0]
        deepest = Path(records[0]["top"]).joinpath(*["d"] * support.CHAIN_DEPTH)
        modes = [stat.S_IMODE(os.lstat(deepest.parents[index] if index >= 0 else deepest).st_mode)
                 for index in (1, 0, -1)]
        assert modes == [0o500, 0o300, 0o000], f"the deepest three folders' modes: {[oct(m) for m in modes]}"
    finally:
        _remove_left(project)
    left = [record["top"] for record in project.records("deep") if os.path.lexists(record["top"])]
    assert not left, f"the cases' own removal without recursion left the chain: {left}"


def test_premise_r11_a_process_started_this_way_begins_with_the_signal_ignored(tmp_path):
    project = support.Project(tmp_path, dict(support.ALPHA), support.SIMPLE_README)
    script = ("import signal, sys; sys.stdout.write(' '.join(str(int(signal.getsignal(s) == signal.SIG_IGN)) "
              "for s in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)))")
    for signum, expected in ((HUP, "1 0 0"), (INT, "0 1 0"), (TERM, "0 0 1")):
        tmpdir = tmp_path / f"premise-tmp-{int(signum)}"
        tmpdir.mkdir()
        process = project._popen([sys.executable, "-c", script], project.root, tmpdir, ignore=(signum,))
        stdout, stderr = process.communicate(timeout=60)
        assert (process.returncode, stdout) == (0, expected), f"signal {int(signum)}: {stdout!r} {stderr[-2000:]}"
