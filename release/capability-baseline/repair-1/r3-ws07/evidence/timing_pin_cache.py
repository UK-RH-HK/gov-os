#!/usr/bin/env python3
"""P2-AR-0038 (WS-7 round 3) — timing of plugin authorisation with a large plugin program, before/after the pin cache.
BUILDER REGRESSION EVIDENCE, not acceptance evidence.

The scenario the round-2 observation names: a project whose embed plugin is the OS capability server of a DEBUG `gov`
binary (~170 MB), declared hand-written (OS_PROVIDED class). Every `gov` process that classifies plugins hashed that
binary (base: once per process). Each command below is a separate `gov` process; wall time and peak RSS are measured
with /usr/bin/time. Usage: GOV_BIN=<debug gov> WS07R3_SCRATCH=<dir> python3 timing_pin_cache.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ws07_r3_named_checks as nc  # noqa: E402  (same harness: fresh machine, provisioned root channel)

GOV = nc.GOV


def timed(p, *args):
    cmd = ["/usr/bin/time", "-f", "%e %M", GOV, "--json", "--root", p.root, "--role", "orchestrator", "--session",
           "S-t", *args]
    r = subprocess.run(cmd, capture_output=True, text=True, env=p.env())
    last = r.stderr.strip().splitlines()[-1].split()
    return float(last[0]), int(last[1]), '"ok":true' in r.stdout.replace(" ", "")


def main():
    size = os.path.getsize(GOV)
    print(f"# gov {GOV} ({size} bytes)")
    p = nc.new_project("timing")
    p.w("governance/project/plugins/os-embed.yaml",
        f"plugin_id: os-embed\ncapability: embed\nversion: \"1\"\nlanguages: []\ncommand: [\"{GOV}\", \"capabilities\", \"serve-embed\", \"--id\", \"os-embed\"]\n")
    for i in range(1, 5):
        for args in (("plugins", "list"), ("plugins", "health")):
            t, rss, ok = timed(p, *args)
            print(f"run {i} gov {' '.join(args):14s} {t:6.2f} s  peak RSS {rss:7d} KB  ok={ok}")
    store = os.path.join(p.state_root(), "plugin-pin-cache", "cache.json")
    print(f"# machine pin cache: {'present' if os.path.exists(store) else 'absent'} ({store})")


if __name__ == "__main__":
    main()
