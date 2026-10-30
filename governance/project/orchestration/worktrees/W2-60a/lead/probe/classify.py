"""Group the failing cases of a JUnit file by folder and by the cause their output names."""
import collections
import re
import sys
import xml.etree.ElementTree as ElementTree

ROLE = re.compile(r"role file .*roles/[a-z-]+\.md|version line|Launch default|default line")
groups = collections.defaultdict(collections.Counter)
others = []
for case in ElementTree.parse(sys.argv[1]).iter("testcase"):
    found = case.find("failure")
    if found is None:
        found = case.find("error")
    if found is None:
        continue
    parts = case.get("classname", "").split(".")
    folder = ".".join(parts[:3]) if len(parts) > 1 and parts[1] == "acceptance" else ".".join(parts[:4])
    text = (found.get("message") or "") + "\n" + (found.text or "")
    if ROLE.search(text):
        groups[folder]["role file without version/default line"] += 1
    else:
        groups[folder]["other"] += 1
        others.append((case.get("classname"), case.get("name"), (found.get("message") or "").splitlines()[0][:220]
                       if found.get("message") else ""))
for folder in sorted(groups):
    print(folder, dict(groups[folder]))
print("--- other causes")
for item in others:
    print(item)
