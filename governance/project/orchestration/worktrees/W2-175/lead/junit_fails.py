import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
for tc in root.iter("testcase"):
    for kind in ("failure", "error"):
        el = tc.find(kind)
        if el is not None:
            msg = (el.get("message") or "").replace("\n", " ")[:240]
            print(f"{kind.upper()} {tc.get('classname')}::{tc.get('name')} | {msg}")
