"""The file-access spy (F1): loaded by every Python child that has this folder on its PYTHONPATH.

An audit hook logs, to the file named by ``W172_SPY``, one JSON line for each ``subprocess.Popen`` (the argument list),
and for each ``open``, ``os.listdir``, ``os.scandir`` and ``os.walk`` of a path under ``W172_SPY_ROOT`` (the sets root,
as given and as its real path): the process id, its full command line (``sys.orig_argv``), the event and the path. The
test keeps the lines of the driver's own process. Nothing is logged when ``W172_SPY`` is unset.
"""
import json
import os
import sys

_PATH = os.environ.get("W172_SPY")
_ROOT = os.environ.get("W172_SPY_ROOT")
_busy = False


def _under(arg):
    if not _ROOT or not isinstance(arg, (str, bytes)):
        return False
    text = os.fsdecode(arg)
    forms = {os.path.abspath(text), os.path.realpath(text)}
    roots = {os.path.abspath(_ROOT), os.path.realpath(_ROOT)}
    return any(f == r or f.startswith(r.rstrip("/") + "/") for f in forms for r in roots)


def _log(kind, arg):
    global _busy
    _busy = True
    try:
        line = json.dumps({"pid": os.getpid(), "argv": list(getattr(sys, "orig_argv", sys.argv)), "kind": kind,
                           "arg": arg}) + "\n"
        fd = os.open(_PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            os.write(fd, line.encode())
        finally:
            os.close(fd)
    finally:
        _busy = False


def _hook(event, args):
    if _busy:
        return
    try:
        if event == "subprocess.Popen":
            _log("popen", [str(a) for a in (args[1] if isinstance(args[1], (list, tuple)) else [args[1]])])
        elif event in ("open", "os.listdir", "os.scandir", "os.walk") and args and _under(args[0]):
            _log(event, os.fsdecode(args[0]))
    except Exception:  # noqa: BLE001: a spy never breaks the program it watches
        pass


if _PATH:
    sys.addaudithook(_hook)
    _log("hello", None)
