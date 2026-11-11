"""W2-96 (DAEO-ouet): the reaping every planted ``gov accept`` in ``tests/unit/accept/test_w2_96*.py`` goes through
(DEC-866 rewrite, incident 2026-11-10 00:43, DEC-1038 (4)).

A planted gov starts in a session of its own, through a wrapper that records the pid of every process gov starts
(the run's pytest, in a session of its own). A reaper process of its own, in a session of its own, started before
the planted gov, blocks on a pipe only the case holds; the pipe ends when the case is done (``planted``'s finaliser
closes it) or when the case's process dies however it dies (SIGTERM, SIGKILL, xdist's worker gone). Then it stops
every recorded process group and the group of every live descendant of a recorded process (a planted test's own
session, as a nested run's): SIGTERM, a short grace, SIGKILL, and it waits until no live member of any of them is
left. It never matches a name: every group is found from a pid the case recorded.

The signals a case sends still go to gov's pid alone, and gov's own handling still decides what they do.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
from pathlib import Path

import pytest

from gov.accept import runner

# appended to every planted gov's wrapper, after its own head: with W296_RECORD set, every process gov starts has
# its pid added to that file the moment it is started, so that the case can reap it whatever happens to gov;
# nothing else in gov changes
RECORD = """record = os.environ.get("W296_RECORD")
if record:
    class _Recorded(subprocess.Popen):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            with open(record, "a") as file:
                file.write(f"{self.pid}\\n")
    subprocess.Popen = _Recorded
"""
TAIL = "from gov.cli.main import main\nsys.exit(main(sys.argv[1:]))\n"

# the reaper: exits 0 when nothing of what it reaps is left, 1 otherwise
REAPER = """import os, signal, sys, time
record, fd = sys.argv[1], int(sys.argv[2])
GRACE, BOUND = float(sys.argv[3]), float(sys.argv[4])
while os.read(fd, 64):
    pass

def recorded():
    try:
        with open(record) as file:
            return {int(word) for word in file.read().split()}
    except (OSError, ValueError):
        return set()

def children(pid):
    found = set()
    try:
        for task in os.listdir(f"/proc/{pid}/task"):
            with open(f"/proc/{pid}/task/{task}/children") as file:
                found.update(int(child) for child in file.read().split())
    except (OSError, ValueError):
        pass
    return found

def descendants(pid):
    found, todo = set(), [pid]
    while todo:
        for child in children(todo.pop()) - found:
            found.add(child)
            todo.append(child)
    return found

def live(groups):
    found = set()
    for name in os.listdir("/proc"):
        if name.isdigit():
            try:
                with open(f"/proc/{name}/stat") as file:
                    fields = file.read().rsplit(")", 1)[1].split()
            except (OSError, IndexError):
                continue
            if fields[0] != "Z" and int(fields[2]) in groups:
                found.add(int(fields[2]))
    return found

def groups():
    found = set()
    for pid in recorded():
        found.add(pid)  # each recorded process leads a group of its own (start_new_session)
        for child in descendants(pid):  # one gov started that the record may not show yet, or a planted test's own
            try:
                found.add(os.getpgid(child))
            except OSError:
                pass
    return found - {os.getpgid(0)}

def signal_all(targets, signum):
    for group in targets:
        try:
            os.killpg(group, signum)
        except OSError:
            pass

targets = groups()
signal_all(live(targets), signal.SIGTERM)
for limit, then in ((GRACE, signal.SIGKILL), (BOUND, None)):
    deadline = time.monotonic() + limit
    while live(targets | groups()) and time.monotonic() < deadline:
        time.sleep(0.02)
    targets |= groups()
    if then is not None:
        signal_all(live(targets), then)
