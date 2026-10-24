"""Build the interim skip guard's known list (owner, DEC-915 item 2): every (test, reason) skip that a green full run's
JUnit XML states, read with the close's own reader (gov.close.evidence.read_junit), so the ids are the ones the
close's evidence block holds. Usage: skip_known_build.py <out.json> <project root>:<junit.xml> [...]. Prints counts and
reasons only. The list is versioned on the record branch; every addition is named in the daily digest."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/src")
from gov.close.evidence import read_junit  # noqa: E402

out = Path(sys.argv[1])
known = {}
for given in sys.argv[2:]:
    root, xml = given.split(":", 1)
    found = read_junit(Path(root), Path(xml))
    for skip in found["skips"]:
        known[(skip["test"], skip["reason"])] = xml
    print(f"{xml}: {len(found['cases'])} cases, {len(found['skips'])} skips")
entries = [{"test": test, "reason": reason} for test, reason in sorted(known)]
out.write_text(json.dumps({"form": 1, "decision": "DEC-915", "entries": entries}, indent=1) + "\n")
reasons = {}
for entry in entries:
    reasons[entry["reason"][:90]] = reasons.get(entry["reason"][:90], 0) + 1
print(f"{len(entries)} known skips")
for reason, count in sorted(reasons.items(), key=lambda item: -item[1]):
    print(f"  {count:3d}  {reason}")
