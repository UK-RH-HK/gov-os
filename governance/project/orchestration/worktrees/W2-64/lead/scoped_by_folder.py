"""Count a JUnit file's cases by folder and outcome (lead's scratch)."""
import collections
import sys
import xml.etree.ElementTree as ET

counts = collections.Counter()
for case in ET.parse(sys.argv[1]).iter("testcase"):
    where = (case.get("classname") or "").split(".")
    folder = ".".join(where[:3])
    state = "failed" if case.find("failure") is not None or case.find("error") is not None else (
        "skipped" if case.find("skipped") is not None else "passed")
    counts[(folder, state)] += 1
for (folder, state), n in sorted(counts.items()):
    print(f"{folder} {state} {n}")
