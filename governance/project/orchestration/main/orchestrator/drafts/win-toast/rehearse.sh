#!/usr/bin/env bash
# The rehearsal of ACT-WIN-TOAST-1, end to end as the operator runs it, in a scratch clone with a planted HOME.
# Only the root is substituted. Writes its log beside this script (rehearsal.log).
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
WORK=/tmp/gov-os-emg-d10/act-win-toast
rm -rf "$WORK"; mkdir -p "$WORK/home"
git clone -q --no-hardlinks "$MAIN" "$WORK/clone" && git -C "$WORK/clone" checkout -q --detach "$(git -C "$MAIN" rev-parse w2/integrate)"
D=$WORK/clone/.gov-runtime/scratch/orchestrator/drafts/win-toast
mkdir -p "$D"; cp "$HERE/apply.sh" "$HERE/test-map.candidate.yaml" "$D/"
export HOME=$WORK/home PYTHONUSERBASE=/home/usain/.local TMPDIR=$WORK/tmp; mkdir -p "$TMPDIR"
cd "$WORK/clone"
echo "== clone at $(git rev-parse --short=12 HEAD)"
echo "== check";  bash "$D/apply.sh" check; echo "exit $?"
echo "== apply";  bash "$D/apply.sh" apply; echo "exit $?"
echo "== diff";   git diff --stat
echo "== check after"; bash "$D/apply.sh" check; echo "exit $?"
echo "== the selection places win_toast.ps1 nowhere now (a change to it runs the full set)"
PYTHONPATH=$WORK/clone/src python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path("governance/project/test-map.yaml").read_text())
ro = m.get("record_only") or []
print("record_only entries:", len(ro), "| win_toast.ps1 listed:", any("win_toast.ps1" in str(e) for e in ro))
PY
echo "== W2-66's live test map suite (both opt-ins)"
PYTHONPATH=$WORK/clone/src python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --optin=lifted,breadth tests/acceptance/W2-66/test_w2_66_live_test_map.py 2>&1 | tail -2
echo "== undo"; bash "$D/apply.sh" undo; echo "exit $?"; git diff --stat | tail -1; echo "(empty diff after undo)"
echo "== F3: apply refuses a changed candidate"; cp "$D/test-map.candidate.yaml" "$WORK/cand.bak"; echo "# x" >> "$D/test-map.candidate.yaml"; bash "$D/apply.sh" apply; echo "exit $? (expected 1)"; git diff --stat | tail -1; cp "$WORK/cand.bak" "$D/test-map.candidate.yaml"
echo "== F2: undo refuses after a later change"; bash "$D/apply.sh" apply >/dev/null; echo "# later" >> governance/project/test-map.yaml; bash "$D/apply.sh" undo; echo "exit $? (expected 1)"; tail -1 governance/project/test-map.yaml; git checkout -q -- governance/project/test-map.yaml
cd /; rm -rf "$WORK"
echo "== done"
