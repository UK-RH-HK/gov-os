"""``gov msg send|read|wait|watch`` as a command module (W2-121c, RT-6, RT-7; the convention is in ``gov.cli.main``).

- ``send <to> {wake,notice} <text> [--from <address>] [--id <id>] [--data <json object>]``: one line appended to
  ``~/.gov-os/inbox/<to>/messages.jsonl``; an id already there is a duplicate (exit 0, nothing appended).
- ``read [<address>] [--peek]``: the messages past the mark, which moves past them (not with ``--peek``).
- ``wait [<address>] [--timeout <s>]``: exit 0 with the unread wake messages (the mark unmoved), 124 at the timeout.
- ``watch --to <address> --name <label> (--pid <pid> | --exit-file <path> | --transcript <path> ...)``: one watch
  request to the watch pass's inbox (``runtime``).

The address defaults to ``$GOV_MSG_ADDRESS``. It prints its own output (the envelope under ``--json``) and ends with
its own code (``CHILD_EXIT_CODE``): 1 for a refusal, 124 for a wait that timed out.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HELP = "messages between sessions: send, read, wait (exit 124 at the timeout) and watch"
CLASS = "act"
CHILD_EXIT_CODE = True
EXIT_TIMEOUT = 124
EXIT_CODES = {EXIT_TIMEOUT: "wait: the timeout passed with no unread wake message"}
NIGHT = re.compile(r"^([01]\d|2[0-3]):[0-5]\d-([01]\d|2[0-3]):[0-5]\d$")


def _common(sub) -> None:
    """The command line's shared options, also after the action (absent, they keep the value given before it)."""
    sub.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    for flag in ("--root", "--session", "--role"):
        sub.add_argument(flag, default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def add_arguments(parser) -> None:
    parser.usage = "gov msg {send,read,wait,watch} ..."
    actions = parser.add_subparsers(dest="action", metavar="{send,read,wait,watch}", required=True)
    send = actions.add_parser("send", help="append one message to an inbox")
    send.add_argument("to", metavar="<to>")
    send.add_argument("kind", choices=("wake", "notice"))
    send.add_argument("text", metavar="<text>")
    send.add_argument("--from", dest="sender", metavar="<address>")
    send.add_argument("--id", dest="message_id", metavar="<id>")
    send.add_argument("--data", metavar="<json object>")
    read = actions.add_parser("read", help="print the unread messages and move the mark past them")
    read.add_argument("address", nargs="?", metavar="<address>")
    read.add_argument("--peek", action="store_true", help="print without moving the mark")
    wait = actions.add_parser("wait", help="wait, bounded, for an unread wake message")
    wait.add_argument("address", nargs="?", metavar="<address>")
    wait.add_argument("--timeout", type=float, metavar="<s>")
    watch = actions.add_parser("watch", help="ask the watch pass to message an end or a stall")
    watch.add_argument("--to", required=True, metavar="<address>")
    watch.add_argument("--name", required=True, metavar="<label>")
    target = watch.add_mutually_exclusive_group(required=True)
    target.add_argument("--pid", type=int, metavar="<pid>")
    target.add_argument("--exit-file", metavar="<absolute path>")
    target.add_argument("--transcript", metavar="<file or folder>")
    watch.add_argument("--stall-after", type=int, metavar="<s>")
    watch.add_argument("--night-stall-after", type=int, metavar="<s>")
    watch.add_argument("--night", metavar="<HH:MM-HH:MM>")
    watch.add_argument("--push", metavar="<command>")
    for sub in (send, read, wait, watch):
        _common(sub)


def _emit(args, ok: bool, result: dict, text: str = "", error=None) -> None:
    if getattr(args, "json", False):
        envelope = {"ok": ok, "command": "msg", "result": result, "session": getattr(args, "session", "")}
        if error is not None:
            envelope["error"] = {"code": error.code, "message": error.message, "details": {}}
        print(json.dumps(envelope))
    elif error is not None:
        print(f"gov msg: {error.code}: {error.message}", file=sys.stderr)
    elif text:
        print(text, end="" if text.endswith("\n") else "\n")


def _line(message: dict) -> str:
    return f"{message.get('at')} {message.get('kind')} {message.get('from')}: {message.get('text')}"


def _address(given) -> str:
    from gov.dispatch.inbox import InboxError
    address = given or os.environ.get("GOV_MSG_ADDRESS")
    if not address:
        raise InboxError("MSG_ADDRESS_MISSING", "no address given and no $GOV_MSG_ADDRESS")
    return address


def _watch(args) -> dict:
    from gov.dispatch.inbox import RUNTIME, InboxError, check, send
    from gov.resources import machine

    check(args.to)
    data = {"to": args.to, "name": args.name}
    if args.pid is not None:
        if args.pid <= 0:
            raise InboxError("MSG_WATCH_INVALID", f"--pid {args.pid} is not a process id")
        data.update(form="pid", pid=args.pid)
        found = machine.identity(args.pid) if machine.alive(args.pid) else None
        if found is not None:
            data.update(boot=found["boot"], start_ticks=found["start_ticks"])
    else:
        form, path = ("exit-file", args.exit_file) if args.exit_file is not None else ("transcript", args.transcript)
        if not os.path.isabs(path):
            raise InboxError("MSG_WATCH_INVALID", f"--{form} {path} is not an absolute path")
        data.update(form=form, path=path)
    if args.pid is not None or args.exit_file is not None:
        if any(v is not None for v in (args.stall_after, args.night_stall_after, args.night, args.push)):
            raise InboxError("MSG_WATCH_INVALID", "--stall-after, --night-stall-after, --night and --push go with "
                             "--transcript only")
    else:
        for flag, value in (("--stall-after", args.stall_after), ("--night-stall-after", args.night_stall_after)):
            if value is not None and value <= 0:
                raise InboxError("MSG_WATCH_INVALID", f"{flag} {value} is not a positive number of seconds")
        if args.night is not None and not NIGHT.match(args.night):
            raise InboxError("MSG_WATCH_INVALID", f"--night {args.night} is not HH:MM-HH:MM")
        data.update({key: value for key, value in (("stall_after", args.stall_after),
                     ("night_stall_after", args.night_stall_after), ("night", args.night), ("push", args.push))
                     if value is not None})
    sent = send(RUNTIME, "watch", f"watch {args.name} for {args.to}", data=data)
    return {"id": sent["id"]}


def run(root: Path, args, config: dict) -> int:
    from gov.dispatch import inbox
    from gov.dispatch.inbox import InboxError

    try:
        if args.action == "send":
            data = None
            if args.data is not None:
                try:
                    data = json.loads(args.data)
                except ValueError as error:
                    raise InboxError("MSG_DATA_INVALID", f"--data is not JSON: {error}") from None
            result = inbox.send(args.to, args.kind, args.text, sender=args.sender, message_id=args.message_id,
                                data=data)
            text = (f"duplicate: {result['id']} is already in {result['to']}'s inbox; not appended again"
                    if result["duplicate"] else f"sent {result['id']} to {result['to']}")
            _emit(args, True, result, text)
            return 0
        if args.action == "read":
            result = inbox.read(_address(args.address), peek=args.peek)
            _emit(args, True, result, "".join(_line(m) + "\n" for m in result["messages"]))
            return 0
        if args.action == "wait":
            address = inbox.check(_address(args.address))
            timeout = inbox.WAIT_DEFAULT_S if args.timeout is None else args.timeout
            if timeout > inbox.WAIT_MAX_S:
                print(f"gov msg wait: --timeout {timeout:g} capped at {inbox.WAIT_MAX_S}", file=sys.stderr, flush=True)
                timeout = inbox.WAIT_MAX_S
            found = inbox.wait(address, max(0.0, timeout))
            if found is None:
                _emit(args, True, {"address": address, "messages": [], "timeout": True},
                      f"wait: no unread wake message for {address} after {timeout:g} s")
                return EXIT_TIMEOUT
            _emit(args, True, {"address": address, "messages": found, "timeout": False},
                  "".join(_line(m) + "\n" for m in found))
            return 0
        result = _watch(args)
        _emit(args, True, result, f"watch {args.name} for {args.to}: request {result['id']}")
        return 0
    except InboxError as error:
        _emit(args, False, {}, error=error)
        return 1
