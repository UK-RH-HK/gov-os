"""A stand-in for run 6's Case D (NC-2, P1-W2-88-NC-1 (a); ``test_w2_88_nc1_commit.py``): an interrupt the moment A9's ``git add`` of
its copies has returned.

Python loads it as ``sitecustomize`` in the child process when this folder is first on that child's ``PYTHONPATH`` (the case sets
it through the adoption's ``extra_env``). A9 stages its copies with a ``git add`` subprocess: that is the seam. This wraps
``subprocess.Popen`` (``subprocess.run``, ``check_output``, ``check_call`` and ``call`` all go through it) so that the **first**
``git`` call whose arguments hold ``add`` and at least one path of A9's copy plan (``W2_88_NC2_COPIES``, a JSON list of paths
relative to the repository) is let run to its end, and ``KeyboardInterrupt`` is raised the moment the call returns to its caller
(``communicate`` or ``wait`` returns). It fires once.

It reports on stderr: ``nc2-plant: fired <json argv>`` when it has fired (a case where it did not fire fails as "the plant did not
take") and, for every ``git`` call that ran, ``nc2-git: <json argv>`` (so a plant that missed A9's staging call can be read).
"""

import json
import os
import shlex
import subprocess
import sys

COPIES = tuple(json.loads(os.environ.get("W2_88_NC2_COPIES") or "[]"))
STATE = {"fired": False}


def _argv(args):
    if isinstance(args, (str, bytes, os.PathLike)):
        args = shlex.split(os.fsdecode(args))
    try:
        return [os.fsdecode(a) for a in args]
    except TypeError:
        return []


def _is_git(argv):
    return bool(argv) and os.path.basename(argv[0]) == "git"


def _stages_a_copy(argv):
    if not _is_git(argv) or "add" not in argv:
        return False
    return any(a == c or a.endswith("/" + c) for a in argv for c in COPIES)


def _install():
    real = subprocess.Popen

    class Popen(real):
        def __init__(self, args, *more, **keywords):
            argv = _argv(args)
            self._nc2_argv = argv if _is_git(argv) else None
            self._nc2_hit = (not STATE["fired"]) and _stages_a_copy(argv)
            if self._nc2_argv is not None:
                sys.stderr.write("nc2-git: " + json.dumps(argv) + "\n")
                sys.stderr.flush()
            super().__init__(args, *more, **keywords)

        _nc2_inside = False

        def _nc2_after(self):
            if self._nc2_hit and not self._nc2_inside and not STATE["fired"] and self.returncode is not None:
                STATE["fired"] = True
                sys.stderr.write("nc2-plant: fired " + json.dumps(self._nc2_argv) + "\n")
                sys.stderr.flush()
                raise KeyboardInterrupt

        def communicate(self, *more, **keywords):
            self._nc2_inside = True          # communicate waits internally: the interrupt comes when it returns
            try:
                result = super().communicate(*more, **keywords)
            finally:
                self._nc2_inside = False
            self._nc2_after()
            return result

        def wait(self, *more, **keywords):
            result = super().wait(*more, **keywords)
            self._nc2_after()
            return result

    subprocess.Popen = Popen


try:
    _install()
except Exception as exc:  # noqa: BLE001
    sys.stderr.write(f"standin_nc2: not installed: {exc!r}\n")
