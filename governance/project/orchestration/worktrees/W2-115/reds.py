import json
import sys
import xml.etree.ElementTree as ET

xml, out = sys.argv[1], sys.argv[2]
known = json.load(open("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json"))
known_ids = set()
if isinstance(known, dict):
    for k, v in known.items():
        if isinstance(v, list):
            known_ids.update(x if isinstance(x, str) else x.get("test", "") for x in v)
        else:
            known_ids.add(k)
elif isinstance(known, list):
    known_ids.update(x if isinstance(x, str) else x.get("test", "") for x in known)
lines = []
for tc in ET.parse(xml).getroot().iter("testcase"):
    bad = [c for c in tc if c.tag in ("failure", "error")]
    if not bad:
        continue
    cls = tc.get("classname", "")
    nid = cls.replace(".", "/") + ".py::" + tc.get("name", "")
    k = any(nid.endswith(x) or x.endswith(tc.get("name", "")) and x.split("::")[0].replace("/", ".").removesuffix(".py") == cls for x in known_ids if x)
    msg = (bad[0].get("message") or "").replace("\n", " ")[:300]
    text = (bad[0].text or "")
    tail = "\n".join(text.strip().splitlines()[-25:])
    lines.append((nid, k, msg, tail))
with open(out, "w") as f:
    for nid, k, msg, tail in lines:
        f.write(f"=== {nid} {'[KNOWN in skip_known.json]' if k else ''}\n{msg}\n{tail}\n\n")
for nid, k, msg, _ in lines:
    print(("KNOWN " if k else "NEW   ") + nid + " :: " + msg[:140])
