"""List the failed and errored cases of a JUnit XML file, with the first line of each message. Arg 1: the file."""
import sys
import xml.etree.ElementTree as ET

for case in ET.parse(sys.argv[1]).getroot().iter("testcase"):
    for kind in ("failure", "error"):
        node = case.find(kind)
        if node is not None:
            message = (node.get("message") or "").splitlines()[0][:240] if node.get("message") else ""
            print(f"{kind.upper()} {case.get('classname')}::{case.get('name')} ({case.get('time')} s) | {message}")
