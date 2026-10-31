"""Support code for W2-96's acceptance tests: planted projects and runs of ``gov accept`` (standard library only).

``gov accept <ticket>`` runs a ticket's acceptance folder in a child pytest and reports pass or fail per KPI line of
the folder's README map, and nothing of the tests' content (DEC-959 item 6, DEC-820 (c), the lead's design note).
These tests use it only through its public interface: the command line, its API-0002 envelope, its exit code, and
what it leaves on disk.

- **The code under test (DEC-732).** ``gov`` is run as ``python3 -m gov.cli.main`` with ``PYTHONPATH`` starting
  with the ``src/`` of the repository that holds this file (``SRC``), never a ``gov`` from ``PATH``. Merged into
  another tree and run from there, the tests exercise that tree's code.
- **Planted projects.** Each case builds a project from scratch under pytest's ``tmp_path`` (``git init``, one
  commit): a ticket ``.tickets/TDPL-a961.md`` (WBS id ``W9-61``) whose ``acceptance_tests.path`` is
  ``tests/acceptance/W9-61/``; a second ticket ``TDPL-b962`` (``W9-62``) whose own folder holds a failing test, so
  a run of the wrong ticket shows; ``src/qzv96leak_lib.py``, which the planted tests import; a ``pyproject.toml`` and
  a ``.gitignore`` (``__pycache__/``, ``.pytest_cache/``) as the real repository has. The planted test files are
  written at test time from the strings below; no planted ``test_*.py`` file is committed where a real run collects.
- **The marker.** Every planted test name, file name, docstring, assertion message, compared value, print, log
  line, warning, exception message, skip reason, fixture, parameter value and parameter id, and the planted
  READMEs' own text, carries ``qzv96leak`` (``MARKER``). The ticket ids, WBS ids and declared paths do not: a
  refusal may name those. After each run the case searches stdout, stderr (the envelope and the error message are
  in them), every file created or changed in the planted project (ignored files included), everything under the
  ``TMPDIR`` the run was given, and the run's ``HOME``: none may hold the marker. Raw pytest output always holds it
  (``test_w2_96_at_premises.py``), so the probe can see a leak.
- **The tree's own src first.** The run's ``PYTHONPATH`` is ``SRC`` and then a decoy folder holding another
  ``qzv96leak_lib``; a planted passing test asserts the planted tree's value, so it passes only when the child put
  the planted project's ``src/`` before what it was given.
- **Probe records.** Each planted test that runs writes a small JSON record (its process id, working folder,
  ``tmp_path``, temporary folder, and for a sleeping test its grandchild's process id) into a probe folder outside
  the project and outside the given ``TMPDIR``. The cases read them to check what ran, where, and that it stopped.
- **The environment** is built from scratch: ``PATH``, an empty ``HOME`` (with ``.local`` linked to the user base,
  where pytest and its plugins are installed, and ``PYTHONUSERBASE`` naming it too), an empty ``TMPDIR`` of the
  run's own, ``USER``, ``LOGNAME``, a UTF-8 locale and ``PYTHONPATH``. Nothing else of the session reaches it: no
  ``PYTHONDONTWRITEBYTECODE``, no ``PYTHONPYCACHEPREFIX``, no ``PYTEST_ADDOPTS``, no ``GOV_ROLE`` or ``GOV_TICKET``,
  so keeping the project free of ``__pycache__`` and ``.pytest_cache`` is the runner's own work.
"""

from __future__ import annotations

import ast
import getpass
import hashlib
import json
import os
import re
import signal
import site
import stat
import subprocess
import sys
import time
import xml.etree.ElementTree as ElementTree
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
HERE = Path(__file__).resolve().parent

MARKER = "qzv96leak"
# Words no output of gov accept holds, whatever the marker: pytest's own words for a traceback, an assertion, a
# node id and a conftest. (Not used for the interrupt case, where gov's own exit may print a traceback of gov.)
GENERIC_PROBES = ("traceback", "assertionerror", "::", "conftest")
# Words of pytest's raw report: a refusal never falls back to raw output.
RAW_OUTPUT_WORDS = ("collected", "PASSED", "FAILED", "=====")

TICKET_ID, WBS_ID, FOLDER = "TDPL-a961", "W9-61", "tests/acceptance/W9-61"
OTHER_ID, OTHER_WBS, OTHER_FOLDER = "TDPL-b962", "W9-62", "tests/acceptance/W9-62"

EXIT_PASS, EXIT_REFUSED, EXIT_FAIL, EXIT_ERROR = 0, 1, 3, 4
NO_MAP, UNKNOWN_TICKET, NO_TESTS = "ACCEPT_NO_MAP", "ACCEPT_UNKNOWN_TICKET", "ACCEPT_NO_TESTS"
MAP_UNREADABLE = "ACCEPT_MAP_UNREADABLE"   # review 1, R4

RESULT_KEYS = ("ticket", "outcome", "error_kind", "lines", "unmapped", "totals")
LINE_KEYS = ("kpi", "outcome", "passed", "failed", "skipped")
COUNT_KEYS = ("passed", "failed", "skipped")

RUN_TIMEOUT_S = 300.0     # a wait under parallel load, not a time the ticket promises
TIMEOUT_OPTION_S = 8      # the --timeout the timeout case gives
START_WAIT_S = 120.0      # how long the interrupt case waits for its sleeping test to start
GONE_WAIT_S = 15.0        # how long a killed process may take to be gone


# --------------------------------------------------------------------------------------------------------------
# The planted test files. ``@PROBE@`` becomes the probe folder's path, ``@NAME@`` the test function's name.
# --------------------------------------------------------------------------------------------------------------

_HEADER = '''"""qzv96leak planted module: its names, messages and values carry the marker."""
import json
import logging
import os
import sys
import tempfile
import uuid
import warnings

import pytest

QZV96LEAK_PROBE = @PROBE@


def qzv96leak_record(kind, **more):
    record = dict(kind=kind, pid=os.getpid(), cwd=os.getcwd(), tempdir=tempfile.gettempdir(), **more)
    path = os.path.join(QZV96LEAK_PROBE, uuid.uuid4().hex)
    with open(path + ".part", "w", encoding="utf-8") as handle:
        json.dump(record, handle)
    os.replace(path + ".part", path + ".json")


def qzv96leak_noise(tmp_path, name):
    print("qzv96leak-stdout " + name)
    sys.stderr.write("qzv96leak-stderr " + name + "\\n")
    logging.getLogger("qzv96leak").warning("qzv96leak-log " + name)
    warnings.warn("qzv96leak-warning " + name)
    (tmp_path / "qzv96leak-left-behind.txt").write_text("qzv96leak-file " + name, encoding="utf-8")
    qzv96leak_record("ran", name=name, tmp_path=str(tmp_path))


@pytest.fixture
def qzv96leak_fixture_value():
    return "qzv96leak-actual-value"


@pytest.fixture
def qzv96leak_broken_setup():
    raise RuntimeError("qzv96leak-setup-error-message")


@pytest.fixture
def qzv96leak_broken_teardown():
    yield "qzv96leak-teardown-value"
    raise RuntimeError("qzv96leak-teardown-error-message")
'''

