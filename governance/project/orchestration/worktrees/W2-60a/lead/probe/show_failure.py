"""Print the full failure text of the cases whose name holds a word. Usage: show_failure.py <xml> <word> [<chars>]"""
import sys
import xml.etree.ElementTree as ElementTree

limit = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
for case in ElementTree.parse(sys.argv[1]).iter("testcase"):
    if sys.argv[2] not in case.get("name", ""):
        continue
    for found in list(case.findall("failure")) + list(case.findall("error")):
        print("=====", case.get("name"))
        print((found.text or "")[-limit:])
