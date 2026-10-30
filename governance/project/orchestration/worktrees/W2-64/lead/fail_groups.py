"""Group a JUnit XML file's failing cases by test file, with a sample message per file (lead's scratch)."""
import collections
import sys
import xml.etree.ElementTree as ET

tree = ET.parse(sys.argv[1])
groups = collections.defaultdict(list)
for case in tree.iter("testcase"):
    bad = case.find("failure")
    if bad is None:
        bad = case.find("error")
    if bad is None:
        continue
    where = case.get("file") or case.get("classname")
    msg = (bad.get("message") or (bad.text or "")[:300]).replace("\n", " ")
    groups[where].append((case.get("name"), msg))
for where, cases in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    print(f"{len(cases):4d} {where}")
    for name, msg in cases[: int(sys.argv[2]) if len(sys.argv) > 2 else 1]:
        print(f"       {name[:90]} :: {msg[:260]}")
