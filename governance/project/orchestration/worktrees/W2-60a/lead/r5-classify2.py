import sys, re, collections
from xml.etree import ElementTree
pat = [("role file unreadable", r"role file \S+ cannot be read"),
       ("model not the role's", r"not the role|model .* is not"),
       ("argv tail / position", r"\[-\d|argv\[|args\[-"),
       ("append-system-prompt", r"append-system-prompt"),
       ("no template", r"LAUNCH_NO_TEMPLATE"),
       ("refused args", r"the CLI arguments carry"),
       ("launch refused other", r"LAUNCH_REFUSED")]
c = collections.Counter(); ex = {}
for case in ElementTree.parse(sys.argv[1]).iter("testcase"):
    f = case.find("failure")
    if f is None: f = case.find("error")
    if f is None: continue
    msg = (f.get("message") or "") + "\n" + (f.text or "")
    k = next((n for n, p in pat if re.search(p, msg)), "unclassified")
    c[k] += 1
    ex.setdefault(k, []).append((case.get("classname").split(".")[-1] + "::" + case.get("name"), re.sub(r"\s+", " ", f.get("message") or "")[:300]))
print(c)
for k, v in ex.items():
    if k == "role file unreadable": continue
    print("==", k, len(v))
    for e in v[:6]: print("  ", e)