_CASES = {
    "pass": '''

def @NAME@(tmp_path):
    """qzv96leak docstring of a passing case."""
    from qzv96leak_lib import TREE_VALUE
    qzv96leak_noise(tmp_path, "@NAME@")
    assert TREE_VALUE == "qzv96leak-planted-tree", "qzv96leak-message: the planted tree's src was not first"
''',
    "param": '''

@pytest.mark.parametrize("qzv96leak_param", ["qzv96leak-value-a", "qzv96leak-value-b"],
                         ids=["qzv96leak-id-a", "qzv96leak-id-b"])
def @NAME@(tmp_path, qzv96leak_param):
    from qzv96leak_lib import TREE_VALUE
    qzv96leak_noise(tmp_path, "@NAME@")
    assert TREE_VALUE == "qzv96leak-planted-tree" and qzv96leak_param.startswith("qzv96leak-value")
''',
    "fail": '''

def @NAME@(tmp_path, qzv96leak_fixture_value):
    qzv96leak_noise(tmp_path, "@NAME@")
    assert qzv96leak_fixture_value == "qzv96leak-expected-value", "qzv96leak-assertion-message"
''',
    "setup_error": '''

def @NAME@(tmp_path, qzv96leak_broken_setup):
    qzv96leak_noise(tmp_path, "@NAME@")
''',
    "teardown_error": '''

def @NAME@(tmp_path, qzv96leak_broken_teardown):
    qzv96leak_noise(tmp_path, "@NAME@")
    assert qzv96leak_broken_teardown == "qzv96leak-teardown-value"
''',
    "skip": '''

def @NAME@(tmp_path):
    qzv96leak_noise(tmp_path, "@NAME@")
    pytest.skip("qzv96leak-skip-reason")
''',
    "sleep": '''

def @NAME@(tmp_path):
    import subprocess
    import time
    qzv96leak_noise(tmp_path, "@NAME@")
    grandchild = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"])
    qzv96leak_record("sleeping", name="@NAME@", grandchild=grandchild.pid)
    time.sleep(600)
''',
    "crash_signal": '''

def @NAME@(tmp_path):
    import signal
    qzv96leak_noise(tmp_path, "@NAME@")
    sys.stdout.flush()
    os.kill(os.getpid(), signal.SIGKILL)
''',
    "crash_internal": '''

def @NAME@(tmp_path):
    qzv96leak_noise(tmp_path, "@NAME@")
    os._exit(3)
''',
    # Review 1 (R3): a failing test that leaves folders without permissions; a test that holds them at a timeout.
    # Both need ``LOCK_UP`` as the file's ``extra``.
    "locked_fail": '''

def @NAME@(tmp_path):
    qzv96leak_noise(tmp_path, "@NAME@")
    qzv96leak_record("locked", name="@NAME@", tops=qzv96leak_lock_up(tmp_path))
    assert False, "qzv96leak-locked-failure-message"
''',
    "locked_sleep": '''

def @NAME@(tmp_path):
    import time
    qzv96leak_noise(tmp_path, "@NAME@")
    qzv96leak_record("sleeping", name="@NAME@", tops=qzv96leak_lock_up(tmp_path))
    time.sleep(600)
''',
    # Review 1 (R7): pytest's own exit call with its "tests failed" code (1), every case so far passed.
    "exit_early": '''

def @NAME@(tmp_path):
    qzv96leak_noise(tmp_path, "@NAME@")
    pytest.exit("qzv96leak-exit-reason", returncode=1)
''',
}

# Review 1 (R3): module-level code that makes, in ``base`` and in a new folder of the temporary folder, a folder
# without read, one without write, one without execute and one without any permission (each holding a file and a
# folder without any permission), and a file without any permission; it returns the two top folders' paths.
LOCK_UP = '''

def qzv96leak_lock_up(base):
    """qzv96leak: folders and a file without read, write or execute permission."""
    import pathlib
    tops = [pathlib.Path(base), pathlib.Path(tempfile.mkdtemp(prefix="qzv96leak-locked-"))]
    for top in tops:
        for name, mode in (("qzv96leak-no-read", 0o300), ("qzv96leak-no-write", 0o500),
                           ("qzv96leak-no-exec", 0o600), ("qzv96leak-no-permission", 0o000)):
            folder = top / name
            inner = folder / "qzv96leak-inner"
            inner.mkdir(parents=True)
            (inner / "qzv96leak-deep.txt").write_text("qzv96leak-locked-content", encoding="utf-8")
            (folder / "qzv96leak-file.txt").write_text("qzv96leak-locked-content", encoding="utf-8")
            os.chmod(inner, 0o000)
            os.chmod(folder, mode)
        locked = top / "qzv96leak-no-permission.txt"
        locked.write_text("qzv96leak-locked-content", encoding="utf-8")
        os.chmod(locked, 0o000)
    return [str(top) for top in tops]
'''

_IMPORT_ERROR = "\nimport qzv96leak_no_such_module_anywhere  # noqa: F401  (a collection error naming the marker)\n"
_SYNTAX_ERROR = '\n\ndef test_qzv96leak_syntax_error(:\n    "qzv96leak-syntax-error-text"\n'
_NO_TEST = '"""qzv96leak acceptance file that defines no test."""\nQZV96LEAK_VALUE = "qzv96leak-no-test"\n'


def planted_file(*cases, extra=""):
    """A planted test file: the header, ``extra`` (a module-level line), then each ``(kind, name)`` case."""
    return _HEADER + extra + "".join(_CASES[kind].replace("@NAME@", name) for kind, name in cases)


ALPHA = {"test_qzv96leak_alpha.py": planted_file(("pass", "test_qzv96leak_alpha_one"),
                                                 ("param", "test_qzv96leak_alpha_param"))}


def common_files():
    """The six files both map forms are tried on: 12 cases pass, 1 fails, 1 is skipped."""
    return {
        **ALPHA,
        "test_qzv96leak_beta.py": planted_file(("pass", "test_qzv96leak_beta_one"), ("pass", "test_qzv96leak_beta_two"),
                                               ("pass", "test_qzv96leak_beta_three")),
        "test_qzv96leak_gamma.py": planted_file(("pass", "test_qzv96leak_gamma_pass"),
                                                ("skip", "test_qzv96leak_gamma_skip")),
        "test_qzv96leak_delta.py": planted_file(("pass", "test_qzv96leak_delta_case"),
                                                ("pass", "test_qzv96leak_delta_case_more")),
        "test_qzv96leak_epsilon.py": planted_file(("param", "test_qzv96leak_epsilon"),
                                                  ("fail", "test_qzv96leak_epsilon_other")),
        "test_qzv96leak_zeta.py": planted_file(("pass", "test_qzv96leak_zeta_pass")),
    }


