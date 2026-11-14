"""W2-130 S5: every Task: and Implements: trailer value in `git log <rev>`'s history that names no record.

Run from the repository's root as `python3 - <rev>` (this script on stdin); standard library and git only; reads
git, writes nothing. A value is read from git's own trailer block (`%(trailers:key=Task,key=Implements,unfold)`),
split on commas and white space. `Task:` names no record when a token is neither `decision-record` (valid under
DEC-861) nor a ticket file `.tickets/<token>.md` at <rev>; `Implements:` names no record when a token is none of: a
register entry (`### DEC-n` in docs/DECISION_REGISTER.md at <rev>), a ticket id, a W2 id (a ticket's `wbs_id` or
`external-ref`), or a capability or master-rule id of docs/contract/contract.yaml at <rev>.
Prints one JSON list of {"trailer", "value", "tokens", "commits"} ((trailer, value) once; tokens: the unresolved
elements; commits: every commit carrying it, newest first).
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
                          check=False).stdout


rev = git("rev-parse", "--verify", sys.argv[1] + "^{commit}").strip()
log = git("log", "--format=%x1e%H%x1f%(trailers:key=Task,key=Implements,unfold)", rev)
tickets = {Path(name).stem for name in git("ls-tree", "--name-only", rev, ".tickets/").split()}
aliases = set(re.findall(r"(?m)^(?:wbs_id|external-ref): *(\S+)",
                         git("grep", "-h", "-E", "^(wbs_id|external-ref):", rev, "--", ".tickets")))
register = set(re.findall(r"(?m)^### (DEC-\d+)\b", git("show", f"{rev}:docs/DECISION_REGISTER.md")))
contract = git("show", f"{rev}:docs/contract/contract.yaml")
capabilities = set(re.findall(r"\b(?:CAP-\d+(?:\.[a-z])?|MR-\d+)\b", contract))
known = register | tickets | aliases | capabilities
found = {}
for item in log.split("\x1e")[1:]:
    sha, block = item.split("\x1f", 1)
    for line in block.splitlines():
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        tokens = [t for t in re.split(r"[,\s]+", value) if t]
        if key == "Task":
            bad = [t for t in tokens if t != "decision-record" and t not in tickets]
        elif key == "Implements":
            bad = [t for t in tokens if t not in known]
        else:
            continue
        if bad:
            entry = found.setdefault((key, value), {"trailer": key, "value": value, "tokens": bad, "commits": []})
            if sha not in entry["commits"]:
                entry["commits"].append(sha)
print(json.dumps([found[k] for k in sorted(found)]))
