"""Lead's plant for batch 8's red check: the real ``w2_67_codegraph`` with ``release`` switched off (the fault:
the fixtures leave the code-graph daemon folders they make). Placed first on the nested run's PYTHONPATH."""
import os
import pathlib

_REAL = pathlib.Path("/home/usain/gov-os-worktrees/W2-67/tests/acceptance/W1-27/w2_67_codegraph.py")
exec(compile(_REAL.read_text(encoding="utf-8"), str(_REAL), "exec"))


def release(since: int = 0):  # noqa: F811 - the planted fault
    marker = os.environ.get("LEAD_PLANT8_MARKER")
    if marker:
        with open(marker, "a", encoding="utf-8") as out:
            out.write("release switched off\n")
