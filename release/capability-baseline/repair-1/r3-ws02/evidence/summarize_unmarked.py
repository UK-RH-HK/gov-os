#!/usr/bin/env python3
"""P2-AR-0033: compact view of an UNMARKED epsilon-r probe output (doctor/audit summary lines per section), for the
before/after comparison in the repair report. Reads the probe outputs only; prints to stdout."""
import json, re, sys
for path in sys.argv[1:]:
    print("#####", path.split("/")[-2], path.split("/")[-1])
    sec = None
    for line in open(path).read().splitlines():
        if line.startswith("=== "):
            sec = line[4:90]
            print("==", sec)
            continue
        m = re.match(r"\s*(doctor|audit)\s*: exit=(\d+) (\{.*\})\s*$", line)
        if m:
            try:
                d = json.loads(m.group(3))
            except Exception:
                print("  ", m.group(1), "exit", m.group(2), "(unparsed)")
                continue
            if m.group(1) == "doctor":
                print(f"   doctor {d.get('verdict')}: " + ", ".join(f"{x[0]}:{x[1]}" for x in d.get("failed", [])))
            else:
                fs = [f"{x[0]}:{x[1]}" for x in d.get("findings", []) if x[1] in ("medium", "high", "critical")]
                print(f"   audit  {d.get('verdict')}: " + ", ".join(sorted(set(fs))))
