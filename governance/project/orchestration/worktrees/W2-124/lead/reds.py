import sys
import xml.etree.ElementTree as ET

for path in sys.argv[1:]:
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        bad = case.find("failure")
        if bad is None:
            bad = case.find("error")
        if bad is not None:
            msg = (bad.get("message") or "").splitlines()
            print(f"{case.get('classname')}::{case.get('name')} | {(msg[0] if msg else '')[:150]}")
