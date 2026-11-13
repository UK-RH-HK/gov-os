"""``gov wait <exit-file> [<max-s>]`` as a command module (W2-160). The package's docstring has the KPI map.

Exit: the job's code (modulo 256) when its exit file is there; 124 RUNNING at ``<max-s>``; 125 GONE (the job's process,
by its pid file, ended without an exit file); 2 a usage error, a ``<max-s>`` that is no number, or an exit file holding no
number. Prints its own lines, no envelope (``CHILD_EXIT_CODE``).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HELP = "wait, bounded, for a job's exit file; its pid file (beside it) tells a gone job; exit 124 running, 125 gone"
CLASS = "read"
CHILD_EXIT_CODE = True
CAP = 570


def add_arguments(parser) -> None:
    parser.usage = "gov wait <exit-file> [<max-s>]"
    parser.add_argument("exit_file", nargs="?", metavar="<exit-file>", help="the job's exit file (<base>.exit)")
    parser.add_argument("max_s", nargs="?", metavar="<max-s>", help=f"seconds to wait (default and ceiling {CAP})")


def _number(name: str, default: float) -> float:
    try:
        value = float(os.environ.get(name, ""))
    except ValueError:
        return default
    return value if value > 0 else default


def _result_object(text: str) -> dict | None:
    for line in reversed(text.splitlines()):
        if line.strip().startswith("{"):
            try:
                found = json.loads(line)
            except ValueError:
                continue
            if isinstance(found, dict) and "result" in found:
                return found
    return None


def _tail(exit_file: str, base: str) -> None:
    lines = int(_number("GOV_WAIT_LINES", 30))
    log = os.environ.get("GOV_WAIT_LOG") or next(
        (c for c in (base + ".log", base + ".json", base + ".txt") if Path(c).is_file()), "")
    if not log or not Path(log).is_file():
        print(f"wait: no log beside {exit_file}")
        return
    text = Path(log).read_text(encoding="utf-8", errors="replace")
    print(f"--- tail of {log}")
    found = _result_object(text)
    if found is not None:
        print(f"session_id={found.get('session_id')} is_error={found.get('is_error')} turns={found.get('num_turns')}")
        print(str(found.get("result"))[-4000:])
    else:
        print("\n".join(line[:400] for line in text.splitlines()[-lines:]))
    if Path(base + ".summary").is_file():
        print(f"--- {base}.summary")
        print(Path(base + ".summary").read_text(encoding="utf-8", errors="replace"), end="")


def run(root: Path, args, config: dict) -> int:
    from gov.wait import liveness

    exit_file, given = args.exit_file, args.max_s
    if not exit_file:
        print("usage: gov wait <exit-file> [<max-s>]", file=sys.stderr)
        return 2
    if given is not None and not (given.isascii() and given.isdigit()):
        print(f"wait: <max-s> is not a number: {given}", file=sys.stderr)
        return 2
    limit = CAP if given is None else int(given)
    if limit > CAP:
        print(f"wait: <max-s> {limit} capped at {CAP}", file=sys.stderr, flush=True)
        limit = CAP
    every = _number("GOV_WAIT_EVERY", 5)
    base = exit_file[:-len(".exit")] if exit_file.endswith(".exit") else exit_file
    exit_path, pid_file = Path(exit_file), base + ".pid"
    written = lambda: exit_path.is_file() and exit_path.stat().st_size > 0  # noqa: E731
    end = time.monotonic() + limit
    while not written():
        pid = liveness.read_pid(pid_file)
        if pid is not None and liveness.gone(pid):
            time.sleep(min(1.0, every / 2))  # the job's last act may be the exit file itself
            if written():
                break
            _tail(exit_file, base)
            print(f"wait: GONE: the job's process ({pid}) exited without writing {exit_file}", flush=True)
            return 125
        left = end - time.monotonic()
        if left <= 0:
            print(f"wait: RUNNING after {limit}s: {exit_file}", flush=True)
            return 124
        time.sleep(min(every, left))
    first = exit_path.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
    code = "".join(first.split())
    _tail(exit_file, base)
    if not (code.isascii() and code.isdigit()):
        print(f"wait: {exit_file} holds no exit code: '{code}'", flush=True)
        return 2
    print(f"wait: DONE exit {code} ({exit_file})", flush=True)
    return int(code) % 256