# What raw pytest gives for ``common_files`` (module::name[id]); checked by the premises.
COMMON_RAW = {
    "test_qzv96leak_alpha::test_qzv96leak_alpha_one": "passed",
    "test_qzv96leak_alpha::test_qzv96leak_alpha_param[qzv96leak-id-a]": "passed",
    "test_qzv96leak_alpha::test_qzv96leak_alpha_param[qzv96leak-id-b]": "passed",
    "test_qzv96leak_beta::test_qzv96leak_beta_one": "passed",
    "test_qzv96leak_beta::test_qzv96leak_beta_two": "passed",
    "test_qzv96leak_beta::test_qzv96leak_beta_three": "passed",
    "test_qzv96leak_gamma::test_qzv96leak_gamma_pass": "passed",
    "test_qzv96leak_gamma::test_qzv96leak_gamma_skip": "skipped",
    "test_qzv96leak_delta::test_qzv96leak_delta_case": "passed",
    "test_qzv96leak_delta::test_qzv96leak_delta_case_more": "passed",
    "test_qzv96leak_epsilon::test_qzv96leak_epsilon[qzv96leak-id-a]": "passed",
    "test_qzv96leak_epsilon::test_qzv96leak_epsilon[qzv96leak-id-b]": "passed",
    "test_qzv96leak_epsilon::test_qzv96leak_epsilon_other": "failed",
    "test_qzv96leak_zeta::test_qzv96leak_zeta_pass": "passed",
}

# The function names whose bodies run under ``common_files``, with how many times (parameter sets).
COMMON_RAN = {"test_qzv96leak_alpha_one": 1, "test_qzv96leak_alpha_param": 2, "test_qzv96leak_beta_one": 1,
              "test_qzv96leak_beta_two": 1, "test_qzv96leak_beta_three": 1, "test_qzv96leak_gamma_pass": 1,
              "test_qzv96leak_gamma_skip": 1, "test_qzv96leak_delta_case": 1, "test_qzv96leak_delta_case_more": 1,
              "test_qzv96leak_epsilon": 2, "test_qzv96leak_epsilon_other": 1, "test_qzv96leak_zeta_pass": 1}

# The unmapped cases of the row-form map, by name fragment: none may appear in any output.
ROWS_UNMAPPED_NAMES = ("beta_three", "delta_case_more", "epsilon_other", "zeta_pass")


def rows_readme(*rows, header=("KPI line", "Tests", "Red because qzv96leak"), title="qzv96leak planted suite"):
    """A row-form README: a title, a line of prose, and one table of ``(kpi cell, tests cell)`` rows."""
    width = len(header)
    lines = [f"# {title}", "", "Prose of the qzv96leak planted README.", "",
             "| " + " | ".join(header) + " |", "|" + "---|" * width]
    for row in rows:
        cells = list(row) + ["qzv96leak"] * (width - len(row))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


# Review 1 (R4) revised the row "Edge qzv96leak (names no line)": a row whose KPI cell names no line and whose Tests
# cell holds a backticked item now refuses the whole run (ACCEPT_MAP_UNREADABLE), so its file is named without
# backticks and the row holds no item; it still maps nothing, and the expected result is unchanged.
ROWS_README = """# qzv96leak planted suite (rows)

Prose that names `test_qzv96leak_zeta.py` and Success 1 outside any table: qzv96leak.

| KPI line | Tests | Red because qzv96leak |
|---|---|---|
| Success 1: qzv96leak words | `test_qzv96leak_alpha.py` (three cases, qzv96leak) | qzv96leak |
| S2 / F1 — qzv96leak | `test_qzv96leak_beta.py::test_qzv96leak_beta_one` | qzv96leak |
| KPI 3 and k4: qzv96leak | `tests/acceptance/W9-61/test_qzv96leak_gamma.py` | qzv96leak |
| s5, K 6: qzv96leak | `qzv96leak_delta_case` | qzv96leak |
| S 7; KPI 8 — qzv96leak | `test_qzv96leak_epsilon` | qzv96leak |
| kpi 10 and S9: qzv96leak | `test_qzv96leak_gamma.py::test_qzv96leak_gamma_pass` | qzv96leak |
| failure 2 / FAILURE 3 / f4 / F 5: qzv96leak | `test_qzv96leak_beta.py::test_qzv96leak_beta_two` | qzv96leak |
| Edge qzv96leak (names no line) | test_qzv96leak_zeta.py, with no backticks: no item | qzv96leak |

## Notes qzv96leak

| Test | Note |
|---|---|
| `test_qzv96leak_zeta.py` | qzv96leak: a table under a heading that names no line maps nothing |
"""

HEADINGS_README = """# qzv96leak planted suite (headings)

Prose of the qzv96leak planted README.

## KPI 1: qzv96leak heading words

| Test | Why |
|---|---|
| `test_qzv96leak_alpha.py` | qzv96leak |

### K2 — qzv96leak

| File |
|---|
| `test_qzv96leak_beta.py::test_qzv96leak_beta_one` |

#### Success 3 and F1 qzv96leak

| Tests | Notes |
|---|---|
| `qzv96leak_delta_case`, `test_qzv96leak_epsilon` | qzv96leak |

## s4 / f2; FAILURE 3: qzv96leak

| Test | Notes |
|---|---|
| `tests/acceptance/W9-61/test_qzv96leak_gamma.py` | qzv96leak |

### Detail qzv96leak (names no line)

| Test | Notes |
|---|---|
| `test_qzv96leak_zeta.py` | qzv96leak: the nearest heading names no line |
"""


def fails_files():
    return {
        **ALPHA,
        "test_qzv96leak_mixed.py": planted_file(("pass", "test_qzv96leak_mixed_pass"),
                                                ("fail", "test_qzv96leak_mixed_fail")),
        "test_qzv96leak_setup.py": planted_file(("setup_error", "test_qzv96leak_setup_error")),
        "test_qzv96leak_teardown.py": planted_file(("teardown_error", "test_qzv96leak_teardown_error")),
        "test_qzv96leak_skips.py": planted_file(("skip", "test_qzv96leak_only_skip")),
        "test_qzv96leak_zeta.py": planted_file(("pass", "test_qzv96leak_zeta_pass")),
    }


FAILS_RAW = {
    "test_qzv96leak_alpha::test_qzv96leak_alpha_one": "passed",
    "test_qzv96leak_alpha::test_qzv96leak_alpha_param[qzv96leak-id-a]": "passed",
    "test_qzv96leak_alpha::test_qzv96leak_alpha_param[qzv96leak-id-b]": "passed",
    "test_qzv96leak_mixed::test_qzv96leak_mixed_pass": "passed",
    "test_qzv96leak_mixed::test_qzv96leak_mixed_fail": "failed",
    "test_qzv96leak_setup::test_qzv96leak_setup_error": "failed",
    "test_qzv96leak_teardown::test_qzv96leak_teardown_error": "failed",
    "test_qzv96leak_skips::test_qzv96leak_only_skip": "skipped",
    "test_qzv96leak_zeta::test_qzv96leak_zeta_pass": "passed",
}

