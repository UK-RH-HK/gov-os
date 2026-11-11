"""Run ``python3 -m gov.memaudit <args>`` with every file access logged (W2-170 S4, F3; F1 S1's "no real
~/gov-os-eval is opened").

Usage: ``python3 w2_170_open_log.py <log file> <memaudit arguments...>``. An audit hook (``sys.addaudithook``) records
the path of every ``open`` event (the built-in ``open`` and ``os.open``), every ``os.*`` event whose first argument
is a path (``os.listdir``, ``os.scandir``, ``os.mkdir``, ``os.rename``, ``os.remove``, ...) and the arguments and
working folder of every ``subprocess.Popen``; then ``gov.memaudit`` runs as ``__main__`` with ``runpy``. The log
holds one entry per line, ``<event>\\t<path or argument>``; the child exits with the tool's own exit code.
"""

import os
import runpy
import sys

LOG = sys.argv[1]
ARGS = sys.argv[2:]
entries = []


def _text(value):
    if isinstance(value, (str, bytes, os.PathLike)):
        try:
            return os.fsdecode(value)
        except (TypeError, ValueError):
            return None
    return None


def _hook(event, args):
    if event == "open" or event.startswith("os.") or event.startswith("shutil."):
        if args:
            path = _text(args[0])
            if path is not None:
                entries.append((event, os.path.join(os.getcwd(), path) if not os.path.isabs(path) else path))
            if event in ("os.rename", "os.replace", "os.link", "os.symlink", "shutil.copyfile") and len(args) > 1:
                second = _text(args[1])
                if second is not None:
                    entries.append((event, second))
    elif event == "subprocess.Popen":
        executable, argv, cwd = args[0], args[1], args[2]
        for value in [executable, cwd, *(argv if isinstance(argv, (list, tuple)) else [argv])]:
            text = _text(value)
            if text is not None:
                entries.append((event, text))


sys.addaudithook(_hook)
sys.argv = ["gov.memaudit", *ARGS]
code = 0
try:
    runpy.run_module("gov.memaudit", run_name="__main__", alter_sys=True)
except SystemExit as stop:
    code = stop.code if isinstance(stop.code, int) else (0 if stop.code is None else 1)
except BaseException as error:  # noqa: BLE001 - the tool's own failure is its exit, the log is still written
    code = 99
    entries.append(("runner-error", type(error).__name__))
finally:
    text = "".join(f"{event}\t{path}\n" for event, path in list(entries))
    with open(LOG, "w", encoding="utf-8") as f:
        f.write(text)
sys.exit(code)
