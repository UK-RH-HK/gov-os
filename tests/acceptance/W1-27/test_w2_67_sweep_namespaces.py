"""W2-67, KPI 4 (DEC-898), batch 5: the clean-up of old base folders across PID namespaces.

The finding (the round's review, described, DEC-136): every run of the suites removes, at its end, older pytest base
folders under the same ``pytest-of-<user>`` folder that are past pytest's retention of three and whose run it judges
to be over. In a sandboxed session each Bash command runs in a PID namespace of its own (its first process is pid 3),
while the commands share one ``TMPDIR``: a pid read from another run's ``.lock`` names another namespace's process.

What must hold:

- **A base folder whose run is still going is kept** by every other run's clean-up, whatever PID namespace that run
  is in, whether or not it loads the root ``tests/conftest.py``, at any point of the run from the moment its base
  folder exists, and under any retention policy the sweeping run is given.
- **The base folder of a killed run of the suites is removed** by a later run's clean-up once it is past the
  retention of three, whatever pid the later run has in its own namespace, so a full run still leaves at most three
  base folders behind. A killed run that did not load the root conftest (a foreign run) may be kept: pytest's own
  rule removes it after three days; no case here asks for its removal.
- **Nothing outside pytest's own numbered base folders is removed.**

How the namespaces are laid out: each run is started by ``unshare --user --map-current-user --pid --fork
--mount-proc --kill-child`` (a PID namespace and a ``/proc`` of its own, as the sandbox gives each Bash command), with
``w2_67_ns_launch.py`` as its pid 1, which starts the run as the pid the case asks. A live run is held live by the
probe waiting for a release file the case writes; nothing waits on a sleep that races. Every run shares the case's
own ``TMPDIR`` (inside its ``tmp_path``), is bounded (one tiny case, one worker, a time limit) and is ended before the
case ends: the launcher is pid 1, so killing its ``unshare`` ends the whole namespace.
"""

from __future__ import annotations

import getpass
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
PROBE = HERE / "w2_67_ns_probe.py"
LAUNCH = HERE / "w2_67_ns_launch.py"
UNSHARE = ("unshare", "--user", "--map-current-user", "--pid", "--fork", "--mount-proc", "--kill-child")
FIRST_PID = 3                 # a sandboxed Bash command's first process
KEEP = 3                      # pytest's own retention (tmp_path_retention_count's default)
RUN_TIMEOUT_S = 180           # a wait under load for one tiny case, not a time the ticket promises
READY_TIMEOUT_S = 120
FLAG = "GOV_ALLOW_BASETEMP"
NUMBERED = re.compile(r"^pytest-(\d+)$")

# A small project of its own, which never loads this repository's conftest. Its one case makes its temp folder,
# says so, waits for the release, and fails if its temp folder vanished meanwhile.
HELD_CASE = '''\
import os
import time
from pathlib import Path

READY = Path({ready!r})
RELEASE = Path({release!r})


def test_held(tmp_path, tmp_path_factory):
    (tmp_path / "held.txt").write_text("held\\n", encoding="utf-8")
    part = Path(str(READY) + ".part")
    part.write_text(str(tmp_path_factory.getbasetemp()) + "\\n", encoding="utf-8")
    os.replace(part, READY)
    deadline = time.monotonic() + 150
    while not RELEASE.exists():
        assert time.monotonic() < deadline, "no release within 150 s"
        time.sleep(0.05)
    assert (tmp_path / "held.txt").is_file(), f"the run's temp folder {{tmp_path}} vanished while the run was going"
'''

# gov close's own test runner on the small project, one worker, as the unit close tests call it (this worktree's code).
CLOSE_DRIVER = '''\
import json, sys
from pathlib import Path
from gov.close.command import _run_tests
root = Path(sys.argv[1])
findings, counts = _run_tests(root, root / "tests", int(sys.argv[2]), workers=1)
print(json.dumps({"findings": findings, "counts": counts}))
sys.exit(1 if findings else 0)
'''


