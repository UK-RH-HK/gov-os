"""W2-85 lead verification, run in the background; each step writes <name>.txt, <name>.xml and <name>.rc under log/.

1. alone-time-limit, alone-green-here: each case alone, without the close's plugin, as the nightly runs it, after
   waiting (at most 30 minutes) for a 1-minute load under 20; the load at start and end is recorded.
2. w2-54-parallel: tests/acceptance/W2-54 in the close's parallel form, with the plugin.
3. readers: W2-57's two list readers (W1-30's r11 is in the selection).
4. sel-parallel: the scoped selection (select_tests.py's pytest_options), parallel, with the plugin.
5. sel-serial: the selection's serial-phase entries (gov.close.serial.phase, filtered by the selection), alone.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-85")
LOG = ROOT / ".gov-runtime/scratch/lead/log"
sys.path.insert(0, str(ROOT / "src"))
from gov.close import select as gsel  # noqa: E402
from gov.close import serial as gserial  # noqa: E402
from gov.close.pytest_plugin import gov_close_serial_only as plugin  # noqa: E402

NODE = "/home/usain/.nvm/versions/node/v22.23.3/bin"
BASE = dict(os.environ, TMPDIR="/tmp/gov-os-lead-W2-85", PATH=NODE + ":" + os.environ.get("PATH", ""),
            PYTHONPATH=str(ROOT / "src"))
for var in ("GOV_CLOSE_SERIAL_ONLY_OF", "GOV_CLOSE_SERIAL_ONLY_GIVEN", "GOV_CLOSE_CHECK_RESULT"):
    BASE.pop(var, None)
PLUG = dict(BASE, PYTHONPATH=f"{ROOT}/src:{ROOT}/src/gov/close/pytest_plugin", GOV_CLOSE_SERIAL_ONLY_OF=str(ROOT))
COMMON = ["-q", "-p", "no:cacheprovider", "--no-header", "-o", "tmp_path_retention_policy=failed", "-rs"]
TIME_LIMIT = ("tests/acceptance/W2-54/test_w2_54_time_limit.py::"
              "test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit")
GREEN_HERE = "tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here"


def load():
    return open("/proc/loadavg").read().split()[0]


def step(name, args, env):
    t0 = time.time()
    l0 = load()
    done = subprocess.run([sys.executable, "-m", "pytest", *args, *COMMON, f"--junitxml={LOG}/{name}.xml"],
                          cwd=ROOT, env=env, capture_output=True, text=True)
    (LOG / f"{name}.txt").write_text(f"load at start {l0}, at end {load()}, {int(time.time() - t0)} s\n"
                                      + done.stdout[-30000:] + "\n--- stderr\n" + done.stderr[-5000:])
    (LOG / f"{name}.rc").write_text(str(done.returncode))


def quiet(limit=1800):
    t0 = time.time()
    while float(load()) >= 20 and time.time() - t0 < limit:
        time.sleep(60)


only = sys.argv[1:]
sel = json.load(open(LOG / "select.txt"))

if not only or "alone" in only:
    quiet()
    step("alone-time-limit", [TIME_LIMIT], BASE)
    quiet()
    step("alone-green-here", [GREEN_HERE], BASE)
if not only or "w2-54" in only:
    step("w2-54-parallel", ["tests/acceptance/W2-54", "-n", "auto", "-p", "gov_close_serial_only"], PLUG)
if not only or "readers" in only:
    step("readers", ["tests/acceptance/W2-57/test_w2_57_serial_list.py",
                     "tests/acceptance/W2-57/test_w2_57_nightly_route.py",
                     "tests/acceptance/W1-30/test_w1_30_r11_declared_here.py"], BASE)
if not only or "sel" in only:
    step("sel-parallel", ["tests", "-n", "auto", "-p", "gov_close_serial_only", *sel["pytest_options"]], PLUG)
    entries = gserial.phase(ROOT, plugin.entries(ROOT))
    entries = [e for e in entries if gsel.runs(e, sel["ignore"], sel["deselect"])]
    (LOG / "sel-serial.entries").write_text("\n".join(entries) + "\n")
    if entries:
        step("sel-serial", [*entries, "-p", "gov_close_serial_only"],
             dict(PLUG, GOV_CLOSE_SERIAL_ONLY_GIVEN="\n".join(entries)))
    else:
        (LOG / "sel-serial.rc").write_text("no entries")
(LOG / "verify.done").write_text("done\n")
