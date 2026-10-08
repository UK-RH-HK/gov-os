"""Support code for the launcher half of the W1-32 acceptance tests (DEC-392).

``gov launch`` is driven as W1-28's and W1-46's suites drive it: the project's
own ``gov`` package, a temporary project, a temporary HOME, and a stand-in for
the CLI at ``<HOME>/.local/bin/claude``. No CLI session is started, no model is
launched and nothing reaches the network.

The stand-in is W1-28's (it records its call in W1-46's form, uses its temp
folder as a plan file says, reports that it runs and waits), with three more
things a plan may ask for:

- ``sealed``: folders in the session's temp folder that the session leaves
  read-only, with a file inside, so that the folder cannot be removed whole;
- ``pid``: a file in which the session writes its process id and start time,
  so that a case can see, without a signal, whether that process still runs;
- ``release``: a file the session watches while it waits; it ends by itself
  when the file appears. This is how a case ends a session that lived on.

**Signals.** A case sends a signal to one process only: the ``gov launch``
process it started itself. The session is never signalled by a case, and
neither is a process group. Whether a session still runs is read from
``/proc``.
"""

from __future__ import annotations

import json
import os
import signal
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

_W28 = str(Path(__file__).resolve().parents[1] / "W1-28")
if _W28 not in sys.path:
    sys.path.insert(0, _W28)

import w1_28_launch_support as w28  # noqa: E402  the temporary project, the stand-in CLI, the plan

w46 = w28.w46
cli_support = w28.cli_support

ENGINEER, ENGINEER_TICKET = w28.ENGINEER, w28.ENGINEER_TICKET
WAIT_S = 30.0            # for the session to report, and for the launcher to end
SESSION_END_S = 5.0    # for the session's process to be gone once the launcher has ended
SESSION_LIMIT_S = 120.0  # a session that nobody ends stops by itself after this
INTERRUPT_EXIT = 130     # DEC-392
LEFT = {"work/left-behind.txt": "left by the session\n", "claude-1000/session/notes.txt": "notes\n"}

_RECORD_ANCHOR = 'record = {"kind": "session"'
_WAIT_ANCHOR = 'if plan.get("wait"):\n    time.sleep(float(plan["wait"]))\n'
_EXTRA = r'''
for folder in folders:
    for rel in plan.get("sealed", []):
        os.makedirs(os.path.join(folder, rel), exist_ok=True)
        with open(os.path.join(folder, rel, "kept.txt"), "w", encoding="utf-8") as handle:
            handle.write("in a folder the session left read-only\n")
        os.chmod(os.path.join(folder, rel), 0o500)
if plan.get("pid"):
    with open("/proc/self/stat", encoding="utf-8") as handle:
        started = handle.read().rsplit(")", 1)[1].split()[19]
    with open(plan["pid"] + ".part", "w", encoding="utf-8") as handle:
        json.dump({"pid": os.getpid(), "started": started}, handle)
    os.replace(plan["pid"] + ".part", plan["pid"])
'''
_WAIT = r'''
if plan.get("wait"):
    _until = time.monotonic() + float(plan["wait"])
    while time.monotonic() < _until and not (plan.get("release") and os.path.exists(plan["release"])):
        time.sleep(0.05)
'''


def _stub_text():
    text = w28._STUB
    assert text.count(_RECORD_ANCHOR) == 1 and text.count(_WAIT_ANCHOR) == 1, \
        "W1-28's stand-in CLI changed: this suite's additions no longer fit it"
    return text.replace(_RECORD_ANCHOR, _EXTRA + _RECORD_ANCHOR).replace(_WAIT_ANCHOR, _WAIT)