# --------------------------------------------------------------------------
# The layout: runs in PID namespaces of their own, one TMPDIR
# --------------------------------------------------------------------------

class InNamespace:
    """A command started as pid ``pid`` of a fresh PID namespace of its own; its output goes to ``log``."""

    def __init__(self, argv, pid, env, cwd, log):
        self.argv, self.pid, self.log = list(argv), pid, log
        with open(log, "w", encoding="utf-8") as out:
            self.process = subprocess.Popen([*UNSHARE, sys.executable, str(LAUNCH), str(pid), "--", *self.argv],
                                            cwd=str(cwd), env=env, stdin=subprocess.DEVNULL, stdout=out,
                                            stderr=subprocess.STDOUT, start_new_session=True)

    def wait(self, timeout=RUN_TIMEOUT_S):
        try:
            return self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.end()
            raise AssertionError(f"a nested run did not end within {timeout} s:\n{self.describe()}") from None

    def end(self):
        if self.process.poll() is None:
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        self.process.wait()

    def output(self):
        try:
            return Path(self.log).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def describe(self):
        return (f"command (pid {self.pid} in its namespace): {' '.join(self.argv)}\n"
                f"exit code: {self.process.poll()}\noutput (last 1500 characters):\n{self.output()[-1500:]}")


@dataclass
class Live:
    run: InNamespace
    base: Path          # its numbered base folder
    lock_pid: str       # the pid its .lock names, in its own namespace
    release: Path


