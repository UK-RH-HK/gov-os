import sys
import xml.etree.ElementTree as ET

for path in sys.argv[1:]:
    root = ET.parse(path).getroot()
    counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for suite in root.iter("testsuite"):
        for k in counts:
            counts[k] += int(suite.get(k, 0))
    print(path, counts)
    for case in root.iter("testcase"):
        for tag in ("failure", "error"):
            el = case.find(tag)
            if el is not None:
                msg = (el.get("message") or "").replace("\n", " ")[:300]
                print(" ", tag.upper(), case.get("classname"), case.get("name"), "|", msg)
