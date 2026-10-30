"""List each failing case of JUnit XML files with the first line of its message. Usage: failing_from_xml.py <xml>..."""
import sys
import xml.etree.ElementTree as ElementTree

for path in sys.argv[1:]:
    for case in ElementTree.parse(path).iter("testcase"):
        for failure in list(case.findall("failure")) + list(case.findall("error")):
            message = (failure.get("message") or "").splitlines()
            first = message[0][:300] if message else ""
            print(f"- {case.get('classname')}::{case.get('name')}\n    {first}")
