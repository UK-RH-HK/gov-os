"""Lists the failed cases of a JUnit file with the first line of each message, and marks those in skip_known.json."""
import json
import sys
import xml.etree.ElementTree as ET

known = json.load(open("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json"))
names = set()
for group in ("entries", "additions"):
    for entry in known.get(group) or []:
        if isinstance(entry, dict):
            names.update(str(v) for v in entry.values() if isinstance(v, str))
        else:
            names.add(str(entry))
for path in sys.argv[1:]:
    for case in ET.parse(path).iter("testcase"):
        bad = case.find("failure")
        if bad is None:
            bad = case.find("error")
        if bad is None:
            continue
        nodeid = f"{case.get('classname')}::{case.get('name')}"
        hit = any(case.get("name") in n or n in nodeid for n in names if n)
        msg = (bad.get("message") or "").splitlines()[0][:220] if bad.get("message") else ""
        print(("KNOWN " if hit else "NEW   ") + nodeid + " | " + msg)
