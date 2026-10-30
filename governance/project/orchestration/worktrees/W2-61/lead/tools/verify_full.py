"""The lead's full verification in the close's form (DEC-889 items 6 and 12, DEC-905): gates, then the parallel run
of every suite under tests/ less the serial-only list, then the serial phase's entries alone, each under the verify
lock, each with JUnit XML, its output and its exit code in the lead's log folder. Argument: a label (full-1, ...).

Every run runs this worktree's src (DEC-732), TMPDIR /tmp/gov-os-lead-W2-61 (DEC-898), retention 'failed' (DEC-905).
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WT = Path("/home/usain/gov-os-worktrees/W2-61")
LOG = WT / ".gov-runtime/scratch/lead/log"
ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
label = sys.argv[1]

sys.path.insert(0, str(WT / "src"))
from gov.close import serial  # noqa: E402
from gov.close.pytest_plugin import gov_close_serial_only as serial_only  # noqa: E402


def gates():
    while True:
        while (ORCH / "CLOSE-RUNNING").exists() or (ORCH / "NIGHTLY-RUNNING").exists():
            time.sleep(60)
        while float(Path("/proc/loadavg").read_text().split()[0]) >= 20:
            time.sleep(60)
        disk = subprocess.run(["bash", str(ORCH / "tools/disk_gate.sh")], capture_output=True, text=True)
        if disk.returncode == 0 and not (ORCH / "CLOSE-RUNNING").exists() and not (ORCH / "NIGHTLY-RUNNING").exists():
            return disk.stderr.strip() + " | load " + Path("/proc/loadavg").read_text().strip()
        time.sleep(60)


LOCK_TIMEOUT = 75  # flock's exit code when it gave up waiting for the verify lock


def seconds_to_deadline(needed):
    """Seconds left to start a run of ``needed`` seconds that must end before 02:00 UTC (DEC-939 item 6); a large
    number outside the night's window (02:00 to 05:00 is the nightly's, and after it the day is open)."""
    now = time.gmtime()
    of_day = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
    if 2 * 3600 <= of_day < 5 * 3600:
        return -1 if (ORCH / "NIGHTLY-RUNNING").exists() or not nightly_seen[0] else 10 ** 6
    end = 2 * 3600 if of_day < 2 * 3600 else 26 * 3600
    return end - needed - of_day


nightly_seen = [len(sys.argv) > 2 and sys.argv[2] == "after-nightly"]  # the lead saw tonight's nightly end


def wait_for_window(needed):
    while seconds_to_deadline(needed) <= 0:
        if (ORCH / "NIGHTLY-RUNNING").exists():
            nightly_seen[0] = True
        now = time.gmtime()
        if now.tm_hour >= 5 and now.tm_hour < 6:
            nightly_seen[0] = True  # no nightly tonight, or it ended: the day is open again
        time.sleep(60)


def run(name, args, extra, needed):
    env = {**os.environ, "TMPDIR": "/tmp/gov-os-lead-W2-61",
           "PATH": "/home/usain/.nvm/versions/node/v22.23.3/bin:" + os.environ["PATH"],
           "PYTHONPATH": f"{WT}/src:{WT}/src/gov/close/pytest_plugin",
           "GOV_CLOSE_SERIAL_ONLY_OF": str(WT), **extra}
    while True:
        wait_for_window(needed)
        note = gates()
        left = seconds_to_deadline(needed)
        if left <= 0:
            continue
        cmd = ["flock", "-E", str(LOCK_TIMEOUT), "-w", str(int(left)), "/tmp/gov-os-verify.lock", "bash",
               str(WT / ".gov-runtime/scratch/lead/tools/after_lock.sh"), str(needed),
               "python3", "-m", "pytest", *args, "-q", "-p", "no:cacheprovider",
               "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs",
               f"--junitxml={LOG}/{label}-{name}.xml"]
        (LOG / f"{label}-{name}.time").write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + note + "\n")
        with open(LOG / f"{label}-{name}.txt", "w") as out:
            code = subprocess.run(cmd, cwd=WT, env=env, stdout=out, stderr=subprocess.STDOUT).returncode
        if code not in (LOCK_TIMEOUT, 76):
            break
        with open(LOG / f"{label}.lockwaits", "a") as t:
            t.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + f" {name}: not started ({code})\n")
    with open(LOG / f"{label}-{name}.time", "a") as t:
        t.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")
    (LOG / f"{label}-{name}.exit").write_text(f"{code}\n")


os.makedirs("/tmp/gov-os-lead-W2-61", exist_ok=True)
if "serial-only" not in sys.argv[3:]:  # a resumed run whose parallel phase has its exit file already
    run("parallel", ["tests", "-n", "auto"], {}, 4400)  # nightly_estimate: setup 942 s + parallel 2949 s, margin 1.1
entries = serial.phase(WT, serial_only.entries(WT))
run("serial", entries, {"GOV_CLOSE_SERIAL_ONLY_GIVEN": "\n".join(entries)}, 800)  # serial 717 s, margin 1.1
(LOG / f"{label}.done").write_text("done\n")