FAILS_README = rows_readme(
    ("Success 1: qzv96leak", "`test_qzv96leak_alpha.py`"),
    ("Success 2: qzv96leak", "`test_qzv96leak_mixed.py`"),
    ("Success 3: qzv96leak", "`test_qzv96leak_setup.py`"),
    ("Success 4: qzv96leak", "`test_qzv96leak_teardown.py`"),
    ("Failure 1: qzv96leak", "`test_qzv96leak_skips.py`"),
    ("Failure 2: qzv96leak", "`qzv96leak_matches_nothing`"),
    header=("KPI", "Test file", "Notes qzv96leak"))

SIMPLE_README = rows_readme(("Success 1: qzv96leak", "`test_qzv96leak_alpha.py`"))


def second_file_readme(item):
    """Success 1 maps the passing file; Success 2 maps ``item``."""
    return rows_readme(("Success 1: qzv96leak", "`test_qzv96leak_alpha.py`"), ("Success 2: qzv96leak", item))


def second_file(kind, name, extra=""):
    """``ALPHA`` and ``test_qzv96leak_second.py`` holding one case of ``kind``."""
    return {**ALPHA, "test_qzv96leak_second.py": planted_file((kind, name), extra=extra)}


SECOND_README = second_file_readme("`test_qzv96leak_second.py`")


def collection_files(kind):
    """A folder whose second file cannot be collected (``import``, ``syntax``), or that holds no test (``empty``)."""
    if kind == "import":
        return second_file("pass", "test_qzv96leak_import_victim", extra=_IMPORT_ERROR)
    if kind == "syntax":
        return {**ALPHA, "test_qzv96leak_second.py": planted_file(("pass", "test_qzv96leak_syntax_victim"))
                + _SYNTAX_ERROR}
    if kind == "empty":
        return {"test_qzv96leak_second.py": _NO_TEST}
    raise ValueError(kind)


OTHER_FILES = {"test_qzv96leak_other.py": planted_file(("fail", "test_qzv96leak_other_fails"))}
OTHER_README = rows_readme(("Success 1: qzv96leak", "`test_qzv96leak_other.py`"))


# --------------------------------------------------------------------------------------------------------------
# Review 1's planted projects (the reviewer's findings as described behaviours, DEC-136). ``root_files`` are
# written in the project itself, outside the acceptance folder, and committed; ``@ROOT@`` becomes the root's path.
# --------------------------------------------------------------------------------------------------------------

SECOND_FAILS = second_file("fail", "test_qzv96leak_second_fails")

# R1: a conftest that refuses a run given a per-run base folder, as this repository's tests/conftest.py does (an
# xdist worker aside), and records that it ran and what base folder it saw.
REFUSING_CONFTEST = {"tests/conftest.py": '''"""qzv96leak planted conftest: a per-run --basetemp is refused."""
import json
import os
import tempfile
import uuid

import pytest

QZV96LEAK_PROBE = @PROBE@


def pytest_configure(config):
    if hasattr(config, "workerinput"):
        return
    basetemp = config.option.basetemp
    record = dict(kind="conftest", pid=os.getpid(), cwd=os.getcwd(), tempdir=tempfile.gettempdir(),
                  basetemp=None if basetemp is None else str(basetemp))
    path = os.path.join(QZV96LEAK_PROBE, uuid.uuid4().hex)
    with open(path + ".part", "w", encoding="utf-8") as handle:
        json.dump(record, handle)
    os.replace(path + ".part", path + ".json")
    if basetemp is not None:
        raise pytest.UsageError("qzv96leak: a per-run --basetemp is refused by the planted conftest")
'''}

# R6: a pytest configuration naming a log file inside the project, by a path relative to the working folder (the
# root) or by an absolute one.
LOG_FILES = {"relative": "qzv96leak-pytest.log", "absolute": "qzv96leak-absolute.log"}


def log_file_config(where):
    path = LOG_FILES[where] if where == "relative" else "@ROOT@/" + LOG_FILES[where]
    return {"pyproject.toml": ('[project]\nname = "planted-w9"\nversion = "0.0.1"\n\n[tool.pytest.ini_options]\n'
                               f'log_file = "{path}"\nlog_file_level = "INFO"\n')}


# R7: three passing cases, then a test that ends the session by pytest.exit(returncode=1), then a failing test that
# never runs.
EXIT_FILES = {**ALPHA, "test_qzv96leak_second.py": planted_file(("exit_early", "test_qzv96leak_exits"),
                                                                ("fail", "test_qzv96leak_after_exit"))}

# R5: two files sharing a function name, so an item by function name maps a case in each.
ITEMS_FILES = {
    **ALPHA,
    "test_qzv96leak_items.py": planted_file(("pass", "test_qzv96leak_items_pass"), ("fail", "test_qzv96leak_items_fail"),
                                            ("pass", "test_qzv96leak_items_twin")),
    "test_qzv96leak_items_more.py": planted_file(("pass", "test_qzv96leak_items_twin"),
                                                 ("pass", "test_qzv96leak_items_extra")),
}

ITEMS_RAW = {
    "test_qzv96leak_alpha::test_qzv96leak_alpha_one": "passed",
    "test_qzv96leak_alpha::test_qzv96leak_alpha_param[qzv96leak-id-a]": "passed",
    "test_qzv96leak_alpha::test_qzv96leak_alpha_param[qzv96leak-id-b]": "passed",
    "test_qzv96leak_items::test_qzv96leak_items_pass": "passed",
    "test_qzv96leak_items::test_qzv96leak_items_fail": "failed",
    "test_qzv96leak_items::test_qzv96leak_items_twin": "passed",
    "test_qzv96leak_items_more::test_qzv96leak_items_twin": "passed",
    "test_qzv96leak_items_more::test_qzv96leak_items_extra": "passed",
}

# R5: an item holding "::" whose part before it is empty or does not end in ".py" maps every test of the folder
# whose function name is the part after the last "::".
ITEMS_COLON_README = rows_readme(
    ("Success 1: qzv96leak", "`::test_qzv96leak_items_pass`"),
    ("Success 2: qzv96leak", "`test_qzv96leak_items::test_qzv96leak_items_fail`"),
    ("Success 3: qzv96leak", "`qzv96leak_every_form::test_qzv96leak_items_twin`"),
    ("Failure 1: qzv96leak", "`test_qzv96leak_alpha.py`"))

# R5: an item naming a test (it holds "::" or begins with "test_") that matches no case fails its line; a line
# whose items all match and pass passes; an item that names no test and matches nothing changes nothing.
ITEMS_UNMATCHED_README = rows_readme(
    ("Success 1: qzv96leak", "`test_qzv96leak_alpha.py`, `test_qzv96leak_items_nothing`"),
    ("Success 2: qzv96leak",
     "`test_qzv96leak_alpha.py::test_qzv96leak_alpha_one`, `test_qzv96leak_items.py::test_qzv96leak_items_missing`"),
    ("Success 3: qzv96leak", "`test_qzv96leak_items_more.py`, `test_qzv96leak_missing_file.py`"),
    ("Success 4: qzv96leak", "`test_qzv96leak_items.py::test_qzv96leak_items_pass`, `::test_qzv96leak_items_absent`"),
    ("Failure 1: qzv96leak", "`::test_qzv96leak_alpha_one`, `test_qzv96leak_alpha_param`, `qzv96leak_items_extra`"),
    ("Failure 2: qzv96leak", "`test_qzv96leak_alpha.py::test_qzv96leak_alpha_one`, `qzv96leak_matches_no_case`"))

