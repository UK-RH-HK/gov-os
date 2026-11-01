"""Classify round 3's failing cases: W2-90's list, load_sensitive, class (i) role files, else by folder and message.
Usage: classify3.py <junit.xml>... Prints counts and every unclassified case with its first message line."""
import collections
import re
import sys
import xml.etree.ElementTree as ElementTree

import yaml

ROOT = "/home/usain/gov-os-worktrees/W2-60a"
W290 = set(open("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/W2-90-cases.txt",
                encoding="utf-8").read().split())
LOAD = {e["test"] for e in yaml.safe_load(open(f"{ROOT}/governance/project/path-map.yaml"))["load_sensitive"]}
ROLE = re.compile(r"role file .*roles/[a-z-]+\.md|version line|Launch default|default line")


def node(case):
    parts = case.get("classname", "").split(".")
    return "/".join(parts) + ".py::" + case.get("name", "")


counts = collections.Counter()
by_folder = collections.defaultdict(collections.Counter)
rest = []
for path in sys.argv[1:]:
    for case in ElementTree.parse(path).iter("testcase"):
        found = case.find("failure")
        kind = "failed"
        if found is None:
            found = case.find("error")
            kind = "error"
        if found is None:
            continue
        nid = node(case)
        base = nid.split("[", 1)[0]
        text = (found.get("message") or "") + "\n" + (found.text or "")
        folder = "/".join(nid.split("/")[:3])
        if nid in W290 or base in W290:
            cause = "W2-90 (ACT 1 live wiring)"
        elif nid in LOAD or base in LOAD or nid.split("::")[0] in LOAD:
            cause = "load_sensitive"
        elif ROLE.search(text):
            cause = "class (i): role file without its lines"
        else:
            cause = "other"
            rest.append((kind, nid, (found.get("message") or "").splitlines()[0][:240] if found.get("message") else ""))
        counts[cause] += 1
        by_folder[cause][folder] += 1
for cause, n in counts.most_common():
    print(n, cause, dict(by_folder[cause]))
print("--- other")
for kind, nid, msg in rest:
    print(kind, nid)
    print("     ", msg)
