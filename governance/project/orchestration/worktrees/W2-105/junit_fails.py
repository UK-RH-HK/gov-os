import sys
from xml.etree import ElementTree
# usage: junit_fails.py <junit.xml> [prefix...] ; prints failures, and per-prefix counts
path, prefixes = sys.argv[1], sys.argv[2:]
counts = {p: [0, 0, 0] for p in prefixes}
for tc in ElementTree.parse(path).iter("testcase"):
    cls, name = tc.get("classname") or "", tc.get("name") or ""
    file = tc.get("file") or cls.replace(".", "/")
    tags = {c.tag for c in tc}
    bad = tags & {"failure", "error"}
    for p in prefixes:
        if file.startswith(p) or cls.replace(".", "/").startswith(p):
            counts[p][0 if not bad and "skipped" not in tags else 1 if bad else 2] += 1
    if bad:
        msg = ""
        for c in tc:
            if c.tag in ("failure", "error"):
                msg = (c.get("message") or "")[:300].replace("\n", " ")
        print("FAIL", cls, name, "|", msg)
for p, (ok, bad, sk) in counts.items():
    print("COUNT", p, "passed", ok, "failed", bad, "skipped", sk)
