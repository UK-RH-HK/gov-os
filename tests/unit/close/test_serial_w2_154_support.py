"""Support of W2-154's acceptance tests (DAEO-l4gf): a planted project for the close's serial plugin, and a planted
folder for ``nightly.sh`` run only through its stub seam (the Interface's I4). It holds no test.

The planted project (under ``tmp_path``) has its own ``tests/conftest.py`` whose opt-in mechanism is modelled on the
real one (``tests/conftest.py``: ``--optin=<name>`` or ``GOV_TESTS_OPTIN``, every ``tests/optin-lifted*.txt`` names
cases a run leaves out unless it opts in; they are *deselected*, reported through ``pytest_deselected``, never skipped).
The serial-only list names four entries, and every one is a different situation:

- ``A`` (``tests/unit/test_a.py``): every case of it is left out by the opt-in list;
- ``B`` (``tests/unit/test_empty.py``): a file with no case at all, which no opt-in list explains;
- ``C`` (``tests/unit/test_c.py``): one case, run by every run;
- ``D`` (``tests/unit/test_d.py``): two cases, one of them left out by the opt-in list.

Each case of the project appends its name and whether it ran in a worker of the parallel runner to the file
``PLANTED_RAN_LOG``, so a test reads where a case ran, and that it ran nowhere.
"""
from __future__ import annotations

import os
import re
import shlex
import site
import subprocess
import sys
from pathlib import Path

from gov.close.pytest_plugin import gov_close_serial_only as serial_only

A = "tests/unit/test_a.py"
B = "tests/unit/test_empty.py"
C = "tests/unit/test_c.py"
D = "tests/unit/test_d.py"
OPT_IN = "lifted"  # the suite of ``tests/optin-lifted-*.txt`` by the real conftest's rule (no "breadth" in the name)
RAN = "PLANTED_RAN_LOG"
OUT_VARIABLE = "GOV_CLOSE_SERIAL_ONLY_OUT"
NOT_IN_RUN = "gov_close_serial_only: not in this run: "
NO_CASE = "no case is named by the entry"
PLUGIN_FOLDER = Path(serial_only.__file__).resolve().parent

CONFTEST = '''\
"""A planted project's opt-in mechanism, modelled on the real tests/conftest.py (DEC-1061)."""
import os
from pathlib import Path

_TESTS = Path(__file__).resolve().parent


def pytest_addoption(parser):
    parser.addoption("--optin", action="append", default=[], metavar="NAME[,NAME]")


def _opted_in(config):
    given = [*(config.getoption("optin") or []), os.environ.get("GOV_TESTS_OPTIN", "")]
    return {name.strip() for value in given for name in value.split(",") if name.strip()}


def pytest_collection_modifyitems(config, items):
    if "lifted" in _opted_in(config):
        return
    entries = []
    for listing in sorted(_TESTS.glob("optin-lifted*.txt")):
        for raw in listing.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if line:
                entries.append(line)
    left = [item for item in items if any(
        item.nodeid == entry or item.nodeid.startswith((entry + "::", entry + "[")) for entry in entries)]
    if left:
        gone = {id(item) for item in left}
        items[:] = [item for item in items if id(item) not in gone]
        config.hook.pytest_deselected(items=left)
'''

CASE = '''\
import os


def {name}():
    with open(os.environ["PLANTED_RAN_LOG"], "a", encoding="utf-8") as log:
        log.write("{name} worker=" + str("PYTEST_XDIST_WORKER" in os.environ) + "\\n")
'''

