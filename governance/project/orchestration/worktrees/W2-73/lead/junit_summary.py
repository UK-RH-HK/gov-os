"""Counts and failing node ids of a JUnit XML file (the lead's verification, W2-73)."""
import sys
import xml.etree.ElementTree as ET

for path in sys.argv[1:]:
    root = ET.parse(path).getroot()
    counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    bad = []
    for case in root.iter("testcase"):
        counts["tests"] += 1
        node = case.get("classname", "") + "::" + case.get("name", "")
        for kind in ("failure", "error"):
            element = case.find(kind)
            if element is not None:
                counts[kind + "s"] += 1
                message = (element.get("message") or "").splitlines()
                bad.append(f"{kind.upper()} {node} :: {message[0][:200] if message else ''}")
        if case.find("skipped") is not None:
            counts["skipped"] += 1
    print(path, counts)
    for line in bad:
        print("  " + line)
