"""Build ACT-GUARD-FIX-5's manifest.json from the bundle (ACT-DISPATCH-NIGHTLY-SLOT-1's form) and print its sha256.

python3 -I build_manifest.py <bundle> <drafts>
The checks are drafts/checks.json; their exits are the applied clone's (rehearsal B9)."""
import hashlib
import json
import os
import sys

bundle, drafts = sys.argv[1], sys.argv[2]
P = ".claude/hooks/bash_writes.py"


def sha(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


root, path, before, after = open(os.path.join(bundle, "list.txt")).read().strip().split("|")
assert root == "repo" and path == P
assert sha(os.path.join(bundle, "before/repo", P)) == before and sha(os.path.join(bundle, "after/repo", P)) == after
checks = json.load(open(os.path.join(drafts, "checks.json")))
files = {}
for rel in (f"before/repo/{P}", f"after/repo/{P}", "apply.sh", "list.txt", "rehearsal.log", "followup-tests.diff"):
    files[rel] = sha(os.path.join(bundle, rel))
manifest = {
    "act": "ACT-GUARD-FIX-5",
    "dec": "DEC-953 (item 2), DEC-958, DEC-1050 (12)",
    "author": "cto",
    "claimed_class": "b",
    "touched": [{"root": "repo", "path": P, "before": before, "after": after}],
    "files": files,
    "checks": [{"cmd": cmd, "exit": 0, "count": None} for cmd in checks],
    "commands": [],
    "companion": {
        "diff": "followup-tests.diff",
        "lands": "after the apply (31 of its 67 new cases are red on the before)",
        "touches": ["tests/unit/hooks/test_live_hook.py", "tests/unit/hooks/fixtures/f1_shell_options.json",
                    "tests/unit/hooks/fixtures/f1_round2_cases.json"],
    },
    "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
}
out = os.path.join(bundle, "manifest.json")
with open(out, "w", encoding="utf-8") as handle:
    json.dump(manifest, handle, indent=1)
    handle.write("\n")
print(sha(out))