# R4: a row of a KPI-column table whose Tests cell holds an item while its KPI cell begins with no line name the
# reader takes; each beside a readable row, so the README has a map.
_READABLE_ROW = ("Success 1: qzv96leak", "`test_qzv96leak_alpha.py`")
UNREADABLE_ROWS = {
    "failure-without-a-number": rows_readme(_READABLE_ROW, ("Failure: qzv96leak, no number",
                                                            "`test_qzv96leak_second.py`")),
    "success-3a": rows_readme(_READABLE_ROW, ("Success 3a: qzv96leak",
                                              "`test_qzv96leak_second.py::test_qzv96leak_second_fails`")),
    "s8b": rows_readme(_READABLE_ROW, ("S8b qzv96leak", "`qzv96leak_second_fails`")),
    "a-cell-naming-no-line": rows_readme(_READABLE_ROW, ("Edge qzv96leak (names no line)",
                                                         "`test_qzv96leak_second.py`")),
}


def _heading_readme(heading):
    return ("# qzv96leak planted suite\n\nProse of the qzv96leak planted README.\n\n## Success 1: qzv96leak\n\n"
            "| Test |\n|---|\n| `test_qzv96leak_alpha.py` |\n\n"
            f"{heading}\n\n| Test | Notes |\n|---|---|\n| `test_qzv96leak_second.py` | qzv96leak |\n")


# R4: a Tests table with no KPI column under a heading that begins with the word success, failure or KPI (any
# case) but names no line the reader takes; each after a readable heading-form table.
UNREADABLE_HEADINGS = {
    "failure-without-a-number": _heading_readme("### Failure: qzv96leak, no number"),
    "success-word": _heading_readme("## SUCCESS qzv96leak lines"),
    "kpi-word": _heading_readme("#### kpi qzv96leak map"),
}


# --------------------------------------------------------------------------------------------------------------
# The expected result (the design note's §6).
# --------------------------------------------------------------------------------------------------------------

def counts(passed=0, failed=0, skipped=0):
    return {"passed": passed, "failed": failed, "skipped": skipped}


def line(kpi, outcome, passed=0, failed=0, skipped=0):
    return {"kpi": kpi, "outcome": outcome, **counts(passed, failed, skipped)}


def result(outcome, lines, unmapped=None, totals=None, ticket=TICKET_ID):
    return {"ticket": ticket, "outcome": outcome, "error_kind": None, "lines": lines,
            "unmapped": unmapped or counts(), "totals": totals or counts()}


def error_result(kind, ticket=TICKET_ID):
    return {"ticket": ticket, "outcome": "error", "error_kind": kind, "lines": [], "unmapped": counts(),
            "totals": counts()}


ROWS_EXPECTED = result("pass", [
    line("success-1", "pass", 3), line("success-2", "pass", 1), line("success-3", "pass", 1, 0, 1),
    line("success-4", "pass", 1, 0, 1), line("success-5", "pass", 1), line("success-6", "pass", 1),
    line("success-7", "pass", 2), line("success-8", "pass", 2), line("success-9", "pass", 1),
    line("success-10", "pass", 1), line("failure-1", "pass", 1), line("failure-2", "pass", 1),
    line("failure-3", "pass", 1), line("failure-4", "pass", 1), line("failure-5", "pass", 1),
], unmapped=counts(3, 1, 0), totals=counts(12, 1, 1))

HEADINGS_EXPECTED = result("pass", [
    line("success-1", "pass", 3), line("success-2", "pass", 1), line("success-3", "pass", 3),
    line("success-4", "pass", 1, 0, 1), line("failure-1", "pass", 3), line("failure-2", "pass", 1, 0, 1),
    line("failure-3", "pass", 1, 0, 1),
], unmapped=counts(4, 1, 0), totals=counts(12, 1, 1))

FAILS_EXPECTED = result("fail", [
    line("success-1", "pass", 3), line("success-2", "fail", 1, 1), line("success-3", "fail", 0, 1),
    line("success-4", "fail", 0, 1), line("failure-1", "fail", 0, 0, 1), line("failure-2", "fail"),
], unmapped=counts(1), totals=counts(5, 3, 1))

SIMPLE_EXPECTED = result("pass", [line("success-1", "pass", 3)], totals=counts(3))

# Review 1: R1's ALPHA and SECOND_FAILS under SECOND_README; R5's two maps over ITEMS_FILES.
SECOND_FAILS_EXPECTED = result("fail", [line("success-1", "pass", 3), line("success-2", "fail", 0, 1)],
                               totals=counts(3, 1))

ITEMS_COLON_EXPECTED = result("fail", [
    line("success-1", "pass", 1), line("success-2", "fail", 0, 1), line("success-3", "pass", 2),
    line("failure-1", "pass", 3),
], unmapped=counts(1), totals=counts(7, 1))

ITEMS_UNMATCHED_EXPECTED = result("fail", [
    line("success-1", "fail", 3), line("success-2", "fail", 1), line("success-3", "fail", 2),
    line("success-4", "fail", 1), line("failure-1", "pass", 4), line("failure-2", "pass", 1),
], unmapped=counts(1, 1), totals=counts(7, 1))


def projection(found):
    """The keys of the design note's §6 only, so a key of the runner's own is not judged here (the marker is)."""
    if not isinstance(found, dict):
        return found
    out = {key: found.get(key, "<missing>") for key in RESULT_KEYS}
    if isinstance(out["lines"], list):
        out["lines"] = [{key: item.get(key, "<missing>") for key in LINE_KEYS} if isinstance(item, dict) else item
                        for item in out["lines"]]
    for key in ("unmapped", "totals"):
        if isinstance(out[key], dict):
            out[key] = {name: out[key].get(name, "<missing>") for name in COUNT_KEYS}
    return out


# --------------------------------------------------------------------------------------------------------------
# Files, snapshots and processes.
# --------------------------------------------------------------------------------------------------------------

def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_snapshot(top):
    """Every folder, file and link under ``top`` (``.git`` aside), with its mtime, and size and digest for a file."""
    top = Path(top)
    found = {}
    if not top.exists():
        return found
    for dirpath, dirnames, filenames in os.walk(top):
        rel_dir = os.path.relpath(dirpath, top)
        rel_dir = "" if rel_dir == "." else rel_dir
        if rel_dir == "" and ".git" in dirnames:
            dirnames.remove(".git")
        found[(rel_dir or ".") + "/"] = ("dir", os.lstat(dirpath).st_mtime_ns)
        links = [name for name in dirnames if os.path.islink(os.path.join(dirpath, name))]
        for name in filenames + links:
            path = os.path.join(dirpath, name)
            info = os.lstat(path)
            rel = os.path.join(rel_dir, name)
            if stat.S_ISREG(info.st_mode):
                found[rel] = ("file", info.st_size, info.st_mtime_ns, _sha256(path))
            else:
                found[rel] = ("other", info.st_mode, info.st_mtime_ns)
    return found


