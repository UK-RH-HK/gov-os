"""Collect the distinct schema findings (path pattern, field, message tail) the failing cases' texts carry
(lead's scratch)."""
import collections
import re
import sys
import xml.etree.ElementTree as ET

tree = ET.parse(sys.argv[1])
seen = collections.Counter()
for case in tree.iter("testcase"):
    bad = case.find("failure")
    if bad is None:
        bad = case.find("error")
    if bad is None:
        continue
    text = ((bad.get("message") or "") + (bad.text or "")).replace("\\n", " ").replace("\\\"", '"')
    for match in re.finditer(r'"message": "([^"]{0,260})', text):
        msg = match.group(1)
        if "refused by" in msg or "SCHEMA" in msg or "schema" in msg:
            key = re.sub(r"[A-Za-z]+-[a-z0-9]{4}\b", "<id>", msg)
            seen[(case.get("classname").split(".")[-2], key)] += 1
for (suite, msg), count in seen.most_common(40):
    print(f"{count:4d} {suite} :: {msg[:240]}")
