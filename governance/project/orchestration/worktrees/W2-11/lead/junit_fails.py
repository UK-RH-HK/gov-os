import sys
import xml.etree.ElementTree as ET
# list failed/errored cases of a JUnit file, with the first line of the message
root = ET.parse(sys.argv[1]).getroot()
for tc in root.iter("testcase"):
    for kind in ("failure", "error"):
        el = tc.find(kind)
        if el is not None:
            msg = (el.get("message") or "").splitlines()[0][:220] if el.get("message") else ""
            print(f"{kind.upper()} {tc.get('classname')}::{tc.get('name')} | {msg}")
