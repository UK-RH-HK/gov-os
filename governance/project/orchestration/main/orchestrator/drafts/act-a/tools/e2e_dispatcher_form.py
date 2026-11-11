"""The dispatcher's own start form, end to end, with a stub lead: `setsid -f bash <launch_now.sh> <W2> <id> <brief> <log>`
(dispatcher.py default_launch_argv), the pinned gov under a planted HOME with the product's reading overrides, and a
stub `claude` that holds for a moment. Looks at the registry, the gate's reading and the sampler while the "lead"
runs, then waits for it by pid (tools/proc.sh wait, bounded). Prints one line per check, ends "failures: <n>".
   python3 e2e_dispatcher_form.py <script> <scratch tmp dir> <proc.sh> <lead_mem.py>
Never starts a real claude session: the CLI path in the script copy is the stub."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

script, tmp, proc_sh, lead_mem = sys.argv[1:5]
here = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(here))
os.environ["LAUNCH_NOW"] = script
os.environ["LEAD_MEM_PY"] = lead_mem
import importlib.util  # noqa: E402

import test_launch_now_gate as t  # noqa: E402

fails = 0


def ok(cond, label):
    global fails
    print(("ok   " if cond else "FAIL ") + label)
    if not cond:
        fails += 1


base = Path(tmp) / "e2e"
base.mkdir(parents=True, exist_ok=True)
b = t.Bed(base, real_gov=True)
init = subprocess.run([t.REAL_GOV, "resources", "--init-config"], cwd=str(b.tree), env=b.env(), capture_output=True,
                      text=True, timeout=60)
ok(init.returncode == 0, "the planted machine folder is initialised")
b.hold.write_text("hold\n")
argv = ["setsid", "-f"] + b.argv()   # the dispatcher's form: detached, no wait, the exit code is setsid's
errf = b.orch / "log" / "W9-1-launch.txt"
with open(errf, "a") as err, open(os.devnull) as nul:
    rc = subprocess.run(argv, cwd=str(base), env=b.env(), stdin=nul, stdout=subprocess.DEVNULL, stderr=err,
                        timeout=60).returncode
ok(rc == 0, f"setsid -f returns at once (exit {rc})")
t.wait_for(b.record, 30)
seen = b.seen()
pid = int(seen["pid"])
ok(f"{pid}.json" in seen["sessions"].split(), "the lead found its own registry entry at its first line")
entry = json.loads((b.home / ".gov-os/machine/sessions" / f"{pid}.json").read_text())
ok(entry["ticket"] == b.ticket and entry["role"] == "orchestrator", f"the entry names {entry['ticket']} as orchestrator")
reading = subprocess.run([t.REAL_GOV, "resources"], cwd=str(b.tree), env=b.env(), capture_output=True, text=True, timeout=60)
sessions = json.loads(reading.stdout)["sessions"]
ok([s["ticket"] for s in sessions] == [b.ticket] and sessions[0]["live_memory_bytes"], f"the gate's reading lists the lead ({sessions})")
spec = importlib.util.spec_from_file_location("lm", lead_mem)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ok(b.ticket in mod.snapshot()["leads_kb"], "lead_mem.py's sampler lists the lead")
sample = subprocess.run([t.REAL_GOV, "resources", "--sample", "--json"], cwd=str(b.tree), env=b.env(), capture_output=True,
                        text=True, timeout=60)
ok(sample.returncode == 0 and b.ticket in sample.stdout, "gov resources --sample takes a sample that holds the lead")
log = errf.read_text()
ok("gate open" in log and f"registered as pid {pid}" in log, "the launch log says the gate was open and the pid registered")
b.hold.unlink()
done = subprocess.run(["bash", proc_sh, "wait", "--max", "30", "--every", "1", str(pid)], capture_output=True, text=True,
                      timeout=60)
ok(done.returncode == 0, f"the lead ended and was waited for by pid ({done.stdout.strip()})")
time.sleep(0.2)
after = subprocess.run([t.REAL_GOV, "resources"], cwd=str(b.tree), env=b.env(), capture_output=True, text=True, timeout=60)
ok(json.loads(after.stdout)["sessions"] == [], "after the lead ended the next reading clears its entry")
print(f"failures: {fails}")
sys.exit(1 if fails else 0)
