"""Count passed, failed, errored and skipped cases per named folder in JUnit XML files."""

import sys
import xml.etree.ElementTree as ET

FOCUS = ["tests.acceptance.W2-03", "tests.acceptance.W1-26", "tests.unit.store", "tests.unit.close",
         "tests.acceptance.W2-68", "tests.unit.records", "tests.unit.decisions", "tests.unit.check",
         "tests.acceptance.W1-42", "tests.acceptance.W2-71", "tests.acceptance.W2-54"]
counts = {name: [0, 0, 0, 0] for name in FOCUS + ["ALL"]}
for path in sys.argv[1:]:
    for case in ET.parse(path).getroot().iter("testcase"):
        cls = case.get("classname") or ""
        kind = 0
        if case.find("failure") is not None:
            kind = 1
        elif case.find("error") is not None:
            kind = 2
        elif case.find("skipped") is not None:
            kind = 3
        for name in FOCUS:
            if cls.startswith(name + "."):
                counts[name][kind] += 1
        counts["ALL"][kind] += 1
for name, (passed, failed, errored, skipped) in counts.items():
    print(f"{name}: {passed} passed, {failed} failed, {errored} errors, {skipped} skipped")
