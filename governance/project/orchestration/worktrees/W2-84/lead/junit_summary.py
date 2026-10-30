"""Summarise a JUnit XML: junit_summary.py <xml> [<expected-green-list>].

Prints counts, failure reasons grouped by their first line, and the passing cases per test function."""
import collections
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
cases = root.iter("testcase")
status = collections.Counter()
reasons = collections.Counter()
passed_by_fn = collections.Counter()
failed_by_fn = collections.Counter()
failed_names = []
for c in cases:
    name = c.get("classname", "") + "::" + c.get("name", "")
    fn = name.split("[")[0]
    bad = c.find("failure") if c.find("failure") is not None else c.find("error")
    skip = c.find("skipped")
    if bad is not None:
        status["failed"] += 1
        failed_by_fn[fn] += 1
        failed_names.append(name)
        msg = (bad.get("message") or "").splitlines()[0][:160]
        key = "allow" if "decision=allow" in (bad.get("message") or "") + (bad.text or "") else msg
        reasons[key] += 1
    elif skip is not None:
        status["skipped"] += 1
    else:
        status["passed"] += 1
        passed_by_fn[fn] += 1
print(dict(status))
print("failure reasons:")
for k, v in reasons.most_common():
    print(" ", v, k)
print("failed per function:")
for k, v in sorted(failed_by_fn.items()):
    print(" ", v, k)
print("passed per function:")
for k, v in sorted(passed_by_fn.items()):
    print(" ", v, k)
if len(sys.argv) > 2:
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write("\n".join(failed_names) + "\n")
