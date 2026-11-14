import sys
import xml.etree.ElementTree as E

r = E.parse(sys.argv[1]).getroot()
for tc in r.iter("testcase"):
    f = tc.find("failure")
    if f is None:
        f = tc.find("error")
    if f is not None:
        print(tc.get("classname"), tc.get("name"), tc.get("file"), tc.get("line"))
        print("   MSG:", (f.get("message") or "")[:600])
        print("   TXT:", (f.text or "")[-1500:])
        print("-----")
