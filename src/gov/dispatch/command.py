"""``gov dispatch tick|status [--root <project>] [--json]`` as a command module (part a, the core; the convention is in
``gov.cli.main``).

- ``tick``: one pass of the dispatcher (``gov.dispatch.run``), run every minute by the host outside any agent session.
- ``status``: prints the last pass's status (the text, or the JSON under ``--json``), and says when it is older than
  three minutes.

Exit codes: 0 a pass done or nothing to do (``status``: always 0), 3 the gate, the disk or the forecast refused a start
(named in the status), 4 another pass holds the lock. 1 (the pass failed) and 2 (a configuration error) are the command
line's own reserved codes: the command ends with them itself, as ``gov plan`` does (``CHILD_EXIT_CODE``: ``run`` returns
the exit code and the command prints its own output, the envelope under ``--json``), because ``EXIT_CODES`` may not
declare 0, 1 or 2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HELP = "the dispatcher: tick (one pass) or status (the last pass's status)"
CLASS = "act"
ACT_PATHS = (".gov-runtime/dispatch/**",)
CHILD_EXIT_CODE = True
EXIT_REFUSED, EXIT_LOCKED = 3, 4
EXIT_CODES = {EXIT_REFUSED: "the gate, the disk or the forecast refused a start", EXIT_LOCKED: "another pass holds the lock"}
ACTIONS = ("tick", "status")


def add_arguments(parser) -> None:
    parser.usage = "gov dispatch {tick,status} [--root <project>] [--json]"
    parser.add_argument("action", choices=ACTIONS, metavar="{tick,status}",
                        help="tick: one pass; status: print the last pass's status")


def _say(args, ok: bool, result: dict, text: str, error: str | None = None) -> None:
    if getattr(args, "json", False):
        envelope = {"ok": ok, "command": "dispatch", "result": result, "session": getattr(args, "session", "")}
        if error is not None:
            envelope["error"] = {"code": "DISPATCH", "message": error, "details": {}}
        print(json.dumps(envelope))
    elif text:
        print(text, end="" if text.endswith("\n") else "\n")


def run(root: Path, args, config: dict) -> int:
    from gov.dispatch import run as dispatch
    from gov.dispatch import state as states
    from gov.dispatch import status

    root = Path(root)
    if args.action == "status":
        found = status.read(states.State(root), states.now())
        if found is None:
            _say(args, True, {"ok": None, "stale": None}, "no pass has run: there is no status yet\n")
            return 0
        text = states.State(root).text("status.txt")
        if found["stale"]:
            text = f"STALE: the last pass is older than three minutes ({found['age_s']} s ago)\n" + text
        _say(args, True, found, text)
        return 0
    try:
        code, data = dispatch.tick(root)
    except Exception as error:  # the status could not be written, or the lock could not be taken
        message = f"{type(error).__name__}: {error}"
        _say(args, False, {}, "", message)
        if not getattr(args, "json", False):
            print(f"gov dispatch: PASS FAILED: {message}", file=sys.stderr)
        return 1
    if data is None:
        _say(args, False, {"lock": "held"}, "another pass holds tick.lock: nothing written\n", "the lock is held")
        return code
    from gov.dispatch import status as render
    _say(args, code in (0, 3), data, render.render(data))
    return code
