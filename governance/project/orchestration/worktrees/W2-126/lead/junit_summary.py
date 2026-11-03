"""Print each test case's outcome and first message line from a JUnit XML file."""
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
counts = {}
for case in root.iter("testcase"):
    name = case.get("classname", "").split(".")[-1] + "::" + case.get("name", "")
    outcome, message = "passed", ""
    for tag in ("failure", "error", "skipped"):
        node = case.find(tag)
        if node is not None:
            outcome = tag
            message = (node.get("message") or "").splitlines()[0][:220] if node.get("message") else ""
            break
    counts[outcome] = counts.get(outcome, 0) + 1
    if len(sys.argv) < 3 or outcome != "passed":
        print(f"{outcome:8} {name} | {message}")
print(counts)
