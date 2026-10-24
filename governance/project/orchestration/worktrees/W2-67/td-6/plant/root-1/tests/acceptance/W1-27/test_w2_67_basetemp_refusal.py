"""W2-67 (DAEO-9nys), KPI 6: the root ``tests/conftest.py`` refuses a run given a per-run ``--basetemp``.

The KPI line (DEC-907 item 2, DEC-898): *the root tests/conftest.py refuses, at the start, a run given a per-run
--basetemp, naming DEC-898; one opt-out stays, the environment flag GOV_ALLOW_BASETEMP=1, for a measured trial.*

What is observed, from outside only: a nested pytest run of this repository's configuration (its root folder, so a
root ``tests/conftest.py`` is loaded) on one tiny probe case of its own, ``w2_67_basetemp_probe.py``, which a run of
``tests`` does not collect. The probe records the temp folder pytest gave it.

- **A run given ``--basetemp``** (``--basetemp=<dir>``, ``--basetemp <dir>``, through ``PYTEST_ADDOPTS``, and with
  ``-n 2``) is refused at the start: a non-zero exit, no test run, its output names DEC-898, and the folder it was
  given receives no test's temp folder.
- **``GOV_ALLOW_BASETEMP=1``** lets the same run go ahead in the folder it was given; any other value opens nothing.
- **A run given no ``--basetemp``** is not refused, also in parallel (``-n 2``): xdist gives each worker a base
  folder of its own, and the refusal must never stop the suite's own parallel runs.

Every nested run is bounded: the one probe case, one worker (two in the parallel cases), its own ``TMPDIR`` inside
the case's ``tmp_path``, ``-p no:cacheprovider``, a time limit, and a ``--basetemp`` inside the case's ``tmp_path``.
Its environment drops every ``PYTEST_*`` variable and the flag of the session that runs the case. The code under
test is this worktree's (DEC-732): the nested run's ``PYTHONPATH`` is its ``src/``.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PROBE = Path(__file__).resolve().with_name("w2_67_basetemp_probe.py")
RECORD_VARIABLE = "W2_67_BASETEMP_PROBE_RECORD"   # the probe's own name for its record file
FLAG = "GOV_ALLOW_BASETEMP"
DECISION = "DEC-898"
RUN_TIMEOUT_S = 180   # a wait under load for one tiny case, not a time the ticket promises


@dataclass(frozen=True)
class Nested:
    command: tuple
    addopts: str | None
    flag: str | None
    returncode: int
    output: str
    ran: tuple          # the temp folders the probe recorded, one per test run
    given: Path         # the --basetemp the case gave, used or not
    tmpdir: Path        # the run's own TMPDIR

    def describe(self):
        return (f"command: {' '.join(self.command)}\nPYTEST_ADDOPTS: {self.addopts!r}\n{FLAG}: {self.flag!r}\n"
                f"exit code: {self.returncode}\ntests run (temp folders recorded): {list(self.ran) or 'none'}\n"
                f"output (last 1500 characters):\n{self.output[-1500:]}")


def nested_run(tmp_path, args=(), addopts=None, flag=None):
    """Run the probe in a nested pytest of this repository; ``flag`` is the value of GOV_ALLOW_BASETEMP, if set."""
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    record = tmp_path / "probe-record.txt"
    env = {key: value for key, value in os.environ.items() if not key.startswith("PYTEST_") and key != FLAG}
    env.update({
        "TMPDIR": str(tmpdir),
        "PYTHONPATH": str(REPO_ROOT / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
        RECORD_VARIABLE: str(record),
    })
    if addopts is not None:
        env["PYTEST_ADDOPTS"] = addopts
    if flag is not None:
        env[FLAG] = flag
    command = (sys.executable, "-m", "pytest", str(PROBE.relative_to(REPO_ROOT)), "-q", "-p", "no:cacheprovider",
               f"--rootdir={REPO_ROOT}", *args)
    try:
        done = subprocess.run(command, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
                              timeout=RUN_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the nested run did not end within {RUN_TIMEOUT_S} s: {' '.join(command)}") from None
    ran = tuple(line for line in record.read_text(encoding="utf-8").splitlines() if line) if record.is_file() else ()
    return Nested(command, addopts, flag, done.returncode, done.stdout + done.stderr, ran,
                  tmp_path / "given-basetemp", tmpdir)


def under(path, folder):
    return Path(path).resolve().is_relative_to(Path(folder).resolve())


# Each ordinary way of giving a per-run --basetemp: case id -> (extra arguments, PYTEST_ADDOPTS) for the given folder.
FORMS = {
    "equals": lambda given: ((f"--basetemp={given.parent}",), None),
    "separate": lambda given: (("--basetemp", str(given)), None),
    "PYTEST_ADDOPTS": lambda given: ((), f"--basetemp={given}"),
    "parallel-n2": lambda given: (("-n", "2", f"--basetemp={given}"), None),
}
SERIAL_FORMS = ("equals", "separate", "PYTEST_ADDOPTS")


def given_run(tmp_path, form, flag=None):
    args, addopts = FORMS[form](tmp_path / "given-basetemp")
    return nested_run(tmp_path, args=args, addopts=addopts, flag=flag)


def refusal_problems(run):
    """What a refused run shows, as a list of what this run lacks; empty when it was refused as the KPI says."""
    problems = []
    if run.returncode == 0:
        problems.append("it ended with exit code 0, not a refusal")
    if run.ran:
        problems.append(f"it ran the probe case ({len(run.ran)} time(s)): the refusal did not come at the start")
    if DECISION not in run.output:
        problems.append(f"its output does not name {DECISION}")
    if run.given.exists() and any(run.given.iterdir()):
        problems.append(f"the folder it was given received {sorted(p.name for p in run.given.iterdir())}")
    return problems


@pytest.mark.parametrize("form", list(FORMS))
def test_a_run_given_a_per_run_basetemp_is_refused_at_the_start(tmp_path, form):
    run = given_run(tmp_path, form)
    problems = refusal_problems(run)
    assert not problems, (f"a run given a per-run --basetemp ({form}) is not refused at the start as DEC-907 item 2 "
                          f"says: " + "; ".join(problems) + f"\n{run.describe()}")


@pytest.mark.parametrize("form", SERIAL_FORMS)
def test_gov_allow_basetemp_1_lets_the_run_use_the_folder_it_was_given(tmp_path, form):
    run = given_run(tmp_path, form, flag="1")
    assert run.returncode == 0, f"with {FLAG}=1 the run given --basetemp ({form}) did not succeed\n{run.describe()}"
    assert len(run.ran) == 1, f"with {FLAG}=1 the probe case did not run once\n{run.describe()}"
    assert under(run.ran[0], run.given), \
        f"with {FLAG}=1 the probe's temp folder is not inside the --basetemp it was given\n{run.describe()}"


@pytest.mark.parametrize("value", ["0", "true", "yes", ""], ids=["0", "true", "yes", "empty"])
def test_a_flag_value_other_than_1_opens_nothing(tmp_path, value):
    run = given_run(tmp_path, "equals", flag=value)
    problems = refusal_problems(run)
    assert not problems, (f"{FLAG}={value!r} opened the refusal of a per-run --basetemp, which only {FLAG}=1 opens: "
                          + "; ".join(problems) + f"\n{run.describe()}")


def test_a_run_given_no_basetemp_is_not_refused(tmp_path):
    run = nested_run(tmp_path)
    assert run.returncode == 0, f"a run given no --basetemp did not succeed\n{run.describe()}"
    assert len(run.ran) == 1, f"a run given no --basetemp did not run the probe case once\n{run.describe()}"
    assert under(run.ran[0], run.tmpdir), \
        f"the probe's temp folder is not in pytest's own base folder under the run's TMPDIR\n{run.describe()}"


def test_a_parallel_run_given_no_basetemp_is_not_refused(tmp_path):
    """xdist gives each worker a base folder of its own; that must not count as a per-run --basetemp."""
    run = nested_run(tmp_path, args=("-n", "2"))
    assert run.returncode == 0, f"a parallel run (-n 2) given no --basetemp did not succeed\n{run.describe()}"
    assert len(run.ran) == 1, f"a parallel run given no --basetemp did not run the probe case once\n{run.describe()}"
    assert under(run.ran[0], run.tmpdir), \
        f"the worker's temp folder is not in pytest's own base folder under the run's TMPDIR\n{run.describe()}"
