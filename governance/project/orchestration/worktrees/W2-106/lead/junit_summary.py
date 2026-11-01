import collections
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
counts = collections.Counter()
failed = collections.Counter()
for case in root.iter("testcase"):
    name = case.get("name").split("[")[0]
    key = (case.get("classname"), name)
    counts[key] += 1
    if case.find("failure") is not None or case.find("error") is not None:
        failed[key] += 1
for key in sorted(counts):
    print(f"{failed[key]:3d}/{counts[key]:3d} failed  {key[0]}::{key[1]}")
for suite in root.iter("testsuite"):
    print("suite:", suite.get("tests"), "tests,", suite.get("failures"), "failures,", suite.get("errors"),
          "errors,", suite.get("skipped"), "skipped,", suite.get("time"), "s")
