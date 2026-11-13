#!/usr/bin/env bash
# The CTO's check before a hand merge (DEC-1141 (4): "each after S6 and the unit suites run on the merge"):
#   hand_merge_check.sh <W2> <head12> <acceptance folder>
# A --no-hardlinks clone of w2/integrate under ~/gov-os-runs/W2-00/hm-<W2>, the ticket's head merged with --no-ff (in the clone
# only), then the ticket's acceptance folder and tests/unit, each one pytest through heavy_slot.sh, TMPDIR outside the repository.
# Prints each run's pytest summary line; exit 0 only when the merge is clean and both runs have 0 failed. Nothing in the main tree.
# Exit 4: the kernel gate (kernel_gate.py) refused or failed, before the merge; nothing merged in the clone.
set -u
W2=$1 HEAD=$2 ACC=$3
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
ORCH=$MAIN/.gov-runtime/scratch/orchestrator
R=/home/usain/gov-os-runs/W2-00/hm-$W2
T=/tmp/claude-1000/hm-tmp-$W2  # TMPDIR outside the repository and outside ~/gov-os-runs (a test reads the runs root)
chmod -R u+w "$R" "$T" 2>/dev/null; rm -rf "$R" "$T"; mkdir -p "$R" "$T"
git clone -q --no-hardlinks --branch w2/integrate "$MAIN" "$R/clone" || exit 2
cd "$R/clone" || exit 2
git fetch -q "$MAIN" "refs/heads/w2/$W2" || exit 2
case "$(git rev-parse FETCH_HEAD)" in "$HEAD"*) ;; *) echo "w2/$W2 is not at $HEAD: $(git rev-parse --short=12 FETCH_HEAD)"; exit 2;; esac
# The kernel gate (owner, 2026-11-12, "item 5 (a)"): a kernel path needs the owner's approval; on the fetched commit itself
python3 "$ORCH/tools/kernel_gate.py" --repo "$MAIN" --branch "$(git rev-parse FETCH_HEAD)" || { echo "KERNEL GATE REFUSED"; exit 4; }
git -c user.name=cto -c user.email=cto@localhost merge -q --no-ff --no-edit FETCH_HEAD || { echo "MERGE CONFLICT"; git status --short | head; exit 3; }
echo "merged $W2 $HEAD onto $(git rev-parse --short=12 HEAD^1): $(git rev-parse --short=12 HEAD)"
rc=0
for sel in "$ACC" tests/unit; do
  out=$(TMPDIR="$T" PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$R/clone/src" \
        bash "$ORCH/tools/heavy_slot.sh" python3 -m pytest -q -rf -p no:cacheprovider -o tmp_path_retention_policy=failed "$sel" 2>&1 | grep -E "^FAILED|^ERROR| passed| failed" | tail -12)
  printf '%s\n' "$out" | grep -E "^(FAILED|ERROR)" | sed "s/^/  /"
  line=$(printf '%s\n' "$out" | grep -E '[0-9]+ (passed|failed)' | tail -1)
  echo "$sel: ${line:-no summary: $(printf '%s' "$out" | tail -1)}"
  printf '%s' "$line" | grep -qE '[0-9]+ failed|error' && rc=1
  [ -z "$line" ] && rc=1
done
echo "hand_merge_check $W2: exit $rc"
exit $rc
