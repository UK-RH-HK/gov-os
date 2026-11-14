#!/usr/bin/env bash
# Check the working-tree diff in a throwaway shared clone: commit it there and run gov links --all --json.
set -euo pipefail
T=/home/usain/gov-os-worktrees/W2-130
C=/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/tmp/clone-check
rm -rf "$C"
git clone -q -s -n "$T" "$C"
git -C "$C" checkout -q --detach "$(git -C "$T" rev-parse HEAD)"
git -C "$T" diff > /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/tmp/wt.diff
git -C "$C" apply /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/tmp/wt.diff
git -C "$C" -c user.name=check -c user.email=check@invalid commit -q -am "check" --trailer "Task: DAEO-q8cl" --trailer "Role: orchestrator"
PYTHONPATH="$T/src" HOME="$T/.gov-runtime/scratch/empty-home" python3 -m gov.cli.main links --all --json --root "$C" > "$T/.gov-runtime/scratch/lead/links-all-clone.json" || true
python3 - <<'EOF'
import json, yaml, glob
C = "/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/tmp/clone-check"
d = json.load(open("/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/links-all-clone.json"))
print(d["result"]["summary"][:500])
st = {}
for p in glob.glob(C + "/.tickets/*.md"):
    st[".tickets/" + p.split("/")[-1]] = (yaml.safe_load(open(p).read().split("---", 2)[1]) or {}).get("status")
live = [f for f in d["result"]["findings"] if f["code"] == "UNLINKED_ID" and st.get(f["path"]) in ("open", "in_progress")]
print("live unlinked", len(live))
import collections
print(collections.Counter(f["code"] for f in d["result"]["findings"]))
EOF
rm -rf "$C"
