"""The runtime folder ``.gov-runtime/session-watch/``: the registered session, the stand-by note, the once-a-turn state
and the log. Read here; only ``state.json`` and ``stop-check.log`` are written (``session.txt`` never)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

FOLDER = Path(".gov-runtime") / "session-watch"


class CheckError(Exception):
    """A reading or writing the check depends on failed: named to the owner and logged, and the turn ends."""


def now() -> float:
    value = os.environ.get("GOV_SESSION_WATCH_NOW")
    return float(value) if value else time.time()


def registered(root: Path, session_id: str) -> bool:
    """Whether ``session_id`` is the registered orchestrator session; no file, or one that cannot be read, is no."""
    try:
        text = (Path(root) / FOLDER / "session.txt").read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return False
    return bool(text) and text == session_id


def standby_age(root: Path) -> float | None:
    """Seconds since the stand-by note was written (its mtime), or None without one."""
    try:
        return now() - (Path(root) / FOLDER / "standby.txt").stat().st_mtime
    except OSError:
        return None


def read_state(root: Path) -> dict:
    """``{check: {session, turn, at}}``; a missing file is an empty state, one that cannot be read or parsed an error."""
    file = Path(root) / FOLDER / "state.json"
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as error:
        raise CheckError(f"{FOLDER / 'state.json'} cannot be read: {type(error).__name__}: {error}") from None
    if not isinstance(data, dict) or not all(isinstance(v, dict) for v in data.values()):
        raise CheckError(f"{FOLDER / 'state.json'} is not a mapping of checks")
    return data


def write_state(root: Path, state: dict) -> None:
    folder = Path(root) / FOLDER
    temporary = folder / f".state.{os.getpid()}.tmp"
    try:
        folder.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps(state) + "\n", encoding="utf-8")
        os.replace(temporary, folder / "state.json")
    except OSError as error:
        raise CheckError(f"{FOLDER / 'state.json'} cannot be written: {error}") from None


def log(root: Path, session_id: str, check: str, decision: str, case: str, detail: str = "") -> None:
    """One tab-separated line: time, session, check, decision, case, detail."""
    fields = [time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(now())), session_id[:8], check, decision, case, detail]
    line = "\t".join(" ".join(str(f).split()) for f in fields)[:2000]
    try:
        folder = Path(root) / FOLDER
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / "stop-check.log", "a", encoding="utf-8") as stream:
            stream.write(line + "\n")
    except OSError as error:
        raise CheckError(f"{FOLDER / 'stop-check.log'} cannot be written: {error}") from None
