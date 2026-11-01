import collections
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
total = collections.Counter()
bad = collections.Counter()
skipped = collections.Counter()
for case in root.iter("testcase"):
    parts = case.get("classname").split(".")
    folder = "/".join(parts[:3]) if parts[1] == "acceptance" else "/".join(parts[:2])
    total[folder] += 1
    if case.find("failure") is not None or case.find("error") is not None:
        bad[folder] += 1
    if case.find("skipped") is not None:
        skipped[folder] += 1
for folder in sorted(total):
    print(f"{folder:32s} {total[folder]:5d} run  {bad[folder]:3d} red  {skipped[folder]:2d} skipped")
