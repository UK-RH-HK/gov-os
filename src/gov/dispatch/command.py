"""``gov dispatch tick|status|watch|limits [--root <project>] [--json]`` as a command module (part a, the core; the
convention is in ``gov.cli.main``).

- ``tick``: one pass of the dispatcher (``gov.dispatch.run``), run every minute by the host outside any agent session.
- ``status``: prints the last pass's status (the text, or the JSON under ``--json``), and says when it is older than
  three minutes.
- ``watch`` (W2-121c, RT-2, RT-7): one machine-wide watch pass (``gov.dispatch.runtime``); ``--root`` is not read and no
  ``dispatch.yaml`` is needed. Exit 0, or 4 when another pass holds the runtime folder's lock.
- ``limits [--gpu-need-mib <n>]`` (W2-121c, RT-3): the machine detected now and each limit with its rule
  (``gov.dispatch.limits``); with a GPU need, ``admit`` (exit 0), ``wait`` or ``refuse`` (exit 3). No project is read.

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
EXIT_CODES = {EXIT_REFUSED: "the gate, the disk or the forecast refused a start; limits: a GPU need waits or is "
                            "refused", EXIT_LOCKED: "another pass holds the lock"}
ACTIONS = ("tick", "status", "watch", "limits")


def add_arguments(parser) -> None:
    parser.usage = "gov dispatch {tick,status,watch,limits} [--gpu-need-mib <n>] [--root <project>] [--json]"
    parser.add_argument("action", choices=ACTIONS, metavar="{tick,status,watch,limits}",
                        help="tick: one pass; status: print the last pass's status; watch: one machine-wide watch "
                             "pass; limits: the machine's limits")
    parser.add_argument("--gpu-need-mib", type=int, metavar="<n>", help="limits: may a GPU need of <n> MiB start now")


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
    if args.action == "watch":
        return _watch(args)
    if args.action == "limits":
        return _limits(args)
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


def _watch(args) -> int:
    from gov.dispatch import runtime
    try:
        code, state = runtime.watch_pass()
    except Exception as error:  # the state could not be written: the pass failed, the previous state stands
        message = f"{type(error).__name__}: {error}"
        _say(args, False, {}, "", message)
        if not getattr(args, "json", False):
            print(f"gov dispatch watch: PASS FAILED: {message}", file=sys.stderr)
        return 1
    if state is None:
        _say(args, False, {"lock": "held"}, "another watch pass holds the runtime folder's lock: nothing written\n",
             "the lock is held")
        return code
    text = (f"watch pass: {len(state['sessions'])} sessions, {len(state['watches'])} watches, "
            f"{len(state['problems'])} problems\n" + "".join(f"problem: {p}\n" for p in state["problems"]))
    _say(args, True, state, text)
    return code


def _limits(args) -> int:
    from gov.dispatch import limits
    found = limits.detect()
    need = getattr(args, "gpu_need_mib", None)
    if need is not None:
        answer, reason = limits.gpu_answer(found, need)
        result = {"answer": answer, "reason": reason, "gpu_need_mib": need,
                  "gpu_used_mib": found["machine"]["gpu_used_mib"], "gpu_budget_mib": found["limits"]["gpu_budget_mib"]}
        _say(args, True, result, f"{answer}: {reason}\n")
        return 0 if answer == "admit" else EXIT_REFUSED
    m = found["machine"]
    gib = f" ({m['ram_bytes'] / 1024 ** 3:.1f} GiB)" if m["ram_bytes"] else ""
    lines = [f"CPUs {m['cpus']}, RAM {m['ram_bytes']} bytes{gib}, GPU memory {m['gpu_total_mib']} MiB total"
             + (f", {m['gpu_used_mib']} MiB used" if m["gpu_used_mib"] is not None else " (no GPU)")]
    lines += [f"measured {key} {value}" for key, value in found["measured"].items()]
    lines += [f"{key} {value} = {found['rules'][key]}" for key, value in found["limits"].items()]
    lines += [f"problem: {p}" for p in found["problems"]]
    _say(args, True, found, "\n".join(lines) + "\n")
    return 0
