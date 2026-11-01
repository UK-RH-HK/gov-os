"""Print the full message of failed cases whose name holds argv[2]."""
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
for case in root.iter("testcase"):
    node = case.find("failure")
    if node is not None and sys.argv[2] in case.get("name", ""):
        print(case.get("name"))
        print((node.get("message") or "")[:900])
        print("---")
