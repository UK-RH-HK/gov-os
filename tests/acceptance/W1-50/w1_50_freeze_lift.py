"""Lifting a freeze in a test (DEC-409): the one seam below the command line, and what is planted through it.

``gov pause --off`` refuses under a Claude Code session and without a terminal,
and every suite runs under an agent session with pipes. So a test that needs a
lifted freeze, or that asks how the lift judges an ancestry or a terminal,
calls the private test function:

    gov.pause.command._lift_test(root, ancestry=None, terminal=None) -> dict

This is NOT the public ``lift(root)`` function. The public function always reads
the real ancestry from ``/proc`` and uses ``(0, 1)`` as its terminal — it has no
``ancestry`` or ``terminal`` parameters, so an agent cannot import it and bypass
the rules with forged values. ``_lift_test`` holds the old behavior with the
seam open, for tests only.

- ``ancestry``: the process chain as the product's own reading returns it, the
  command's own process first and the system's first process last. Each
  process is a dict ``{"pid", "ppid", "comm", "exe", "cmdline"}``; ``exe`` is
  None when its link cannot be read, ``cmdline`` is a list of words. ``None``
  (what the command passes) reads the real chain from ``/proc``.
- ``terminal``: a pair of file descriptors ``(input, output)``. ``None`` (what
  the command passes) is ``(0, 1)``. The product itself asks ``os.isatty`` of
  both, so a planted pipe refuses here as it does at the command line.
- It returns the command's result (``{"paused": False}``) or raises
  ``GovError``.

The contract is written out in ``w1_50_freeze_README.md``. The call is made in
a new process whose environment is built from scratch (the ``GOV_ROLE`` of the
session that runs the tests never reaches it), with a pseudo-terminal the
driver opens, reads the shown code from and types the reply on.

This module imports nothing of another suite, so an earlier suite's support
code can import it without a cycle (``w1_28_support.lift``).

**No test lifts or sets a freeze of this repository**: ``drive`` refuses a
project inside it.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
MODULE, FUNCTION = "gov.pause.command", "_lift_test"
SEAM_FUNCTION = "lift"
CODE = re.compile(r"LIFT-\d{4}")           # DEC-409: "type LIFT-<4 digits> to lift the freeze"
DRIVER_TIMEOUT_S = 120.0

# What is typed back when a code has been shown.
RIGHT, WRONG, EMPTY_LINE, END_OF_INPUT = "right", "wrong", "empty", "eof"
# What the function is handed as its terminal.
PTY = "pty"                    # input and output are one pseudo-terminal
PIPE_IN = "pipe-in"            # input is a pipe, output is a pseudo-terminal ("piped input")
PIPE_OUT = "pipe-out"          # input is a pseudo-terminal, output is a pipe ("stdout is not a TTY")
PIPES = "pipes"                # both are pipes
NO_TERMINAL = "devnull"        # both are /dev/null ("no TTY at all")

LIFTED, REFUSED, MISSING, HANG, CRASH = "lifted", "refused", "missing", "hang", "crash"


# --------------------------------------------------------------------------
# Planted ancestries
# --------------------------------------------------------------------------

HOME = "/home/owner"
VERSION_FILE = f"{HOME}/.local/share/claude/versions/2.1.288"     # the file's name is the version, not ``claude``
CLI = f"{HOME}/.local/bin/claude"                                 # DEC-205; ``CLI_REL`` of the launcher
EXTENSION_BINARY = (f"{HOME}/.vscode-server/extensions/anthropic.claude-code-2.1.288-linux-x64/resources/"
                    "native-binary/claude")
EDITOR = f"{HOME}/.vscode-server/bin/0f0d87fa9e96c856c5212fc86db137ac0d783365"

# One process: (comm, exe, cmdline). ``exe`` None: the link cannot be read (another user's process).
OWN = ("python3", "/usr/bin/python3.12", ["python3", "-m", "gov.cli.main", "pause", "--off"])
LOGIN_SHELL = ("bash", "/usr/bin/bash", ["-bash"])
BASH_C = ("bash", "/usr/bin/bash", ["/bin/bash", "-c", "python3 -m gov.cli.main pause --off"])
INIT = ("init", None, ["/init"])                                  # the system's first process on this machine
EDITOR_NODE = ("node", f"{EDITOR}/node", [f"{EDITOR}/node", f"{EDITOR}/out/server-main.js", "--host=127.0.0.1"])
EDITOR_SH = ("sh", "/usr/bin/dash", ["sh", f"{EDITOR}/bin/code-server", "--host=127.0.0.1"])
# The three shapes seen on this machine (the README's "What a Claude Code session looks like").
HEADLESS = ("claude", VERSION_FILE, [CLI, "-p", "do the ticket's work"])
CONSOLE = ("claude", EXTENSION_BINARY, [EXTENSION_BINARY, "--output-format", "stream-json", "--verbose"])
LAUNCHED = ("claude", VERSION_FILE, [CLI, "--settings", '{"env":{"GOV_ROLE":"engineer"}}', "-p", "do the work"])
GOV_LAUNCH = ("python3", "/usr/bin/python3.12",
              ["python3", "-m", "gov.cli.main", "launch", "engineer", "DAEO-zz90", "--", "-p", "do the work"])
# Not seen here, and read the stricter way: one sign alone is a session.
NPM_INSTALL = ("node", "/usr/bin/node", ["node", "/usr/lib/node_modules/@anthropic-ai/claude-code/cli.js", "-p", "x"])
VERSION_FILE_RUN_BY_NAME = ("2.1.288", VERSION_FILE, [VERSION_FILE, "-p", "x"])
RENAMED_COMM = ("worker", None, [CLI, "-p", "x"])                 # only the command line says it
# What a launched session's sandbox shows of itself (seen from inside one on 2026-10-06): the chain ends at a
# process 1 that is the sandbox's own, not the system's.
SANDBOX_FIRST = ("3", None, ["/proc/self/fd/3", "/bin/bash", "-c", "python3 -m gov.cli.main pause --off"])


def chain(*processes):
    """A readable chain of ``processes``, nearest first; the last one gets pid 1 and parent 0."""
    pids = [4000 - 10 * index for index in range(len(processes) - 1)] + [1]
    return [{"pid": pid, "ppid": parent, "comm": comm, "exe": exe, "cmdline": list(cmdline)}
            for (comm, exe, cmdline), pid, parent in zip(processes, pids, [*pids[1:], 0])]


# No Claude Code session, readable to the system's first process: the only ancestries that may lift.
PLAIN_TERMINAL = chain(OWN, LOGIN_SHELL, INIT)
EDITOR_TERMINAL = chain(OWN, LOGIN_SHELL, EDITOR_NODE, EDITOR_NODE, EDITOR_SH, INIT)

# A Claude Code session among the ancestors (rule 1).
SESSION_ANCESTRIES = {
    "headless-p": chain(OWN, BASH_C, HEADLESS, LOGIN_SHELL, INIT),
    "operator-console": chain(OWN, BASH_C, CONSOLE, EDITOR_NODE, EDITOR_NODE, EDITOR_SH, INIT),
    "gov-launch": chain(OWN, BASH_C, LAUNCHED, GOV_LAUNCH, LOGIN_SHELL, INIT),
    "several-levels-up": chain(
        OWN,
        ("env", "/usr/bin/env", ["env", "-u", "GOV_ROLE", "python3", "-m", "gov.cli.main", "pause", "--off"]),
        ("timeout", "/usr/bin/timeout", ["timeout", "60", "env", "-u", "GOV_ROLE", "python3", "-m", "gov.cli.main"]),
        ("setsid", "/usr/bin/setsid", ["setsid", "--wait", "timeout", "60", "env"]),
        ("nohup", "/usr/bin/nohup", ["nohup", "setsid", "--wait", "timeout", "60", "env"]),
        ("python3", "/usr/bin/python3.12", ["python3", "-c", "import subprocess; subprocess.run(['nohup', 'setsid'])"]),
        BASH_C, HEADLESS, LOGIN_SHELL, INIT),
    "a-session-inside-a-session": chain(OWN, BASH_C, HEADLESS, BASH_C, CONSOLE, EDITOR_NODE, EDITOR_SH, INIT),
    "npm-install-shape": chain(OWN, BASH_C, NPM_INSTALL, LOGIN_SHELL, INIT),
    "the-version-file-run-by-name": chain(OWN, BASH_C, VERSION_FILE_RUN_BY_NAME, LOGIN_SHELL, INIT),
    "only-the-command-line-says-it": chain(OWN, BASH_C, RENAMED_COMM, LOGIN_SHELL, INIT),
}


def _unreadable():
    broken = chain(OWN, LOGIN_SHELL, INIT)[:2]                    # ends at a process whose parent was not read
    unlinked = chain(OWN, LOGIN_SHELL, INIT)
    unlinked[0]["ppid"] = 4242                                    # the next entry is not this process's parent
    nameless = chain(OWN, ("", None, []), LOGIN_SHELL, INIT)      # a process of which nothing could be read
    nameless[1]["comm"] = None
    orphan = chain(OWN, LOGIN_SHELL)                              # "pid 1, parent 0" that is a shell, not a first process
    return {
        "nothing-could-be-read": [],
        "the-chain-stops-before-the-first-process": broken,
        "an-entry-is-not-the-parent-of-the-one-before": unlinked,
        "a-process-of-which-nothing-was-read": nameless,
        "the-sandbox-s-own-first-process": chain(OWN, BASH_C, SANDBOX_FIRST),
        "a-first-process-that-is-a-shell": orphan,
    }


# The ancestry cannot be read (rule 1: that refuses).
UNREADABLE_ANCESTRIES = _unreadable()


# --------------------------------------------------------------------------
# The driver: one process, one or more calls of the function
# --------------------------------------------------------------------------

_DRIVER = r'''
import importlib, json, os, random, re, select, sys, threading

job = json.loads(sys.argv[1])
CODE = re.compile(r"LIFT-\d{4}")


def close(*fds):
    for fd in fds:
        try:
            os.close(fd)
        except (OSError, TypeError):
            pass


def one(function):
    kind, reply = job["terminal"], job["reply"]
    master = slave = None
    watch = feed = None          # where the test reads what the function shows; where it types
    opened = []
    if kind in ("pty", "pipe-in", "pipe-out"):
        master, slave = os.openpty()
        opened += [master, slave]
    if kind == "pty":
        in_fd, out_fd, watch, feed = slave, slave, master, master
    elif kind == "pipe-in":
        read_end, write_end = os.pipe()
        opened += [read_end, write_end]
        in_fd, out_fd, watch, feed = read_end, slave, master, write_end
    elif kind == "pipe-out":
        read_end, write_end = os.pipe()
        opened += [read_end, write_end]
        in_fd, out_fd, watch, feed = slave, write_end, read_end, master
    elif kind == "pipes":
        in_read, in_write = os.pipe()
        out_read, out_write = os.pipe()
        opened += [in_read, in_write, out_read, out_write]
        in_fd, out_fd, watch, feed = in_read, out_write, out_read, in_write
    else:
        in_fd, out_fd = os.open(os.devnull, os.O_RDONLY), os.open(os.devnull, os.O_WRONLY)
        opened += [in_fd, out_fd]

    seen = {"shown": b"", "before": None, "typed": None}
    done = threading.Event()

    def typist():
        while watch is not None:
            try:
                ready = select.select([watch], [], [], 0.05)[0]
            except (OSError, ValueError):
                return
            if ready:
                try:
                    data = os.read(watch, 65536)
                except OSError:
                    return
                if not data and kind != "pty":
                    return
                seen["shown"] += data
            found = CODE.search(seen["shown"].decode("utf-8", "replace"))
            if found and seen["typed"] is None:
                code = found.group(0)
                seen["before"] = seen["shown"]
                if reply == "right":
                    text = code + "\n"
                elif reply == "wrong":
                    text = "LIFT-%04d\n" % ((int(code[5:]) + 1) % 10000)
                elif reply == "empty":
                    text = "\n"
                else:
                    text = None
                seen["typed"] = text or ""
                try:
                    if text is not None:
                        os.write(feed, text.encode())
                    elif feed == master:
                        os.write(feed, b"\x04")      # end of input on a terminal
                    else:
                        os.close(feed)
                except OSError:
                    pass
            if done.is_set() and not ready:
                return

    outcome = {}

    def call():
        try:
            value = function(job["root"], ancestry=job["ancestry"], terminal=(in_fd, out_fd))
            outcome.update(status="lifted", result=value)
        except TypeError as error:
            if "ancestry" in str(error) or "terminal" in str(error) or "argument" in str(error):
                outcome.update(status="missing", detail=f"the function does not take the contract's parameters: {error}")
            else:
                outcome.update(status="crash", detail=repr(error))
        except Exception as error:
            if type(error).__name__ == "GovError":
                outcome.update(status="refused", error={"code": getattr(error, "code", ""),
                                                        "message": getattr(error, "message", str(error)),
                                                        "details": getattr(error, "details", {})})
            else:
                outcome.update(status="crash", detail=repr(error))
        except BaseException as error:
            outcome.update(status="crash", detail=repr(error))

    watcher = threading.Thread(target=typist, daemon=True)
    worker = threading.Thread(target=call, daemon=True)
    watcher.start()
    worker.start()
    worker.join(job["limit"])
    hung = worker.is_alive()
    done.set()
    watcher.join(2)
    if hung:
        outcome = {"status": "hang", "detail": "the function was still waiting %s s after the reply" % job["limit"]}
    shown = seen["shown"].decode("utf-8", "replace")
    before = (seen["before"] if seen["before"] is not None else seen["shown"]).decode("utf-8", "replace")
    outcome.update(shown=shown, shown_before_reply=before, typed=seen["typed"])
    if not hung:
        close(*opened)
    return outcome, hung


def main():
    try:
        function = getattr(importlib.import_module(job["module"]), job["function"])
    except (ImportError, AttributeError) as error:
        print(json.dumps([{"status": "missing", "detail": repr(error)}]))
        return
    runs = []
    for _ in range(job["runs"]):
        if job["seed"] is not None:
            random.seed(job["seed"])
        outcome, hung = one(function)
        try:
            json.dumps(outcome)
        except (TypeError, ValueError):
            outcome["result"] = repr(outcome.get("result"))
        runs.append(outcome)
        if hung:
            break
    sys.stdout.write(json.dumps(runs))
    sys.stdout.flush()
    os._exit(0)                  # a function that still waits must not keep the process


main()
'''


@dataclass(frozen=True)
class Lift:
    """One call of the internal function."""
    status: str                 # lifted | refused | missing | hang | crash
    result: object = None       # what the function returned
    error: dict = field(default_factory=dict)   # the GovError: code, message, details
    shown: str = ""             # everything that came out of the function's terminal output (typed text is echoed)
    shown_before_reply: str = ""
    typed: str | None = None    # what was typed back; None when no code was shown
    detail: str = ""

    @property
    def codes(self):
        """The codes shown before anything was typed."""
        return CODE.findall(self.shown_before_reply)

    @property
    def message(self):
        return str(self.error.get("message", ""))

    def says(self):
        """Everything the function gave back that is not the terminal: its result, or its error."""
        return json.dumps({"result": self.result, "error": self.error}, sort_keys=True, default=str)

    def describe(self):
        return (f"status={self.status} result={self.result!r} error={self.error!r} typed={self.typed!r} "
                f"shown={self.shown[:300]!r} {self.detail}")


def _environment(sandbox, role):
    """Built from scratch, as ``w1_28_support`` builds the command's: no variable of the session is inherited."""
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(getattr(sandbox, "tmp", None) or sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "GIT_CONFIG_NOSYSTEM": "1",
        "PYTHONPATH": str(SRC),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }
    if role is not None:
        env["GOV_ROLE"] = role
    return env


