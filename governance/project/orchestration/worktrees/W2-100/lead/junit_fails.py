import sys
import xml.etree.ElementTree as ET

for path in sys.argv[1:]:
    for tc in ET.parse(path).iter("testcase"):
        for kind in ("failure", "error"):
            f = tc.find(kind)
            if f is not None:
                msg = (f.get("message") or "").replace("\n", " ")[:170]
                print(f"{tc.get('classname')}::{tc.get('name')} | {msg}")
