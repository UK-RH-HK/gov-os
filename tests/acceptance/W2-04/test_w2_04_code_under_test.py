"""DEC-732: every process the suite starts runs the ``src/`` of the tree the suite stands in. Passes today."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import w2_04_support as s


def test_the_processes_the_suite_starts_run_this_trees_code(api):
    for env in (api.env(), api.env(mode="log", watch=(s.SRC, "gov/__init__.py"))):
        done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=env,
                              capture_output=True, text=True, cwd=str(api.workdir / "elsewhere"), timeout=60)
        assert done.returncode == 0, done.stderr
        found = Path(done.stdout.strip().splitlines()[0]).resolve()
        assert found == (s.SRC / "gov" / "__init__.py").resolve(), \
            f"a child process imports gov from {found}, not from {s.SRC}"
