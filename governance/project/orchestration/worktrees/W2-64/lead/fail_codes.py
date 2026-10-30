"""For each failing case of a JUnit XML file, which SCHEMA_* codes and check names its failure text mentions
(lead's scratch): counts of each code, and the cases mentioning none."""
import collections
import re
import sys
import xml.etree.ElementTree as ET

tree = ET.parse(sys.argv[1])
codes = collections.Counter()
none = []
for case in tree.iter("testcase"):
    bad = case.find("failure")
    if bad is None:
        bad = case.find("error")
    if bad is None:
        continue
    text = (bad.get("message") or "") + (bad.text or "")
    found = set(re.findall(r"SCHEMA_[A-Z_]+", text))
    for code in found:
        codes[code] += 1
    if "core-schema" in text:
        codes["mentions core-schema"] += 1
    if not found:
        none.append(f"{case.get('classname')}::{case.get('name')}")
print(codes.most_common())
print(len(none), "cases name no SCHEMA_ code:")
for name in none:
    print("  ", name[:160])
