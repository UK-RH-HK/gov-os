"""Count JUnit cases per outcome for class names containing a fragment: python3 junit_folder.py <xml> <fragment>..."""
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
for frag in sys.argv[2:]:
    counts = {"passed": 0, "failed": 0, "error": 0, "skipped": 0}
    for case in root.iter("testcase"):
        if frag not in case.get("classname", ""):
            continue
        tags = {child.tag for child in case}
        if "failure" in tags:
            counts["failed"] += 1
        elif "error" in tags:
            counts["error"] += 1
        elif "skipped" in tags:
            counts["skipped"] += 1
        else:
            counts["passed"] += 1
    print(frag, counts)
