import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
pattern = sys.argv[2] if len(sys.argv) > 2 else ""
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 600
seen = 0
for case in root.iter("testcase"):
    bad = case.find("failure")
    if bad is None:
        bad = case.find("error")
    if bad is None:
        continue
    nid = f"{case.get('classname')}::{case.get('name')}"
    if pattern and pattern not in nid:
        continue
    seen += 1
    text = (bad.get("message") or "") + "\n" + (bad.text or "")
    print(f"=== [{bad.tag}] {nid}")
    print(text[-limit:])
print("cases:", seen)
