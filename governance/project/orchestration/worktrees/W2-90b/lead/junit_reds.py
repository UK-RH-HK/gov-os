#!/usr/bin/env python3
"""Print every failed, errored or skipped case of a JUnit XML file, one per line, with a short reason."""
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
counts = {"passed": 0, "failure": 0, "error": 0, "skipped": 0}
for case in root.iter("testcase"):
    kind = "passed"
    msg = ""
    for child in case:
        if child.tag in ("failure", "error", "skipped"):
            kind = child.tag
            msg = (child.get("message") or "").replace("\n", " ")[:180]
            break
    counts[kind] += 1
    if kind != "passed":
        print(f"{kind.upper()} {case.get('classname')}::{case.get('name')} | {msg}")
print(counts)
