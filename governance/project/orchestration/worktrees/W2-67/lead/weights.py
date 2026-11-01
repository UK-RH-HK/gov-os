"""Run 7: per top folder, the summed test time and count in run 6's scoped JUnit file (to split the run in two parts)."""
import collections
import xml.etree.ElementTree as ET

root = ET.parse("/tmp/gov-os-lead-W2-67/verify-r6b/parallel.xml").getroot()
t = collections.Counter()
n = collections.Counter()
for case in root.iter("testcase"):
    parts = case.get("classname", "").split(".")
    key = ".".join(parts[:3]) if parts[:2] == ["tests", "acceptance"] else ".".join(parts[:2])
    t[key] += float(case.get("time") or 0)
    n[key] += 1
for k, v in t.most_common():
    print(f"{k}\t{v:.0f}s\t{n[k]}")
print("total", f"{sum(t.values()):.0f}s", sum(n.values()))
