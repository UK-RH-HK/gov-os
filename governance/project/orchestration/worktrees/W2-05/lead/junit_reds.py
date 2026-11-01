"""List the failed or errored cases of JUnit XML files, as pytest node ids, with the first line of each message.
Prints no commit ids (the message line is cut at 160 characters). Usage: junit_reds.py <xml> [<xml> ...] [--ids]"""
import sys
import xml.etree.ElementTree as ET

ids_only = "--ids" in sys.argv
for path in [a for a in sys.argv[1:] if a != "--ids"]:
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        bad = case.find("failure")
        if bad is None:
            bad = case.find("error")
        if bad is None:
            continue
        classname, name = case.get("classname", ""), case.get("name", "")
        parts = classname.split(".")
        # classname is the module path with dots; the file is the module path + .py
        node = "/".join(parts) + ".py::" + name
        if ids_only:
            print(node)
        else:
            message = (bad.get("message") or "").splitlines()[0:1]
            print(node, "|", (message[0] if message else "")[:160])
