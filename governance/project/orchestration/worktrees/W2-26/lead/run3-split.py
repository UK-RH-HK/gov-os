"""Count run3-parallel.xml's cases per suite (tests/unit against tests/acceptance/W2-07)."""
import collections
import xml.etree.ElementTree as ET

PATH = "/home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-parallel.xml"
counts = collections.Counter()
for case in ET.parse(PATH).iter("testcase"):
    name = case.get("classname", "")
    suite = "W2-07" if "W2-07" in name or "w2_07" in name else "unit"
    outcome = "passed"
    for child in case:
        if child.tag in ("failure", "error", "skipped"):
            outcome = child.tag
    counts[(suite, outcome)] += 1
for key in sorted(counts):
    print(key[0], key[1], counts[key])
