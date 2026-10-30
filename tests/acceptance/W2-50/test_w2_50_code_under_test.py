"""DEC-732: the suite's child processes run this worktree's ``gov``.

Every process under test gets ``PYTHONPATH`` from ``w2_50_support.python_path``:
the runner's own value (set per command, DEC-732), else this worktree's
``src``. This case shows which ``gov`` such a child imports.
"""

from __future__ import annotations

import subprocess
import sys

import w2_50_support as support


def test_a_child_process_imports_this_worktrees_gov(sandbox):
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], capture_output=True, text=True,
                          cwd=str(sandbox.elsewhere), env=support.base_environment(sandbox), timeout=60)
    assert done.returncode == 0, done.stderr
    imported = done.stdout.strip()
    assert imported.startswith(str(support.REPO_ROOT / "src") + "/"), (
        f"a child process imports gov from {imported}, not from this worktree's src ({support.REPO_ROOT / 'src'}): "
        "run the suite with PYTHONPATH set to this worktree's src (DEC-732)")
