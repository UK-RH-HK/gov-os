"""W1-50, KPI line 2 (DEC-402), a review finding for a live session (DEC-136): a pause set at any moment stays set.

One live case (``local_only``, as the first batch marks its own; a launched
test designer cannot run it, the ticket lead does).

A session launched while a marked flag exists has settings that name the
flag's path (DEC-311). When the owner then lifts the freeze, the name no
longer exists, so the sandbox puts its empty read-only placeholder at the path
for as long as one of that session's commands runs. If a real, marked flag is
put at the path during that command (a new file renamed over the placeholder,
which is how a pause over a placeholder leaves a real flag), the sandbox's
clean-up at the end of the command must not take it away.

**It is not known what the sandbox's clean-up does.** If this case is red when
the lead runs it, it becomes a decision package: the failure message says
exactly what was seen at the path (gone, emptied, replaced) and when.
"""

from __future__ import annotations

import os
import shutil
import stat
import threading
import time
from pathlib import Path

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import freeze_launch_base  # noqa: F401  fixture

launch_support = support.launch_support
ENGINEER = support.ENGINEER
FLAG = support.FLAG_REL
SCRATCH = ".gov-runtime/scratch/w1-50-pause"
SESSION_TIMEOUT_S = 420.0
PROBE_SLEEP_S = 15
NOT_INHERITED = ("GOV_ROLE", "GOV_TICKET", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_PROJECT_DIR",
                 "CLAUDE_CODE_SSE_PORT")
# The flag at launch, and the flag the test puts over the placeholder: told apart by their times.
FLAG_AT_LAUNCH = b"FROZEN owner 2026-10-05T00:00:00Z\n"
FLAG_PUT_DURING_THE_COMMAND = b"FROZEN owner 2026-10-05T11:11:11Z\nput by the acceptance test during the command\n"
PROBE = f"""#!/bin/bash
# W1-50 acceptance probe: a command that lasts long enough for the test to act at the flag's path from outside.
OUT={SCRATCH}/results.txt
echo "start=1" > "$OUT"
sleep {PROBE_SLEEP_S}
if [ -s {FLAG} ]; then echo "inside_at_end=non-empty" >> "$OUT"
elif [ -e {FLAG} ] || [ -L {FLAG} ]; then echo "inside_at_end=empty" >> "$OUT"
else echo "inside_at_end=absent" >> "$OUT"; fi
echo "end=1" >> "$OUT"
"""
PROMPT = ("Do exactly this one step, once, and nothing else. If it is refused or fails, do not retry it and do not "
          f"work around it. Run this Bash command as written: bash {SCRATCH}/probe.sh  Then answer DONE.")


def _seen(path):
    """What is at ``path`` on the file system outside the sandbox, in words."""
    try:
        status = os.lstat(path)
    except OSError:
        return "gone: nothing is at the path"
    mode = oct(stat.S_IMODE(status.st_mode))
    if stat.S_ISLNK(status.st_mode):
        return f"replaced by a symbolic link to {os.readlink(path)!r}"
    if not stat.S_ISREG(status.st_mode):
        return f"replaced by something that is not a regular file (file type {oct(stat.S_IFMT(status.st_mode))})"
    if status.st_size == 0:
        return f"emptied: an empty regular file, mode {mode}"
    try:
        content = Path(path).read_bytes()
    except OSError as error:
        return f"a regular file of {status.st_size} bytes, mode {mode}, that cannot be read: {error}"
    if content == FLAG_PUT_DURING_THE_COMMAND:
        return f"the marked flag the test put there, mode {mode}"
    if content == FLAG_AT_LAUNCH:
        return f"the flag of the launch, mode {mode}"
    return f"replaced: a regular file of {status.st_size} bytes, mode {mode}, starting {content[:80]!r}"


class _Owner(threading.Thread):
    """What the owner does from outside the sandbox while the session runs, and what is then seen at the path.

    1. When the launcher has built the session's settings (its temp folder
       appears), the flag is removed: the owner lifts the freeze.
    2. When the sandbox's placeholder appears at the path (a command of the
       session runs), a new marked flag is renamed over it.
    3. From then on every change of what is at the path is noted, with the
       time since step 2 and whether the command had ended.
    """

    def __init__(self, flag, launch_tmp, new_flag, results):
        super().__init__(daemon=True)
        self.flag, self.launch_tmp, self.new_flag, self.results = flag, launch_tmp, new_flag, results
        self.stop = threading.Event()
        self.lifted = False
        self.placeholder = None     # what was at the path when the test put its flag there
        self.put_at = None
        self.put_before_the_command_ended = None
        self.log = []               # (seconds since the flag was put, command ended?, what is at the path)
        self.error = None

    def _command_ended(self):
        try:
            return "end=1" in self.results.read_text(encoding="utf-8")
        except OSError:
            return False

    def run(self):
        try:
            last = None
            while not self.stop.is_set():
                if not self.lifted:
                    if any(name.startswith("gov-launch-") for name in os.listdir(self.launch_tmp)):
                        os.unlink(self.flag)
                        self.lifted = True
                elif self.put_at is None:
                    if os.path.lexists(self.flag):
                        self.placeholder = _seen(self.flag)
                        os.replace(self.new_flag, self.flag)
                        self.put_at = time.monotonic()
                        self.put_before_the_command_ended = not self._command_ended()
                else:
                    now = _seen(self.flag)
                    if now != last:
                        self.log.append((round(time.monotonic() - self.put_at, 2), self._command_ended(), now))
                        last = now
                time.sleep(0.05)
        except Exception as error:  # reported by the test: a thread's exception is otherwise lost
            self.error = error


