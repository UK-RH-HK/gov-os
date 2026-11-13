"""Every external command of a pass, limited by one timeout (S6: a hung command is a named failed check)."""

from __future__ import annotations

import os
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path

from gov.util.gitenv import git_env


class CommandFailed(Exception):
    """A command that did not finish or could not start; the message names the command and why."""


@dataclass
class Done:
    code: int
    out: str
    err: str


class Runner:
    """Runs argv lists with ``timeout`` seconds each. A program that timed out once is not run again in the same pass
    (so a hung ``git`` costs one timeout, not one per entry)."""

    def __init__(self, timeout: float):
        self.timeout = timeout
        self.hung: dict[str, str] = {}

    def run(self, argv: list[str], cwd: Path | None = None, env: dict | None = None,
            stdin: str | None = None) -> Done:
        name = argv[0]
        if name in self.hung:
            raise CommandFailed(f"`{name}` timed out earlier in this pass ({self.hung[name]})")
        shown = " ".join(argv)
        try:
            child = subprocess.Popen(argv, cwd=cwd, env=env, text=True, errors="replace", start_new_session=True,
                                     stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as error:
            raise CommandFailed(f"`{shown}` cannot be started: {error}") from None
        try:
            out, err = child.communicate(stdin, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except OSError:
                child.kill()
            try:
                child.communicate(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                pass
            why = f"`{shown}` timed out after {self.timeout:g} s"
            self.hung[name] = why
            raise CommandFailed(why) from None
        return Done(child.returncode, out, err)

    def git(self, folder: Path, *args: str) -> Done:
        """``git -C folder args`` for a read: the person's configuration unread, no optional locks."""
        return self.run(["git", "--no-optional-locks", "-C", str(folder), *args], env=git_env(folder, pinned=True))
