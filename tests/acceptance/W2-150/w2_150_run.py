"""Run Python in a fresh subprocess on this tree's own ``src`` (W2-150 S3 and S4)."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from w2_150_walk import SRC


def run_py(code: str, *, home=None, cwd=None, timeout: int = 120) -> subprocess.CompletedProcess:
    """``python3 -c code`` with ``PYTHONPATH`` the tree's ``src`` only."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if home is not None:
        env["HOME"] = str(home)
    return subprocess.run([sys.executable, "-c", code], env=env, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout)


def run_json(code: str, **kwargs):
    """Run ``code``, which prints one JSON value as its last stdout line; return that value."""
    done = run_py(code, **kwargs)
    assert done.returncode == 0, f"exit {done.returncode}\nstdout:\n{done.stdout}\nstderr:\n{done.stderr}"
    return json.loads(done.stdout.strip().splitlines()[-1])
