import sys, xml.etree.ElementTree as ET
for p in sys.argv[1:]:
    for tc in ET.parse(p).getroot().iter("testcase"):
        for k in ("failure", "error"):
            e = tc.find(k)
            if e is not None:
                msg = (e.get("message") or "").replace("\n", " ")[:300]
                print(f"{k.upper()} {tc.get('classname')}::{tc.get('name')} | {msg}")
