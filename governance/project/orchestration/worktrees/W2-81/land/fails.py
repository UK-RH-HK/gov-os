import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
for tc in root.iter("testcase"):
    for kind in ("failure", "error"):
        el = tc.find(kind)
        if el is not None:
            msg = (el.get("message") or "").splitlines()
            print(kind, tc.get("classname"), tc.get("name"), "|", (msg[0] if msg else "")[:200])
