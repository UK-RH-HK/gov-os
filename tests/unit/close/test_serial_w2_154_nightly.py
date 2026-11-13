"""W2-154 (DAEO-l4gf) S3, F2: ``nightly.sh`` reports the serial cases it ran, and a night that ran none is red.

Every case runs ``nightly.sh`` only through its stub seam (the Interface's I4): ``NIGHTLY_SERIAL_STUB=<file>`` makes
the script skip the clone, the rebuild, the gate and both suites, source the stub (which sets ``ENTRIES`` and
``s_exit`` and writes ``$JUNIT/serial.xml``) and run only the serial count and verdict steps. The script is a copy
with every path of its own under ``tmp_path`` (``test_serial_w2_154_support.run_nightly``); no case starts a suite,
touches the real logs or pings anyone. The Interface's I3 is the contract: N is the number of ``<testcase>``
elements of ``serial.xml``; ``serial: N cases run`` with entries declared, ``serial: 0 declared`` with none (not
red); a serial phase of 0 cases, or whose exit is neither 0 nor 1, appends ``verdict: red serial: 0 cases run`` or
``verdict: red serial: collection error, exit E`` after ``nightly_alone.py``'s line, so the night's final verdict
reads red and the P1 ping follows.
"""
from __future__ import annotations

from . import test_serial_w2_154_support as support

ENTRIES = "tests/unit/test_a.py\ntests/unit/test_b.py::test_b"


def _not_red(night: support.Night) -> None:
    verdict = night.verdict()
    assert verdict is not None, "the night ended with no verdict line:\n" + night.describe()
    assert not verdict.startswith("verdict: red"), "the night reads red:\n" + night.describe()
    assert not [ping for ping in night.pings if "NIGHTLY-RED" in ping], night.describe()


def test_s3_i3_a_serial_phase_that_ran_five_cases_reports_them_and_is_not_red_from_that_step(tmp_path):
    """S3: the stub runs 5 cases (``serial.xml`` with 5 ``<testcase>``, ``s_exit`` 0): ``serial: 5 cases run``."""
    night = support.run_nightly(tmp_path, entries=ENTRIES, s_exit=0, cases=5)
    assert night.stated(r"serial: 5 cases run\b"), "no 'serial: 5 cases run' line:\n" + night.describe()
    assert not night.stated(r"serial: \d+ declared"), night.describe()
    _not_red(night)
    assert night.code != 2, night.describe()


def test_f2_s3_i3_a_serial_phase_that_ran_no_case_is_red_though_its_junit_file_is_green(tmp_path):
    """F2, S3: the stub runs none (``serial.xml`` green with no ``<testcase>``, ``s_exit`` 0): the final verdict is
    ``verdict: red serial: 0 cases run``, after the verdict ``nightly_alone.py`` gave, and the red night pings P1.
    Green there is the failure."""
    night = support.run_nightly(tmp_path, entries=ENTRIES, s_exit=0, cases=0)
    assert night.stated(r"serial: 0 cases run\b"), "no 'serial: 0 cases run' line:\n" + night.describe()
    assert night.verdict() == "verdict: red serial: 0 cases run", \
        "a night whose serial phase ran no case does not read red:\n" + night.describe()
    assert [ping for ping in night.pings if ping.startswith("P1 NIGHTLY-RED")], \
        "no P1 ping follows the red:\n" + night.describe()
    assert "verdict: red serial: 0 cases run" in night.stdout, "the printed run.txt does not end on the red verdict"


def _collection_error(tmp_path, exit_code):
    night = support.run_nightly(tmp_path, entries=ENTRIES, s_exit=exit_code, cases=5)
    assert night.verdict() == f"verdict: red serial: collection error, exit {exit_code}", \
        "a serial phase that ended in a collection error does not read red:\n" + night.describe()
    assert [ping for ping in night.pings if ping.startswith("P1 NIGHTLY-RED")], night.describe()


def test_s3_i3_a_serial_phase_that_ended_with_exit_4_is_red_though_its_junit_file_is_green(tmp_path):
    """S3: the stub ends with exit 4 (a usage error at collection), its JUnit file green: the final verdict is
    ``verdict: red serial: collection error, exit 4`` and the night pings P1."""
    _collection_error(tmp_path, 4)


def test_s3_i3_a_serial_phase_that_ended_with_exit_2_is_red_though_its_junit_file_is_green(tmp_path):
    """S3: the same with exit 2 (an interrupted run): ``verdict: red serial: collection error, exit 2``."""
    _collection_error(tmp_path, 2)


def test_s3_i3_a_serial_phase_that_ended_with_failures_only_is_not_a_collection_error(tmp_path):
    """S3 (an edge): exit 1 is a run with failing cases, not a collection error ("neither 0 nor 1"); the count
    is still reported and this step adds no red line."""
    night = support.run_nightly(tmp_path, entries=ENTRIES, s_exit=1, cases=5)
    assert night.stated(r"serial: 5 cases run\b"), night.describe()
    assert "collection error" not in night.run_txt, night.describe()
    _not_red(night)


def test_s3_i3_a_serial_phase_with_nothing_declared_reads_0_declared_and_is_not_red(tmp_path):
    """S3: ``ENTRIES`` empty: ``serial: 0 declared``, the phase skipped, not red, and not today's exit 2 with
    "no serial-only entry read"."""
    night = support.run_nightly(tmp_path, entries="", s_exit=0, cases=None)
    assert night.stated(r"serial: 0 declared\b"), "no 'serial: 0 declared' line:\n" + night.describe()
    assert "no serial-only entry read" not in night.run_txt + night.stdout, night.describe()
    assert not night.stated(r"serial: \d+ cases run"), "a phase with nothing declared reports cases run:\n" + night.describe()
    assert night.code != 2, night.describe()
    _not_red(night)
