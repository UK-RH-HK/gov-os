"""Pytest plugin for W2-67 batch 1b's planted faults (throwaway; ``-p w2_67b_plant``).

Wraps ``w1_07_support.write_launcher`` in the test process: every launcher a case writes first imports
``w2_67b_child`` from this folder and applies the faults named in ``W2_67_PLANT`` (comma-separated), in that
``gov`` process only. The tracked tree is never written.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PLANT_DIR = str(Path(__file__).resolve().parent)
_W1_07 = "/home/usain/gov-os-worktrees/W2-67/tests/acceptance/W1-07"


def pytest_configure(config):
    if _W1_07 not in sys.path:
        sys.path.insert(0, _W1_07)
    import w1_07_support

    faults = [name for name in os.environ.get("W2_67_PLANT", "").split(",") if name]
    if not faults or getattr(w1_07_support.write_launcher, "_w2_67b", False):
        return
    original = w1_07_support.write_launcher

    def write_launcher(code_root, sandbox):
        launcher = original(code_root, sandbox)
        header = (
            "import sys as _plant_sys\n"
            f"_plant_sys.path.insert(0, {PLANT_DIR!r})\n"
            "import w2_67b_child as _plant_child\n"
            f"_plant_child.apply({faults!r})\n"
        )
        launcher.write_text(header + launcher.read_text(encoding="utf-8"), encoding="utf-8")
        return launcher

    write_launcher._w2_67b = True
    w1_07_support.write_launcher = write_launcher
    config._w2_67b_faults = faults

    # The recovery check runs as ``sh -c "python3 -m gov.rebuild.check"``, not through a launcher: that one
    # process gets ``site/`` first on its PYTHONPATH, whose sitecustomize applies the same faults.
    import subprocess
    original_run = subprocess.run

    def run(args, *rest, **kwargs):
        env = kwargs.get("env")
        if (isinstance(args, (list, tuple)) and len(args) == 3 and args[0] == "sh"
                and "gov.rebuild.check" in str(args[2]) and isinstance(env, dict)):
            env = dict(env)
            env["PYTHONPATH"] = os.pathsep.join((str(Path(PLANT_DIR) / "site"), env.get("PYTHONPATH", "")))
            env["W2_67_PLANT"] = ",".join(faults)
            kwargs["env"] = env
        return original_run(args, *rest, **kwargs)

    subprocess.run = run


def pytest_report_header(config):
    return f"W2-67 batch 1b plant: {os.environ.get('W2_67_PLANT', '')!r} from {PLANT_DIR}"