@pytest.mark.local_only
def test_a_flag_put_over_the_placeholder_during_a_command_stays(freeze_launch_base, tmp_path):
    """A real engineer session, one Bash call of about fifteen seconds, with the owner acting from outside."""
    missing = [name for name in ("bwrap", "socat") if shutil.which(name) is None]
    if not (Path.home() / launch_support.CLI_REL).is_file():
        missing.append("~/.local/bin/claude")
    if missing:
        pytest.fail(f"a launched session needs {missing} on this machine", pytrace=False)

    project = tmp_path / "repo"
    shutil.copytree(freeze_launch_base, project, symlinks=True)
    sandbox = launch_support.cli_support.make_sandbox(tmp_path / "sandbox")
    support.w47.configure_stand_in(project, support.w47.make_stand_in(sandbox.elsewhere / "held-out-stand-in"))
    launch_support.write(project, f"{SCRATCH}/probe.sh", PROBE)
    flag = support.put_text(project, FLAG_AT_LAUNCH)          # a marked flag exists at launch: the settings name it
    new_flag = tmp_path / "the-flag-to-put"                   # on the project's file system: a rename, not a copy
    new_flag.write_bytes(FLAG_PUT_DURING_THE_COMMAND)
    launch_tmp = tmp_path / "launch-tmp"                      # the launcher's temp folder appears here, alone
    launch_tmp.mkdir()
    results_path = project / SCRATCH / "results.txt"

    owner = _Owner(flag, launch_tmp, new_flag, results_path)
    env = {key: value for key, value in os.environ.items() if key not in NOT_INHERITED}
    env.update({"PYTHONPATH": str(project / "src"), "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
                "TMPDIR": str(launch_tmp)})
    owner.start()
    try:
        run = launch_support.run_gov(project, sandbox, "launch", ENGINEER, launch_support.TICKET_OF[ENGINEER], "--",
                                     "-p", PROMPT, "--permission-mode", "acceptEdits", "--model", "haiku",
                                     "--max-turns", "6", "--allowedTools", "Bash", env=env, timeout=SESSION_TIMEOUT_S)
        time.sleep(1.0)   # what the end of the session does at the path is in the log too
    finally:
        owner.stop.set()
        owner.join(timeout=5)
    at_the_end = _seen(flag)
    history = "; ".join(f"{seconds} s after it was put ({'after' if ended else 'during'} the command): {what}"
                        for seconds, ended, what in owner.log) or "nothing was noted"

    # Did the case observe what it is about? If not, it shows nothing.
    assert owner.error is None, f"the test's own watcher failed: {owner.error!r}"
    assert owner.lifted, f"the launcher's temp folder never appeared in {launch_tmp}: no session was started\n" \
                         f"{run.describe()[-1500:]}"
    results = results_path.read_text(encoding="utf-8") if results_path.is_file() else ""
    if "end=1" not in results:
        pytest.fail(f"the launched session did not run the probe to its end (results: {results!r})\n"
                    f"{run.describe()[-1500:]}", pytrace=False)
    assert owner.put_at is not None, (
        f"after the flag was removed, nothing appeared at {FLAG} while the session's command ran: the sandbox put "
        f"no placeholder there, so this case observed nothing. At the end: {at_the_end}"
    )
    assert owner.put_before_the_command_ended, (
        f"the placeholder at {FLAG} was seen only after the command had ended ({owner.placeholder}): the flag was "
        f"not put during the command, so this case observed nothing"
    )

    # The behaviour: a pause set at any moment stays set. The file's mode is not pinned, only that it is the test's
    # flag with its content.
    lost = [(seconds, ended, what) for seconds, ended, what in owner.log
            if not what.startswith("the marked flag the test put there")]
    assert not lost and at_the_end.startswith("the marked flag the test put there"), (
        f"a marked flag put at {FLAG} over the sandbox's placeholder ({owner.placeholder}) while a command of the "
        f"session ran did not stay. Seen at the path: {history}. When the session had ended: {at_the_end}. "
        f"Inside the sandbox the command saw: {results.split()!r}. A pause set during a launched session's command "
        f"is undone by the sandbox (DEC-402): this is a decision package."
    )
