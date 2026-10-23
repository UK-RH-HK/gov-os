"""Pytest plugin for W2-67 batch 2's planted faults (throwaway; ``-p w2_67c_plant``, this folder on PYTHONPATH).

Wraps ``w1_07_support.write_launcher`` in the test process: every launcher a case writes first imports
``w2_67c_child`` from this folder and applies the faults named in ``W2_67_PLANT`` (comma-separated), in that
``gov`` process only (and, for a fault of a declared check, in that check's own process). The tracked tree is
never written.
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
    if not faults or getattr(w1_07_support.write_launcher, "_w2_67c", False):
        return
    original = w1_07_support.write_launcher

    def write_launcher(code_root, sandbox):
        launcher = original(code_root, sandbox)
        header = (
            "import sys as _plant_sys\n"
            f"_plant_sys.path.insert(0, {PLANT_DIR!r})\n"
            "import w2_67c_child as _plant_child\n"
            f"_plant_child.apply({faults!r})\n"
        )
        launcher.write_text(header + launcher.read_text(encoding="utf-8"), encoding="utf-8")
        return launcher

    write_launcher._w2_67c = True
    w1_07_support.write_launcher = write_launcher

    # W2-02's support runs the declared schema check as ``sh -c "python3 -m gov.check.schema"``, not through a
    # launcher: for a fault of that module's text, that one command runs the module with the fault in memory.
    sys.path.insert(0, PLANT_DIR)
    import subprocess

    import w2_67c_child
    schema_faults = [name for name in faults
                     if name in w2_67c_child.CHILD_TEXT and w2_67c_child.CHILD_TEXT[name][0] == "gov.check.schema"]
    if not schema_faults:
        return
    original_run = subprocess.run

    def run(args, *rest, **kwargs):
        if (isinstance(args, (list, tuple)) and len(args) == 3 and args[0] == "sh"
                and str(args[2]).strip() == "python3 -m gov.check.schema"):
            args = ["sh", "-c", f"python3 {w2_67c_child.RUN_PATCHED} {schema_faults[0]}"]
        return original_run(args, *rest, **kwargs)

    subprocess.run = run


def pytest_report_header(config):
    return f"W2-67 batch 2 plant: {os.environ.get('W2_67_PLANT', '')!r} from {PLANT_DIR}"
