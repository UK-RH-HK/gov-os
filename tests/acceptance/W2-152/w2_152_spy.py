"""Run ``gov`` under a Python audit hook (PEP 578) that logs every file open, every call that changes the file
system and every process start, one JSON line each, to the log file named first (W2-152 F3, README).

    python3 w2_152_spy.py <log> <gov arguments...>

The log is opened before the hook is installed, so its own writes are not events. The exit code is gov's.
"""

from __future__ import annotations

import json
import os
import sys

CHANGES = {
    "os.mkdir", "os.rename", "os.replace", "os.remove", "os.rmdir", "os.symlink", "os.link", "os.truncate",
    "os.chmod", "os.chown", "os.utime", "os.chflags", "os.lchflags", "os.mkfifo", "os.mknod",
    "shutil.copyfile", "shutil.copymode", "shutil.copystat", "shutil.copytree", "shutil.move", "shutil.rmtree",
    "shutil.make_archive", "shutil.unpack_archive", "tempfile.mkstemp", "tempfile.mkdtemp",
}
PROCESSES = {
    "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.forkpty",
    "os.startfile", "pty.spawn",
}
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND


def _path(value):
    if isinstance(value, (str, bytes, os.PathLike)):
        return os.path.abspath(os.fsdecode(value))
    return None


def main() -> int:
    log_path, argv = sys.argv[1], sys.argv[2:]
    log = open(log_path, "w", encoding="utf-8", buffering=1)

    def hook(event, args):
        try:
            if event == "open":
                path = _path(args[0]) if args else None
                mode = args[1] if len(args) > 1 and isinstance(args[1], str) else ""
                flags = args[2] if len(args) > 2 and isinstance(args[2], int) else 0
                if path is None:
                    return
                write = any(c in mode for c in "wax+") or bool(flags & WRITE_FLAGS)
                log.write(json.dumps({"event": "open", "path": path, "write": write}) + "\n")
            elif event in CHANGES:
                log.write(json.dumps({"event": event, "args": [repr(a)[:300] for a in args]}) + "\n")
            elif event in PROCESSES:
                log.write(json.dumps({"event": event, "args": [repr(a)[:300] for a in args]}) + "\n")
        except Exception:  # the hook never breaks the run it watches
            pass

    sys.addaudithook(hook)
    sys.argv = ["gov", *argv]
    import runpy

    try:
        runpy.run_module("gov.cli.main", run_name="__main__", alter_sys=True)
        code = 0
    except SystemExit as stop:
        code = stop.code if isinstance(stop.code, int) else (0 if stop.code is None else 1)
    sys.stdout.flush()
    log.flush()
    return code


if __name__ == "__main__":
    sys.exit(main())