def install_stand_in_cli(sandbox):
    """W1-46's decoy on PATH and this suite's stand-in at ``<HOME>/.local/bin/claude``."""
    cli = w46.install_stand_in_cli(sandbox)
    text = (_stub_text().replace("@PYTHON@", sys.executable).replace("@SHARED@", repr(str(sandbox.tmpdir)))
            .replace("@PLAN@", repr(str(w28._plan_file(cli)))).replace("@LOG@", repr(str(cli.log))))
    cli.path.write_text(text, encoding="utf-8")
    cli.path.chmod(cli.path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return cli


def plan(cli, files=None, exit_code=0, sealed=(), ready=None, pid=None, release=None, wait=None):
    """What the next stand-in session does in its temp folder, and how it ends."""
    data = {"files": dict(files or {}), "links": {}, "exit": int(exit_code), "sealed": list(sealed)}
    for key, value in (("ready", ready), ("pid", pid), ("release", release)):
        if value is not None:
            data[key] = str(value)
    if wait is not None:
        data["wait"] = float(wait)
    w28._plan_file(cli).write_text(json.dumps(data), encoding="utf-8")


def launch(project, sandbox, cli, role=ENGINEER, ticket=ENGINEER_TICKET):
    """``gov launch <role> <ticket>`` to its end; W1-46's ``Launch``."""
    return w46.launch(project, sandbox, cli, role, ticket)


def listing(sandbox):
    """The entries of the directory the launcher makes its temp folders in."""
    return sorted(os.listdir(sandbox.tmpdir))


def unseal(folder):
    """Make every directory under ``folder`` writable again, so that the test's own folder can be removed."""
    for current, names, _ in os.walk(folder):
        for name in names:
            path = os.path.join(current, name)
            if not os.path.islink(path):
                os.chmod(path, 0o700)


# --------------------------------------------------------------------------
# Whether the session's process still runs, read from /proc (no signal)
# --------------------------------------------------------------------------

def session_runs(session):
    """Whether the process the session reported is still that process and not a zombie."""
    try:
        fields = Path(f"/proc/{session['pid']}/stat").read_text(encoding="utf-8").rsplit(")", 1)[1].split()
    except (FileNotFoundError, ProcessLookupError):
        return False
    return fields[0] != "Z" and fields[19] == session["started"]


# --------------------------------------------------------------------------
# A launch whose launcher is sent a signal while its session runs
# --------------------------------------------------------------------------

def _own_session_with_default_signals():
    """Runs in the child before ``gov`` starts: a session of its own, and the three signals at their defaults.

    A test runner may have been started with SIGINT or SIGHUP ignored, and a
    child inherits that. The launcher under test is started as a foreground
    command is.
    """
    os.setsid()
    for number in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(number, signal.SIG_DFL)


@dataclass(frozen=True)
class Signalled:
    signal: str
    folder: Path           # the session's temp folder, a directory while the session ran
    returncode: int        # of ``gov launch``; negative when the signal killed it
    stdout: str
    stderr: str
    session_ended: bool    # the session's process was gone within SESSION_END_S of the launcher's end
    before: list           # the temp directory's entries before the launch
    after: list            # and after the launcher ended

    def describe(self):
        return (f"gov launch after {self.signal}: exit code {self.returncode}\nstdout:\n{self.stdout}\n"
                f"stderr:\n{self.stderr[-1500:]}")


def signalled_launch(project, sandbox, cli, signum, role=ENGINEER, ticket=ENGINEER_TICKET):
    """Start ``gov launch``, wait until its session runs, send ``signum`` to the launcher alone, wait for its end."""
    assert sys.platform.startswith("linux"), "the session's process is read from /proc"
    ready, pid_file, release = (sandbox.elsewhere / name for name in
                                ("session-is-running.json", "session-process.json", "session-may-end"))
    plan(cli, files=LEFT, ready=ready, pid=pid_file, release=release, wait=SESSION_LIMIT_S)
    before = listing(sandbox)
    script = cli_support.write_launcher(project, sandbox)
    # Files, not pipes: a session that lives on keeps a pipe open, and the launcher's end would not be seen.
    out_path, err_path = sandbox.elsewhere / "launch-stdout.txt", sandbox.elsewhere / "launch-stderr.txt"
    with open(out_path, "w", encoding="utf-8") as out_file, open(err_path, "w", encoding="utf-8") as err_file:
        process = subprocess.Popen([sys.executable, str(script), "launch", role, ticket], cwd=str(project),
                                   env=w46.gov_environment(project, sandbox, cli), stdin=subprocess.DEVNULL,
                                   stdout=out_file, stderr=err_file, preexec_fn=_own_session_with_default_signals)

    def output():
        return out_path.read_text(encoding="utf-8"), err_path.read_text(encoding="utf-8")

    session = None
    try:
        deadline = time.monotonic() + WAIT_S
        while not ready.is_file():
            if process.poll() is not None or time.monotonic() > deadline:
                raise AssertionError(f"gov launch {role} {ticket} started no session within {WAIT_S:.0f} s "
                                     f"(exit code {process.poll()}): {''.join(output()).strip()[-400:]}")
            time.sleep(0.02)
        folders = json.loads(ready.read_text(encoding="utf-8"))
        assert len(folders) == 1, f"the session was not given exactly one temp folder of its own: {folders}"
        folder = Path(folders[0])
        assert (folder / "work" / "left-behind.txt").is_file(), "the session could not write in its temp folder"
        session = json.loads(pid_file.read_text(encoding="utf-8"))
        assert session_runs(session), "the stand-in session does not run: nothing to end"
        os.kill(process.pid, signum)                      # the launcher this case started, and nothing else
        try:
            process.wait(timeout=WAIT_S)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"gov launch did not end within {WAIT_S:.0f} s of "
                                 f"{signal.Signals(signum).name}") from None
        deadline = time.monotonic() + SESSION_END_S
        while session_runs(session) and time.monotonic() < deadline:
            time.sleep(0.05)
        out, err = output()
        return Signalled(signal.Signals(signum).name, folder, process.returncode, out, err,
                         not session_runs(session), before, listing(sandbox))
    finally:
        release.write_text("the case is over\n", encoding="utf-8")   # a session that lived on ends by itself
        if process.poll() is None:
            process.kill()                                # the case's own launcher
            process.wait(timeout=WAIT_S)
        deadline = time.monotonic() + SESSION_END_S
        while session is not None and session_runs(session) and time.monotonic() < deadline:
            time.sleep(0.05)
