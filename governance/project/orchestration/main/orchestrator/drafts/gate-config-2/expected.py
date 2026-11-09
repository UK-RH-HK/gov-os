"""ACT-GATE-CONFIG-2 (DEC-1103 (1), the CTO's ruling 2026-11-09): the bytes `gov resources --init-config` writes, from
W2-20's own code at 28fbcfebf, for this process's CPUs (as init() itself reads them), without writing anything. The
file no longer depends on HOME (round 2 dropped `disk_path`). Run with W2-20's src on PYTHONPATH.

    python3 expected.py [--cpus 0-19] [--out FILE]    prints the sha256 (and writes the bytes to FILE)
"""
import argparse
import hashlib
import json
import os

from gov.resources import config

ap = argparse.ArgumentParser()
ap.add_argument("--cpus")
ap.add_argument("--out")
a = ap.parse_args()
cpus = sorted(config.parse_cpus(a.cpus)) if a.cpus else sorted(os.sched_getaffinity(0))
text = json.dumps(config.template(cpus=cpus), indent=2) + "\n"  # as config.write() writes it
if a.out:
    with open(a.out, "w", encoding="utf-8") as handle:
        handle.write(text)
print(hashlib.sha256(text.encode("utf-8")).hexdigest())
