import json, xml.etree.ElementTree as ET
known = {e["test"] for e in json.load(open('/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json'))["entries"]}
t = ET.parse('.gov-runtime/scratch/lead/log/verify/parallel.xml')
for tc in t.iter('testcase'):
    f = tc.find('failure')
    if f is None:
        f = tc.find('error')
    if f is None: continue
    name = f"{tc.get('classname')}::{tc.get('name')}"
    msg = (f.get('message') or '').replace('\n', ' ')[:220]
    print(("KNOWN " if name in known else "NEW   ") + name + "\n      " + msg)
