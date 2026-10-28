"""Per-phase sums of the per-test durations in JUnit files: for calibrating the nightly's estimate (DEC-933 item 2).

    python3 junit_sums.py <xml> [<xml> ...]

Prints, per file: the test cases, the sum of their durations, the longest case, and the file's own total time
(the testsuite's `time`, the run's wall time as pytest measured it).
"""
import sys
import xml.etree.ElementTree as ET

for path in sys.argv[1:]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    cases = [float(c.get("time") or 0) for c in root.iter("testcase")]
    wall = sum(float(s.get("time") or 0) for s in suites)
    print(f"{path}: {len(cases)} cases, sum {sum(cases):.0f} s, longest {max(cases or [0]):.0f} s, wall {wall:.0f} s")
