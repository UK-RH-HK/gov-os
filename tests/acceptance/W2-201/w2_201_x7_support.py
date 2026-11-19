"""Support code for W2-201's fix line X7 (DEC-1219 (5)): the relaunch keeps the kind.

It stands on W2-205's support (``tests/acceptance/W2-205/w2_205_support.py``, imported as ``rt``): its fixture machine
``Home`` (a HOME of its own, the planted load and gate, ``gov dispatch watch`` as the watch pass, a dead registry entry
planted as the launcher writes one, the relaunch key in ``~/.gov-os/runtime/config.json``) and its relaunch fixture
``Rig`` (W2-184's launch sandbox and recording stand-in CLI on the same HOME). And on W2-121c's ``LaunchKit``, whose
stand-in CLI captures the session's registry entry when it starts. Nothing of those modules is changed.

Added here: the stand-in ``gov`` that records its argv. The pass starts the relaunch in the entry's repository with
the ``gov`` it runs as (``python3 -m gov.cli.main``, W2-205's interface), so the stand-in is a package ``gov`` planted
in that repository, which ``python3 -m`` finds first from its working folder; a ``gov`` on the pass's ``PATH`` records
the same way, so either form of start is seen. Each start appends one JSON line ``{"argv", "cwd"}``.
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-205"))

import w2_205_support as rt  # noqa: E402

base = rt.base  # w2_121c_support
write, poll = rt.write, rt.poll

FIX_LINE = "the count is off by one when the list is empty"
CHORE_LINE = "tidy the release notes' headings (tests unchanged and green)"
ON = {"relaunch": True}
LEAD_ADDRESS = "lead:DAEO-x7ld"
CHORE_LABEL = "chore-1a2b3c4d"
WORKER, LEAD = "engineer", "orchestrator"

_RECORDER = """import json, os, sys
with open({log!r}, "a", encoding="utf-8") as out:
    out.write(json.dumps({{"argv": sys.argv[1:], "cwd": os.getcwd()}}) + "\\n")
"""


def stand_in_repository(folder, log) -> Path:
    """A repository folder whose ``gov`` package records its argv to ``log`` and starts nothing."""
    folder = Path(folder)
    write(folder / "gov" / "__init__.py", "")
    write(folder / "gov" / "cli" / "__init__.py", "")
    write(folder / "gov" / "cli" / "main.py", _RECORDER.format(log=str(log)))
    return folder


def stand_in_path_gov(home, log) -> None:
    """``gov`` on the pass's ``PATH`` (the fixture machine's stub folder) records its argv too."""
    path = home.bin / "gov"
    write(path, f"#!{sys.executable}\n" + _RECORDER.format(log=str(log)))
    path.chmod(0o755)


def recorded(log) -> list[dict]:
    log = Path(log)
    if not log.is_file():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


class Machine:
    """A fixture machine with the relaunch on, a stand-in repository and the stand-in ``gov``."""

    def __init__(self, folder):
        self.home = rt.Home(Path(folder) / "machine")
        self.log = self.home.base / "gov-argv.jsonl"
        self.repository = stand_in_repository(self.home.base / "repository", self.log)
        stand_in_path_gov(self.home, self.log)
        self.home.config(ON)

    def died(self, role, ticket, **kind):
        """A dead registry entry of ``role`` on ``ticket`` (a ticket id, or a chore's label), with a session id and
        the ``kind`` keys given (none for an entry from before the change)."""
        session_id = str(uuid.uuid4())
        entry = self.home.died(ticket, self.repository, LEAD_ADDRESS, session_id, role=role, **kind)
        return entry, session_id

    def spawned(self, seconds=15.0) -> list[dict]:
        """The stand-in's starts, once there is one (at most ``seconds``), and a moment more for a second."""
        poll(lambda: recorded(self.log), seconds)
        poll(lambda: False, 0.5)
        return recorded(self.log)

    def cleanup(self):
        self.home.cleanup()


def split(argv) -> tuple[list[str], list[str]]:
    """``(the words before the first --, the words after it)``."""
    assert "--" in argv, f"the spawned command has no -- before the CLI's arguments: {argv}"
    at = argv.index("--")
    return argv[:at], argv[at + 1:]


def without_pairs(words, *flags) -> tuple[list[str], dict]:
    """``words`` less each ``flag`` and the value after it: ``(what is left, {flag: [values]})``."""
    left, values, skip = [], {flag: [] for flag in flags}, False
    for index, word in enumerate(words):
        if skip:
            skip = False
            continue
        if word in flags:
            values[word].append(words[index + 1] if index + 1 < len(words) else None)
            skip = True
            continue
        left.append(word)
    return left, values
