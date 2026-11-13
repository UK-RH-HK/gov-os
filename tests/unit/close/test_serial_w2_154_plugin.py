"""W2-154 (DAEO-l4gf) S1, S2, F1: the close's serial plugin and an entry its opt-in lists leave out of the run.

Each case builds a project under ``tmp_path`` with its own serial-only list and its own opt-in mechanism (see
``test_serial_w2_154_support``), and runs the project's tests through a real ``python3 -m pytest`` with the plugin
(``-p gov_close_serial_only``), or through the close's own test run (``gov.close.command._run_tests``, which
``test_parallel_runs.py`` drives the same way) to read its stated record. The Interface (I1, I2) is the contract:
the plugin takes an entry with no collected case and at least one case another plugin deselected as "not in this
run"; it prints and writes it; the close's stated record names it; an entry with neither still ends the run with
exit 4, "no case is named by the entry".
"""
from __future__ import annotations

from functools import partial

import pytest

from gov.close import command

from . import test_serial_w2_154_support as support
from .test_serial_w2_154_support import A, B, C, D

LIMIT = 180
_run_tests = partial(command._run_tests, workers=1)
ZERO = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}


@pytest.fixture(autouse=True)
def in_no_worker(monkeypatch, tmp_path):
    """These cases may themselves run in a worker of the parallel runner: the runs they start begin in none, with
    no opt-in of the caller's, and every planted case logs under this test's folder."""
    for name in ("PYTEST_XDIST_WORKER", "PYTEST_XDIST_WORKER_COUNT", "PYTEST_XDIST_TESTRUNUID", "GOV_TESTS_OPTIN",
                 support.OUT_VARIABLE):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(support.RAN, str(tmp_path / "close.ran"))


def _plant(tmp_path, entries=(A, B, C, D)):
    root = tmp_path / "project"
    support.plant(root, entries)
    return root


def _close_run(root, tmp_path):
    """The close's test run of the planted project's ``tests/``: its findings, its counts and its stated record."""
    tests = root / "tests"
    stated: list[dict] = []
    findings, counts = _run_tests(root, tests, LIMIT, ignore=tests / "acceptance", none_collected_ok=True,
                                  stated=stated)
    return findings, counts, stated


def _serial_record(stated):
    runs = [run for run in stated if run["form"] == "serial-afterwards"]
    assert len(runs) == 1, f"the close states {len(runs)} serial-afterwards runs: {stated}"
    return runs[0]


# ---- S1 / I1 / I2: the plugin, in the serial run afterwards --------------------------------------------------------

def test_s1_i1_i2_an_entry_whose_every_case_the_optin_list_leaves_out_is_not_in_the_run(tmp_path):
    """S1: A's every case is left out by the opt-in list. I1, I2: the run does not stop (exit 0), says
    ``gov_close_serial_only: not in this run: <A>``, writes A to the file ``GOV_CLOSE_SERIAL_ONLY_OUT`` names, and
    A's cases ran nowhere (not in this run, not in the parallel run either)."""
    root = _plant(tmp_path, (A,))
    serial = support.run_plugin(root, tmp_path / "w", given=(A,), name="serial")
    assert serial.code == 0, "an entry the opt-in list leaves out stopped the serial phase:\n" + serial.describe()
    assert any(line.strip() == support.NOT_IN_RUN + A for line in serial.text.splitlines()), serial.describe()
    assert serial.not_in_this_run() == [A], serial.describe()
    parallel = support.run_plugin(root, tmp_path / "w", name="parallel")
    assert parallel.code == 0, parallel.describe()
    assert [line for line in serial.ran() + parallel.ran() if line.startswith("test_a_")] == [], \
        "a case of A ran, in the serial run or in the parallel run: " + str(serial.ran() + parallel.ran())
    assert "test_other_one worker=True" in parallel.ran(), parallel.describe()


