"""List failed/error cases of a JUnit file, with the first line of each message."""
import sys
import xml.etree.ElementTree as ET

for case in ET.parse(sys.argv[1]).getroot().iter("testcase"):
    for tag in ("failure", "error"):
        el = case.find(tag)
        if el is not None:
            msg = (el.get("message") or "").splitlines()
            print(f"{tag.upper()} {case.get('classname')}::{case.get('name')} | {msg[0][:300] if msg else ''}")
