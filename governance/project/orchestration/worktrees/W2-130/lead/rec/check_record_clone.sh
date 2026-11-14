#!/usr/bin/env bash
# Commit the record and LINK-RECONCILIATION.md in a throwaway clone at HEAD; compare gov links --all with build.json's after counts.
set -euo pipefail
T=/home/usain/gov-os-worktrees/W2-130
C=$T/.gov-runtime/scratch/tmp/clone-rec
rm -rf "$C"
git clone -q -s -n "$T" "$C"
git -C "$C" checkout -q --detach "$(git -C "$T" rev-parse HEAD)"
mkdir -p "$C/governance/project/orchestration/packages/LIFT-1"
cp "$T/docs/research/W2-130-link-cleanup.md" "$C/docs/research/W2-130-link-cleanup.md"
cp "$T/governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md" "$C/governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md"
git -C "$C" add -A
git -C "$C" -c user.name=check -c user.email=check@invalid commit -q -m "record" -m "Task: DAEO-q8cl
Role: orchestrator
Implements: DEC-1073, DEC-1109, DEC-1072, DEC-866, DEC-825, DEC-927, DEC-861, DEC-953, DEC-1010, DEC-1098, DEC-1088"
PYTHONPATH="$T/src" HOME="$T/.gov-runtime/scratch/empty-home" python3 -m gov.cli.main links --all --json --root "$C" > "$T/.gov-runtime/scratch/lead/rec/links-rec-clone.json" || true
python3 - <<'EOF'
import json, collections
d = json.load(open("/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/rec/links-rec-clone.json"))["result"]["findings"]
b = json.load(open("/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/rec/build.json"))["data"]["counts-after"]["by_code"]
mine = dict(collections.Counter(f["code"] for f in d))
print("same by_code:", mine == b, mine)
EOF
rm -rf "$C"
