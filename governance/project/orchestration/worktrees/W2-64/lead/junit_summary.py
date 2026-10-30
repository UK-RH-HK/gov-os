"""Summarise a JUnit XML file: each failing case and the first assertion line of its message (lead's scratch)."""
import sys
import xml.etree.ElementTree as ET

tree = ET.parse(sys.argv[1])
counts = {"passed": 0, "failed": 0, "skipped": 0}
for case in tree.iter("testcase"):
    bad = case.find("failure") if case.find("failure") is not None else case.find("error")
    if case.find("skipped") is not None:
        counts["skipped"] += 1
        print("SKIP", case.get("name"), (case.find("skipped").get("message") or "")[:150])
    elif bad is not None:
        counts["failed"] += 1
        msg = (bad.get("message") or "").replace("\n", " ")
        print("FAIL", case.get("classname").split(".")[-1], case.get("name"), "::", msg[:230])
    else:
        counts["passed"] += 1
        if len(sys.argv) > 2:
            print("PASS", case.get("classname").split(".")[-1], case.get("name"))
print(counts)