FILES = {
    "pytest.ini": "[pytest]\n",
    "tests/conftest.py": CONFTEST,
    # the opt-in list: every case of A, and one case of D (a node id)
    "tests/optin-lifted-w2154.txt": f"{A}  # planted: every case of A\n{D}::test_d_off  # planted: one case of D\n",
    "tests/acceptance/serial-only.txt": "".join(f"{entry}  # serial: latency: planted\n" for entry in (A, B, C, D)),
    A: CASE.format(name="test_a_one") + "\n\n" + CASE.format(name="test_a_two").replace("import os\n\n\n", ""),
    B: "def helper():\n    return 1\n",
    C: CASE.format(name="test_c_one"),
    D: CASE.format(name="test_d_on") + "\n\n" + CASE.format(name="test_d_off").replace("import os\n\n\n", ""),
    "tests/unit/test_other.py": CASE.format(name="test_other_one"),
}


def plant(root: Path, entries: tuple[str, ...] = (A, B, C, D)) -> Path:
    """The planted project at ``root``, its serial-only list holding ``entries``; the project's ``tests/``."""
    for rel, text in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (root / serial_only.LIST_REL).write_text(
        "".join(f"{entry}  # serial: latency: planted\n" for entry in entries), encoding="utf-8")
    return root / "tests"


def clean_environment() -> dict[str, str]:
    """The caller's environment without what would reach into a nested run of the planted project."""
    drop = ("PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTEST_XDIST_WORKER", "PYTEST_XDIST_WORKER_COUNT",
            "PYTEST_XDIST_TESTRUNUID", "PYTEST_CURRENT_TEST", "GOV_TESTS_OPTIN", RAN, OUT_VARIABLE,
            serial_only.ROOT_VARIABLE, serial_only.GIVEN_VARIABLE)
    return {key: value for key, value in os.environ.items() if key not in drop}


class Run:
    """One run of the planted project's test runner: its exit code, its output, the file it was asked to write
    its not-in-this-run entries to and the cases that ran, in order."""

    def __init__(self, process: subprocess.CompletedProcess, out: Path, log: Path):
        self.code = process.returncode
        self.stdout, self.stderr = process.stdout, process.stderr
        self.out, self.log = out, log

    @property
    def text(self) -> str:
        return self.stdout + "\n" + self.stderr

    def not_in_this_run(self) -> list[str]:
        """The entries the run wrote to the file named by ``GOV_CLOSE_SERIAL_ONLY_OUT``, one per line."""
        return self.out.read_text(encoding="utf-8").splitlines() if self.out.is_file() else []

    def ran(self) -> list[str]:
        """Each case that ran, as ``name worker=<bool>``."""
        return self.log.read_text(encoding="utf-8").splitlines() if self.log.is_file() else []

    def describe(self) -> str:
        return (f"exit {self.code}\n--- stdout\n{self.stdout[-1500:]}\n--- stderr\n{self.stderr[-1500:]}\n"
                f"--- out file: {self.not_in_this_run()}\n--- ran: {self.ran()}")


def run_plugin(root: Path, work: Path, *, given: tuple[str, ...] | None = None, optin: str | None = None,
               optin_form: str = "variable", name: str = "run") -> Run:
    """The close's pytest run of the planted project with the plugin, through a real ``python3 -m pytest``.

    ``given`` is the serial-afterwards run: its entries are the arguments of the run and the plugin's
    ``GOV_CLOSE_SERIAL_ONLY_GIVEN``, its ``GOV_CLOSE_SERIAL_ONLY_OUT`` names a file under ``work``, and the run has
    one worker at most. Without ``given`` it is the parallel run of the planted list (``-n 1``).
    ``optin`` opts in to a suite, by ``GOV_TESTS_OPTIN`` or, with ``optin_form="option"``, by ``--optin=``."""
    work.mkdir(parents=True, exist_ok=True)
    out, log = work / f"{name}.out", work / f"{name}.ran"
    env = clean_environment()
    env.update({"PYTHONPATH": str(PLUGIN_FOLDER), serial_only.ROOT_VARIABLE: str(root), RAN: str(log),
                "HOME": str(work), "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONUSERBASE": site.getuserbase()})  # where pytest is installed, whatever ``HOME`` the run has
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "--tb=line",
           "-p", serial_only.PLUGIN]
    if given is not None:
        env.update({serial_only.GIVEN_VARIABLE: "\n".join(given), OUT_VARIABLE: str(out),
                    "PYTEST_XDIST_AUTO_NUM_WORKERS": "1"})
        cmd = [cmd[0], cmd[1], cmd[2], *given, *cmd[3:]]
    else:
        cmd = [cmd[0], cmd[1], cmd[2], "tests", "--ignore", "tests/acceptance", *cmd[3:], "-n", "1"]
    if optin and optin_form == "variable":
        env["GOV_TESTS_OPTIN"] = optin
    if optin and optin_form == "option":
        cmd.append(f"--optin={optin}")
    process = subprocess.run(cmd, cwd=str(root), env=env, capture_output=True, text=True, timeout=240,
                             stdin=subprocess.DEVNULL)
    return Run(process, out, log)


