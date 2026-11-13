"""``gov session-watch stop-check waiter|idle [--root <project>]``: the orchestrator's two Stop checks (the package's
docstring has the KPI map).

Run as a Stop hook: the hook's JSON is on standard input; at most one JSON object is printed, ``{"decision": "block",
"reason": ...}`` or ``{"systemMessage": ...}``, or nothing. Always exit code 0 and no envelope (``CHILD_EXIT_CODE``):
any failure is a ``systemMessage`` and a log line, never a traceback and never a trapped session (S4).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HELP = "the orchestrator's Stop checks: stop-check waiter (the inbox waiter armed) or idle (no unblocked work left idle)"
CLASS = "act"
ACT_PATHS = (".gov-runtime/session-watch/**", ".gov-runtime/dispatch/inbox/**")  # + helper-watch's inbox items
CHILD_EXIT_CODE = True
CHECKS = ("waiter", "idle")


def add_arguments(parser) -> None:
    parser.usage = ("gov session-watch stop-check {waiter,idle} [--root <project>]  (the Stop hook's JSON on stdin)\n"
                    "       gov session-watch helper-watch [--every 300] [--max 86400] [--stale-min 30] [--window-h 24] [--once]")
    parser.add_argument("action", choices=("stop-check", "helper-watch"), metavar="{stop-check,helper-watch}",
                        help="the Stop hook's check, or the helper watch")
    parser.add_argument("check", nargs="?", choices=CHECKS, metavar="{waiter,idle}", help="which check (stop-check)")
    for option, default in (("every", 300), ("max", 86400), ("stale-min", 30), ("window-h", 24)):
        parser.add_argument(f"--{option}", type=float, default=default, help=f"helper-watch: {option} (default {default})")
    parser.add_argument("--once", action="store_true", help="helper-watch: one look")


def _decide(root: Path, check: str, data: dict, session: str):
    """The check's ``Verdict`` for the registered session; None for any other session (it says nothing)."""
    from gov.session_watch import checks, config, state, transcript

    if not state.registered(root, session):
        return None
    turn, reason = transcript.read(data)
    context = checks.Context(root, config.load(root), state.read_state(root), data, session, turn, reason)
    return checks.waiter(context) if check == "waiter" else checks.idle(context)


def run(root: Path, args, config: dict) -> int:
    from gov.session_watch import checks, state

    if args.action == "helper-watch":
        from gov.session_watch import helper_watch
        return helper_watch.run(Path(root), args)
    if args.check is None:  # stop-check's check is required, as it was when the parser said so
        print("gov session-watch: stop-check needs a check: waiter or idle", file=sys.stderr)
        return 2
    root, check, session = Path(root), args.check, ""
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise state.CheckError("the hook's input is not a JSON object")
        session = str(data.get("session_id") or "")
        verdict = _decide(root, check, data, session)
    except Exception as error:  # noqa: BLE001 - named to the owner and logged: a check never traps a session
        case = str(error) if type(error).__name__ in ("CheckError", "ConfigError") else f"{type(error).__name__}: {error}"
        verdict = checks.Verdict("error", case[:300], "", {
            "systemMessage": f"Stop check {check} could not run: {case[:300]}. The turn ends unchecked (logged in "
                             f"{state.FOLDER / 'stop-check.log'})."})
    if verdict is not None:
        output = verdict.output
        try:
            state.log(root, session, check, verdict.decision, verdict.case, verdict.detail)
        except state.CheckError as error:  # the block was recorded but cannot be logged: the turn ends, named
            output = {"systemMessage": f"Stop check {check}: {error}. The turn ends unchecked."}
        if output:
            print(json.dumps(output))
    return 0
