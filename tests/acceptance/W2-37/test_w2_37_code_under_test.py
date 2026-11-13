"""DEC-732: the processes this suite starts run this worktree's own ``src/``."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import w2_37_support as support


def test_the_processes_the_suite_starts_run_this_worktrees_code(box):
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], cwd=str(box.elsewhere),
                          env=support.child_env(box), capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    loaded = Path(done.stdout.strip()).resolve()
    assert support.SRC.resolve() in loaded.parents, \
        f"a started process imports gov from {loaded}, not from this worktree's {support.SRC}"
