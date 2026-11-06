"""Runs ``gov`` in this process under an audit hook and writes what it did to a report (W2-129 S1, F2).

    python3 w2_129_probe.py <report.json> <gov arguments ...>

The report holds the exit code, every process started (``subprocess.Popen``, ``os.system``, ``os.exec*``,
``os.posix_spawn``), every socket call, every file opened for writing or created, renamed or removed, and the
modules loaded. Recording stops before the report itself is written. Run it with ``PYTHONDONTWRITEBYTECODE=1`` so
the interpreter's own byte-code cache is no write of the command's.
"""

from __future__ import annotations

import json
import os
import sys

REPORT, ARGV = sys.argv[1], sys.argv[2:]
EVENTS: dict[str, list] = {"processes": [], "sockets": [], "writes": []}
STATE = {"recording": True}
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
SOCKETS = ("socket.connect", "socket.getaddrinfo", "socket.bind", "socket.sendto", "socket.sendmsg",
           "socket.gethostbyname", "socket.gethostbyaddr", "socket.__new__")
CHANGES = ("os.rename", "os.replace", "os.remove", "os.rmdir", "os.mkdir", "os.symlink", "os.link", "os.truncate",
           "shutil.copyfile", "shutil.copytree", "shutil.move", "shutil.rmtree", "os.chmod", "os.utime")
SPAWNS = ("os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.forkpty")


def _name(value) -> str:
    return os.fsdecode(value) if isinstance(value, (str, bytes, os.PathLike)) else repr(value)


def hook(event: str, args: tuple) -> None:
    if not STATE["recording"]:
        return
    if event == "subprocess.Popen":
        executable, argv = args[0], list(args[1] or [])
        EVENTS["processes"].append([_name(executable or (argv[0] if argv else "")), [_name(a) for a in argv]])
    elif event in SPAWNS:
        EVENTS["processes"].append([event, [repr(args)[:300]]])
    elif event in SOCKETS:
        EVENTS["sockets"].append([event, repr(args)[:300]])
    elif event == "open":
        path, mode, flags = args
        if isinstance(path, int):
            return
        if any(c in (mode or "") for c in "wax+") or (isinstance(flags, int) and flags & WRITE_FLAGS):
            EVENTS["writes"].append(os.path.abspath(_name(path)))
    elif event in CHANGES:
        target = args[0] if args else ""
        EVENTS["writes"].append(os.path.abspath(_name(target)) if not isinstance(target, int) else repr(args))


sys.addaudithook(hook)

code = 99
try:
    from gov.cli import main as cli

    code = cli.main(ARGV)
except SystemExit as stop:
    code = stop.code if isinstance(stop.code, int) else 1
finally:
    STATE["recording"] = False
    with open(REPORT, "w", encoding="utf-8") as handle:
        json.dump({"code": code, **EVENTS, "modules": sorted(sys.modules)}, handle)
sys.exit(0)