def changed(before, after):
    """The paths added, removed or changed between two snapshots."""
    return sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))


def everything_under(top):
    """Every path under ``top``, relative, folders included (links not followed)."""
    top = Path(top)
    if not top.exists():
        return []
    out = []
    for dirpath, dirnames, filenames in os.walk(top):
        for name in dirnames + filenames:
            out.append(os.path.relpath(os.path.join(dirpath, name), top))
    return sorted(out)


def files_holding_marker(paths):
    held = []
    for path in paths:
        path = Path(path)
        if path.is_symlink() or not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if MARKER.encode() in data.lower():
            held.append(str(path))
    return held


def pid_gone(pid, wait_s=GONE_WAIT_S):
    """True once ``pid`` is gone or a zombie, within ``wait_s``."""
    deadline = time.monotonic() + wait_s
    while True:
        try:
            state = Path(f"/proc/{int(pid)}/stat").read_text().rsplit(")", 1)[1].split()[0]
        except (OSError, IndexError, ValueError):
            return True
        if state in ("Z", "X"):
            return True
        if time.monotonic() > deadline:
            return False
        time.sleep(0.2)


def kill_quietly(pid, group=False):
    try:
        if group:
            os.killpg(int(pid), signal.SIGKILL)
        elif int(pid) != os.getpid():
            os.kill(int(pid), signal.SIGKILL)
    except (OSError, ValueError):
        pass


def unlock(top):
    """Read, write and execute given back to the owner on ``top`` and everything under it (links not followed), so
    what a planted test locked (review 1, R3) can be measured and removed by pytest's own clean-up."""
    try:
        info = os.lstat(top)
    except OSError:
        return
    if stat.S_ISLNK(info.st_mode):
        return
    is_dir = stat.S_ISDIR(info.st_mode)
    try:
        os.chmod(top, 0o700 if is_dir else 0o600)
    except OSError:
        return
    if is_dir:
        try:
            names = os.listdir(top)
        except OSError:
            return
        for name in names:
            unlock(os.path.join(top, name))


# --------------------------------------------------------------------------------------------------------------
# The planted project and its runs.
# --------------------------------------------------------------------------------------------------------------

def acceptance_block(path):
    return f"acceptance_tests:\n  path: {path}\n  author: independent-test-designer (planted)\n"


DEFAULT_ACCEPTANCE = acceptance_block(FOLDER + "/")


def ticket_text(ticket_id, wbs_id, acceptance):
    """A ticket in the form of ``.tickets/*.md`` (every field the real tickets carry); ``acceptance`` as YAML or None."""
    lines = ["---", f"id: {ticket_id}", "status: in_progress", "deps: []", "links: []",
             "created: 2026-10-31T00:00:00Z", "type: task", "priority: 2", "assignee: engineer",
             f"external-ref: {wbs_id}", "tags: [planted]", f"wbs_id: {wbs_id}",
             f"title: 'A planted ticket for gov accept ({wbs_id})'", "class: implementation",
             "state_class: AUTHORITATIVE", "role: engineer", "depends_on: []", "allowed_paths:", "- src/planted/**",
             "kpis:", "  success:", "  - 'the planted success line'", "  failure:", "  - 'the planted failure line'",
             "profile: LITE", "sources:", "- DEC-959", "est_loc: 10"]
    if acceptance is not None:
        lines += acceptance.rstrip("\n").splitlines()
    lines += ["track: A", "list_rows: []", "---", f"# {wbs_id} A planted ticket", ""]
    return "\n".join(lines)


def _git_env(home):
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "GIT_CONFIG_NOSYSTEM": "1",
            "LC_ALL": "C.UTF-8"}


def _git(root, home, *args):
    command = ["git", "-c", "user.name=W2-96 test designer", "-c", "user.email=td@example.invalid",
               "-c", "init.defaultBranch=main", "-c", "commit.gpgsign=false", *args]
    subprocess.run(command, cwd=root, env=_git_env(home), check=True, capture_output=True, stdin=subprocess.DEVNULL)


