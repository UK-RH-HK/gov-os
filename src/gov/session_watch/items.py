"""The open items, from the project's configuration (S5): the dispatcher's ready list, or a file and a reader.

An item is ``Item(id, title, state)``, the state one of ``open`` (unblocked), ``owner`` (waits on the owner), ``job``
(waits on a running job or another wait) or ``closed``. The file readers: ``lines`` (built in) and
``module.path:function``, called as ``function(path)`` with the item file's absolute path as a string.
"""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

from gov.session_watch.config import Items
from gov.session_watch.state import FOLDER, CheckError

PLAN_TIMEOUT_S = 10
STATES = ("open", "owner", "job", "closed")


class Item(NamedTuple):
    id: str
    title: str
    state: str


def lines_reader(text: str) -> list[Item]:
    """One item per non-``#`` non-empty line, ``<id> <state words>``: ``WAIT owner...`` waits on the owner, any other
    ``WAIT ...`` on something else, ``DONE`` or ``CLOSED`` is closed, anything else is unblocked."""
    out = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        name, _, words = line.strip().partition(" ")
        words = words.strip()
        first, _, rest = words.partition(" ")
        if first.upper() == "WAIT":
            state = "owner" if rest.strip().lower().startswith("owner") else "job"
        else:
            state = "closed" if first.upper() in ("DONE", "CLOSED") else "open"
        out.append(Item(name, words, state))
    return out


def _from_reader(root: Path, spec: Items) -> list[Item]:
    path = (Path(root) / spec.path).resolve()
    if spec.reader == "lines":
        try:
            return lines_reader(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise CheckError(f"the item file {spec.path} cannot be read: {error}") from None
    module, _, name = spec.reader.partition(":")
    sys.path.insert(0, str(root))
    try:
        found = getattr(importlib.import_module(module), name)(str(path))
    except Exception as error:  # a project's reader: whatever it raises is named
        raise CheckError(f"the item reader {spec.reader} failed: {type(error).__name__}: {error}") from None
    finally:
        sys.path.remove(str(root))
    try:
        items = [Item(str(e["id"]), str(e.get("title", "")), e["state"]) for e in found]
    except (TypeError, KeyError):
        raise CheckError(f"the item reader {spec.reader} must return a list of {{id, title, state}}") from None
    if any(i.state not in STATES for i in items):
        raise CheckError(f"the item reader {spec.reader} returned a state outside {', '.join(STATES)}")
    return items


def dispatcher_items(root: Path, running: set) -> list[Item]:
    """Batch 1 of ``gov plan --ready`` as unblocked items (id: the ticket id, title: its name), less ``running``."""
    gov = os.environ.get("GOV_SESSION_WATCH_GOV")
    command = [gov] if gov else [sys.executable, "-m", "gov.cli.main"]
    folder = Path(root) / FOLDER
    try:
        folder.mkdir(parents=True, exist_ok=True)
        handle, ready = tempfile.mkstemp(prefix="plan-ready-", suffix=".txt", dir=folder)
        os.close(handle)
    except OSError as error:
        raise CheckError(f"gov plan not run: {error}") from None
    try:
        try:
            done = subprocess.run([*command, "plan", "--root", str(root), "--ready", ready], capture_output=True,
                                  text=True, timeout=PLAN_TIMEOUT_S, cwd=str(root), stdin=subprocess.DEVNULL)
            text = Path(ready).read_text(encoding="utf-8")
        except subprocess.TimeoutExpired:
            raise CheckError(f"gov plan timed out after {PLAN_TIMEOUT_S} s") from None
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            raise CheckError(f"gov plan could not run: {type(error).__name__}: {error}") from None
    finally:
        try:
            os.unlink(ready)
        except OSError:
            pass
    if done.returncode not in (0, 1):  # 1 is a plan with findings: its list is whole; 2 and more could not run
        why = (done.stderr.strip().splitlines() or [""])[0][:200]
        raise CheckError(f"gov plan failed (exit {done.returncode}){': ' + why if why else ''}")
    batch, out = 0, []
    for line in text.splitlines():
        if line.startswith("# batch"):
            batch += 1
        elif batch == 1 and not line.startswith("#") and len(line.split()) >= 2:
            name, ticket = line.split()[:2]
            if name not in running and ticket not in running:
                out.append(Item(ticket, name, "open"))
    if not batch:
        raise CheckError("gov plan wrote no ready list (no batch in it)")
    return out


def load(root: Path, spec: Items, running: set) -> list[Item]:
    return dispatcher_items(root, running) if spec.source == "dispatcher" else _from_reader(root, spec)
