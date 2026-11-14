import sys, re, json, collections
from xml.etree import ElementTree
known = json.load(open("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json"))
ks = json.dumps(known)
byfile = collections.Counter(); reasons = collections.Counter(); other = []
for case in ElementTree.parse(sys.argv[1]).iter("testcase"):
    f = case.find("failure") if case.find("failure") is not None else case.find("error")
    if f is None: continue
    cls = case.get("classname"); name = case.get("name")
    path = cls.replace(".", "/")
    byfile[path] += 1
    msg = (f.get("message") or "") + (f.text or "")
    role = "role file" in msg and "cannot be read" in msg
    if role: reasons["role file cannot be read"] += 1
    else:
        reasons["other"] += 1
        other.append((cls, name, (f.get("message") or "")[:200], name in ks or cls.split(".")[-1] in ks))
for k, v in sorted(byfile.items()): print(v, k)
print(reasons)
for o in other: print("OTHER", o)
