"""Build ACT-LEADS-ADD-DIR-1's manifest.json from the bundle (the LB-A form) and print its sha256.

python3 -I build_manifest.py <bundle> <drafts> <rehearsal exit codes file or ''>
The checks are drafts/checks.json; their exits are the applied clone's (rehearsal section E)."""
import hashlib
import json
import os
import sys

bundle, drafts = sys.argv[1], sys.argv[2]
P = "governance/project/orchestration/tools/dispatch/launch_now.sh"


def sha(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


root, path, before, after = open(os.path.join(bundle, "list.txt")).read().strip().split("|")
assert root == "repo" and path == P
assert sha(os.path.join(bundle, "before/repo", P)) == before and sha(os.path.join(bundle, "after/repo", P)) == after
checks = json.load(open(os.path.join(drafts, "checks.json")))
files = {}
for rel in (f"before/repo/{P}", f"after/repo/{P}", "apply.sh", "list.txt", "rehearsal.log",
            "companion-tests.diff", "followup-tests.diff"):
    files[rel] = sha(os.path.join(bundle, rel))
manifest = {
    "act": "ACT-LEADS-ADD-DIR-1",
    "dec": "DEC-1161 (2), DEC-313, DEC-1157",
    "author": "cto",
    "claimed_class": "b",
    "touched": [{"root": "repo", "path": P, "before": before, "after": after}],
    "files": files,
    "checks": [{"cmd": cmd, "exit": 0, "count": None} for cmd in checks],
    "commands": [],
    "companion": {
        "diff": "companion-tests.diff",
        "lands": "before the apply (check 3 refuses the ACT until it has)",
        "touches": ["tests/acceptance/W2-153/test_w2_153_dispatch.py", "tests/unit/launch/test_w2_153_template.py"],
        "followup": "followup-tests.diff (two unit tests of the new line), after the apply",
    },
    "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
}
out = os.path.join(bundle, "manifest.json")
with open(out, "w", encoding="utf-8") as handle:
    json.dump(manifest, handle, indent=1)
    handle.write("\n")
print(sha(out))
