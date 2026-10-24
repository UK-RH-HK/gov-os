"""W2-67 batch 6's planted source for KPI 4's static guard: an argument list that passes ``f"--basetemp={folder}"``.

Never run; read by the guard only, under ``GOV_TD6_GUARD_PLANT=other``.
"""

import subprocess
import sys


def run(folder):
    return subprocess.run([sys.executable, "-m", "pytest", f"--basetemp={folder}"], check=False)