def test_s1_i2_the_run_goes_on_with_the_entries_that_ran_and_names_only_the_one_that_is_out(tmp_path):
    """S1 (an edge): A (out) and C (one case, kept) given together: exit 0, C's case runs serially, only A is named
    as not in this run."""
    root = _plant(tmp_path, (A, C))
    serial = support.run_plugin(root, tmp_path / "w", given=(A, C), name="serial")
    assert serial.code == 0, serial.describe()
    assert serial.not_in_this_run() == [A], serial.describe()
    assert serial.ran() == ["test_c_one worker=False"], serial.describe()
    assert support.NOT_IN_RUN + C not in serial.text


def test_s1_i1_an_entry_with_some_of_its_cases_kept_is_in_the_run(tmp_path):
    """S1 (an edge, I1): D has two cases, the opt-in list leaves one out: D has a collected case, so it is in the
    run: its kept case runs serially and D is not named as out."""
    root = _plant(tmp_path, (D,))
    serial = support.run_plugin(root, tmp_path / "w", given=(D,), name="serial")
    assert serial.code == 0, serial.describe()
    assert serial.ran() == ["test_d_on worker=False"], serial.describe()
    assert serial.not_in_this_run() == [], serial.describe()
    assert support.NOT_IN_RUN not in serial.text, serial.describe()


def test_s1_i2_the_close_states_the_entry_that_is_not_in_the_run_and_counts_a_serial_run_of_no_case(tmp_path):
    """S1, I2: through the close's test run, with A the only given entry: no finding; the serial run it states is a
    run of 0 cases whose ``not_in_this_run`` is ``[A]`` and whose ``cases`` do not list A; the other case ran in
    the parallel phase; A's cases ran nowhere."""
    root = _plant(tmp_path, (A,))
    findings, counts, stated = _close_run(root, tmp_path)
    assert findings == [], "the close made a finding of an entry its opt-in list leaves out: " + str(findings)
    serial = _serial_record(stated)
    assert serial["not_in_this_run"] == [A], stated
    assert A not in serial["cases"], stated
    assert (serial["passed"], serial["failed"], serial["errors"]) == (0, 0, 0), stated
    parallel = [run for run in stated if run["form"] == "parallel"]
    # the parallel phase ran C, D's kept case and the plain case; A's two cases are in neither phase
    assert len(parallel) == 1 and parallel[0]["passed"] == 3, stated
    assert counts == ZERO | {"passed": 3}, counts
    log = (tmp_path / "close.ran").read_text(encoding="utf-8").splitlines()
    assert not [line for line in log if line.startswith("test_a_")], log


def test_s1_i2_the_close_states_the_ones_that_ran_in_cases_and_the_one_that_is_out_apart(tmp_path):
    """S1, I2: A (out) and C (kept) declared: ``cases`` keeps only C, ``not_in_this_run`` names only A, the serial
    run counts C's one case, and there is no finding."""
    root = _plant(tmp_path, (A, C))
    findings, counts, stated = _close_run(root, tmp_path)
    assert findings == [], findings
    serial = _serial_record(stated)
    assert serial["cases"] == [C], stated
    assert serial["not_in_this_run"] == [A], stated
    assert (serial["passed"], serial["failed"], serial["errors"]) == (1, 0, 0), stated
    log = (tmp_path / "close.ran").read_text(encoding="utf-8").splitlines()
    assert "test_c_one worker=False" in log and not [line for line in log if line.startswith("test_a_")], log


# ---- F1: an entry that names no case, and no opt-in list explains, still stops the phase ---------------------------

def test_f1_an_entry_that_names_no_case_and_no_optin_list_explains_stops_the_serial_run_with_exit_4(tmp_path):
    """F1: B (a file with no case) alone: exit 4 (``pytest.UsageError``), "no case is named by the entry", naming B.
    A pass there is the failure. (This case may pass on today's code: it guards the behaviour S1 must keep.)"""
    root = _plant(tmp_path, (B,))
    serial = support.run_plugin(root, tmp_path / "w", given=(B,), name="serial")
    assert serial.code == 4, "an entry that names no case did not stop the serial run:\n" + serial.describe()
    assert support.NO_CASE in serial.text and B in serial.text, serial.describe()
    assert support.NOT_IN_RUN not in serial.text, serial.describe()


