"""Lists the failing and erroring cases of a JUnit file (argv[1]) with the first line of each message."""
import sys
import xml.etree.ElementTree as ET

for tc in ET.parse(sys.argv[1]).getroot().iter("testcase"):
    for kind in ("failure", "error"):
        el = tc.find(kind)
        if el is not None:
            msg = (el.get("message") or el.text or "").strip().splitlines()
            print(kind.upper(), tc.get("classname"), tc.get("name"), "|", (msg[0] if msg else "")[:300])
