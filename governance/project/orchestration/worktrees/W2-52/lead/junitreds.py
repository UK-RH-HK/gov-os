"""List failures and errors from a JUnit XML file: grouped by file, with the first line of each message."""
import collections
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
by_file = collections.defaultdict(list)
for case in root.iter("testcase"):
    for kind in ("failure", "error"):
        el = case.find(kind)
        if el is not None:
            msg = (el.get("message") or "").splitlines()[0][:220] if el.get("message") else ""
            by_file[case.get("classname", "")].append((kind, case.get("name"), msg))
for cls in sorted(by_file):
    print("==", cls, len(by_file[cls]))
    seen = collections.Counter(m for _, _, m in by_file[cls])
    for kind, name, msg in by_file[cls][:4]:
        print("  ", kind, name)
    for m, n in seen.most_common(3):
        print("   msg x%d: %s" % (n, m))