class Layout:
    """The case's own TMPDIR and the runs it starts, each in a PID namespace of its own."""

    def __init__(self, tmp_path):
        self.tmp_path = tmp_path
        self.tmpdir = tmp_path / "tmp"
        self.tmpdir.mkdir()
        self.root = self.tmpdir / f"pytest-of-{getpass.getuser()}"
        self.runs = []
        self.count = 0

    def env(self, **extra):
        env = {key: value for key, value in os.environ.items() if not key.startswith("PYTEST_") and key != FLAG}
        env.update({"TMPDIR": str(self.tmpdir), "PYTHONPATH": str(REPO_ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"})
        env.update(extra)
        return env

    def start(self, argv, pid, env, cwd):
        self.count += 1
        run = InNamespace(argv, pid, env, cwd, self.tmp_path / f"run-{self.count}.log")
        self.runs.append(run)
        return run

    def suite_run(self, mode, pid, policy=None, **extra):
        """The repository's own suites (the root conftest loaded) on the probe, one worker, no --basetemp."""
        command = [sys.executable, "-m", "pytest", str(PROBE.relative_to(REPO_ROOT)), f"--rootdir={REPO_ROOT}",
                   "-q", "--no-header", "-p", "no:cacheprovider", "-p", "no:xdist", "-p", "no:randomly"]
        if policy is not None:
            command += ["-o", f"tmp_path_retention_policy={policy}"]
        return self.start(command, pid, self.env(W2_67_NS_MODE=mode, **extra), REPO_ROOT)

    def held_project(self, ready, release):
        project = self.tmp_path / "project"
        (project / "tests").mkdir(parents=True)
        (project / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
        (project / "tests" / "test_held.py").write_text(HELD_CASE.format(ready=str(ready), release=str(release)),
                                                        encoding="utf-8")
        return project

    def start_live(self, form):
        """A run still going, as ``form``, its first process pid 3 in its namespace; back once its base folder
        exists and the run waits for the release."""
        ready, release = self.tmp_path / f"ready-{form}", self.tmp_path / f"release-{form}"
        if form == "close-runner":
            project = self.held_project(ready, release)
            run = self.start([sys.executable, "-c", CLOSE_DRIVER, str(project), str(RUN_TIMEOUT_S)], FIRST_PID,
                             self.env(), project)
        elif form == "foreign-project":
            project = self.held_project(ready, release)
            run = self.start([sys.executable, "-m", "pytest", "tests/test_held.py", f"--rootdir={project}", "-q",
                              "--no-header", "-p", "no:cacheprovider", "-p", "no:xdist", "-p", "no:randomly"],
                             FIRST_PID, self.env(), project)
        else:
            mode = {"suite-in-setup": "hold-setup", "suite-mid-test": "hold-call",
                    "suite-in-teardown": "hold-teardown"}[form]
            run = self.suite_run(mode, FIRST_PID, W2_67_NS_READY=str(ready), W2_67_NS_RELEASE=str(release))
        deadline = time.monotonic() + READY_TIMEOUT_S
        while not ready.is_file():
            if run.process.poll() is not None or time.monotonic() > deadline:
                raise AssertionError(f"the live run ({form}) never got to its wait:\n{run.describe()}")
            time.sleep(0.05)
        base = self.numbered(Path(ready.read_text(encoding="utf-8").strip()))
        lock = base / ".lock"
        assert lock.is_file(), f"the live run's base folder {base} holds no .lock: {sorted(os.listdir(base))}"
        return Live(run, base, lock.read_text(encoding="utf-8").strip(), release)

    def numbered(self, path):
        """The numbered base folder (``pytest-<n>`` under the user's folder) that holds ``path``."""
        for folder in (path, *path.parents):
            if folder.parent == self.root and NUMBERED.match(folder.name):
                return folder
        raise AssertionError(f"{path} is in no numbered base folder under {self.root}")

    def plant_finished(self, how_many):
        """Base folders as finished runs leave them (no ``.lock``), numbered after every folder there."""
        numbers = [int(NUMBERED.match(name).group(1)) for name in self.base_folders()]
        start = max(numbers, default=-1) + 1
        for number in range(start, start + how_many):
            (self.root / f"pytest-{number}" / "test_left0").mkdir(parents=True)
            (self.root / f"pytest-{number}" / "test_left0" / "left.txt").write_text("a finished run\n",
                                                                                   encoding="utf-8")

    def base_folders(self):
        if not self.root.is_dir():
            return []
        return sorted((path.name for path in self.root.iterdir()
                       if NUMBERED.match(path.name) and path.is_dir() and not path.is_symlink()),
                      key=lambda name: int(NUMBERED.match(name).group(1)))

    def end(self):
        for run in self.runs:
            run.end()


@pytest.fixture
def layout(tmp_path):
    if shutil.which("unshare") is None:
        pytest.fail("unshare (util-linux) is not installed: the PID namespaces cannot be laid out")
    trial = subprocess.run([*UNSHARE, sys.executable, "-c", "import os; print(os.getpid())"],
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    assert trial.returncode == 0 and trial.stdout.strip() == "1", (
        f"this machine refuses the PID namespaces the cases need: {' '.join(UNSHARE)} gave exit {trial.returncode}, "
        f"{trial.stdout.strip()!r} {trial.stderr.strip()[-500:]!r}")
    lay = Layout(tmp_path)
    try:
        yield lay
    finally:
        lay.end()


# --------------------------------------------------------------------------
# A run still going keeps its base folder
# --------------------------------------------------------------------------

LIVE_FORMS = ("close-runner", "foreign-project", "suite-in-setup", "suite-mid-test", "suite-in-teardown")
POLICIES = ("all", "failed", "none")


@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("form", LIVE_FORMS)
def test_a_live_runs_base_folder_is_kept_by_a_sweep_from_another_pid_namespace(layout, form, policy):
    """A run still going (``form``), pid 3 in its namespace; then, under ``all`` and ``failed``, three finished runs'
    folders numbered after it (none under ``none``, which keeps no folder); then a passing run of the suites in a
    namespace of its own, its pytest the next pid after the live run's (as the sandbox numbers its commands), given
    ``-o tmp_path_retention_policy=<policy>``. The live run's base folder must be there when the sweep has ended, and
    the live run must then pass."""
    live = layout.start_live(form)
    if policy != "none":
        layout.plant_finished(KEEP)
    before = layout.base_folders()
    sweeper = layout.suite_run("pass", int(live.lock_pid) + 1, policy=policy)
    swept = sweeper.wait()
    after = layout.base_folders()
    kept = live.base.is_dir()
    live.release.write_text("go\n", encoding="utf-8")
    ended = live.run.wait()
    assert swept == 0, f"the sweeping run did not pass, so it shows nothing:\n{sweeper.describe()}"
    assert kept, (
        f"the base folder of a run still going ({form}, {live.base.name}, its .lock naming pid {live.lock_pid} in its "
        f"own namespace) was removed by a passing run of the suites in another PID namespace, given "
        f"tmp_path_retention_policy={policy}: base folders before {before}, after {after}.\n"
        f"The live run, released afterwards:\n{live.run.describe()}")
    assert ended == 0, f"the live run ({form}) failed once released:\n{live.run.describe()}"


# --------------------------------------------------------------------------
# A killed run of the suites loses its base folder past the retention
# --------------------------------------------------------------------------

@pytest.mark.parametrize("sweeper_pid", ["same-pid", "next-pid"])
@pytest.mark.parametrize("killed_when", ["mid-test", "in-setup"])
def test_a_killed_suite_runs_base_folder_is_removed_past_retention_whatever_the_sweepers_pid(layout, killed_when,
                                                                                              sweeper_pid):
    """A run of the suites killed with SIGKILL in the middle of its test (``mid-test``) or in its first test's setup,
    once its base folder exists (``in-setup``), pid 3 in its namespace; three finished runs' folders numbered after
    it; then a passing run of the suites in a namespace of its own, its pytest pid 3 (``same-pid``) or pid 4
    (``next-pid``), pytest's default retention. The killed run's folder is past the retention and must be gone; at
    most three base folders are left (KPI 4); nothing that is not a numbered base folder is removed."""
    root, tmpdir = layout.root, layout.tmpdir
    ready = layout.tmp_path / "ready-killed"
    mode = {"mid-test": "kill-call", "in-setup": "kill-setup"}[killed_when]
    killed = layout.suite_run(mode, FIRST_PID, W2_67_NS_READY=str(ready))
    code = killed.wait()
    assert code == 128 + signal.SIGKILL and ready.is_file(), f"the run to kill did not die by SIGKILL:\n{killed.describe()}"
    base = layout.numbered(Path(ready.read_text(encoding="utf-8").strip()))
    lock = base / ".lock"
    assert lock.is_file(), f"the killed run left no .lock in {base}: {sorted(os.listdir(base))}"
    lock_pid = lock.read_text(encoding="utf-8").strip()
    layout.plant_finished(KEEP)
    others = [root / "keep-me" / "left.txt", root / "notes.txt", tmpdir / "other-tool" / "left.txt"]
    for path in others:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not a base folder of pytest's\n", encoding="utf-8")
    before = layout.base_folders()
    pid = int(lock_pid) if sweeper_pid == "same-pid" else int(lock_pid) + 1
    sweeper = layout.suite_run("pass", pid)
    assert sweeper.wait() == 0, f"the sweeping run did not pass, so it shows nothing:\n{sweeper.describe()}"
    after = layout.base_folders()
    problems = []
    if base.exists():
        problems.append(f"the killed run's folder {base.name} (its .lock naming pid {lock_pid} in a namespace that "
                        f"has ended) was kept by a sweep whose pytest is pid {pid} in its own namespace")
    if len(after) > KEEP:
        problems.append(f"{len(after)} base folders left behind, more than {KEEP} (DEC-898)")
    gone = [str(path.relative_to(tmpdir)) for path in others if not path.is_file()]
    if gone:
        problems.append(f"files outside pytest's numbered base folders were removed: {gone}")
    assert not problems, "; ".join(problems) + f". Base folders before the sweep {before}, after {after}."
