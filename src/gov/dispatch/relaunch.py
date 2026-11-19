"""The relaunch of a session that died (the run-time tool, slice 3: RT-5, F1; audit 3 D5).

Off by default, until the cut-over: the watch pass reads ``~/.gov-os/runtime/config.json`` (``{"relaunch": true}``;
the file absent, unreadable or the key anything but true means off). A session of the registry **died** when its
process is gone and it did not return: no message with its end id from its own address in its ``notify`` inbox (the
launcher sends one when the session ends, whatever the exit code) and no ``exit_file`` of the entry holding 0. A
launcher still running means the session is only ending (it has not sent its message yet): that is not a death.

``decide`` says what a death is: ``go`` (relaunch), ``unresumable`` (no recorded session id), ``twice`` (the ticket was
relaunched already in this boot) or a reason to do nothing. A relaunch is claimed in a file before the launch
(``~/.gov-os/runtime/relaunch/relaunch:<ticket>:<boot>:<pid>:<start_ticks>``, created with ``O_EXCL``): the claim is
the idempotence, so a pass killed between the launch and its log line never launches again (F1), and any other claim
for the same ticket and boot makes the next death ``twice``, which is never relaunched.

``spawn`` starts ``gov launch <role> <ticket> -- --resume <session id> "<text>"`` in the entry's repository, detached,
with the ``gov`` the pass itself runs as; the text names the checkpoint's next step. The checkpoint is read, never
written: a relaunch does not rewrite it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

CONFIG, CLAIMS, LAUNCH_LOG = "config.json", "relaunch", "relaunch.log"
FALLBACK_STEP = "no checkpoint was recorded for this ticket: read its ticket file and `gov checkpoint --resume`"


def enabled(place: Path) -> tuple[bool, str | None]:
    """``(on, problem)``: whether ``config.json`` switches the relaunch on; the problem names a file that is there
    and cannot be read (the relaunch stays off)."""
    path = place / CONFIG
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return False, None
    except (OSError, ValueError, UnicodeDecodeError) as error:
        return False, f"{path} cannot be read ({error}): the relaunch stays off"
    return isinstance(data, dict) and data.get("relaunch") is True, None


def claim_id(entry: dict) -> str:
    return f"relaunch:{entry.get('ticket')}:{entry.get('boot')}:{entry.get('pid')}:{entry.get('start_ticks')}"


def _prefix(entry: dict) -> str:
    return f"relaunch:{entry.get('ticket')}:{entry.get('boot')}:"


def claimed(place: Path, entry: dict) -> bool:
    return (place / CLAIMS / claim_id(entry)).exists()


def earlier(place: Path, entry: dict) -> bool:
    """Whether another death of this ticket in this boot was claimed already."""
    try:
        names = os.listdir(place / CLAIMS)
    except OSError:
        return False
    own = claim_id(entry)
    return any(name.startswith(_prefix(entry)) and name != own for name in names)


def claim(place: Path, entry: dict) -> bool:
    """Create the claim file; False when it is there already (a pass that claimed and was killed)."""
    folder = place / CLAIMS
    folder.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(folder / claim_id(entry), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return False
    try:
        os.write(fd, (json.dumps({"ticket": entry.get("ticket"), "pid": entry.get("pid"),
                                  "session_id": entry.get("session_id")}) + "\n").encode("utf-8"))
    finally:
        os.close(fd)
    return True


def returned(entry: dict) -> bool:
    """Whether the session returned: its launcher's end message is in the ``notify`` inbox, or its exit file holds 0."""
    from gov.dispatch import inbox, runtime
    exit_file = entry.get("exit_file")
    if isinstance(exit_file, str) and exit_file:
        try:
            if Path(exit_file).read_text(encoding="utf-8", errors="replace").split("\n", 1)[0].strip() == "0":
                return True
        except OSError:
            pass
    notify, address = entry.get("notify"), entry.get("address")
    if not (isinstance(notify, str) and isinstance(address, str)):
        return False
    try:
        wanted = runtime.end_id(entry)
        return any(m.get("id") == wanted and m.get("from") == address for m in inbox.messages(notify))
    except (OSError, inbox.InboxError, KeyError):
        return False


def decide(place: Path, entry: dict, on: bool) -> str:
    """``off``, ``returned``, ``ending`` (its launcher still runs), ``claimed`` (this death was relaunched already),
    ``unresumable``, ``twice`` or ``go``."""
    from gov.resources import machine
    if not on:
        return "off"
    if returned(entry):
        return "returned"
    launcher = entry.get("launcher_pid")
    if isinstance(launcher, int) and not isinstance(launcher, bool) and launcher > 0 and machine.alive(launcher):
        return "ending"
    if claimed(place, entry):
        return "claimed"
    session = entry.get("session_id")
    if not isinstance(session, str) or not session.strip():
        return "unresumable"
    if earlier(place, entry):
        return "twice"
    return "go"


def next_step(entry: dict) -> str:
    """The latest checkpoint's next step of the entry's ticket, read from its repository."""
    from gov.checkpoint import record
    try:
        return str(record.brief(Path(entry["repository"]), entry["ticket"])["next_action"]).strip() or FALLBACK_STEP
    except Exception:  # noqa: BLE001 - a checkpoint that cannot be read never stops the relaunch
        return FALLBACK_STEP


def text(entry: dict) -> str:
    return f"Resume at the recorded next step ({entry.get('ticket')}): {next_step(entry)}"


def spawn(place: Path, entry: dict) -> int:
    """Start the launch, detached; its pid. Its output goes to ``relaunch.log`` beside the state file."""
    command = [sys.executable, "-m", "gov.cli.main", "launch", str(entry["role"]), str(entry["ticket"]),
               "--root", str(entry["repository"]), "--", "--resume", str(entry["session_id"]), text(entry)]
    env = dict(os.environ)
    if isinstance(entry.get("notify"), str) and entry["notify"]:
        env["GOV_MSG_ADDRESS"] = entry["notify"]  # the relaunched session's end message goes to the same watcher
    place.mkdir(parents=True, exist_ok=True)
    with open(place / LAUNCH_LOG, "ab") as log:
        child = subprocess.Popen(command, cwd=entry["repository"], env=env, stdin=subprocess.DEVNULL, stdout=log,
                                 stderr=log, start_new_session=True, close_fds=True)
    return child.pid