# ---- nightly.sh, run only through its stub (I4) ----------------------------------------------------------------

NIGHTLY_REL = "governance/project/orchestration/nightly"
REPO_ROOT = Path(__file__).resolve().parents[3]
TESTCASE = '<testcase classname="tests.unit.test_planted" name="test_case_{n}" time="0.01"/>'


def serial_xml(cases: int) -> str:
    return ('<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest" errors="0" failures="0" '
            f'skipped="0" tests="{cases}" time="0.1">' + "".join(TESTCASE.format(n=n) for n in range(cases))
            + "</testsuite></testsuites>\n")


def stub_text(clone: Path, *, entries: str, s_exit: int, cases: int | None) -> str:
    """A stub serial phase: it sets ``ENTRIES`` and ``s_exit`` and writes ``$JUNIT/serial.xml`` with ``cases``
    ``<testcase>`` elements (no file at all when ``cases`` is None). It also says where the clone is, so the
    last step (``nightly_alone.py``) reads a planted one, whatever else the script does."""
    lines = ['mkdir -p "$JUNIT"', f"ENTRIES={shlex.quote(entries)}", f"s_exit={s_exit}", f"CLONE={shlex.quote(str(clone))}"]
    if cases is not None:
        lines.append(f"cat > \"$JUNIT/serial.xml\" <<'XML'\n{serial_xml(cases)}XML")
    return "\n".join(lines) + "\n"


class Night:
    """One stubbed run of ``nightly.sh`` on a copy of the script whose every path is under ``work``."""

    def __init__(self, process: subprocess.CompletedProcess, work: Path):
        self.code = process.returncode
        self.stdout, self.stderr = process.stdout, process.stderr
        self.work = work
        found = sorted((work / "orch" / "log" / "nightly").glob("20*/run.txt"))
        self.run_txt = found[-1].read_text(encoding="utf-8") if found else ""
        digest = work / "orch" / "log" / "nightly" / "digest.txt"
        self.digest = digest.read_text(encoding="utf-8") if digest.is_file() else ""
        pings = work / "pings.txt"
        self.pings = pings.read_text(encoding="utf-8").splitlines() if pings.is_file() else []

    @property
    def lines(self) -> list[str]:
        return self.run_txt.splitlines()

    def verdict(self) -> str | None:
        """The night's verdict: the last line of ``run.txt`` that begins ``verdict:`` (as ``nightly.sh`` takes it)."""
        found = [line for line in self.lines if line.startswith("verdict:")]
        return found[-1].strip() if found else None

    def stated(self, pattern: str) -> list[str]:
        return [line for line in self.lines if re.match(pattern, line)]

    def describe(self) -> str:
        return (f"exit {self.code}\n--- run.txt\n{self.run_txt[-2500:]}\n--- stdout\n{self.stdout[-800:]}\n"
                f"--- stderr\n{self.stderr[-800:]}\n--- pings: {self.pings}")


