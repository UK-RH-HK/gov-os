"""ACT 1 (DEC-925 item 2's sweep, scoped under DEC-953): run every test folder that reads the hook wiring in the trial
clone with the regenerated settings; re-run each failing test with the change stashed (the base), so only the reds
ACT 1 causes are named. Writes /tmp/gov-os-act1/result.json and prints a summary.
    python3 act1_tests.py /tmp/gov-os-act1/repo"""
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

clone = sys.argv[1]
out = "/tmp/gov-os-act1"
VL = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"
grep = subprocess.run(["grep", "-rlE", r"settings\.json|hooks\.jsonc|posttooluse|PostToolUse", "tests",
                       "--include=*.py"], cwd=clone, capture_output=True, text=True).stdout.split()
folders = sorted({os.path.dirname(f) for f in grep})
env = {k: v for k, v in os.environ.items() if k not in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")}
env.update(PYTHONPATH=clone + "/src", TMPDIR="/tmp/gov-os-act1/tmp",
           PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", ""))
os.makedirs(env["TMPDIR"], exist_ok=True)


def run(args, xml):
    p = subprocess.run(["bash", VL, sys.executable, "-m", "pytest", *args, "-q", "-p", "no:cacheprovider",
                        "--no-header", "-o", "tmp_path_retention_policy=failed", f"--junitxml={xml}"],
                       cwd=clone, env=env, capture_output=True, text=True)
    failed = []
    if os.path.isfile(xml):
        for case in ET.parse(xml).iter("testcase"):
            if case.find("failure") is not None or case.find("error") is not None:
                f = case.get("file") or (case.get("classname", "").replace(".", "/") + ".py")
                failed.append(f"{f}::{case.get('name')}")
    return p.returncode, p.stdout.strip().splitlines()[-1:] if p.stdout else [], failed


rc, last, failed = run([*folders, "-n", "auto"], out + "/new.xml")
print("with ACT 1:", last, "failed", len(failed))
subprocess.run(["git", "-C", clone, "checkout", "-q", "HEAD^", "--", ".claude", ".rulesync"], check=True)
try:
    _, last_b, failed_b = run(failed, out + "/base.xml") if failed else (0, [], [])
finally:
    subprocess.run(["git", "-C", clone, "checkout", "-q", "HEAD", "--", ".claude", ".rulesync"], check=True)
caused = sorted(set(failed) - set(failed_b))
also_base = sorted(set(failed) & set(failed_b))
json.dump({"folders": folders, "with_act1_last": last, "failed_with_act1": failed, "failed_on_base_too": also_base,
           "caused_by_act1": caused}, open(out + "/result.json", "w"), indent=1)
print("folders", len(folders), "| failed with ACT 1", len(failed), "| also on the base", len(also_base),
      "| caused by ACT 1", len(caused))
for c in caused:
    print("CAUSED", c)
