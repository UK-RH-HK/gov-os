"""The nightly's last step: read both JUnit files, re-run each failing case alone once, and give a verdict.

    python3 nightly_alone.py <clone> <out folder>

Prints one line per failing case (`red-alone` or `passes-alone`) and a last line `verdict: green`, `verdict: red <n>`
(cases that fail alone too: a red of the head, a P1 package) or `verdict: flaky-candidates <n>` (all pass alone).
The accepted reds of the path map are named as such and are not reds of the head.
"""
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

clone, out = Path(sys.argv[1]), Path(sys.argv[2])
accepted = {e["test"] for e in (yaml.safe_load((clone / "governance/project/path-map.yaml").read_text())
                                .get("accepted_reds") or [])}
failing = []
for name in ("parallel.xml", "serial.xml"):
    path = out / name
    if not path.is_file():
        print(f"{name}: missing")
        continue
    for case in ET.parse(path).iter("testcase"):
        if case.find("failure") is not None or case.find("error") is not None:
            file = case.get("file") or (case.get("classname", "").replace(".", "/") + ".py")
            failing.append(f"{file}::{case.get('name')}")
env = {k: v for k, v in os.environ.items() if k not in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")}
env["PYTHONPATH"] = str(clone / "src")
reds = flaky = 0
for node in dict.fromkeys(failing):
    if node in accepted:
        print(f"accepted-red {node}")
        continue
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", node],
                          cwd=clone, env=env, capture_output=True, text=True, timeout=1800)
    if done.returncode == 0:
        flaky += 1
        print(f"passes-alone {node}")
    else:
        reds += 1
        print(f"red-alone {node}: {done.stdout.strip().splitlines()[-1] if done.stdout.strip() else done.returncode}")
print("verdict: " + (f"red {reds}" if reds else f"flaky-candidates {flaky}" if flaky else "green"))
