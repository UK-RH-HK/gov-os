"""Run 5: list the failing and erroring cases of the pinned runs' JUnit files, as pytest node ids, one per line.

argv: <out file> <junit.xml> [<junit.xml> ...]
"""
import sys
import xml.etree.ElementTree as ET

ids = []
for path in sys.argv[2:]:
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        print(f"{path}: {error}")
        continue
    for case in root.iter("testcase"):
        if case.find("failure") is None and case.find("error") is None:
            continue
        classname, name = case.get("classname", ""), case.get("name", "")
        parts = classname.split(".")
        # tests.acceptance.W1-02.test_x -> tests/acceptance/W1-02/test_x.py; a class name may follow the module
        module, rest = [], []
        for part in parts:
            if rest or (module and module[-1].startswith("test_")):
                rest.append(part)
            else:
                module.append(part)
        node = "/".join(module) + ".py" + "".join(f"::{r}" for r in rest) + f"::{name}"
        ids.append(node)
with open(sys.argv[1], "w", encoding="utf-8") as handle:
    handle.write("".join(f"{i}\n" for i in dict.fromkeys(ids)))
print(f"{len(ids)} red case(s)")