class Project:
    """A planted project under ``base``: ``project/`` (the repository), and beside it ``home/``, ``probe/``,
    ``decoy/``, ``elsewhere/`` (an empty folder to run from), ``outside/`` (a folder outside the root, when asked)
    and one fresh ``given-tmp-<n>/`` per run."""

    def __init__(self, base, files, readme, *, acceptance=DEFAULT_ACCEPTANCE, outside=None, root_files=None):
        self.base = Path(base)
        self.root = self.base / "project"
        self.home = self.base / "home"
        self.probe = self.base / "probe"
        self.decoy = self.base / "decoy"
        self.elsewhere = self.base / "elsewhere"
        self.runs = 0
        self._build(files, readme, acceptance, outside, root_files or {})

    def _fill(self, text):
        return text.replace("@PROBE@", repr(str(self.probe))).replace("@ROOT@", str(self.root))

    def _folder(self, folder, files, readme):
        folder.mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            write(folder / name, self._fill(text))
        if readme is not None:
            write(folder / "README.md", readme)

    def _build(self, files, readme, acceptance, outside, root_files):
        for folder in (self.root, self.home, self.probe, self.decoy, self.elsewhere):
            folder.mkdir(parents=True)
        userbase = Path(site.getuserbase())
        if userbase.is_dir():
            (self.home / ".local").symlink_to(userbase, target_is_directory=True)
        write(self.decoy / "qzv96leak_lib.py", 'TREE_VALUE = "qzv96leak-decoy-tree"\n')
        write(self.root / "src" / "qzv96leak_lib.py",
              '"""qzv96leak planted library of the planted tree."""\nTREE_VALUE = "qzv96leak-planted-tree"\n')
        write(self.root / "pyproject.toml", '[project]\nname = "planted-w9"\nversion = "0.0.1"\n')
        write(self.root / ".gitignore", "__pycache__/\n*.pyc\n.pytest_cache/\n")
        write(self.root / ".tickets" / f"{TICKET_ID}.md", ticket_text(TICKET_ID, WBS_ID, acceptance))
        write(self.root / ".tickets" / f"{OTHER_ID}.md",
              ticket_text(OTHER_ID, OTHER_WBS, acceptance_block(OTHER_FOLDER + "/")))
        self._folder(self.root / FOLDER, files, readme)
        self._folder(self.root / OTHER_FOLDER, OTHER_FILES, OTHER_README)
        if outside is not None:
            self._folder(self.base / "outside", *outside)
        for rel, text in root_files.items():
            write(self.root / rel, self._fill(text))
        _git(self.root, self.home, "init", "-q")
        _git(self.root, self.home, "add", "-A")
        _git(self.root, self.home, "commit", "-q", "-m", "the planted project")

    def env(self, tmpdir):
        user = getpass.getuser()
        return {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.home),
            "USER": user,
            "LOGNAME": user,
            "TMPDIR": str(tmpdir),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONPATH": os.pathsep.join([str(SRC), str(self.decoy)]),   # DEC-732; the decoy after
            "PYTHONUSERBASE": site.getuserbase(),                          # where pytest and its plugins are
        }

    def records(self, kind=None):
        found = []
        for path in sorted(self.probe.glob("*.json")):
            try:
                found.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        return [record for record in found if kind is None or record.get("kind") == kind]

    def ran(self):
        """How many times each planted function's body ran in the last run."""
        tally = {}
        for record in self.records("ran"):
            tally[record["name"]] = tally.get(record["name"], 0) + 1
        return tally

    def kill_recorded(self):
        for record in self.records():
            for key in ("pid", "grandchild"):
                if record.get(key):
                    kill_quietly(record[key])

    def _clear_probe(self):
        for path in self.probe.iterdir():
            path.unlink()

    def _prepare(self, args, json_mode, cwd):
        self.runs += 1
        tmpdir = self.base / f"given-tmp-{self.runs}"
        tmpdir.mkdir()
        self._clear_probe()
        workdir = Path(cwd) if cwd else self.root
        command = [sys.executable, "-m", "gov.cli.main", "accept", *args] + (["--json"] if json_mode else [])
        watched = {"project": self.root}
        if workdir != self.root:
            watched["cwd"] = workdir
        return tmpdir, workdir, command, watched

    def _popen(self, command, workdir, tmpdir):
        return subprocess.Popen(command, cwd=workdir, env=self.env(tmpdir), stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                                errors="replace", start_new_session=True)

    def run(self, *args, json_mode=True, cwd=None, timeout=RUN_TIMEOUT_S):
        """``gov accept <args>`` (``--json`` unless ``json_mode`` is false), from the root or ``cwd``."""
        tmpdir, workdir, command, watched = self._prepare(args, json_mode, cwd)
        before = {name: tree_snapshot(path) for name, path in watched.items()}
        started = time.monotonic()
        process = self._popen(command, workdir, tmpdir)
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            kill_quietly(process.pid, group=True)
            self.kill_recorded()
            stdout, stderr = process.communicate()
            raise AssertionError(f"gov accept did not end within {timeout:.0f} s: {command}\n"
                                 f"stdout: {stdout[-2000:]}\nstderr: {stderr[-2000:]}") from None
        elapsed = time.monotonic() - started
        after = {name: tree_snapshot(path) for name, path in watched.items()}
        return Run(self, command, process.returncode, stdout, stderr, tmpdir, watched, before, after, elapsed)

    def start(self, *args, json_mode=True):
        """``gov accept <args>`` started, not waited for (the interrupt case)."""
        tmpdir, workdir, command, watched = self._prepare(args, json_mode, None)
        before = {name: tree_snapshot(path) for name, path in watched.items()}
        return Started(self, command, self._popen(command, workdir, tmpdir), tmpdir, watched, before)

    def raw_pytest(self, python_path=None, timeout=RUN_TIMEOUT_S, basetemp=True):
        """Raw pytest on the planted folder, outside ``gov accept`` (the premises): its run and its outcomes.
        ``basetemp`` false runs it without ``--basetemp`` (pytest's own base folder, under the run's TMPDIR)."""
        self.runs += 1
        raw = self.base / f"raw-{self.runs}"
        (raw / "tmp").mkdir(parents=True)
        self._clear_probe()
        report = raw / "report.xml"
        env = {**self.env(raw / "tmp"), "PYTHONPATH": python_path or str(self.root / "src"),
               "PYTHONDONTWRITEBYTECODE": "1"}
        command = [sys.executable, "-m", "pytest", FOLDER, "-rA", "-p", "no:cacheprovider",
                   *(["--basetemp", str(raw / "basetemp")] if basetemp else []),
                   "--junitxml", str(report), "-o", "junit_family=xunit2"]
        done = subprocess.run(command, cwd=self.root, env=env, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout, stdin=subprocess.DEVNULL, start_new_session=True)
        return done, (junit_outcomes(report) if report.is_file() else None)


def junit_outcomes(report):
    """``{module::name[id]: passed|failed|skipped}`` from a JUnit XML report; an error counts as failed."""
    outcomes = {}
    for case in ElementTree.parse(report).iter("testcase"):
        tags = {child.tag for child in case}
        outcome = "failed" if tags & {"failure", "error"} else "skipped" if "skipped" in tags else "passed"
        key = f"{case.get('classname', '').rsplit('.', 1)[-1]}::{case.get('name')}"
        if outcomes.get(key) != "failed":
            outcomes[key] = outcome
    return outcomes


class Run:
    """One finished run of ``gov accept``: its output, exit code, the given ``TMPDIR``, and the watched folders."""

    def __init__(self, project, command, returncode, stdout, stderr, tmpdir, watched, before, after, elapsed):
        self.project, self.command, self.returncode = project, command, returncode
        self.stdout, self.stderr, self.tmpdir = stdout or "", stderr or "", tmpdir
        self.watched, self.before, self.after, self.elapsed = watched, before, after, elapsed

    def describe(self):
        return (f"command: {' '.join(self.command[2:])}\nexit code: {self.returncode}\n"
                f"stdout: {self.stdout[-3000:]}\nstderr: {self.stderr[-3000:]}")

    def envelope(self):
        """The API-0002 envelope on stdout; an AssertionError naming the output when there is none."""
        try:
            envelope = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"gov accept gave no API-0002 envelope on stdout\n{self.describe()}") from None
        assert isinstance(envelope, dict) and {"ok", "command", "result", "session"} <= set(envelope), \
            f"not an API-0002 envelope\n{self.describe()}"
        assert envelope["command"] == "accept", f"the envelope names another command\n{self.describe()}"
        return envelope

    def changes(self):
        """What changed in the watched folders (the project, and the working folder when it is another)."""
        return {name: changed(self.before[name], self.after[name]) for name in self.watched
                if changed(self.before[name], self.after[name])}

    def problems(self, generic=True):
        """Every way the run broke KPI 2 or KPI 5's rules on what it may show and leave."""
        found = []
        for channel, text in (("stdout", self.stdout), ("stderr", self.stderr)):
            low = text.lower()
            if MARKER in low:
                found.append(f"{channel} holds the marker {MARKER!r}")
            for word in GENERIC_PROBES if generic else ():
                if word in low:
                    found.append(f"{channel} holds {word!r}")
        scanned = [self.watched[name] / rel for name, rels in self.changes().items() for rel in rels]
        scanned += [self.tmpdir / rel for rel in everything_under(self.tmpdir)]
        scanned += [self.project.home / rel for rel in everything_under(self.project.home)]
        for path in files_holding_marker(scanned):
            found.append(f"a file left behind holds the marker: {path}")
        left = everything_under(self.tmpdir)
        if left:
            found.append(f"the given TMPDIR holds {len(left)} entries after the run: {left[:8]}")
        for name, paths in self.changes().items():
            found.append(f"the {name} folder changed ({len(paths)} paths): {paths[:8]}")
        return found


