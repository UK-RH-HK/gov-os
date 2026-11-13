import json
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
known = json.load(open("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json"))
text = json.dumps(known)
for case in ET.parse(path).getroot().iter("testcase"):
    bad = case.find("failure")
    if bad is None:
        bad = case.find("error")
    if bad is None:
        continue
    name = case.get("classname", "") + "::" + case.get("name", "")
    short = case.get("name", "").split("[")[0]
    msg = (bad.get("message") or "").replace("\n", " ")[:260]
    print(name, "| time", case.get("time"), "| known" if short in text else "| not known")
    print("   ", msg)