sys.exit(1 if live(targets) else 0)
"""
REAP_GRACE, REAP_BOUND = 3.0, 20.0


def group_alive(group: int) -> bool:
    """Whether any process of the group is alive (a zombie is not), read from the kernel by pid, never by name."""
    for name in os.listdir("/proc"):
        if name.isdigit():
            try:
                fields = Path(f"/proc/{name}/stat").read_text().rsplit(")", 1)[1].split()
            except (OSError, IndexError):
                continue
            if fields[0] != "Z" and int(fields[2]) == group:
                return True
    return False


def launch_gov(root: Path, temp: Path, folder: Path, *, head: str = "", env: dict[str, str] | None = None,
               ignore: tuple = (), record: Path | None = None) -> subprocess.Popen:
    """Start ``gov accept DAEO-t001 --json --root <root>`` as its own process, in a session of its own, through a
    wrapper: ``head`` (the case's own patching), then the recording, then gov's ``main``. ``env`` is added to the
    environment (every ``W296_*`` variable of the caller's is dropped first); ``ignore`` names signals gov starts
    with ignored. With ``record``, gov's pid and every pid gov starts are added to that file."""
    script = folder / "w296_gov.py"
    script.write_text("import os, subprocess, sys, time\n" + head + RECORD + TAIL)
    full = {name: value for name, value in os.environ.items() if not name.startswith("W296_")}
    full.update(PYTHONPATH=str(Path(runner.__file__).parents[2]), TMPDIR=str(temp), **(env or {}))
    if record is not None:
        full["W296_RECORD"] = str(record)

    def _ignore():
        for signum in ignore:
            signal.signal(signum, signal.SIG_IGN)

    # a session of its own: one killpg reaches gov and anything left in its group, and a stop sent to the case's
    # own group never reaches it
    gov = subprocess.Popen([sys.executable, str(script), "accept", "DAEO-t001", "--json", "--root", str(root)],
                           env=full, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=_ignore,
                           start_new_session=True)
    if record is not None:
        with open(record, "a") as file:
            file.write(f"{gov.pid}\n")
    return gov


@contextlib.contextmanager
def planted(folder: Path, head: str = ""):
    """Launch planted gov processes that are reaped on every ending of the case: the body's success, an assertion,
    a timeout, an exception, KeyboardInterrupt, and the case's process being stopped or killed (the reaper then
    does it alone). Yields ``launch(root, temp, env=None, ignore=())``, whose wrapper starts with ``head``;
    ``launch.reaper`` is the reaper's pid.
    """
    folder.mkdir(parents=True, exist_ok=True)
    record, script = folder / "w296_planted", folder / "w296_reaper.py"
    record.write_text("")
    script.write_text(REAPER)
    read, write = os.pipe()
    try:
        reaper = subprocess.Popen([sys.executable, str(script), str(record), str(read), str(REAP_GRACE),
                                   str(REAP_BOUND)], pass_fds=(read,), start_new_session=True,
                                  stdin=subprocess.DEVNULL)
    finally:
        os.close(read)
    launched: list[subprocess.Popen] = []

    def launch(root: Path, temp: Path, env: dict[str, str] | None = None, ignore: tuple = ()) -> subprocess.Popen:
        gov = launch_gov(root, temp, folder, head=head, env=env, ignore=ignore, record=record)
        launched.append(gov)
        return gov

    launch.reaper = reaper.pid
    try:
        yield launch
    finally:
        os.close(write)  # the reaper wakes and stops whatever is left
        try:
            code = reaper.wait(timeout=REAP_GRACE + REAP_BOUND + 30)
        except subprocess.TimeoutExpired:
            reaper.kill()
            code = reaper.wait()
        for gov in launched:
            try:
                gov.wait(timeout=10)
            except subprocess.TimeoutExpired:  # never expected: the reaper has killed gov's group already
                gov.kill()
                gov.wait()
            if gov.stdout is not None:
                gov.stdout.close()
        assert code == 0, "the reaper left a planted process group alive"


def launch_fixture(head: str = ""):
    """A ``launch`` fixture for a test file: its planted gov (wrapper head ``head``) reaped, with everything it
    started, however the case ends."""
    @pytest.fixture
    def launch(tmp_path):
        with planted(tmp_path / "w296_reap", head) as start:
            yield start
    return launch
