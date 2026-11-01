"""Group a JUnit XML's failures and errors by file and test function; print one example message each.
Usage: junit_groups.py <xml> [--ids]  (with --ids, print every failing node id instead)"""
import collections
import sys
import xml.etree.ElementTree as ET

ids = "--ids" in sys.argv
groups = collections.OrderedDict()
for case in ET.parse(sys.argv[1]).iter("testcase"):
    bad = case.find("failure")
    kind = "F"
    if bad is None:
        bad = case.find("error")
        kind = "E"
    if bad is None:
        continue
    cls = case.get("classname", "")
    name = case.get("name", "")
    func = name.split("[")[0]
    if ids:
        print(kind, cls, name)
        continue
    key = (kind, cls, func)
    msg = (bad.get("message") or "").replace("\n", " ")[:230]
    groups.setdefault(key, [0, msg])
    groups[key][0] += 1
for (kind, cls, func), (n, msg) in groups.items():
    print(f"{kind} {n:4d} {cls}::{func}\n         {msg}")
