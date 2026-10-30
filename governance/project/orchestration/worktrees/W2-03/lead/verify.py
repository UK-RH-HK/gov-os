"""Run 3's full verification in the close's form (LEAD-w2-common step 4): one phase per call, `parallel` or `serial`.

The serial phase runs the serial-only list's entries the close runs (gov.close.serial.phase: the entries not routed
to the nightly), with GOV_CLOSE_SERIAL_ONLY_GIVEN set to them, one per line. Each phase writes its JUnit XML, its
output and an exit-code file under the lead's log folder.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = "/home/usain/gov-os-worktrees/W2-03"
LOG = Path(ROOT) / ".gov-runtime/scratch/lead/log"
TMP = "/tmp/gov-os-lead-W2-03"


def main(phase: str, tag: str) -> int:
    sys.path.insert(0, ROOT + "/src")
    from gov.close.pytest_plugin import gov_close_serial_only as serial_only
    from gov.close import serial

    os.makedirs(TMP, exist_ok=True)
    env = dict(os.environ)
    env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env["PATH"]
    env["PYTHONPATH"] = ROOT + "/src:" + ROOT + "/src/gov/close/pytest_plugin"
    env["GOV_CLOSE_SERIAL_ONLY_OF"] = ROOT
    env["TMPDIR"] = TMP
    base = ["flock", "/tmp/gov-os-verify.lock", sys.executable, "-m", "pytest"]
    common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only",
              "-o", "tmp_path_retention_policy=failed", "-rs"]
    if phase == "parallel":
        command = base + ["tests", "-n", "auto"] + common + ["--junitxml=" + str(LOG / (tag + "-parallel.xml"))]
    elif phase == "serial":
        entries = serial.phase(Path(ROOT), serial_only.entries(Path(ROOT)))
        env["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(entries)
        command = base + entries + common + ["--junitxml=" + str(LOG / (tag + "-serial.xml"))]
    else:
        command = base + sys.argv[3:] + common + ["--junitxml=" + str(LOG / (tag + ".xml"))]
    out = LOG / (tag + "-" + phase + ".txt")
    with open(out, "w") as handle:
        handle.write("# " + " ".join(command) + "\n")
        handle.flush()
        code = subprocess.call(command, cwd=ROOT, env=env, stdout=handle, stderr=subprocess.STDOUT)
    (LOG / (tag + "-" + phase + ".exit")).write_text(str(code) + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
