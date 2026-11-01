"""W2-84 -- the code under test is this worktree's ``src/`` (DEC-732).

Every child the cases start (the guard) gets ``PYTHONPATH`` from
``w2_84_support.python_path()``: the runner's own value, else the ``src`` of the
worktree that holds this suite. This case shows which ``gov`` a child imports.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import w2_84_support as s


def test_a_child_imports_gov_from_the_code_under_test(tmp_path):
    sandbox = s.make_sandbox(tmp_path / "w2-84")
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], capture_output=True, text=True,
                          env=s.base_environment(sandbox), cwd=str(sandbox.base), timeout=s.COMMAND_TIMEOUT_S)
    assert done.returncode == 0, done.stderr
    imported = Path(done.stdout.strip()).resolve()
    roots = [Path(p).resolve() for p in s.python_path().split(":") if p]
    assert any(root in imported.parents for root in roots), (
        f"a child imports gov from {imported}, outside PYTHONPATH {roots}")
    if s.python_path() == str(s.REPO_ROOT / "src"):
        assert (s.REPO_ROOT / "src") in imported.parents, f"gov imported from {imported}"
