"""For each decision-citations finding, whether the cited id has a `### DEC-n` heading at all in that commit's
register: a finding with no heading is flagged under any entry rule; one with a heading is due to the stricter rule."""

import json
import re
import subprocess

ROOT = "/home/usain/gov-os-worktrees/W2-03"
data = json.load(open(ROOT + "/.gov-runtime/scratch/lead/log/r3b-check.json"))["result"]["checks"]
check = [c for c in data if c.get("id") == "core-decision-citations"][0]
pattern = re.compile(r"commit ([0-9a-f]+) cites ((?:DEC|ADR)-[0-9]+), which its tree does not record")
no_heading, with_heading, other = [], [], []
cache = {}
for finding in check["findings"]:
    match = pattern.fullmatch(finding.get("message", ""))
    if not match:
        other.append(finding.get("message"))
        continue
    commit, rid = match.groups()
    if commit not in cache:
        done = subprocess.run(["git", "-C", ROOT, "show", f"{commit}:docs/DECISION_REGISTER.md"],
                              capture_output=True, text=True)
        cache[commit] = done.stdout if done.returncode == 0 else ""
    if re.search(rf"^### {rid}(?=[ :\-–—])", cache[commit], re.M):
        with_heading.append((commit, rid))
    else:
        no_heading.append((commit, rid))
print("no heading at that commit:", len(no_heading))
print("a heading at that commit (the stricter rule):", len(with_heading), with_heading[:20])
print("other findings:", len(other), other[:5])