def _rewrite(text: str, work: Path) -> str:
    """The script with its own paths replaced by ``work``'s, as ``test_nightly.sh`` does with ``sed``: every line
    that begins ``ORCH=``, ``REPO=``, ``RUNS=``, ``JUNIT=`` or ``PING=``, and the night window's end (far off)."""
    for name, value in (("ORCH", work / "orch"), ("REPO", work / "repo"), ("RUNS", work / "runs"),
                        ("JUNIT", work / "junit"), ("PING", work / "ping")):
        text, count = re.subn(rf"^{name}=.*$", lambda _m, n=name, v=value: f"{n}={shlex.quote(str(v))}", text,
                              flags=re.MULTILINE)
        assert count == 1, f"nightly.sh no longer has exactly one line beginning {name}= (found {count})"
    text, count = re.subn(r"^  window_end=.*$", "  window_end=$(( $(date +%s) + 99999 ))", text, flags=re.MULTILINE)
    assert count == 1, f"nightly.sh no longer has exactly one line beginning '  window_end=' (found {count})"
    return text


def run_nightly(work: Path, *, entries: str, s_exit: int, cases: int | None) -> Night:
    """``nightly.sh night`` on a copy in ``work`` with its seam: ``NIGHTLY_SERIAL_STUB`` names a stub serial phase.

    The copy's folder holds the real ``nightly_alone.py``, a fake estimate (it records nothing) and a fake disk gate;
    the ping is a script that writes its message to ``work/pings.txt``; the repository is a planted one, clean, whose
    head is old, so a night's start conditions hold. Every path of the copy is under ``work``: the real logs, the
    real digest and the real estimate history are never touched, and nothing here starts a suite. A run that does
    not honour the seam stops at a place the copy has no stores for (the secrets switch), long before any suite."""
    work.mkdir(parents=True, exist_ok=True)
    folder, clone, repo = work / "n", work / "clone", work / "repo"
    folder.mkdir()
    (clone / "governance" / "project").mkdir(parents=True)
    (clone / "governance" / "project" / "path-map.yaml").write_text("accepted_reds: []\n", encoding="utf-8")
    source = REPO_ROOT / NIGHTLY_REL
    script = folder / "nightly.sh"
    script.write_text(_rewrite((source / "nightly.sh").read_text(encoding="utf-8"), work), encoding="utf-8")
    (folder / "nightly_alone.py").write_text((source / "nightly_alone.py").read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "nightly_estimate.py").write_text(
        "import sys\nif sys.argv[1:2] == ['estimate']:\n    print('{\"estimate_s\": 600}')\n", encoding="utf-8")
    (folder / "disk_gate.sh").write_text("exit 0\n", encoding="utf-8")
    ping = work / "ping"
    ping.write_text(f'#!/bin/bash\necho "$*" >> {shlex.quote(str(work / "pings.txt"))}\n', encoding="utf-8")
    ping.chmod(0o755)
    (work / "orch" / "log" / "nightly").mkdir(parents=True)
    (work / "runs").mkdir()
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    subprocess.run(["git", "init", "-q", "-b", "w2/integrate", str(repo)], check=True, capture_output=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", "old"], check=True,
                   capture_output=True, env={**os.environ, "GIT_COMMITTER_DATE": "2026-10-01T00:00:00",
                                             "GIT_AUTHOR_DATE": "2026-10-01T00:00:00"})
    stub = work / "stub.sh"
    stub.write_text(stub_text(clone, entries=entries, s_exit=s_exit, cases=cases), encoding="utf-8")

    env = {key: value for key, value in os.environ.items() if not key.startswith("NIGHTLY_")
           and key not in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")}
    env.update({"NIGHTLY_SERIAL_STUB": str(stub), "HOME": str(work), "TMPDIR": str(work),
                "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")})
    assert "NIGHTLY_SERIAL_STUB" in env and stub.is_file(), "a case of this file never runs nightly.sh without its stub"
    process = subprocess.run(["bash", str(script), "night"], cwd=str(clone), env=env, capture_output=True,
                             text=True, timeout=90, stdin=subprocess.DEVNULL)
    return Night(process, work)