def drive(project, sandbox, ancestry=None, terminal=PTY, reply=RIGHT, role=None, runs=1, seed=None, limit=10.0,
          function=None):
    """Call the internal function ``runs`` times in one new process; a list of ``Lift``.

    ``ancestry`` None is ``PLAIN_TERMINAL``: the function is always handed a
    planted ancestry and a planted terminal. ``seed`` seeds Python's ``random``
    before each call. A function that is not built, or does not take the
    contract's parameters, gives ``status == "missing"``: the test fails, the
    file is still collected.

    ``function`` overrides ``FUNCTION``: pass ``SEAM_FUNCTION`` to call
    ``lift`` (the public function) instead of ``_lift_test``.
    """
    project = Path(project)
    assert REPO_ROOT not in (project, *project.parents), f"refusing to lift in {project}: it is this repository"
    job = {"module": MODULE, "function": function or FUNCTION, "root": str(project),
           "ancestry": PLAIN_TERMINAL if ancestry is None else ancestry, "terminal": terminal, "reply": reply,
           "runs": runs, "seed": seed, "limit": limit}
    try:
        done = subprocess.run([sys.executable, "-c", _DRIVER, json.dumps(job)], cwd=str(project),
                              env=_environment(sandbox, role), capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=DRIVER_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the lift's driver did not end within {DRIVER_TIMEOUT_S:.0f} s") from None
    try:
        outcomes = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"the lift's driver did not answer (exit code {done.returncode}):\n{done.stdout[-600:]}\n"
                             f"{done.stderr[-1500:]}") from None
    names = ("status", "result", "error", "shown", "shown_before_reply", "typed", "detail")
    return [Lift(**{name: outcome[name] for name in names if outcome.get(name) is not None}) for outcome in outcomes]


def built(run):
    """The contract function exists and takes the contract's parameters; the test fails here until it does."""
    if run.status == MISSING:
        pytest.fail(f"DEC-409 is not built: {MODULE}.{FUNCTION}(root, ancestry=None, terminal=None) is missing — "
                    f"the private test function must accept ancestry and terminal kwargs "
                    f"({run.detail}). The contract is in tests/acceptance/W1-50/w1_50_freeze_README.md.",
                    pytrace=False)
    assert run.status not in (HANG, CRASH), f"the lift did not end as a result or a refusal: {run.describe()}"
    return run


def lift(project, sandbox, **planted):
    """One call of the function; the ``Lift``. The planted values are ``drive``'s."""
    return built(drive(project, sandbox, **planted)[0])


def lift_as_the_owner(project, sandbox):
    """The owner in person: a plain terminal's ancestry, a terminal, and the shown code typed back.

    Returns the function's result. A refusal fails the test; a caller that
    expects one (a directory at the flag's path) uses ``lift``.
    """
    run = lift(project, sandbox)
    assert run.status == LIFTED, (
        "with no Claude Code session among the ancestors, a terminal and the shown code typed back, the freeze was "
        f"not lifted: {run.describe()}"
    )
    return run.result
