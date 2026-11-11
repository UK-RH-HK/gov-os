import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
for case in root.iter("testcase"):
    for kind in ("failure", "error"):
        el = case.find(kind)
        if el is not None:
            msg = (el.get("message") or "").replace("\n", " ")[:400]
            print(f"{kind.upper()} {case.get('classname')}::{case.get('name')} ({case.get('time')}s)\n    {msg}")
