import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
prefixes = sys.argv[2:]
counts = {p: [0, 0, 0] for p in prefixes}
for tc in root.iter("testcase"):
    cls = tc.get("classname") or ""
    for p in prefixes:
        if cls.startswith(p):
            c = counts[p]
            c[0] += 1
            if tc.find("failure") is not None or tc.find("error") is not None:
                c[1] += 1
            if tc.find("skipped") is not None:
                c[2] += 1
for p, (n, f, s) in counts.items():
    print(p, "tests", n, "failed", f, "skipped", s)
