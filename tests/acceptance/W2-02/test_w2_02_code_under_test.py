"""DEC-732: the processes this suite starts import this worktree's ``gov``, not the editable install's."""

from __future__ import annotations

import subprocess
import sys

import w2_02_support as support


def test_the_processes_the_suite_starts_run_this_worktrees_code(tmp_path):
    """``gov.__file__`` in a process started with the suite's environment lies under this worktree's ``src/``.
    Passes today."""
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], cwd=str(tmp_path),
                          env=support.env(tmp_path), capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().startswith(str(support.SRC) + "/"), \
        f"the suite's processes import gov from {done.stdout.strip()}, not from {support.SRC}"
