"""Lists the failing and erroring cases of a JUnit XML file, grouped by file, with the first line of each message."""
import collections
import sys
import xml.etree.ElementTree as ET

tree = ET.parse(sys.argv[1])
by_file = collections.defaultdict(list)
for case in tree.iter("testcase"):
    for kind in ("failure", "error"):
        node = case.find(kind)
        if node is not None:
            name = f"{case.get('classname')}::{case.get('name')}"
            msg = (node.get("message") or "").strip().splitlines()
            by_file[case.get("classname")].append((case.get("name"), kind, msg[0][:170] if msg else ""))
total = 0
for cls, cases in sorted(by_file.items()):
    print(f"{cls}: {len(cases)}")
    total += len(cases)
    for name, kind, msg in cases[: int(sys.argv[2]) if len(sys.argv) > 2 else 3]:
        print(f"   {kind} {name[:110]} | {msg}")
print("total", total)
