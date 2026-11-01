"""List failing and erroring cases of JUnit XML files, with the first part of each message."""
import sys
import xml.etree.ElementTree as ET

width = 260
for path in sys.argv[1:]:
    print("==", path)
    counts = {"failed": 0, "error": 0, "skipped": 0, "total": 0}
    for tc in ET.parse(path).iter("testcase"):
        counts["total"] += 1
        bad = tc.find("failure")
        kind = "failed"
        if bad is None:
            bad = tc.find("error")
            kind = "error"
        if tc.find("skipped") is not None:
            counts["skipped"] += 1
        if bad is None:
            continue
        counts[kind] += 1
        msg = (bad.get("message") or "").replace("\n", " ")[:width]
        print(f"{kind}: {tc.get('classname')}::{tc.get('name')} | {msg}")
    print(counts)