class Started:
    """A run of ``gov accept`` still going (the interrupt case)."""

    def __init__(self, project, command, process, tmpdir, watched, before):
        self.project, self.command, self.process = project, command, process
        self.tmpdir, self.watched, self.before = tmpdir, watched, before
        self.started = time.monotonic()

    def wait_for(self, kind, wait_s):
        """The first probe record of ``kind``; an AssertionError if gov ends first or ``wait_s`` passes."""
        deadline = time.monotonic() + wait_s
        while time.monotonic() < deadline:
            records = self.project.records(kind)
            if records:
                return records[0]
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                raise AssertionError(f"gov accept ended (exit code {self.process.returncode}) before a planted "
                                     f"test recorded {kind!r}\nstdout: {stdout[-2000:]}\nstderr: {stderr[-2000:]}")
            time.sleep(0.2)
        raise AssertionError(f"no planted test recorded {kind!r} within {wait_s:.0f} s")

    def interrupt(self, wait_s=60.0):
        """SIGINT to gov alone, then the finished run."""
        return self.send(signal.SIGINT, wait_s)

    def send(self, signum, wait_s=60.0):
        """``signum`` to gov alone (not its process group), then the finished run (review 1, R2)."""
        os.kill(self.process.pid, signum)
        try:
            stdout, stderr = self.process.communicate(timeout=wait_s)
        except subprocess.TimeoutExpired:
            self.stop()
            raise AssertionError(f"gov accept did not end within {wait_s:.0f} s of signal {int(signum)}") from None
        after = {name: tree_snapshot(path) for name, path in self.watched.items()}
        return Run(self.project, self.command, self.process.returncode, stdout, stderr, self.tmpdir, self.watched,
                   self.before, after, time.monotonic() - self.started)

    def stop(self):
        """Whatever is left of the run killed: gov's process group and every recorded planted process."""
        kill_quietly(self.process.pid, group=True)
        self.project.kill_recorded()
        try:
            self.process.communicate(timeout=30)
        except (subprocess.TimeoutExpired, ValueError, OSError):
            pass


# --------------------------------------------------------------------------------------------------------------
# Assertions every case shares.
# --------------------------------------------------------------------------------------------------------------

def assert_outcome(run, expected, exit_code):
    """The envelope's ``ok: true``, its result as expected (the §6 keys), then the exit code."""
    envelope = run.envelope()
    assert envelope["ok"] is True, f"ok is not true for a run that ended in a result\n{run.describe()}"
    got = projection(envelope["result"])
    assert got == expected, (f"the result is not the expected one\nexpected: {json.dumps(expected)}\n"
                             f"got:      {json.dumps(got)}\n{run.describe()}")
    assert run.returncode == exit_code, f"exit code {run.returncode}, expected {exit_code}\n{run.describe()}"
    return envelope["result"]


def assert_refusal(run, code):
    """The envelope's ``ok: false`` with ``error.code`` ``code``, and exit code 1."""
    envelope = run.envelope()
    assert envelope["ok"] is False, f"a refusal must answer ok: false\n{run.describe()}"
    error = envelope.get("error")
    assert isinstance(error, dict) and error.get("code") == code, f"expected error code {code}\n{run.describe()}"
    assert run.returncode == EXIT_REFUSED, f"exit code {run.returncode}, expected 1\n{run.describe()}"
    return error


def assert_clean(run, generic=True):
    """Nothing of the tests' content anywhere, nothing left in the TMPDIR, nothing written in the project."""
    problems = run.problems(generic=generic)
    assert not problems, "\n".join(problems) + "\n" + run.describe()


def assert_no_raw_output(run):
    """No word of pytest's raw report in stdout or stderr (a refusal never falls back to raw output)."""
    found = [word for word in RAW_OUTPUT_WORDS if word in run.stdout + run.stderr]
    assert not found, f"raw pytest output reached the caller ({found})\n{run.describe()}"


def text_problems(text, expected):
    """How the text output disagrees with the expected result. The command line prints a dict ``result`` as JSON;
    a text form of the runner's own is read line by line: each KPI line on a line with its outcome and counts."""
    try:
        parsed = json.loads(text)
    except ValueError:
        parsed = None
    if isinstance(parsed, dict):
        return [] if projection(parsed) == expected else [f"the printed result differs: {json.dumps(parsed)}"]
    problems = []
    low = text.lower()
    if expected["outcome"] not in low:
        problems.append(f"the outcome {expected['outcome']!r} is not in the text")
    if expected["error_kind"] and expected["error_kind"] not in low:
        problems.append(f"the error kind {expected['error_kind']!r} is not in the text")
    rows, start = text.splitlines(), 0
    for item in expected["lines"]:
        pattern = re.compile(rf"(?<![\w-]){re.escape(item['kpi'])}(?![\w-])")
        index = next((i for i in range(start, len(rows)) if pattern.search(rows[i])), None)
        if index is None:
            problems.append(f"{item['kpi']} is not in the text, in order")
            continue
        start = index + 1
        rest = pattern.sub(" ", rows[index]).lower()
        numbers = re.findall(r"\d+", rest)
        if item["outcome"] not in rest or str(item["passed"]) not in numbers or str(item["failed"]) not in numbers:
            problems.append(f"the line of {item['kpi']} lacks its outcome or counts: {rows[index]!r}")
    if not expected["lines"] and re.search(r"(success|failure)-\d", low):
        problems.append("a run error's text names a KPI line")
    return problems


# --------------------------------------------------------------------------------------------------------------
# The README map form (the design note's §1), for this folder's own README (a premise).
# --------------------------------------------------------------------------------------------------------------

# A number followed by a letter, digit or underscore is no line name (review 1, R4: ``Success 3a``, ``S8b``).
_NAME = re.compile(r"(success|failure|kpi|s|k|f)\s*(\d+)(?!\w)", re.IGNORECASE)
_SEPARATOR = re.compile(r"\s*(?:/|,|;|\band\b)\s*", re.IGNORECASE)


def line_names(text):
    """The KPI lines named at the start of ``text``, in the normal form (``success-1``, ``failure-2``)."""
    names, text = [], text.strip()
    match = _NAME.match(text)
    while match:
        word = match.group(1).lower()
        names.append(("failure" if word in ("failure", "f") else "success") + f"-{int(match.group(2))}")
        separator = _SEPARATOR.match(text, match.end())
        match = _NAME.match(text, separator.end()) if separator else None
    return names


def test_functions(path):
    """The names of the module-level test functions of a test file (read with ``ast``, never imported)."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    return {node.name for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test")}


def markdown_tables(text):
    """Each Markdown table of ``text`` as ``(header cells, body rows)``."""
    def cells(row):
        row = row.strip()
        row = row[1:] if row.startswith("|") else row
        row = row[:-1] if row.endswith("|") else row
        return [cell.strip() for cell in row.split("|")]

    rows, tables, index = text.splitlines(), [], 0
    while index < len(rows):
        if rows[index].lstrip().startswith("|") and index + 1 < len(rows) \
                and re.match(r"^\s*\|?\s*:?-{3,}", rows[index + 1]):
            header, body, index = cells(rows[index]), [], index + 2
            while index < len(rows) and rows[index].lstrip().startswith("|"):
                body.append(cells(rows[index]))
                index += 1
            tables.append((header, body))
        else:
            index += 1
    return tables