def test_f1_with_an_entry_that_is_out_given_too_the_one_that_names_no_case_still_stops_the_run(tmp_path):
    """F1 (an edge, I1): B and A given together: the run stops with exit 4 for B ("no case is named by the entry"
    names B); A, which the opt-in list explains, is not what the run stops on."""
    root = _plant(tmp_path, (A, B))
    serial = support.run_plugin(root, tmp_path / "w", given=(A, B), name="serial")
    assert serial.code == 4, serial.describe()
    message = [line for line in serial.text.splitlines() if support.NO_CASE in line]
    assert message and B in " ".join(message), serial.describe()
    assert A not in " ".join(message), "the run stops on an entry its opt-in list explains:\n" + serial.describe()


def test_f1_the_close_does_not_pass_an_entry_that_names_no_case(tmp_path):
    """F1 through the close: B declared (it names no case, no opt-in list explains it): the close's run has a finding
    and states no ``not_in_this_run`` for B. (May pass on today's code: a guard.)"""
    root = _plant(tmp_path, (B, C))
    findings, _counts, stated = _close_run(root, tmp_path)
    assert findings, "the close passed an entry that names no case: " + str(stated)
    assert all(B not in run.get("not_in_this_run", []) for run in stated), stated


# ---- S2 / I1: the same project, the opt-in list switched on -------------------------------------------------------

def _s2_plugin_run(tmp_path, form):
    root = _plant(tmp_path, (A,))
    serial = support.run_plugin(root, tmp_path / "w", given=(A,), optin=support.OPT_IN, optin_form=form, name="serial")
    assert serial.code == 0, serial.describe()
    assert sorted(serial.ran()) == ["test_a_one worker=False", "test_a_two worker=False"], serial.describe()
    assert serial.not_in_this_run() == [], serial.describe()
    assert support.NOT_IN_RUN not in serial.text, serial.describe()
    parallel = support.run_plugin(root, tmp_path / "w", optin=support.OPT_IN, optin_form=form, name="parallel")
    assert parallel.code == 0, parallel.describe()
    assert not [line for line in parallel.ran() if line.startswith("test_a_")], \
        "a case of A ran in the parallel phase: " + str(parallel.ran())


def test_s2_i1_in_a_run_that_opts_in_by_the_variable_the_entry_is_back_in_the_serial_phase_not_the_parallel_one(tmp_path):
    """S2: ``GOV_TESTS_OPTIN=lifted``: A's cases run in the serial run afterwards (in no worker), none in the
    parallel run, and A is not named as out."""
    _s2_plugin_run(tmp_path, "variable")


def test_s2_i1_in_a_run_that_opts_in_by_the_option_the_entry_is_back_in_the_serial_phase_not_the_parallel_one(tmp_path):
    """S2: the same with ``--optin=lifted`` (the run's other form of opting in)."""
    _s2_plugin_run(tmp_path, "option")


def test_s2_the_close_states_the_cases_in_the_serial_phase_when_the_run_opts_in(tmp_path, monkeypatch):
    """S2 through the close: with ``GOV_TESTS_OPTIN=lifted`` the serial run it states has A in ``cases``, ran
    A's two cases, and names no entry as not in the run; the parallel run ran none of A (the run's record shows
    those cases in the serial phase and none in the parallel phase)."""
    monkeypatch.setenv("GOV_TESTS_OPTIN", support.OPT_IN)
    root = _plant(tmp_path, (A,))
    findings, counts, stated = _close_run(root, tmp_path)
    assert findings == [], findings
    serial = _serial_record(stated)
    assert serial["cases"] == [A] and A not in serial.get("not_in_this_run", []), stated
    assert serial["passed"] == 2, stated
    log = (tmp_path / "close.ran").read_text(encoding="utf-8").splitlines()
    assert sorted(line for line in log if line.startswith("test_a_")) == [
        "test_a_one worker=False", "test_a_two worker=False"], log
