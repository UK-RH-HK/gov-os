"""Print the full failure text of the failing cases whose name contains a given word (lead's scratch)."""
import sys
import xml.etree.ElementTree as ET

tree = ET.parse(sys.argv[1])
shown = 0
for case in tree.iter("testcase"):
    bad = case.find("failure")
    if bad is None:
        bad = case.find("error")
    if bad is None or sys.argv[2] not in case.get("name", ""):
        continue
    print("==", case.get("classname"), case.get("name"), "tag:", bad.tag)
    print(((bad.text or bad.get("message") or ""))[: int(sys.argv[3])])
    shown += 1
    if shown >= 2:
        break
