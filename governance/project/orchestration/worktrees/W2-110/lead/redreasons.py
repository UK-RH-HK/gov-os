"""Classify the red check's failures by reason, from its JUnit XML."""
import collections
import sys
import xml.etree.ElementTree as ET

counts = collections.Counter()
for case in ET.parse(sys.argv[1]).iter("testcase"):
    fail = case.find("failure")
    if fail is None:
        fail = case.find("error")
    if fail is None:
        continue
    text = (fail.get("message") or "") + (fail.text or "")
    if "decision='ask'" in text or "'ask'" in text.split("\n")[0]:
        counts["asked (base asks any acting orchestrator)"] += 1
    elif "roster.yaml" in text or "coordination_ticket" in text:
        counts["refused without naming the file and key"] += 1
    elif "P1" in text or "escalat" in text:
        counts["refused without the P1 escalation words"] += 1
    else:
        counts["other: " + text.split("\n")[0][:120]] += 1
for k, v in counts.most_common():
    print(v, k)
